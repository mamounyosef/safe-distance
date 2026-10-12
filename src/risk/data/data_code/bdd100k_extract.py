"""Extract our drawn BDD100K clips into the Modal Volume and decode their frames (Modal, CPU only).

For every clip in src/risk/data/bdd100k_ids/zip_index.json (made by bdd100k_draw.py):
  1. download its bytes straight out of the 1.97 TB Hugging Face zip with HTTP byte
     ranges, check them against the zip's checksum (CRC), and save the video:
         /data/bdd100k/videos/100k/<split>/<id>.mov
  2. decode the frames BADAS sees (8 per second, 224x224 RGB, raw uint8) and save:
         /data/cache/badas224/bdd100k_videos_100k_<split>/<id>.npy
     (same frames and same layout as the cache made by badas_modal.py --cache)

Resume-safe: each clip is saved as soon as it is done, and a re-run skips clips
that are already saved. Progress, speed, ETA and cost are printed as it goes,
and a summary is written to src/risk/data/bdd100k_ids/extract_summary.json.

RUN IT (see current_modal_commands.txt):

    python -m modal run src\\risk\\data\\data_code\\bdd100k_extract.py --limit 2   # timed test: 2 clips per split
    python -m modal run src\\risk\\data\\data_code\\bdd100k_extract.py             # all 4,500
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import modal
from huggingface_hub import get_token

# Repo paths exist only on this PC; inside a Modal container the script sits alone in /root.
REPO = Path(__file__).resolve().parents[4] if modal.is_local() else Path("/root")
if modal.is_local():
    sys.path.insert(0, str(REPO / "scripts"))     # split_zip_remote.py (byte-range reader for the zip)

# ---- CONFIG ----
VOLUME = "safe-distance-data"
IDS_DIR = REPO / "src/risk/data/bdd100k_ids"
VIDEO_DIR = "bdd100k/videos/100k"                  # inside the Volume: <VIDEO_DIR>/<split>/<id>.mov
FRAME_CACHE_DIR = "cache/badas224"                 # same cache folder as badas_modal.py
CPU, MEMORY_MB = 2, 2048                           # per container
MAX_CONTAINERS = 16
PRINT_EVERY = 25                                   # progress line every 25 clips
# Modal prices: $0.0473 per physical core per hour, $0.008 per GiB of memory per hour
COST_PER_CONTAINER_S = (CPU * 0.0473 + MEMORY_MB / 1024 * 0.008) / 3600
# ----------------

app = modal.App("safe-distance-bdd100k-extract")
volume = modal.Volume.from_name(VOLUME)
secret = modal.Secret.from_dict({"HF_TOKEN": get_token() or ""})
image = (modal.Image.debian_slim(python_version="3.12").apt_install("libgl1", "libglib2.0-0")
         .pip_install("opencv-python-headless", "numpy", "requests", "huggingface_hub")
         .add_local_python_source("split_zip_remote"))


def decode_frames(path: str):
    """The frames BADAS sees, in ONE pass: frame round(i x fps / 8) for i = 0, 1, 2 ...,
    resized to 224x224, BGR turned into RGB. Identical to badas_modal.decode_frames."""
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(path)
    fps, total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    wanted = [w for w in (int(round(i * fps / 8.0)) for i in range(int(round(total / fps * 8.0)))) if w < total]
    frames, k, j = [], 0, 0
    while j < len(wanted):
        ok, img = cap.read()
        if not ok:
            break
        while j < len(wanted) and wanted[j] == k:     # this video frame is one BADAS uses
            frames.append(cv2.cvtColor(cv2.resize(img, (224, 224)), cv2.COLOR_BGR2RGB))
            j += 1
        k += 1
    cap.release()
    return np.stack(frames) if frames else np.zeros((0, 224, 224, 3), np.uint8), fps


@app.function(image=image, cpu=CPU, memory=MEMORY_MB, volumes={"/data": volume}, secrets=[secret],
              timeout=1800, max_containers=MAX_CONTAINERS, retries=2)
def extract(cid: str, clip: dict) -> dict:
    """Download, check and save one clip, then decode and save its frames. Skips finished steps."""
    import os
    import struct
    import zlib

    import numpy as np
    from split_zip_remote import SplitHttpFile

    start = time.time()
    video = Path("/data", VIDEO_DIR, clip["split"], f"{cid}.mov")
    frames_out = Path("/data", FRAME_CACHE_DIR, f"{VIDEO_DIR}/{clip['split']}".replace("/", "_"), f"{cid}.npy")
    if video.exists() and frames_out.exists():
        return {"id": cid, "split": clip["split"], "skipped": True}
    rec = {"id": cid, "split": clip["split"], "skipped": False, "download_s": 0.0, "mb": 0.0}

    # 1. Video: the zip's local header (30 bytes + name + extra field) comes right before the data.
    if not video.exists():
        t = time.time()
        f = SplitHttpFile(os.environ["HF_TOKEN"] or None)
        f.seek(clip["header_offset"])
        header = f.read(30)
        name_len, extra_len = struct.unpack("<HH", header[26:30])
        f.seek(clip["header_offset"] + 30 + name_len + extra_len)
        data = f.read(clip["size"])
        if len(data) != clip["size"] or zlib.crc32(data) != clip["crc"]:
            raise RuntimeError(f"{cid}: download does not match the zip's size/checksum")
        video.parent.mkdir(parents=True, exist_ok=True)
        tmp = video.with_suffix(".part")                      # write, then rename: no half-written files
        tmp.write_bytes(data)
        tmp.rename(video)
        rec["download_s"], rec["mb"] = round(time.time() - t, 1), round(len(data) / 1e6, 1)

    # 2. Frames (raw uint8, n x 224 x 224 x 3).
    t = time.time()
    frames, fps = decode_frames(str(video))
    if len(frames) < 16:
        raise RuntimeError(f"{cid}: only {len(frames)} frames decoded")
    frames_out.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(frames_out) + ".part.npy", frames)
    Path(str(frames_out) + ".part.npy").rename(frames_out)
    volume.commit()
    rec.update(decode_s=round(time.time() - t, 1), frames=len(frames), fps=round(fps, 2),
               seconds=round(len(frames) / 8.0, 1), total_s=round(time.time() - start, 1))
    return rec


def clock(sec: float) -> str:
    """Seconds as 1h02m03s / 2m03s / 3s."""
    sec = int(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s" if m else f"{s}s"


@app.local_entrypoint()
def main(limit: int = 0) -> None:
    index = json.loads((IDS_DIR / "zip_index.json").read_text())["clips"]
    jobs = list(index.items())
    if limit:                                          # test run: the first `limit` clips of each split
        jobs = [j for s in ("train", "val", "test") for j in [j for j in jobs if j[1]["split"] == s][:limit]]
    per_split = {s: sum(c["split"] == s for _, c in jobs) for s in ("train", "val", "test")}
    print(f"{len(jobs):,} clips {per_split}, {MAX_CONTAINERS} containers x {CPU} CPU / {MEMORY_MB} MB")

    start, recs, failed = time.time(), [], []
    for r in extract.starmap(jobs, return_exceptions=True, order_outputs=False):
        if isinstance(r, Exception):
            failed.append(repr(r))                     # repr: shows the error type even with no message
            print(f"  FAILED: {r}", flush=True)
        else:
            recs.append(r)
        done = len(recs) + len(failed)
        if done % PRINT_EVERY == 0 or done == len(jobs):
            new = [x for x in recs if not x["skipped"]]
            elapsed = time.time() - start
            rate = done / elapsed
            cont_s = sum(x["total_s"] for x in new)
            mb = sum(x["mb"] for x in new)
            print(f"  {done:,}/{len(jobs):,} clips  new={len(new):,} skipped={len(recs) - len(new):,} "
                  f"failed={len(failed)}  elapsed={clock(elapsed)}  ETA={clock((len(jobs) - done) / rate)}  "
                  f"{rate * 60:.1f} clips/min  downloaded={mb / 1e3:.1f} GB  "
                  f"avg/clip: download {sum(x['download_s'] for x in new) / max(len(new), 1):.1f} s, "
                  f"decode {sum(x['decode_s'] for x in new) / max(len(new), 1):.1f} s  "
                  f"cost so far=${cont_s * COST_PER_CONTAINER_S:.2f}", flush=True)

    new = [x for x in recs if not x["skipped"]]
    cont_s = sum(x["total_s"] for x in new)
    summary = {"clips": len(jobs), "new": len(new), "skipped": len(recs) - len(new), "failed": len(failed),
               "failures": failed, "wall_s": round(time.time() - start), "container_s": round(cont_s),
               "cost_usd_estimate": round(cont_s * COST_PER_CONTAINER_S, 3),
               "gb_downloaded": round(sum(x["mb"] for x in new) / 1e3, 2),
               "avg_download_s": round(sum(x["download_s"] for x in new) / max(len(new), 1), 2),
               "avg_decode_s": round(sum(x["decode_s"] for x in new) / max(len(new), 1), 2),
               "per_clip": sorted(new, key=lambda x: x["id"])}
    if new and limit:                                  # what the full run would cost and take
        per_clip = cont_s / len(new)
        summary["full_run_estimate"] = {"cost_usd": round(per_clip * len(index) * COST_PER_CONTAINER_S, 2),
                                        "wall_s": round(per_clip * len(index) / MAX_CONTAINERS)}
        print(f"full run estimate ({len(index):,} clips): ${summary['full_run_estimate']['cost_usd']:.2f}, "
              f"about {clock(summary['full_run_estimate']['wall_s'])} with {MAX_CONTAINERS} containers")
    out = IDS_DIR / ("extract_summary_test.json" if limit else "extract_summary.json")
    out.write_text(json.dumps(summary, indent=1))
    print(f"done: {len(new)} new, {summary['skipped']} skipped, {len(failed)} failed; "
          f"cost about ${summary['cost_usd_estimate']:.2f}; saved {out}")
