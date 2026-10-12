"""Decode raw frames for Nexar train (1,500 clips) and Nexar Public test (672 clips) on Modal (CPU only).

The videos are already in the Volume (/data/nexar/...). For each clip we save the
frames BADAS sees (8 per second, 224x224 RGB, raw uint8) to:
    /data/cache/badas224/nexar_<split>_<positive|negative>/<id>.npy
(same layout as the BDD100K cache). Nexar Private is NOT decoded: it is kept
untouched for the final score.

Resume-safe: each clip is saved when done; a re-run skips saved clips. Progress,
ETA and cost are printed; a summary goes to src/risk/data/nexar_cache_summary.json.

RUN IT (see current_modal_commands.txt):

    python -m modal run src\\risk\\data\\data_code\\nexar_cache.py --limit 2   # timed test: 2 clips per folder
    python -m modal run src\\risk\\data\\data_code\\nexar_cache.py             # all 2,172
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import modal

# Repo paths exist only on this PC; inside a Modal container the script sits alone in /root.
REPO = Path(__file__).resolve().parents[4] if modal.is_local() else Path("/root")
if modal.is_local():
    sys.path.insert(0, str(Path(__file__).resolve().parent))      # frames.py
from frames import decode_frames  # noqa: E402

# ---- CONFIG ----
VOLUME = "safe-distance-data"
FOLDERS = ["train/positive", "train/negative", "test-public/positive", "test-public/negative"]
FRAME_CACHE_DIR = "cache/badas224"
CPU, MEMORY_MB = 2, 2048                           # per container
MAX_CONTAINERS = 16
PRINT_EVERY = 25
SUMMARY = REPO / "src/risk/data/nexar_cache_summary.json"
# Modal prices: $0.0473 per physical core per hour, $0.008 per GiB of memory per hour
COST_PER_CONTAINER_S = (CPU * 0.0473 + MEMORY_MB / 1024 * 0.008) / 3600
# ----------------

app = modal.App("safe-distance-nexar-cache")
volume = modal.Volume.from_name(VOLUME)
image = (modal.Image.debian_slim(python_version="3.12").apt_install("libgl1", "libglib2.0-0")
         .pip_install("opencv-python-headless", "numpy")
         .add_local_python_source("frames"))


@app.function(image=image, volumes={"/data": volume})
def clip_list() -> list[str]:
    """Every Nexar video to decode, as a path inside the Volume (nexar/<folder>/<id>.mp4)."""
    return [f"nexar/{f}/{p.name}" for f in FOLDERS for p in sorted(Path("/data/nexar", f).glob("*.mp4"))]


@app.function(image=image, cpu=CPU, memory=MEMORY_MB, volumes={"/data": volume}, timeout=1800,
              max_containers=MAX_CONTAINERS, retries=2)
def cache(video: str) -> dict:
    """Decode one clip and save its frames (skipped if already saved)."""
    import numpy as np

    folder = str(Path(video).parent).replace("/", "_")        # nexar_train_positive, ...
    out = Path("/data", FRAME_CACHE_DIR, folder, f"{Path(video).stem}.npy")
    if out.exists():
        return {"video": video, "skipped": True}
    t = time.time()
    frames, fps = decode_frames(f"/data/{video}")
    if len(frames) < 16:
        raise RuntimeError(f"{video}: only {len(frames)} frames decoded")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(out) + ".part.npy", frames)                      # write, then rename: no half-written files
    Path(str(out) + ".part.npy").rename(out)
    volume.commit()
    return {"video": video, "skipped": False, "frames": len(frames), "fps": round(fps, 2),
            "seconds": round(len(frames) / 8.0, 1), "decode_s": round(time.time() - t, 1)}


def clock(sec: float) -> str:
    """Seconds as 1h02m03s / 2m03s / 3s."""
    sec = int(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s" if m else f"{s}s"


@app.local_entrypoint()
def main(limit: int = 0) -> None:
    videos = clip_list.remote()
    total_all = len(videos)
    if limit:                                          # test run: the first `limit` clips of each folder
        videos = [v for f in FOLDERS for v in [v for v in videos if f"/{f}/" in v][:limit]]
    per_folder = {f: sum(f"/{f}/" in v for v in videos) for f in FOLDERS}
    print(f"{len(videos):,} clips {per_folder}, {MAX_CONTAINERS} containers x {CPU} CPU / {MEMORY_MB} MB")

    start, recs, failed = time.time(), [], []
    for r in cache.map(videos, return_exceptions=True, order_outputs=False):
        if isinstance(r, Exception):
            failed.append(repr(r))                     # repr: shows the error type even with no message
            print(f"  FAILED: {r!r}", flush=True)
        else:
            recs.append(r)
        done = len(recs) + len(failed)
        if done % PRINT_EVERY == 0 or done == len(videos):
            new = [x for x in recs if not x["skipped"]]
            elapsed = time.time() - start
            rate = done / elapsed
            print(f"  {done:,}/{len(videos):,} clips  new={len(new):,} skipped={len(recs) - len(new):,} "
                  f"failed={len(failed)}  elapsed={clock(elapsed)}  ETA={clock((len(videos) - done) / rate)}  "
                  f"{rate * 60:.1f} clips/min  avg decode {sum(x['decode_s'] for x in new) / max(len(new), 1):.1f} s"
                  f"  cost so far=${sum(x['decode_s'] for x in new) * COST_PER_CONTAINER_S:.2f}", flush=True)

    new = [x for x in recs if not x["skipped"]]
    cont_s = sum(x["decode_s"] for x in new)
    summary = {"clips": len(videos), "new": len(new), "skipped": len(recs) - len(new), "failed": len(failed),
               "failures": failed, "wall_s": round(time.time() - start), "container_s": round(cont_s),
               "cost_usd_estimate": round(cont_s * COST_PER_CONTAINER_S, 3),
               "per_clip": sorted(new, key=lambda x: x["video"])}
    if new and limit:                                  # what the full run would cost and take
        per_clip = cont_s / len(new)
        summary["full_run_estimate"] = {"cost_usd": round(per_clip * total_all * COST_PER_CONTAINER_S, 2),
                                        "wall_s": round(per_clip * total_all / MAX_CONTAINERS)}
        print(f"full run estimate ({total_all:,} clips): ${summary['full_run_estimate']['cost_usd']:.2f}, "
              f"about {clock(summary['full_run_estimate']['wall_s'])} with {MAX_CONTAINERS} containers")
    out = SUMMARY.with_name("nexar_cache_summary_test.json") if limit else SUMMARY
    out.write_text(json.dumps(summary, indent=1))
    print(f"done: {len(new)} new, {summary['skipped']} skipped, {len(failed)} failed; "
          f"cost about ${summary['cost_usd_estimate']:.2f}; saved {out}")
