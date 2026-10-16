"""Show the stage 1 label rule on Nexar TRAIN crash clips: one video per case, 5 clips each (this PC, free).

The label comes from src/risk/stage1_labels.py, the same code training will use. For every frame the video shows
the label a 2 s window ENDING at that frame would get, plus a timeline under the video:
    coloured zones   green = 0, orange = ramp, red = 1, grey = not used (skip / no 2 s history), purple = after crash
    white curve      the label value (bottom of the strip = 0, top = 1)
    yellow lines     ALERT, ALERT + 0.5 s (late alerts), 2.4 s before (label reaches 1), CRASH
    white cursor     now; the shaded bracket behind it is the 2 s of video the window covers
The picture freezes for a moment at each of those lines.

Cases (alert lead = seconds from the alert to the crash; see CASES): A late 0.5-2.4 s, B early 2.4-4 s,
C very early over 4 s, D under 0.5 s. Fixed random clips, never one listed in src/risk/data/nexar_excluded.json.

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\stage1_label_demo.py

Output: Downloads\\safe-distance-testing\\nexar\\6_label_case_<case>.mp4 (+ .json with every clip's numbers).
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))                     # src/risk, for stage1_labels
from nexar_samples import CACHE, volume_get  # noqa: E402
from sample_video import Writer, card, text  # noqa: E402
import stage1_labels as L  # noqa: E402

# ---- CONFIG ----
OUT_DIR = Path.home() / "Downloads" / "safe-distance-testing" / "nexar"
# One video per case: (alert lead range in s before the crash, title, what the rule does)
CASES = {
    "A_late": (L.MARGIN_S, L.HARD_S, "LATE alert (0.5-2.4 s before the crash)",
               "skip the first 0.5 s after the alert, then label 1"),
    "B_early": (L.HARD_S, L.VERY_EARLY_S, "EARLY alert (2.4-4 s before the crash)",
                "ramp 0.25 at the alert -> 1 at -2.4 s, then 1"),
    "C_very_early": (L.VERY_EARLY_S, 99.0, "VERY EARLY alert (more than 4 s before the crash)",
                     "same ramp: 0.25 at the alert -> 1 at -2.4 s, then 1"),
    "D_alert_under_0.5s": (0.0, L.MARGIN_S, "ALERT UNDER 0.5 s before the crash",
                           "alert + 0.5 s is after the crash: NO danger window (only safe windows before the alert)"),
}
N, SEED = 5, 16
EXCLUDED = HERE.parents[0] / "nexar_excluded.json"            # clips the person removed (never shown, never used)
VIDEO, PANEL_H = (1280, 680), 230                            # video area + timeline strip under it
SIZE, FPS = (VIDEO[0], VIDEO[1] + PANEL_H), 30.0
AFTER_S = 1.0                                                # shown after the crash
FREEZE_S, TITLE_S = 1.2, 3.0
COLOURS = {L.ZERO: (60, 160, 60), L.RAMP: (0, 150, 255), L.ONE: (40, 40, 220), L.SKIP: (120, 120, 120),
           L.NO_HISTORY: (70, 70, 70), L.AFTER: (130, 50, 130)}        # BGR
NAMES = {L.ZERO: "0", L.RAMP: "ramp", L.ONE: "1", L.SKIP: "NOT USED (skip)", L.NO_HISTORY: "NOT USED (no 2 s history)",
         L.AFTER: "NEVER USED (after crash)"}
# ----------------


def markers(alert: float, event: float) -> list[tuple[float, str]]:
    """The moments worth a line on the timeline (and a short freeze), in time order."""
    lead = event - alert
    m = [(alert, "ALERT")]
    if lead <= L.HARD_S:
        m.append((alert + L.MARGIN_S, "ALERT+0.5 s: label 1"))
    else:
        m.append((event - L.HARD_S, "-2.4 s: label 1"))
    m.append((event, "CRASH"))
    return sorted((t, s) for t, s in m if t <= event)


def panel(t_now: float, t0: float, t1: float, alert: float, event: float) -> np.ndarray:
    """The timeline strip: zones, label curve, marker lines, the 2 s window and the cursor."""
    img = np.full((PANEL_H, SIZE[0], 3), 25, np.uint8)
    left, right, top, bot = 60, SIZE[0] - 30, 40, PANEL_H - 55
    x = lambda t: int(left + (t - t0) / (t1 - t0) * (right - left))          # time -> pixel
    y = lambda v: int(bot - v * (bot - top))                                  # label value -> pixel
    # 1) coloured zones and the label curve, sampled every 1/100 s
    pts, prev = [], None
    for t in np.arange(t0, t1, 0.01):
        v, z = L.window_label(float(t), alert, event)
        cv2.rectangle(img, (x(t), top), (x(t + 0.01) + 1, bot), COLOURS[z], -1)
        if v is not None:
            pts.append((x(t), y(v)))
        elif pts:                                                             # gap in the curve where not used
            cv2.polylines(img, [np.array(pts)], False, (255, 255, 255), 3, cv2.LINE_AA)
            pts = []
    if pts:
        cv2.polylines(img, [np.array(pts)], False, (255, 255, 255), 3, cv2.LINE_AA)
    # 2) value axis: 0, 0.25, 1
    for v in (0.0, L.RAMP_START, 1.0):  # value axis labels
        text(img, f"{v:g}", (8, y(v) + 6), 0.5)
    # 3) the 2 s window behind the cursor (what BADAS reads for the reading at "now")
    a, b = x(max(t0, t_now - L.WINDOW_S)), x(t_now)
    over = img.copy()
    cv2.rectangle(over, (a, top - 18), (b, bot), (255, 255, 255), -1)
    img = cv2.addWeighted(over, 0.18, img, 0.82, 0)
    cv2.rectangle(img, (a, top - 18), (b, top - 4), (255, 255, 255), -1)
    text(img, "2 s window", (a + 4, top - 22), 0.45)
    # 4) marker lines with their names, alternating heights so close ones do not overlap
    for k, (t, s) in enumerate(markers(alert, event)):
        cv2.line(img, (x(t), top), (x(t), bot), (0, 230, 255), 2)
        text(img, s, (max(2, min(x(t) - 40, SIZE[0] - 220)), bot + 22 + 20 * (k % 2)), 0.5, (0, 230, 255))
    # 5) seconds-before-crash ticks
    for s in range(int(np.floor(t0 - event)), int(t1 - event) + 1):
        if t0 <= event + s <= t1:
            cv2.line(img, (x(event + s), bot), (x(event + s), bot + 6), (200, 200, 200), 1)
            text(img, f"{s:+d}s" if s else "0", (x(event + s) - 14, PANEL_H - 4), 0.42, (200, 200, 200))
    # 6) the cursor
    cv2.line(img, (x(t_now), top - 18), (x(t_now), bot), (255, 255, 255), 3)
    return img


def pick_clips(meta: list[dict], lo: float, hi: float) -> list[dict]:
    """N fixed random clips whose alert lead is in (lo, hi], never an excluded clip, sorted by lead."""
    excluded = set(json.loads(EXCLUDED.read_text())["clips"])
    lead = lambda r: float(r["time_of_event"]) - float(r["time_of_alert"])
    pool = [r for r in meta if lo < lead(r) <= hi and r["file_name"] not in excluded]
    return sorted(random.Random(SEED).sample(pool, min(N, len(pool))), key=lead), len(pool)


def make_video(name: str, meta: list[dict]) -> None:
    """One video for one case: a title card, then N clips with the label of the window ending at each frame."""
    lo, hi, title, rule = CASES[name]
    clips, pool = pick_clips(meta, lo, hi)
    out = OUT_DIR / f"6_label_case_{name}.mp4"
    wr, shown = Writer(out, SIZE, FPS), []
    wr.write(card(SIZE, [f"Case {name[0]}: {title}", f"rule: {rule}",
                         f"{pool} of the 750 Nexar train crash clips are this case (excluded clips not counted)",
                         "label = label of the 2 s window ENDING at each frame",
                         "green 0   orange ramp   red 1   grey not used   purple after crash"]), 5.0)
    for k, r in enumerate(clips, 1):
        event, alert = float(r["time_of_event"]), float(r["time_of_alert"])
        lead = event - alert
        t0, t1 = max(0.0, event - max(6.0, lead + 2.5)), event + AFTER_S          # shown span
        wr.write(card(SIZE, [f"Case {name[0]}, clip {k}/{len(clips)}: alert {lead:.2f} s before the crash", rule,
                             f"Nexar {r['file_name']}   {r['light_conditions']}, {r['weather']}, {r['scene']}"]),
                 TITLE_S)
        path = volume_get(f"nexar/train/positive/{r['file_name']}", CACHE / r["file_name"])
        cap = cv2.VideoCapture(str(path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        todo, f = markers(alert, event), 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            t, f = f / fps, f + 1
            if t < t0 or t > t1:
                continue
            v, z = L.window_label(t, alert, event)
            img = np.zeros((SIZE[1], SIZE[0], 3), np.uint8)
            img[:VIDEO[1]] = cv2.resize(frame, VIDEO)
            cv2.rectangle(img, (0, 0), (VIDEO[0] - 1, VIDEO[1] - 1), COLOURS[z], 12)   # frame colour = zone
            text(img, f"{abs(event - t):.2f} s {'before' if t <= event else 'after'} the crash", (25, 120), 1.0)
            text(img, f"label: {f'ramp {v:.2f}' if z == L.RAMP else NAMES[z]}", (25, 170), 1.3, (255, 255, 255), 3)
            text(img, f"case {name[0]}  clip {k}/{len(clips)}  alert {lead:.2f} s", (VIDEO[0] - 400, 120), 0.7)
            img[VIDEO[1]:] = panel(t, t0, t1, alert, event)
            wr.write(img)
            while todo and t >= todo[0][0]:                       # hold the first frame at each marker
                text(img, todo[0][1], (25, 220), 1.0, (0, 230, 255), 3)
                wr.write(img, FREEZE_S)
                todo.pop(0)
        cap.release()
        shown.append({"n": k, "clip": r["file_name"], "alert_s": alert, "event_s": event, "lead_s": round(lead, 3),
                      "markers": [(round(t - event, 3), s) for t, s in markers(alert, event)]})
        print(f"  [{name} {k}/{len(clips)}] {r['file_name']}: alert {lead:.2f} s before the crash", flush=True)
    wr.close()
    out.with_suffix(".json").write_text(json.dumps({"case": name, "rule": rule, "clips_in_case": pool,
                                                    "shown": shown}, indent=1))
    print(f"saved {out}  ({pool} clips in this case)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = list(csv.DictReader(volume_get("nexar/train/positive/metadata.csv", CACHE / "metadata.csv").open()))
    for name in CASES:
        make_video(name, meta)


if __name__ == "__main__":
    main()
