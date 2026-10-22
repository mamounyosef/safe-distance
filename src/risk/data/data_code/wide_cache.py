"""Build the 16:9 frame cache (256 x 448, shape kept) for every clip stage 1 uses (Modal, CPU only).

Decodes straight from the videos already in the data volume (no download, no zips), with frames.decode_frames(wide=
True): 8 frames per second (frame round(i x fps / 8)), each shrunk to 455 x 256 and cut to the middle 448 x 256
(src/risk/wide_input.py). Saved as one <clip>.npy per clip (n x 256 x 448 x 3, uint8) in:
    /data/cache/wide256x448/<folder>/<clip>.npy
with the same folder names as the old squashed cache (cache/badas224/), which is left untouched.

Clips:
    Nexar train crash + normal (1,500) and Nexar Public test (667). Nexar Private is NOT decoded (final score only).
    BDD100K train: the 2,576 clean clips. BDD100K val: all 500. BDD100K test: all 1,000 (for the final score).

Resume-safe: a clip already saved is skipped. Progress, ETA and cost are printed; a summary is written to
src/risk/data/wide_cache_summary.json.

RUN IT (from the repo root):
    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session18.toml"
    python -m modal run src\\risk\\data\\data_code\\wide_cache.py --limit 2    # timed test: 2 clips per folder
    python -m modal run src\\risk\\data\\data_code\\wide_cache.py              # everything
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import modal

LOCAL = modal.is_local()
REPO = Path(__file__).resolve().parents[4] if LOCAL else Path("/root")
if LOCAL:
    sys.path.insert(0, str(Path(__file__).resolve().parent))          # frames.py
    sys.path.insert(0, str(REPO / "src/risk"))                        # wide_input.py
from frames import decode_frames  # noqa: E402

# ---- CONFIG ----
VOLUME = "safe-distance-data"
CACHE_DIR = "cache/wide256x448"                     # the new 16:9 cache (the old one is cache/badas224)
NEXAR_FOLDERS = ["train/positive", "train/negative", "test-public/positive", "test-public/negative"]
BDD_LISTS = {"train": REPO / "src/risk/data/bdd100k_ids/train_clean.txt",     # the 2,576 clean clips
             "val": REPO / "src/risk/data/bdd100k_ids/val_500.txt",
             "test": REPO / "src/risk/data/bdd100k_ids/test_1000.txt"}
CPU, MEMORY_MB = 2, 3072                            # per container (a 40 s clip = about 110 MB of frames)
MAX_CONTAINERS = 64                                 # many CPU containers at once: same cost, 4x faster
PRINT_EVERY = 50
SUMMARY = REPO / "src/risk/data/wide_cache_summary.json"
# Modal prices: $0.0473 per physical core per hour, $0.008 per GiB of memory per hour
COST_PER_CONTAINER_S = (CPU * 0.0473 + MEMORY_MB / 1024 * 0.008) / 3600
# ----------------

app = modal.App("safe-distance-wide-cache")
volume = modal.Volume.from_name(VOLUME)
image = (modal.Image.debian_slim(python_version="3.12").apt_install("libgl1", "libglib2.0-0")
         .pip_install("opencv-python-headless", "numpy")
         .add_local_python_source("frames")
         .add_local_file(str(REPO / "src/risk/wide_input.py"), "/root/wide_input.py"))


def jobs() -> list[tuple[str, str]]:
    """(video path in the volume, cache folder name) for every clip to decode."""
    out = []
    if LOCAL:
        for split, ids_file in BDD_LISTS.items():
            for c in ids_file.read_text().split():
                out.append((f"bdd100k/videos/100k/{split}/{c}.mov", f"bdd100k_videos_100k_{split}"))
    return out


@app.function(image=image, volumes={"/data": volume})
def nexar_videos() -> list[tuple[str, str]]:
    """The Nexar videos (listed inside the volume)."""
    return [(f"nexar/{f}/{p.name}", f"nexar_{f.replace('/', '_')}") for f in NEXAR_FOLDERS
            for p in sorted(Path("/data/nexar", f).glob("*.mp4"))]


@app.function(image=image, cpu=CPU, memory=MEMORY_MB, volumes={"/data": volume}, timeout=1800,
              max_containers=MAX_CONTAINERS, retries=2)
def cache(video: str, folder: str) -> dict:
    """Decode one clip at 256 x 448 and save its frames (skipped if already saved)."""
    import numpy as np

    out = Path("/data", CACHE_DIR, folder, f"{Path(video).stem}.npy")
    if out.exists():
        return {"video": video, "skipped": True}
    t = time.time()
    frames, fps = decode_frames(f"/data/{video}", wide=True)
    if len(frames) < 16 or frames.shape[1:] != (256, 448, 3):
        raise RuntimeError(f"{video}: {frames.shape} frames decoded")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(out) + ".part.npy", frames)                      # write, then rename: no half-written files
    Path(str(out) + ".part.npy").rename(out)
    volume.commit()
    return {"video": video, "skipped": False, "frames": len(frames), "fps": round(fps, 2),
            "decode_s": round(time.time() - t, 1)}


def clock(sec: float) -> str:
    """Seconds as 1h02m03s / 2m03s / 3s."""
    sec = int(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s" if m else f"{s}s"


@app.local_entrypoint()
def main(limit: int = 0, tag: str = "") -> None:      # tag: e.g. session19 (keeps each workspace's summary)
    todo = nexar_videos.remote() + jobs()
    total_all = len(todo)
    if limit:                                          # test run: the first `limit` clips of each folder
        folders = sorted({f for _, f in todo})
        todo = [j for f in folders for j in [j for j in todo if j[1] == f][:limit]]
    per_folder = {}
    for _, f in todo:
        per_folder[f] = per_folder.get(f, 0) + 1
    print(f"{len(todo):,} clips {per_folder}, {MAX_CONTAINERS} containers x {CPU} CPU / {MEMORY_MB} MB")

    start, recs, failed = time.time(), [], []
    for r in cache.starmap(todo, return_exceptions=True, order_outputs=False):
        if isinstance(r, Exception):
            failed.append(repr(r))
            print(f"  FAILED: {r!r}", flush=True)
        else:
            recs.append(r)
        done = len(recs) + len(failed)
        if done % PRINT_EVERY == 0 or done == len(todo):
            new = [x for x in recs if not x["skipped"]]
            elapsed = time.time() - start
            rate = done / elapsed
            print(f"  {done:,}/{len(todo):,} clips  new={len(new):,} skipped={len(recs) - len(new):,} "
                  f"failed={len(failed)}  elapsed={clock(elapsed)}  ETA={clock((len(todo) - done) / rate)}  "
                  f"cost so far=${sum(x['decode_s'] for x in new) * COST_PER_CONTAINER_S:.2f}", flush=True)

    new = [x for x in recs if not x["skipped"]]
    cont_s = sum(x["decode_s"] for x in new)
    summary = {"clips": len(todo), "new": len(new), "skipped": len(recs) - len(new), "failed": len(failed),
               "failures": failed, "per_folder": per_folder, "wall_s": round(time.time() - start),
               "container_s": round(cont_s), "cost_usd_estimate": round(cont_s * COST_PER_CONTAINER_S, 3)}
    if new and limit:                                  # what the full run would cost and take
        per_clip = cont_s / len(new)
        summary["full_run_estimate"] = {"cost_usd": round(per_clip * total_all * COST_PER_CONTAINER_S, 2),
                                        "wall_s": round(per_clip * total_all / MAX_CONTAINERS)}
        print(f"full run estimate ({total_all:,} clips): ${summary['full_run_estimate']['cost_usd']:.2f}, "
              f"about {clock(summary['full_run_estimate']['wall_s'])}")
    out = SUMMARY.with_name("wide_cache_summary_test.json") if limit else SUMMARY
    if tag:                                            # a second workspace: its own summary file
        out = out.with_name(f"{out.stem}_{tag}.json")
    out.write_text(json.dumps(summary, indent=1))
    print(f"done: {len(new)} new, {summary['skipped']} skipped, {len(failed)} failed; "
          f"cost about ${summary['cost_usd_estimate']:.2f}; saved {out}")
