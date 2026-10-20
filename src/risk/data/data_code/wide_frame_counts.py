"""Count the frames of every clip in the 16:9 cache, once, and save the counts to a small file (Modal, CPU only).

Why: stage1_train.py needs each clip's length (a window can only end inside the clip). Reading about 5,000 file
headers from the Modal volume at the start of training, 32 at a time, choked the GPU container (no progress,
"heartbeat failed" messages), while an A100 was being paid for. Counting once here, on cheap CPU containers, and
shipping the result with the code means training reads no volume files to start.

Reads only each .npy file's header (its first bytes: shape and type), with plain file reads, not the frames.

Writes: src/risk/data/wide_frame_counts.json   {"<cache folder>/<clip>": number of frames, ...}

RUN IT (from the repo root):
    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session18.toml"
    python -m modal run src\\risk\\data\\data_code\\wide_frame_counts.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import modal

LOCAL = modal.is_local()
REPO = Path(__file__).resolve().parents[4] if LOCAL else Path("/root")

# ---- CONFIG ----
VOLUME = "safe-distance-data"
CACHE = "/data/cache/wide256x448"                   # the 16:9 cache (one <clip>.npy per clip)
FOLDERS = ["nexar_train_positive", "nexar_train_negative", "nexar_test-public_positive",
           "nexar_test-public_negative", "bdd100k_videos_100k_train", "bdd100k_videos_100k_val",
           "bdd100k_videos_100k_test"]
THREADS = 4                                         # header reads at once inside each folder's container (gentle)
OUT = REPO / "src/risk/data/wide_frame_counts.json"
# ----------------

app = modal.App("safe-distance-wide-frame-counts")
volume = modal.Volume.from_name(VOLUME)
image = modal.Image.debian_slim(python_version="3.12").pip_install("numpy")


def header_frames(path: str) -> int:
    """Number of frames in one .npy file, from its header only (the first bytes), with a plain read.

    Arguments:
        path: the clip's .npy file.
    """
    import numpy as np
    with open(path, "rb") as f:
        major, _ = np.lib.format.read_magic(f)                       # .npy format version
        read = np.lib.format.read_array_header_1_0 if major == 1 else np.lib.format.read_array_header_2_0
        shape, _, _ = read(f)                                        # e.g. (321, 256, 448, 3)
    return int(shape[0])


@app.function(image=image, volumes={"/data": volume}, cpu=1, memory=1024, timeout=1800)
def count_folder(folder: str) -> dict:
    """Frame counts of every clip in one cache folder.

    Arguments:
        folder: a folder name inside the cache (e.g. nexar_train_positive).
    """
    from concurrent.futures import ThreadPoolExecutor
    t = time.time()
    paths = sorted(p for p in Path(CACHE, folder).glob("*.npy") if not p.name.endswith(".part.npy"))
    with ThreadPoolExecutor(THREADS) as ex:
        counts = list(ex.map(header_frames, [str(p) for p in paths]))
    return {"folder": folder, "counts": {f"{folder}/{p.stem}": n for p, n in zip(paths, counts)},
            "seconds": round(time.time() - t, 1)}


@app.local_entrypoint()
def main() -> None:
    start, counts = time.time(), {}
    for r in count_folder.map(FOLDERS, order_outputs=False):        # one container per folder, all at once
        counts.update(r["counts"])
        print(f"  {r['folder']:<30} {len(r['counts']):>5} clips  {r['seconds']:>6.1f} s", flush=True)
    OUT.write_text(json.dumps(dict(sorted(counts.items())), indent=0))
    print(f"done: {len(counts):,} clips in {time.time() - start:.0f} s; saved {OUT}")
