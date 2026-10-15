"""Label BDD100K train clips by hand, one key per clip (this PC, free).

Plain BADAS-Open ranks the 3,000 BDD100K train clips by risk. Ranks 1-200 were mostly real near-misses and
ranks below 638 almost all normal; ranks 201-638 are a mix, and they hold the valuable hard "normal" examples
(stopping close behind a car), so a person labels every one of them here.

Two steps:
  1. --prepare : download each clip from the Modal Volume, cut the moment around its riskiest reading
                 into a small mp4 on D:, delete the full video. Resume-safe, 4 at a time.
  2. (default) : the labelling window. Clips in rank order; the BADAS risk is drawn on the frame.

Keys in the window:
    1 = normal      2 = real danger (crash)      3 = unsure          (label, then jump to the next clip)
    right arrow / d = next clip    left arrow / a = previous clip    space = replay    q / Esc = quit
Every key press is saved at once to src/risk/data/bdd100k_ids/manual_labels.json (safe to quit any time;
the next start opens at the first clip without a label).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_label.py --prepare
    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_label.py
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bdd100k_review import SERIES, rank, risk_at  # noqa: E402

# ---- CONFIG ----
FIRST, LAST = 201, 638                      # ranks to label (1 = riskiest)
CLIPS = Path(r"D:\safe-distance-label-clips")                  # small cut clips (C: is nearly full)
LABELS = Path(__file__).resolve().parents[1] / "bdd100k_ids" / "manual_labels.json"
VOLUME, PROFILE = "safe-distance-data", Path.home() / ".modal_session18.toml"
BEFORE_S, AFTER_S = 2.5, 1.0                # seconds kept around the riskiest moment
SIZE = (960, 540)                           # cut clip size (enough to judge, small on disk)
WORKERS = 4
KEYS = {ord("1"): "normal", ord("2"): "real", ord("3"): "unsure"}
NEXT, PREV = (2555904, ord("d")), (2424832, ord("a"))          # right / left arrow codes on Windows
COLOURS = {"real": (0, 0, 255), "normal": (0, 200, 0), "unsure": (0, 200, 255), None: (200, 200, 200)}
# ----------------


def todo() -> list[dict]:
    """The clips to label, in rank order, with their riskiest moment."""
    series = json.loads(SERIES.read_text())
    full = rank(series)
    for i, r in enumerate(full, 1):
        r["rank"] = i
    return full[FIRST - 1:LAST]


def prepare_one(r: dict) -> str:
    """Download one full video, cut its riskiest moment to a small mp4, delete the full video."""
    out = CLIPS / f"{r['rank']:04d}_{r['clip']}.mp4"
    if out.exists():
        return "skipped"
    full = CLIPS / "tmp" / f"{r['clip']}.mov"
    full.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "MODAL_CONFIG_PATH": str(PROFILE)}
    for attempt in range(3):                 # the download sometimes drops: retry
        p = subprocess.run([sys.executable, "-m", "modal", "volume", "get", "--force", VOLUME,
                            f"bdd100k/videos/100k/train/{r['clip']}.mov", str(full)],
                           env=env, capture_output=True, text=True)
        if p.returncode == 0 and full.exists():
            break
        time.sleep(3 * (attempt + 1))
    else:
        return f"FAILED download: {p.stderr.strip()[-200:]}"
    start = max(0.0, r["peak_s"] - BEFORE_S)
    tmp = out.with_suffix(".part.mp4")
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-i", str(full),
                        "-t", f"{BEFORE_S + AFTER_S:.2f}", "-vf", f"scale={SIZE[0]}:{SIZE[1]}", "-an",
                        "-c:v", "libx264", "-crf", "26", "-pix_fmt", "yuv420p", str(tmp)],
                       capture_output=True, text=True)
    full.unlink(missing_ok=True)
    if p.returncode != 0:
        tmp.unlink(missing_ok=True)
        return f"FAILED cut: {p.stderr.strip()[-200:]}"
    tmp.replace(out)                          # only complete clips get the final name
    return "new"


def prepare() -> None:
    rows = todo()
    CLIPS.mkdir(parents=True, exist_ok=True)
    t0, done, failed = time.time(), 0, []
    with ThreadPoolExecutor(WORKERS) as ex:
        for r, res in zip(rows, ex.map(prepare_one, rows)):
            done += 1
            if res.startswith("FAILED"):
                failed.append((r["rank"], r["clip"], res))
                print(f"  rank {r['rank']} {r['clip']}: {res}", flush=True)
            if done % 20 == 0 or done == len(rows):
                el = time.time() - t0
                print(f"  {done}/{len(rows)} clips  failed={len(failed)}  elapsed={el:.0f}s  "
                      f"ETA={(len(rows) - done) * el / done:.0f}s", flush=True)
    print(f"done: {len(rows) - len(failed)} clips ready in {CLIPS}, {len(failed)} failed (re-run to retry)")


def load_labels() -> dict:
    return json.loads(LABELS.read_text()) if LABELS.exists() else {}


def save_labels(labels: dict) -> None:
    """Write atomically: a crash mid-write never leaves a broken file."""
    tmp = LABELS.with_suffix(".tmp")
    tmp.write_text(json.dumps(labels, indent=1))
    tmp.replace(LABELS)


def read_frames(path: Path) -> tuple[list, float]:
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        frames.append(img)
    cap.release()
    return frames, fps


def draw(img, lines: list[tuple[str, tuple]]) -> np.ndarray:
    img = img.copy()
    for i, (s, c) in enumerate(lines):
        y = 32 + 34 * i
        cv2.putText(img, s, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 5, cv2.LINE_AA)
        cv2.putText(img, s, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, c, 2, cv2.LINE_AA)
    return img


def label() -> None:
    rows = todo()
    series = json.loads(SERIES.read_text())
    labels = load_labels()
    i = next((k for k, r in enumerate(rows) if r["clip"] not in labels), len(rows) - 1)
    win = "BDD100K labelling  (1 normal, 2 crash, 3 unsure, arrows/a/d move, space replay, q quit)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, *SIZE)
    while 0 <= i < len(rows):
        r = rows[i]
        path = CLIPS / f"{r['rank']:04d}_{r['clip']}.mp4"
        frames, fps = read_frames(path) if path.exists() else ([], 30.0)
        if not frames:                       # not prepared (or broken): show a message, allow moving on
            frames = [np.zeros((SIZE[1], SIZE[0], 3), np.uint8)]
            missing = True
        else:
            missing = False
        start = max(0.0, r["peak_s"] - BEFORE_S)
        got = labels.get(r["clip"], {}).get("label")
        done = sum(1 for x in rows if x["clip"] in labels)
        key, t0 = -1, time.perf_counter()
        while key == -1:                     # loop the clip until a key is pressed
            # Frame chosen from the real clock (not a frame counter), so playback runs at true speed
            # however long drawing takes; slow moments skip a frame instead of slowing down.
            f = int((time.perf_counter() - t0) * fps)
            img = frames[f % len(frames)]
            t = start + (f % len(frames)) / fps
            p = risk_at(series[r["clip"]], t)
            lines = [(f"{i + 1}/{len(rows)}   rank {r['rank']}   labelled {done}/{len(rows)}", (255, 255, 255)),
                     (f"BADAS risk now {'-' if p is None else f'{p:.3f}'}   peak {r['max_risk']:.3f}"
                      f"   {t - r['peak_s']:+.1f} s from peak", (255, 255, 255)),
                     (f"your label: {got or '-'}", COLOURS[got])]
            if missing:
                lines.append(("clip not prepared: run with --prepare (arrows to move on)", (0, 0, 255)))
            cv2.imshow(win, draw(img, lines))
            wait = (f + 1) / fps - (time.perf_counter() - t0)            # time left until the next frame
            key = cv2.waitKeyEx(max(1, int(wait * 1000)))
            if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:    # window closed with the X
                key = ord("q")
            if key == ord(" "):              # replay from the start
                key, t0 = -1, time.perf_counter()
        if key in (ord("q"), 27):
            break
        if key in KEYS:
            labels[r["clip"]] = {"rank": r["rank"], "label": KEYS[key], "max_risk": r["max_risk"],
                                 "peak_s": r["peak_s"], "at": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_labels(labels)
            i += 1
        elif key in NEXT:
            i = min(i + 1, len(rows) - 1)
        elif key in PREV:
            i = max(i - 1, 0)
    cv2.destroyAllWindows()
    counts = {}
    for v in labels.values():
        counts[v["label"]] = counts.get(v["label"], 0) + 1
    print(f"saved {LABELS}: {len(labels)} labelled {counts}; "
          f"{sum(1 for r in rows if r['clip'] not in labels)} of {len(rows)} still to do")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", action="store_true", help="download and cut the clips first")
    prepare() if ap.parse_args().prepare else label()
