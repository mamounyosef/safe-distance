"""Visual demo of the Time To Collision (TTC) stage, with the best method so far.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\ttc\\scripts\\ttc_demo.py

Keys: SPACE pause / play, N next frame (while paused), Q quit.
No GPU: it replays the depth model's distances and the detector's boxes that
earlier benchmark runs saved, and runs the TTC filter live, frame by frame,
exactly as it would run in the car.

Two modes (set MODE below):
    "kitti"    a real KITTI recording. Every object gets a box and its numbers;
               the nearest object in our path is plotted over time against the
               laser truth.
    "braking"  a simulated car ahead that suddenly brakes hard, seen from above,
               so you can watch the warning come on.

What you see per object:  #id  distance | closing speed | TTC
    closing speed  how fast the gap shrinks, m/s (positive = getting closer)
    TTC            seconds until contact if nothing changes = distance / closing speed
    colour         green = safe, orange = TTC under 6 s, red = WARNING
                   (TTC under 2.5 s for 2 frames in a row), grey = not in our path
"""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src/ttc/benchmarks/kitti_tracking"))

from src.ttc.kalman import FusedKalman, time_to_collision  # noqa: E402

# ---- CONFIG ----------------------------------------------------------------
MODE = "kitti"              # "kitti" or "braking"
SEQUENCE = "0017"           # KITTI recording; 0017 and 0019 have cars really approaching
SPEED = 1.0                 # playback speed (1.0 = real time, 10 frames per second)
SAVE_VIDEO = None           # e.g. "out/ttc_demo.mp4" to also save what is shown

# The best method so far (from src/ttc/benchmarks/kitti_tracking/results):
# the COMBINED filter, fed with the depth model's distance AND the box height.
ACCEL_NOISE = 0.2           # how suddenly the approach rate may change (1/s^2)
DEPTH_NOISE = 0.03          # trust in the distance for motion (3% wobble assumed)
SIZE_NOISE = 0.011          # box height wobble, measured: 1.1% per frame
GATE_MPS = 1.0              # only show a speed once the filter is sure within 1 m/s
WARN_TTC_S = 2.5            # warn when TTC is under this ...
WARN_FRAMES = 2             # ... for this many frames in a row
CORRIDOR_M = 1.2            # "in our path" = within 1.2 m of our car's centre line
MAX_GAP_FRAMES = 5          # an object unseen longer than this starts over

# Braking mode: the car ahead drives at our speed, then brakes.
BRAKE_GAP_M, BRAKE_DECEL, BRAKE_AFTER_S = 30.0, 6.0, 4.0
SIM_DEPTH_ERR, SIM_SIZE_ERR, SIM_SEED = 0.015, 0.011, 1   # measured noise sizes
# ----------------------------------------------------------------------------

FPS = 10.0
DATA = REPO / "data/kitti_tracking/training"
DIST_FILE = REPO / "src/distance/benchmarks/kitti_tracking/results/metric3d-v2-small-fp16_f150/observations.csv"
DIST_COL = "metric3d-v2-small-fp16_p10"
SIZE_FILE = REPO / "src/ttc/benchmarks/kitti_tracking/results/sizes_f150/observations.csv"

GREEN, ORANGE, RED, GREY, WHITE = (60, 200, 60), (0, 165, 255), (0, 0, 255), (150, 150, 150), (255, 255, 255)
BLUE, YELLOW, CYAN = (255, 120, 0), (0, 220, 255), (255, 255, 0)


class ObjectState:
    """One object's live filter, plus its history for the plots."""

    def __init__(self) -> None:
        self.kf: FusedKalman | None = None
        self.last_frame: int | None = None
        self.warn_run = 0                      # frames in a row with TTC under the threshold
        self.history: list[dict] = []          # per frame: numbers to plot

    def step(self, frame: int, distance: float, size: float | None) -> dict:
        """Feed this frame's readings to the filter; return its outputs."""
        if self.kf is None or frame - self.last_frame > MAX_GAP_FRAMES:   # new or lost: start over
            self.kf, self.warn_run = FusedKalman(ACCEL_NOISE, DEPTH_NOISE, SIZE_NOISE), 0
        else:
            self.kf.predict((frame - self.last_frame) / FPS)
            if frame - self.last_frame != 1:
                self.warn_run = 0
        self.kf.update(distance, size)
        self.last_frame = frame
        sure = self.kf.updates >= 2 and self.kf.closing_sigma <= GATE_MPS
        closing = self.kf.closing_speed if sure else None
        ttc = time_to_collision(self.kf.distance, closing) if sure else None
        self.warn_run = self.warn_run + 1 if (ttc is not None and ttc < WARN_TTC_S) else 0
        return {"distance": self.kf.distance, "closing": closing, "ttc": ttc,
                "warning": self.warn_run >= WARN_FRAMES}


# ---- drawing helpers --------------------------------------------------------

def text(img, s, xy, colour=WHITE, scale=0.5, thick=1, backing=False):
    """Write text; backing=True puts a dark box behind it (for text on the camera image)."""
    if backing:
        (w, h), base = cv2.getTextSize(s, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)
        x, y = xy
        cv2.rectangle(img, (x - 2, y - h - 3), (x + w + 2, y + base), (0, 0, 0), -1)
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, colour, thick, cv2.LINE_AA)


def colour_of(out: dict, in_path: bool):
    if not in_path:
        return GREY
    if out["warning"]:
        return RED
    if out["ttc"] is not None and out["ttc"] < 6.0:
        return ORANGE
    return GREEN


def label_of(out: dict) -> str:
    c = "--" if out["closing"] is None else f"{out['closing']:+.1f} m/s"
    t = "--" if out["ttc"] is None else ("never" if math.isinf(out["ttc"]) else f"{out['ttc']:.1f} s")
    return f"{out['distance']:.1f} m | {c} | TTC {t}"


def plot(img, x, y, w, h, title, series, y_range, t_now, t_span=10.0, hline=None):
    """Small line chart. series: [(label, colour, [(t, value)], dots?)]."""
    cv2.rectangle(img, (x, y), (x + w, y + h), (40, 40, 40), -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), (90, 90, 90), 1)
    lo, hi = y_range
    t0 = t_now - t_span
    px = lambda t: int(x + (t - t0) / t_span * w)  # noqa: E731
    py = lambda v: int(y + h - (min(max(v, lo), hi) - lo) / (hi - lo) * h)  # noqa: E731
    for k in range(5):   # horizontal grid with values
        v = lo + (hi - lo) * k / 4
        cv2.line(img, (x, py(v)), (x + w, py(v)), (60, 60, 60), 1)
        text(img, f"{v:g}", (x + 3, py(v) - 3), GREY, 0.38)
    if hline is not None:
        for xx in range(x, x + w, 12):
            cv2.line(img, (xx, py(hline[0])), (min(xx + 6, x + w), py(hline[0])), RED, 1)
        text(img, hline[1], (x + w - 140, py(hline[0]) - 4), RED, 0.4)
    for i, (label, colour, pts, dots) in enumerate(series):
        pts = [(t, v) for t, v in pts if t >= t0 and v is not None and math.isfinite(v)]
        if dots:
            for t, v in pts:
                cv2.circle(img, (px(t), py(v)), 2, colour, -1)
        else:
            for (ta, va), (tb, vb) in zip(pts, pts[1:]):
                if tb - ta <= 0.15:
                    cv2.line(img, (px(ta), py(va)), (px(tb), py(vb)), colour, 2, cv2.LINE_AA)
        text(img, label, (x + 50 + i * 170, y + 16), colour, 0.42)
    text(img, title, (x + 5, y + h + 16), WHITE, 0.45)


def plots_panel(width: int, hist: list[dict], t_now: float, title: str) -> np.ndarray:
    """Three charts of one object over the last 10 s."""
    panel = np.full((330, width, 3), 25, np.uint8)
    text(panel, title, (10, 20), YELLOW, 0.55)
    w = (width - 40) // 3
    get = lambda k: [(h["t"], h.get(k)) for h in hist]  # noqa: E731
    dmax = max([h["true_m"] for h in hist if h.get("true_m")] + [h["measured_m"] for h in hist] + [10])
    plot(panel, 10, 35, w, 260, "1. DISTANCE (m): dots = depth model, blue = filter, yellow = laser truth",
         [("depth model", GREY, get("measured_m"), True), ("filter", BLUE, get("distance"), False),
          ("truth", YELLOW, get("true_m"), False)], (0, math.ceil(dmax / 10) * 10), t_now)
    plot(panel, 20 + w, 35, w, 260, "2. CLOSING SPEED (m/s): + = getting closer",
         [("filter", BLUE, get("closing"), False), ("truth", YELLOW, get("true_closing"), False)],
         (-6, 10), t_now, hline=(0, ""))
    plot(panel, 30 + 2 * w, 35, w, 260, "3. TIME TO COLLISION (s), red line = warning level",
         [("filter", BLUE, get("ttc"), False), ("truth", YELLOW, get("true_ttc"), False)],
         (0, 15), t_now, hline=(WARN_TTC_S, f"warn under {WARN_TTC_S:g} s"))
    return panel


def header(width: int, lines: list[str], warning: bool) -> np.ndarray:
    bar = np.full((28 + 22 * len(lines), width, 3), 25, np.uint8)
    if warning:
        bar[:] = (0, 0, 170)
    for i, s in enumerate(lines):
        text(bar, s, (10, 22 + 22 * i), WHITE, 0.55 if i == 0 else 0.48, 2 if i == 0 else 1)
    return bar


# ---- the two modes ------------------------------------------------------------

def true_speed_and_ttc(rows: list[dict]) -> None:
    """Laser truth for the plots: closing speed = slope of the true distance over
    +-0.5 s; true TTC = true distance / that speed (infinity if not closing)."""
    frames = np.array([r["frame"] for r in rows])
    true = np.array([r["true_m"] for r in rows])
    for r in rows:
        near = np.abs(frames - r["frame"]) <= 5
        if near.sum() >= 6:
            slope = np.polyfit(frames[near] / FPS, true[near], 1)[0]
            r["true_closing"] = -slope
            r["true_ttc"] = time_to_collision(r["true_m"], -slope) if -slope >= 0.5 else math.inf
        else:
            r["true_closing"] = r["true_ttc"] = None


def kitti_frames():
    """Yield one composed picture per frame of the chosen KITTI recording."""
    per_frame = defaultdict(list)
    boxes = {}
    with SIZE_FILE.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["sequence"] == SEQUENCE:
                boxes[(int(r["frame"]), int(r["track_id"]))] = r
    by_track = defaultdict(list)
    with DIST_FILE.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["sequence"] != SEQUENCE or r[DIST_COL] in ("", "None"):
                continue
            key = (int(r["frame"]), int(r["track_id"]))
            b = boxes[key]
            row = {"frame": key[0], "track_id": key[1], "measured_m": float(r[DIST_COL]),
                   "true_m": float(r["true_nearest_surface_m"]), "lateral_m": float(r["lateral_gap_m"]),
                   "box": tuple(int(float(b[k])) for k in ("x1", "y1", "x2", "y2")),
                   "size": None if b["touches_edge"] == "1" else float(b["y2"]) - float(b["y1"])}
            by_track[key[1]].append(row)
    for rows in by_track.values():
        rows.sort(key=lambda r: r["frame"])
        true_speed_and_ttc(rows)
        for r in rows:
            per_frame[r["frame"]].append(r)

    states = defaultdict(ObjectState)
    focus = None
    images = sorted((DATA / "image_02" / SEQUENCE).glob("*.png"))[:150]
    for path in images:
        frame = int(path.stem)
        img = cv2.imread(str(path))
        t = frame / FPS
        warning = False
        in_path_now = []
        for r in per_frame.get(frame, []):
            st = states[r["track_id"]]
            out = st.step(frame, r["measured_m"], r["size"])
            st.history.append({"t": t, **out, **{k: r[k] for k in ("measured_m", "true_m", "true_closing", "true_ttc")}})
            in_path = r["lateral_m"] <= CORRIDOR_M
            warning |= in_path and out["warning"]
            colour = colour_of(out, in_path)
            x1, y1, x2, y2 = r["box"]
            cv2.rectangle(img, (x1, y1), (x2, y2), colour, 3 if in_path else 1)
            text(img, f"#{r['track_id']} " + label_of(out), (x1, max(y1 - 6, 14)), colour, 0.45, backing=True)
            if in_path:
                in_path_now.append((out["distance"], r["track_id"]))
        if in_path_now:
            focus = min(in_path_now)[1]
        top = header(img.shape[1], [
            "WARNING: collision risk ahead" if warning else
            f"KITTI recording {SEQUENCE}, frame {frame}, t = {t:.1f} s",
            "Best method: COMBINED filter = depth model distance + box growth, one Kalman filter. "
            f"Warning = TTC under {WARN_TTC_S:g} s for {WARN_FRAMES} frames.",
            "Thick boxes = in our path. Green safe, orange TTC < 6 s, red warning, grey not in path. "
            "Label: distance | closing speed | TTC",
        ], warning)
        hist = states[focus].history if focus is not None else []
        panel = plots_panel(img.shape[1], hist, t, f"Plots: object #{focus}, nearest in our path"
                            if focus is not None else "Plots: no object in our path yet")
        yield np.vstack([top, img, panel])


def braking_frames():
    """Yield one composed picture per frame of the simulated braking."""
    rng = np.random.default_rng(SIM_SEED)
    t_end = BRAKE_AFTER_S + math.sqrt(2 * BRAKE_GAP_M / BRAKE_DECEL)
    st = ObjectState()
    width = 1242
    first_warn = None
    for frame in range(int(t_end * FPS) + 1):
        t = frame / FPS
        tb = max(t - BRAKE_AFTER_S, 0.0)
        true_d = max(BRAKE_GAP_M - 0.5 * BRAKE_DECEL * tb ** 2, 0.1)
        true_closing = BRAKE_DECEL * tb
        true_ttc = time_to_collision(true_d, true_closing)
        measured = true_d * (1 + SIM_DEPTH_ERR * rng.standard_normal())
        size = 1080.0 / true_d * (1 + SIM_SIZE_ERR * rng.standard_normal())
        out = st.step(frame, measured, size)
        st.history.append({"t": t, **out, "measured_m": measured, "true_m": true_d,
                           "true_closing": true_closing, "true_ttc": true_ttc})
        if out["warning"] and first_warn is None:
            first_warn = t
        # Top-down road view: our car on the left, the car ahead at its true gap.
        road = np.full((260, width, 3), 50, np.uint8)
        cv2.rectangle(road, (0, 80), (width, 180), (80, 80, 80), -1)
        for xx in range(0, width, 60):
            cv2.line(road, (xx, 130), (xx + 30, 130), WHITE, 2)
        scale = (width - 260) / BRAKE_GAP_M
        x_us, x_lead = 60, int(160 + true_d * scale)
        cv2.rectangle(road, (x_us, 105), (x_us + 100, 155), BLUE, -1)
        text(road, "us", (x_us + 35, 137), WHITE, 0.6, 2)
        colour = colour_of(out, True)
        cv2.rectangle(road, (x_lead, 105), (x_lead + 100, 155), colour, -1)
        text(road, "car ahead", (x_lead + 5, 137), (0, 0, 0), 0.5, 2)
        cv2.arrowedLine(road, (x_us + 105, 95), (x_lead - 5, 95), WHITE, 1, tipLength=0.02)
        text(road, f"true gap {true_d:.1f} m", ((x_us + x_lead) // 2, 88), WHITE, 0.5)
        text(road, "filter: " + label_of(out), (10, 215), colour, 0.6, 2)
        text(road, f"truth:  {true_d:.1f} m | {true_closing:+.1f} m/s | TTC "
                   + ("never" if math.isinf(true_ttc) else f"{true_ttc:.1f} s"), (10, 245), YELLOW, 0.6, 2)
        phase = "driving steady" if t < BRAKE_AFTER_S else f"CAR AHEAD BRAKING HARD ({BRAKE_DECEL:g} m/s^2)"
        top = header(width, [
            "WARNING: collision risk ahead" + (f" (first warning at t = {first_warn:.1f} s)" if first_warn else "")
            if out["warning"] else f"Simulated braking, t = {t:.1f} s: {phase}",
            "Best method: COMBINED filter = depth model distance + box growth, one Kalman filter. "
            f"Warning = TTC under {WARN_TTC_S:g} s for {WARN_FRAMES} frames.",
            f"Readings get random noise of the measured size: distance {SIM_DEPTH_ERR:.1%}, "
            f"box height {SIM_SIZE_ERR:.1%} per frame.",
        ], out["warning"])
        panel = plots_panel(width, st.history, max(t, 10.0) if t_end > 10 else t_end, "Plots: the car ahead")
        yield np.vstack([top, road, panel])


def main() -> None:
    frames = kitti_frames() if MODE == "kitti" else braking_frames()
    writer, paused = None, False
    delay = max(1, int(1000 / (FPS * SPEED)))
    for pic in frames:
        if SAVE_VIDEO:
            if writer is None:
                Path(SAVE_VIDEO).parent.mkdir(parents=True, exist_ok=True)
                writer = cv2.VideoWriter(SAVE_VIDEO, cv2.VideoWriter_fourcc(*"mp4v"), FPS * SPEED,
                                         (pic.shape[1], pic.shape[0]))
            writer.write(pic)
        cv2.imshow("Time To Collision demo", pic)
        while True:
            key = cv2.waitKey(0 if paused else delay) & 0xFF
            if key == ord("q"):
                cv2.destroyAllWindows()
                return
            if key == ord(" "):
                paused = not paused
            if not paused or key == ord("n"):
                break
    if writer:
        writer.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
