"""Run the detector over a video and write an annotated copy.

This is the detection step only: no tracking, no distance, no warnings.
It exists to prove detection is stable across frames and to measure speed.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\detection\\scripts\\detect_video.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Make the repo root importable, so "src.detection" resolves when this file
# is run directly. This file is at src/detection/scripts/, three levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.detection.detector import Detector
from src.detection.drawing import draw

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Input video. This one is Lost and Found scene 04: real obstacles placed on
# the road, built from the dataset frames by scripts/frames_to_video.py.
SOURCE = "data/videos/lost_and_found_04.mp4"

# Annotated output video.
OUTPUT = "out/detected.mp4"

# Checkpoint: yolo26n / s / m / l / x .pt, fastest to most accurate.
# Add "-seg" (yolo26s-seg.pt) for segmentation: gives a pixel outline per
# object, so the road contact point lands on a tyre instead of a box corner.
# Use "weights/yoloe-11s-seg.pt" for open-vocabulary mode, where the classes
# are the words in ROAD_PROMPTS (src/detection/detector.py) instead of the
# fixed COCO 80. That one finds traffic cones and barriers; COCO cannot.

# "weights/yolo26s-seg.pt" (default: best on cars and pedestrians, see the
# KITTI benchmark) or "weights/yoloe-11s-seg.pt" (best on unusual obstacles,
# see the Lost and Found benchmark).
WEIGHTS = "weights/yolo26s-seg.pt"

# How strongly segmentation masks are tinted, 0.0 to 1.0. No effect on boxes.
MASK_ALPHA = 0.4

# "cuda" (GPU) or "cpu" (about 20x slower).
DEVICE = "cuda"

# Longest side fed to the model, multiple of 32. Aspect ratio is kept by
# padding (letterboxing), so 1920x1080 at 640 becomes 640x384.
# Measured on this clip: 640 and 960 both ~21 ms, 1280 ~26 ms, so we are not
# GPU-bound at the low end and 1280 is nearly free. At 640 the roadworks
# barriers are invisible; at 1280 they are detected. 640/960/1280.
IMGSZ = 960

# Minimum confidence, 0.0 to 1.0. Lower catches more but flickers.
CONF = 0.05

# FP16 (16-bit floating point): 1.5 to 2x faster on GPU, ignored on CPU.
HALF = True

# Cap on detections per frame. Road scenes never reach this.
MAX_DET = 300

# Detect every Nth frame. 1 = every frame. Higher saves compute but goes
# blind between detections, so raise it only if we miss the edge budget.
STRIDE = 1

# Frames to process. 0 = whole video.
MAX_FRAMES = 300000000000

# Show a live preview window while running. Press q to stop early.
SHOW = True

# Preview window size as a fraction of the video, so 1080p fits on screen.
SHOW_SCALE = 0.6

# ----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Command-line overrides. Every default comes from the CONFIG block."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default=SOURCE)
    ap.add_argument("--output", default=OUTPUT)
    ap.add_argument("--weights", default=WEIGHTS)
    ap.add_argument("--device", default=DEVICE)
    ap.add_argument("--imgsz", type=int, default=IMGSZ)
    ap.add_argument("--conf", type=float, default=CONF)
    ap.add_argument("--half", action="store_true", default=HALF)
    ap.add_argument("--no-half", dest="half", action="store_false")
    ap.add_argument("--max-det", type=int, default=MAX_DET)
    ap.add_argument("--stride", type=int, default=STRIDE)
    ap.add_argument("--max-frames", type=int, default=MAX_FRAMES)
    ap.add_argument("--show", action="store_true", default=SHOW)
    ap.add_argument("--no-show", dest="show", action="store_false")
    ap.add_argument("--show-scale", type=float, default=SHOW_SCALE)
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.source}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"input:  {width}x{height} @ {fps:.2f} fps, {total} frames")
    print(
        f"config: {args.weights} imgsz={args.imgsz} conf={args.conf} "
        f"half={args.half} stride={args.stride} device={args.device}"
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )

    detector = Detector(
        weights=args.weights,
        device=args.device,
        conf=args.conf,
        imgsz=args.imgsz,
        half=args.half,
        max_det=args.max_det,
    )

    times: list[float] = []
    counts: list[int] = []
    detections: list = []
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # With stride > 1 the skipped frames reuse the previous detections.
        if frame_idx % args.stride == 0:
            t0 = time.perf_counter()
            detections = detector.detect(frame)
            times.append((time.perf_counter() - t0) * 1000.0)

        counts.append(len(detections))
        annotated = draw(frame, detections, MASK_ALPHA)
        writer.write(annotated)
        frame_idx += 1

        if args.show:
            preview = cv2.resize(annotated, None, fx=args.show_scale, fy=args.show_scale)
            cv2.putText(
                preview, f"frame {frame_idx}  {times[-1]:.0f} ms  {len(detections)} obj",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA,
            )
            cv2.imshow("safe-distance: detection", preview)
            # waitKey also pumps the window's event loop, so it must be called
            # every frame or the window freezes. 1 ms is the shortest wait.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\nstopped early by user")
                break

        if frame_idx % 50 == 0:
            print(f"  frame {frame_idx}: {len(detections)} objects, {times[-1]:.1f} ms")
        if args.max_frames and frame_idx >= args.max_frames:
            break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    if not times:
        raise SystemExit("No frames were read.")

    # Drop the first few passes: they include CUDA warmup and are not typical.
    warm = np.array(times[5:] if len(times) > 5 else times)
    print(f"\nprocessed {frame_idx} frames -> {out_path}")
    print(f"detections per frame: mean {np.mean(counts):.1f}, max {max(counts)}")
    print(
        f"inference ms: mean {warm.mean():.1f}, median {np.median(warm):.1f}, "
        f"p95 {np.percentile(warm, 95):.1f}, min {warm.min():.1f}"
    )
    print(f"throughput: {1000.0 / warm.mean():.1f} detections per second")


if __name__ == "__main__":
    main()
