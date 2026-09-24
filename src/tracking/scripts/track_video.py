"""Run detection plus tracking over a video and write an annotated copy.

Each object is labelled with its track ID (#7) and draws a trail of where its
road contact point has been. A stable ID and a smooth trail mean tracking is
working; an ID that keeps changing on the same car means it is not.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\tracking\\scripts\\track_video.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

import cv2
import numpy as np

# Make the repo root importable, so "src" resolves when this file is run
# directly. This file is at src/tracking/scripts/, three levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.detection.detector import Detector
from src.detection.drawing import colour_of, draw
from src.tracking.tracker import Tracker

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Input video and annotated output.
SOURCE = r"C:\Users\mamou\Videos\2026-09-21 20-45-12.mp4"
OUTPUT = "out/tracked.mp4"

# Detector settings, same meaning as in src/detection/scripts/detect_video.py.
WEIGHTS = "weights/yolo26s-seg.pt"
IMGSZ = 960
CONF = 0.05
HALF = True

# "botsort" (default) or "bytetrack". BoT-SORT adds camera motion
# compensation for our moving camera. On the KITTI tracking benchmark it cut
# ID switches by about 25% for cars and pedestrians and raised car MOTA from
# 64.8% to 72.0%, for 6 ms more per frame at KITTI's size (about 17 ms at
# 1080p). See src/tracking/benchmarks/kitti_tracking/COMPARISON.md.
TRACKER = "botsort"

# Tracker settings. Defaults are Ultralytics' except TRACK_LOW_THRESH.
# A track is continued by a detection scoring at least TRACK_HIGH_THRESH in
# the first matching pass, and at least TRACK_LOW_THRESH in the second chance
# pass. Ultralytics' default low threshold is 0.1, which would throw away
# every detection between our CONF (0.05) and 0.1, so it is lowered to match.
TRACK_HIGH_THRESH = 0.25
TRACK_LOW_THRESH = 0.05

# A detection must score at least this to START a new track. Higher means
# fewer short-lived false tracks, but new objects are picked up later.
NEW_TRACK_THRESH = 0.25

# Frames an unmatched track is kept alive before deletion. 30 = 1 s at 30 fps.
# Higher survives longer occlusions but risks re-attaching an old ID to a
# different object.
TRACK_BUFFER = 30

# How similar a prediction and a detection must be to match, 0 to 1.
# Higher accepts looser matches.
MATCH_THRESH = 0.8

# How many past positions each object's trail shows.
TRAIL_LENGTH = 30

# Tracks shorter than this many frames are counted as "short-lived" in the
# summary: usually a flickering false detection or an ID that broke.
SHORT_TRACK = 5

# Mask tint, frames to process (0 = all), live preview, preview size.
MASK_ALPHA = 0.4
MAX_FRAMES = 0
SHOW = True
SHOW_SCALE = 0.6

# ----------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Command-line overrides. Every default comes from the CONFIG block."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", default=SOURCE)
    ap.add_argument("--output", default=OUTPUT)
    ap.add_argument("--weights", default=WEIGHTS)
    ap.add_argument("--imgsz", type=int, default=IMGSZ)
    ap.add_argument("--conf", type=float, default=CONF)
    ap.add_argument("--tracker", default=TRACKER)
    ap.add_argument("--max-frames", type=int, default=MAX_FRAMES)
    ap.add_argument("--show", action="store_true", default=SHOW)
    ap.add_argument("--no-show", dest="show", action="store_false")
    return ap.parse_args()


def draw_trails(frame: np.ndarray, trails: dict, colours: dict) -> None:
    """Draw each track's recent contact points as a fading line."""
    for track_id, points in trails.items():
        pts = list(points)
        for k in range(1, len(pts)):
            thickness = max(1, int(3 * k / len(pts)))  # thicker towards the present
            cv2.line(frame, pts[k - 1], pts[k], colours[track_id], thickness, cv2.LINE_AA)


def main() -> None:
    args = parse_args()

    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.source}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"input:  {width}x{height} @ {fps:.2f} fps")
    print(f"config: {args.weights} imgsz={args.imgsz} conf={args.conf} tracker={args.tracker}")

    detector = Detector(weights=args.weights, conf=args.conf, imgsz=args.imgsz, half=HALF)
    tracker = Tracker(
        detector,
        method=args.tracker,
        track_high_thresh=TRACK_HIGH_THRESH,
        track_low_thresh=TRACK_LOW_THRESH,
        new_track_thresh=NEW_TRACK_THRESH,
        track_buffer=TRACK_BUFFER,
        match_thresh=MATCH_THRESH,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    trails: dict[int, deque] = defaultdict(lambda: deque(maxlen=TRAIL_LENGTH))
    trail_colours: dict[int, tuple] = {}
    lifetimes: dict[int, int] = defaultdict(int)  # frames each ID was seen
    times: list[float] = []
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        t0 = time.perf_counter()
        tracked = tracker.update(frame)
        times.append((time.perf_counter() - t0) * 1000.0)

        seen = set()
        for d in tracked:
            if d.track_id is None:
                continue
            seen.add(d.track_id)
            lifetimes[d.track_id] += 1
            cx, cy = d.contact_point
            trails[d.track_id].append((int(cx), int(cy)))
            trail_colours.setdefault(d.track_id, colour_of(d))
        # Trails of objects no longer tracked fade out instead of freezing.
        for track_id in list(trails):
            if track_id not in seen:
                trails[track_id].popleft()
                if not trails[track_id]:
                    del trails[track_id]

        annotated = draw(frame, tracked, MASK_ALPHA)
        draw_trails(annotated, trails, trail_colours)
        writer.write(annotated)
        frame_idx += 1

        if args.show:
            preview = cv2.resize(annotated, None, fx=SHOW_SCALE, fy=SHOW_SCALE)
            cv2.putText(
                preview, f"frame {frame_idx}  {times[-1]:.0f} ms  {len(tracked)} tracked  "
                f"{len(lifetimes)} IDs so far  [{args.tracker}]",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA,
            )
            cv2.imshow("safe-distance: tracking", preview)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\nstopped early by user")
                break

        if frame_idx % 100 == 0:
            print(f"  frame {frame_idx}: {len(tracked)} tracked, {len(lifetimes)} IDs so far")
        if args.max_frames and frame_idx >= args.max_frames:
            break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    if not times:
        raise SystemExit("No frames were read.")

    # Summary. Fewer IDs for the same scene and fewer short-lived tracks mean
    # steadier tracking; compare these between trackers on the same clip.
    warm = np.array(times[5:] if len(times) > 5 else times)
    lengths = np.array(list(lifetimes.values())) if lifetimes else np.array([0])
    short = int((lengths < SHORT_TRACK).sum())
    print(f"\nprocessed {frame_idx} frames -> {out_path}")
    print(f"unique track IDs: {len(lifetimes)}")
    print(f"track length (frames): median {np.median(lengths):.0f}, max {lengths.max()}")
    print(f"short-lived tracks (< {SHORT_TRACK} frames): {short} ({short / max(len(lengths), 1):.0%})")
    print(f"ms per frame (detect + track): median {np.median(warm):.1f}, p95 {np.percentile(warm, 95):.1f}")


if __name__ == "__main__":
    main()
