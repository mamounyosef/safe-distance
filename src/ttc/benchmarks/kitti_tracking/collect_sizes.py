"""Collect each object's IMAGE SIZE per frame on KITTI tracking (GPU, detector only).

Time To Collision can be measured without any distance: as an object gets
closer it grows in the image, and size / growth rate = time to collision
("looming"). This script saves the sizes it needs, for the same objects and
frames as the distance stability benchmark (labelled objects matched to the
detector's boxes, first 150 frames of all 21 sequences), so both can be joined
on (sequence, frame, track_id).

Saved per matched object and frame: the detector's box (x1, y1, x2, y2), its
mask outline's area and height, whether the box touches the image edge (a cut-off
object does not grow normally), and the laser truth.

Output: results/sizes_f150/observations.csv and a short info.json.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\kitti_tracking\\collect_sizes.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src/distance/benchmarks/kitti"))
sys.path.insert(0, str(REPO / "src/distance/benchmarks/kitti_tracking"))

from benchmark_distance_stability import CLASSES, DATA, FRAMES_PER_SEQUENCE, read_labels  # noqa: E402
from benchmark_kitti_distance import match  # noqa: E402
from src.detection.benchmarks.common import provenance  # noqa: E402
from src.detection.detector import Detector  # noqa: E402

# ---- CONFIG (detector settings identical to the stability benchmark) ----
WEIGHTS = "weights/yolo26s-seg.pt"
IMGSZ = 1280
CONF = 0.25
EDGE_MARGIN_PX = 3
OUT = Path(__file__).resolve().parent / "results" / "sizes_f150"
# -------------------------------------------------------------------------


def main() -> None:
    detector = Detector(weights=WEIGHTS, conf=CONF, imgsz=IMGSZ)
    rows, n_frames = [], 0
    sequences = sorted(p.name for p in (DATA / "image_02").iterdir() if p.is_dir())
    for seq in sequences:
        labels = read_labels(DATA / "label_02" / f"{seq}.txt")
        frames = sorted((DATA / "image_02" / seq).glob("*.png"))[:FRAMES_PER_SEQUENCE or None]
        for path in frames:
            frame_no = int(path.stem)
            gt = labels.get(frame_no, [])
            img = cv2.imread(str(path))
            h, w = img.shape[:2]
            dets = detector.detect(img)
            # Pair each labelled object with the detector box that overlaps it most
            # (same rule as the stability benchmark), then save that box's sizes.
            for gi, bi in match(gt, [(d.x1, d.y1, d.x2, d.y2) for d in dets]).items():
                g, d = gt[gi], dets[bi]
                has_mask = d.mask is not None and len(d.mask) >= 3   # mask = outline polygon in pixels
                rows.append({
                    "sequence": seq, "frame": frame_no, "track_id": g["track_id"], "class": CLASSES[g["type"]],
                    "x1": round(d.x1, 2), "y1": round(d.y1, 2), "x2": round(d.x2, 2), "y2": round(d.y2, 2),
                    "mask_area_px": round(float(cv2.contourArea(d.mask.astype(np.float32))), 1) if has_mask else "",
                    "mask_height_px": round(float(np.ptp(d.mask[:, 1])), 2) if has_mask else "",
                    "touches_edge": int(d.x1 <= EDGE_MARGIN_PX or d.y1 <= EDGE_MARGIN_PX
                                        or d.x2 >= w - EDGE_MARGIN_PX or d.y2 >= h - EDGE_MARGIN_PX),
                    "true_nearest_surface_m": round(g["true_nearest_surface_m"], 3),
                    "lateral_gap_m": round(g["lateral_gap_m"], 3),
                })
            n_frames += 1
        print(f"  sequence {seq}: {len(frames)} frames, {len(rows)} observations so far", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "observations.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "info.json").write_text(json.dumps({
        "provenance": provenance(), "weights": WEIGHTS, "imgsz": IMGSZ, "conf": CONF,
        "frames": n_frames, "sequences": len(sequences), "observations": len(rows),
        "edge_margin_px": EDGE_MARGIN_PX}, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
