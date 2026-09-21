"""Run the detector over a video and write an annotated copy.

This is the detection step only: no tracking, no distance, no warnings.
It exists to prove detection is stable across frames and to measure speed.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\detect_video.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.detection.detector import OTHER_CLASS, Detector

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Input video.
SOURCE = r"C:\Users\mamou\Videos\2026-09-21 20-45-12.mp4"

# Annotated output video.
OUTPUT = "out/detected.mp4"

# Checkpoint: yolo26n / s / m / l / x .pt, fastest to most accurate.
# Add "-seg" (yolo26s-seg.pt) for segmentation: gives a pixel outline per
# object, so the road contact point lands on a tyre instead of a box corner.
WEIGHTS = "weights/yolo26s-seg.pt"

# How strongly segmentation masks are tinted, 0.0 to 1.0. No effect on boxes.
MASK_ALPHA = 0.4

# "cuda" (GPU) or "cpu" (about 20x slower).
DEVICE = "cuda"

# Longest side fed to the model, multiple of 32. Aspect ratio is kept by
# padding (letterboxing), so 1920x1080 at 640 becomes 640x384.
# Higher sees distant objects better; cost scales with the square. 640/960/1280.
IMGSZ = 960

# Minimum confidence, 0.0 to 1.0. Lower catches more but flickers.
CONF = 0.4

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

# Colours are BGR (Blue, Green, Red), which is the order OpenCV uses.
COLOURS: dict[str, tuple[int, int, int]] = {
    "person": (0, 200, 255),
    "bicycle": (0, 200, 255),
    "motorcycle": (0, 200, 255),
    "car": (0, 255, 0),
    "bus": (0, 255, 0),
    "truck": (0, 255, 0),
    "train": (0, 255, 0),
    "cat": (255, 200, 0),
    "dog": (255, 200, 0),
    OTHER_CLASS: (160, 160, 160),
}


def draw(frame: np.ndarray, detections) -> np.ndarray:
    """Draw one box, label and (if present) mask per detection."""
    out = frame.copy()

    # Masks are filled on a separate layer and blended once, so overlapping
    # objects do not stack into an opaque blob.
    if any(d.mask is not None for d in detections):
        layer = out.copy()
        for d in detections:
            if d.mask is not None and len(d.mask) >= 3:
                colour = COLOURS.get(d.class_name, COLOURS[OTHER_CLASS])
                cv2.fillPoly(layer, [d.mask.astype(np.int32)], colour)
        cv2.addWeighted(layer, MASK_ALPHA, out, 1 - MASK_ALPHA, 0, out)

    for d in detections:
        colour = COLOURS.get(d.class_name, COLOURS[OTHER_CLASS])
        p1 = (int(d.x1), int(d.y1))
        p2 = (int(d.x2), int(d.y2))
        cv2.rectangle(out, p1, p2, colour, 2)

        label = f"{d.class_name} {d.confidence:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (p1[0], p1[1] - th - 6), (p1[0] + tw + 4, p1[1]), colour, -1)
        cv2.putText(
            out, label, (p1[0] + 2, p1[1] - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA,
        )

        # The road contact point the ground-plane distance estimator will use.
        # White ring = taken from the mask, so it sits on a tyre.
        # Hollow ring = box fallback, which sits on empty road if the car is angled.
        cx, cy = d.contact_point
        cv2.circle(out, (int(cx), int(cy)), 5, (255, 255, 255), -1 if d.mask is not None else 2)
        cv2.circle(out, (int(cx), int(cy)), 3, colour, -1)
    return out


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
        annotated = draw(frame, detections)
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
