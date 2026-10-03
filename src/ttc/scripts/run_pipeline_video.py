"""Run the WHOLE pipeline on a dashcam video and show it live (GPU).

    detection (YOLO26s-seg) -> tracking (BoT-SORT) -> distance (Metric3D v2
    Small FP16, CLAHE if the clip is dark) -> closing speed and Time To
    Collision (combined Kalman filter: distance + box growth) -> warning
    (TTC under 2.5 s for 2 frames in a row, objects in our path only)

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\ttc\\scripts\\run_pipeline_video.py

While processing, a live window shows progress (SPACE pause, Q stop). The
result is saved as a video (OUT_DIR) and then opened in a viewer with a slider
to move anywhere in it (see view_video.py for its keys).

Clips with crash labels:
    CCD (C:\\safe-distance-data\\ccd\\<id>.mp4): every clip is a real crash;
        Crash-1500.txt marks the crash frames (shown as a red band).
    Nexar (C:\\safe-distance-data\\nexar\\train\\positive\\<id>.mp4): crash or
        near-miss; metadata.csv gives the event time (red line) and the time a
        warning should come by (orange line).
Any other video works too, without the timeline marks.

Limits: these dashcams' lenses are unknown, so the focal length is GUESSED from
an assumed field of view (HFOV_DEG). A 10% focal error roughly halves distance
accuracy; the box-growth part of the filter does not need it.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.detection.detector import Detector  # noqa: E402
from src.distance.camera import Camera  # noqa: E402
from src.distance.depth_models import BACKENDS, DepthModelEstimator, EnhancedBackend  # noqa: E402
from src.tracking.tracker import Tracker  # noqa: E402
from ttc_demo import ObjectState, colour_of, header, label_of, plots_panel, text  # noqa: E402

# ---- CONFIG ----------------------------------------------------------------
VIDEO = r"C:\safe-distance-data\nexar\train\positive\00286.mp4"
# Nexar car-ahead clips, sharp: 00286, 00912, 00528, 00556, 00562 (cut-in).
# Nexar car-ahead clips, lower quality: 00060, 00142, 00543 (night), 00584, 00791 (night).
# CCD: any of C:\safe-distance-data\ccd\000001.mp4 ... 001500.mp4.
OPEN_VIEWER = True          # when done, open the saved video in the viewer (slider, steps)

HFOV_DEG = 110.0            # assumed horizontal field of view of the dashcam (guess)
CAMERA_HEIGHT_M = 1.3       # assumed dashcam height above the road
PROCESS_FPS = 10.0          # frames per second actually processed (the filter was tuned at 10)
NIGHT_BRIGHTNESS = 70       # mean image brightness (0-255) below which CLAHE is used
WEIGHTS = "weights/yolo26s-seg.pt"
CONF, IMGSZ = 0.25, 1280
DEPTH_MODEL = "metric3d-v2-small-fp16"
OUT_DIR = REPO / "out" / "pipeline"
# ----------------------------------------------------------------------------

CORRIDOR_M = 1.2            # "in our path" = box within 1.2 m of our centre line (as in the benchmarks)
GREY, RED, ORANGE, WHITE, CYAN = (150, 150, 150), (0, 0, 255), (0, 165, 255), (255, 255, 255), (255, 255, 0)


def crash_labels(video: Path) -> dict:
    """Crash timing from the dataset's labels, if the clip has any.
    Returns {"crash_s": [start, end] or None, "alert_s": time or None, "source": ...}."""
    ccd = video.parent / "Crash-1500.txt"
    if ccd.exists():
        for line in ccd.read_text().splitlines():
            if line.startswith(video.stem + ","):
                bins = json.loads(line[line.index("["):line.index("]") + 1])
                hit = [i for i, b in enumerate(bins) if b]
                return {"crash_s": [hit[0] / 10.0, (hit[-1] + 1) / 10.0] if hit else None,
                        "alert_s": None, "source": "CCD"}
    meta = video.parent / "metadata.csv"
    if meta.exists():
        for r in csv.DictReader(meta.open()):
            if r["file_name"] == video.name and r["time_of_event"]:
                return {"crash_s": [float(r["time_of_event"]), float(r["time_of_event"])],
                        "alert_s": float(r["time_of_alert"]) if r["time_of_alert"] else None, "source": "Nexar"}
    return {"crash_s": None, "alert_s": None, "source": None}


def lateral_gap_m(det, distance: float, camera: Camera) -> float:
    """Sideways gap (m) between our car's centre line and the object's nearest
    side, from the box edges: pixel offset / focal length x distance."""
    if det.x1 <= camera.cx <= det.x2:
        return 0.0
    edge_px = min(abs(det.x1 - camera.cx), abs(det.x2 - camera.cx))
    return edge_px / camera.fx * distance


def timeline(width: int, t_now: float, duration: float, labels: dict, warnings: list[float]) -> np.ndarray:
    """A strip under the video: red = crash (from the dataset's labels), orange
    line = when a warning should come by (Nexar), red ticks = our warnings."""
    bar = np.full((46, width, 3), 25, np.uint8)
    x = lambda t: int(10 + (width - 20) * min(max(t / duration, 0), 1))  # noqa: E731
    cv2.rectangle(bar, (10, 14), (width - 10, 30), (60, 60, 60), -1)
    if labels["crash_s"]:
        a, b = labels["crash_s"]
        cv2.rectangle(bar, (x(a), 10), (max(x(b), x(a) + 3), 34), (0, 0, 200), -1)
    if labels["alert_s"] is not None:
        cv2.line(bar, (x(labels["alert_s"]), 6), (x(labels["alert_s"]), 38), ORANGE, 2)
    for t in warnings:
        cv2.line(bar, (x(t), 16), (x(t), 28), RED, 1)
    cv2.line(bar, (x(t_now), 4), (x(t_now), 42), WHITE, 2)
    text(bar, f"{t_now:.1f} s", (min(x(t_now) + 4, width - 60), 44), WHITE, 0.4)
    return bar


class Models:
    """The networks, loaded once and reused for every clip (loading takes seconds)."""

    def __init__(self) -> None:
        self.detector = Detector(weights=WEIGHTS, conf=CONF, imgsz=IMGSZ)
        base = BACKENDS[DEPTH_MODEL]()
        self.depth_day = DepthModelEstimator(base, "p10")
        self.depth_night = DepthModelEstimator(EnhancedBackend(base, "clahe4"), "p10")  # same network, CLAHE first


def warning_episodes(times: list[float], gap_s: float = 0.5) -> list[list[float]]:
    """Group warning moments into episodes: [start, end] of each stretch of warnings."""
    episodes = []
    for t in times:
        if episodes and t - episodes[-1][1] <= gap_s:
            episodes[-1][1] = t
        else:
            episodes.append([t, t])
    return episodes


def run_clip(video: Path, models: Models, window: str, allow_skip: bool = False) -> str:
    """Process one clip live in `window` and save it. Returns "done" at the end of
    the clip, "quit" if Q was pressed, or "next" if R was pressed (allow_skip)."""
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w, h = int(cap.get(3)), int(cap.get(4))
    step = max(1, round(fps / PROCESS_FPS))
    duration = n_frames / fps
    labels = crash_labels(video)

    # Camera: focal length from the assumed field of view; centre of the image.
    fx = (w / 2) / math.tan(math.radians(HFOV_DEG) / 2)
    camera = Camera(fx=fx, fy=fx, cx=w / 2, cy=h / 2, height_m=CAMERA_HEIGHT_M, pitch_rad=0.0)

    # Dark clip? Then the depth model gets CLAHE-enhanced images (the detector never does).
    ok, first = cap.read()
    night = ok and float(cv2.cvtColor(first, cv2.COLOR_BGR2GRAY).mean()) < NIGHT_BRIGHTNESS
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    depth = models.depth_night if night else models.depth_day

    tracker = Tracker(models.detector, "botsort", track_low_thresh=0.05)   # fresh IDs for every clip
    states: dict[int, ObjectState] = {}
    warn_times: list[float] = []

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{labels['source'] or 'video'}_{video.stem}.mp4"
    writer = None
    paused, focus, k, result = False, None, 0, "done"
    print(f"{video.name}: {w}x{h}, {fps:.1f} fps, {duration:.1f} s; processing every {step} frame(s); "
          f"{'night: CLAHE on' if night else 'day'}; focal length {fx:.0f} px (assumed {HFOV_DEG:g} deg)")

    while True:
        ok, img = cap.read()
        if not ok:
            break
        if k % step:
            k += 1
            continue
        t = k / fps
        frame_no = k // step          # filter frame number: consecutive at PROCESS_FPS
        k += 1

        dets = tracker.update(img)
        dists = depth.estimate(img, dets, camera)
        warning, in_path_now = False, []
        for d, dist in zip(dets, dists):
            if d.track_id is None or dist is None:
                continue
            at_edge = d.x1 <= 3 or d.y1 <= 3 or d.x2 >= w - 3 or d.y2 >= h - 3
            st = states.setdefault(d.track_id, ObjectState())
            out = st.step(frame_no, dist, None if at_edge else d.y2 - d.y1)
            st.history.append({"t": t, **out, "measured_m": dist, "true_m": None,
                               "true_closing": None, "true_ttc": None})
            in_path = lateral_gap_m(d, out["distance"], camera) <= CORRIDOR_M
            warning |= in_path and out["warning"]
            colour = colour_of(out, in_path)
            cv2.rectangle(img, (int(d.x1), int(d.y1)), (int(d.x2), int(d.y2)), colour, 3 if in_path else 1)
            text(img, f"#{d.track_id} {d.class_name} " + label_of(out), (int(d.x1), max(int(d.y1) - 6, 14)),
                 colour, 0.5, backing=True)
            if in_path:
                in_path_now.append((out["distance"], d.track_id))
        if warning:
            warn_times.append(t)
        if in_path_now:
            focus = min(in_path_now)[1]

        crash = labels["crash_s"]
        status = "WARNING: collision risk ahead" if warning else f"{video.name}, t = {t:.1f} s"
        if crash and crash[0] <= t <= max(crash[1], crash[0] + 0.3):
            status += "   <<< CRASH (dataset label) >>>"
        top = header(w, [
            status,
            f"Pipeline: YOLO26s-seg -> BoT-SORT -> Metric3D v2 Small{' + CLAHE (dark clip)' if night else ''} "
            "-> combined Kalman filter -> warn if TTC < 2.5 s for 2 frames",
            f"Timeline: red band = crash ({labels['source'] or 'no labels'}), orange line = warning due by "
            f"(Nexar), red ticks = our warnings. Focal length assumed ({HFOV_DEG:g} deg view).",
        ], warning)
        hist = states[focus].history if focus in states else []
        panel = plots_panel(w, hist, t, f"Plots: object #{focus}, nearest in our path (no ground truth here)"
                            if focus in states else "Plots: no object in our path")
        pic = np.vstack([top, img, timeline(w, t, duration, labels, warn_times), panel])

        if writer is None:
            writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps / step,
                                     (pic.shape[1], pic.shape[0]))
        writer.write(pic)
        cv2.imshow(window, pic)
        key = cv2.waitKey(0 if paused else 1) & 0xFF
        if key == ord(" "):
            paused = not paused
        if key == ord("q"):
            result = "quit"
            break
        if allow_skip and key == ord("r"):
            result = "next"
            break

    if writer:
        writer.release()
    # Every warning episode is kept. The one that counts for the crash is the
    # first episode starting in the 4 s before the event; earlier ones are
    # false warnings (nothing about to happen yet).
    episodes = warning_episodes(warn_times)
    summary = {"video": str(video), "labels": labels, "night_clahe": bool(night), "focal_px": round(fx, 1),
               "finished": result == "done", "warning_episodes_s": [[round(a, 2), round(b, 2)] for a, b in episodes]}
    if labels["crash_s"]:
        event = labels["crash_s"][0]
        before = [a for a, _ in episodes if event - 4.0 <= a <= event + 0.5]
        summary["crash_warning_s"] = round(before[0], 2) if before else None
        summary["crash_warning_before_event_s"] = round(event - before[0], 2) if before else None
        summary["early_false_warnings"] = sum(1 for a, _ in episodes if a < event - 4.0)
    (OUT_DIR / f"{out_path.stem}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"saved {out_path}")
    return result


def main() -> None:
    window = "Safe distance: full pipeline"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    out_path = OUT_DIR / f"{crash_labels(Path(VIDEO))['source'] or 'video'}_{Path(VIDEO).stem}.mp4"
    run_clip(Path(VIDEO), Models(), window)
    cv2.destroyAllWindows()
    if OPEN_VIEWER:
        from view_video import view   # same folder
        view(str(out_path))


if __name__ == "__main__":
    main()
