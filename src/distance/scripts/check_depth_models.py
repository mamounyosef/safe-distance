"""Check that depth models load and run: one KITTI image per model.

A quick, near-free test before any benchmark: catches install problems,
missing downloads and wrong output scales for a few seconds per model. Models
are loaded one at a time and freed before the next, to keep GPU memory low.

For each model it prints the inference time, peak GPU memory, the range of
depths it predicted, and its median depth inside three labelled cars next to
their laser-measured distances.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\distance\\scripts\\check_depth_models.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import gc
import math
import sys
import traceback
from pathlib import Path

import cv2
import numpy as np
import torch

# Make the repo root importable. This file is at src/distance/scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.distance.camera import Camera
from src.distance.depth_models import BACKENDS

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Models to check, by name from BACKENDS in src/distance/depth_models.py.
# None = all of them.
MODELS = None

# KITTI image to test on. 000009 has three labelled cars at 24, 66 and 68 m.
IMAGE_ID = "000009"
DATA = Path("data/kitti/training")

# ----------------------------------------------------------------------------


def main() -> None:
    names = MODELS or list(BACKENDS)
    img = cv2.imread(str(DATA / "image_2" / f"{IMAGE_ID}.png"))
    cam = Camera.from_kitti_calib(DATA / "calib" / f"{IMAGE_ID}.txt")
    cars = []
    for line in (DATA / "label_2" / f"{IMAGE_ID}.txt").read_text().splitlines():
        f = line.split()
        if f and f[0] == "Car":
            x1, y1, x2, y2 = map(float, f[4:8])
            cars.append(((int(x1), int(y1), int(x2), int(y2)), math.hypot(float(f[11]), float(f[13]))))

    for name in names:
        backend = None
        try:
            backend = BACKENDS[name]()
            backend.predict(img, cam)                 # load + first (warm-up) pass
            depth = backend.predict(img.copy(), cam)  # timed second pass (a copy defeats the cache)
            reads = [f"{np.median(depth[y1:y2, x1:x2]):5.1f}/{true:4.1f}" for (x1, y1, x2, y2), true in cars]
            mem = torch.cuda.max_memory_allocated() / 1e9
            print(f"OK   {name:18s} {backend.times_ms[-1]:7.1f} ms  peak GPU {mem:4.1f} GB  "
                  f"range {np.nanmin(depth):5.1f}-{np.nanmax(depth):6.1f}  cars est/true: {'  '.join(reads)}",
                  flush=True)
        except Exception as e:
            print(f"FAIL {name:18s} {type(e).__name__}: {str(e)[:200]}", flush=True)
            traceback.print_exc(limit=3, file=sys.stdout)
        finally:
            backend = None
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()


if __name__ == "__main__":
    main()
