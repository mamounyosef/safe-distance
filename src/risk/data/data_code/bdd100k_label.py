"""Label BDD100K train clips by hand, one key per clip (this PC, free).

Plain BADAS-Open ranks the 3,000 BDD100K train clips by risk. Ranks 1-200 were mostly real near-misses and
ranks below 638 almost all normal; ranks 201-638 are a mix, and they hold the valuable hard "normal" examples
(stopping close behind a car), so a person labels every one of them here.

Two steps:
  1. --prepare : download each clip from the Modal Volume, cut the moment around its riskiest reading
                 into a small mp4 on D:, delete the full video. Resume-safe, 4 at a time.
  2. (default) : the labelling window. Clips in rank order; the BADAS risk is drawn on the frame.

Keys in the window:
    1 = normal      2 = risk (real danger)      3 = unsure      4 = bad example: camera not straight (never train on it)
    (label, then jump to the next clip)
    right arrow / d = next clip    left arrow / a = previous clip    space = replay    q / Esc = quit
Every key press is saved at once to src/risk/data/bdd100k_ids/manual_labels.json (safe to quit any time;
the next start opens at the first clip without a label).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_label.py --prepare
    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_label.py

Spot checks (see SPOTS: 1 = 20 clips from 639-700, 2 = 10 from 701-900 + 10 from 901-1107): set LABEL_SPOT=<check>
first, same commands (also for the web tool).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bdd100k_review import SERIES as TRAIN_SERIES, rank, risk_at  # noqa: E402

# ---- CONFIG ----
# LABEL_SET=val / test: label BDD100K val or test instead (shorter clips, own labels file).
# Val ranks 1-25 match train ranks 3-93, where the reviews found 23/23 real near-misses: removed without labelling.
# Test uses the same BADAS peak limits as val: peak >= TEST_REMOVE_PEAK removed without labelling (like val ranks
# 1-25), peak >= TEST_LABEL_PEAK labelled (like val ranks 26-137, which match train ranks up to about 692).
SPLIT = os.environ.get("LABEL_SET", "train")
VAL = SPLIT in ("val", "test")                                    # the short-clip modes
RUNS = Path(__file__).resolve().parents[2] / "runs/baseline_badas_open/results"
SERIES = {"train": TRAIN_SERIES, "val": RUNS / "eval/series_bdd_val.json",
          "test": RUNS / "bdd_test/series_bdd_test.json"}[SPLIT]
TEST_REMOVE_PEAK, TEST_LABEL_PEAK = 0.99565, 0.98915             # between val ranks 25/26 and 137/138


def _test_ranks() -> tuple[int, int]:
    """Test ranks to label, from the peak limits (the test set gets its own ranking by plain BADAS-Open)."""
    peaks = [r["max_risk"] for r in rank(json.loads(SERIES.read_text()))]
    return sum(p >= TEST_REMOVE_PEAK for p in peaks) + 1, sum(p >= TEST_LABEL_PEAK for p in peaks)


FIRST, LAST = {"train": (201, 638), "val": (26, 137)}.get(SPLIT) or _test_ranks()   # ranks to label (1 = riskiest)
SPOT_SEED = 20261016                        # spot checks below the labelled ranks: LABEL_SPOT=<check> picks one
SPOTS = {"1": [(639, 700, 20)],                                  # (first rank, last rank, random clips)
         "2": [(701, 900, 10), (901, 1107, 10)],
         "3": [(639, 700, 20)]}                                  # 20 more from 639-700 (the rest get removed)
SPOT_EXCLUDE = {"3": "1"}                   # check 3 never redraws the clips check 1 already showed
CLIPS = Path({"train": r"D:\safe-distance-label-clips-v2", "val": r"D:\safe-distance-label-clips-val",
              "test": r"D:\safe-distance-label-clips-test"}[SPLIT])                          # small cut clips
OLD_CLIPS = Path(r"D:\safe-distance-label-clips")              # first cut (1 s after the peak; froze in browsers)
LABELS = Path(__file__).resolve().parents[1] / "bdd100k_ids" / {"train": "manual_labels.json", "val": "val_labels.json",
                                                                  "test": "test_labels.json"}[SPLIT]
VOLUME, PROFILE = "safe-distance-data", Path.home() / ".modal_session18.toml"
# Seconds kept around the riskiest moment. BADAS reads the 2 s before each reading, so 2 s before the peak shows
# what alarmed it; after the peak shows how it ends. Val: 3 s clips (train had 4.5 s) to label faster.
BEFORE_S, AFTER_S = (2.0, 1.0) if VAL else (2.5, 2.0)
SIZE = (960, 540)                           # cut clip size (enough to judge, small on disk)
WORKERS = 4
KEYS = {ord("1"): "normal", ord("2"): "risk", ord("3"): "unsure", ord("4"): "bad"}   # bad = camera not straight (tilted mount), never train on it
NEXT, PREV = (2555904, ord("d")), (2424832, ord("a"))          # right / left arrow codes on Windows
COLOURS = {"risk": (0, 0, 255), "normal": (0, 200, 0), "unsure": (0, 200, 255), "bad": (200, 0, 200),
           None: (200, 200, 200)}
# ----------------


def todo() -> list[dict]:
    """The clips to label, in rank order, with their riskiest moment.
    With LABEL_SPOT=<check> set: that spot check instead (random clips per rank band in SPOTS, fixed seed),
    to see how deep below rank 638 real dangers still appear."""
    series = json.loads(SERIES.read_text())
    full = rank(series)
    for i, r in enumerate(full, 1):
        r["rank"] = i
    check = os.environ.get("LABEL_SPOT")
    return spot_pick(full, check) if check else full[FIRST - 1:LAST]


def spot_pick(full: list[dict], check: str) -> list[dict]:
    """The clips of one spot check: a fixed random draw per rank band, so the same clips come back every run."""
    # check 1 keeps its original draw; later checks get their own seed
    rng = random.Random(SPOT_SEED if check == "1" else SPOT_SEED + int(check))
    skip = {r["clip"] for r in spot_pick(full, SPOT_EXCLUDE[check])} if check in SPOT_EXCLUDE else set()
    pick = [r for lo, hi, n in SPOTS[check]
            for r in rng.sample([x for x in full[lo - 1:hi] if x["clip"] not in skip], n)]
    return sorted(pick, key=lambda r: r["rank"])


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
                            f"bdd100k/videos/100k/{SPLIT}/{r['clip']}.mov", str(full)],
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
                        "-c:v", "libx264", "-crf", "26", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(tmp)],      # index at the start: browsers stream it smoothly
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


def set_label(clip: str, entry: dict) -> dict:
    """Add ONE label to the file and return all labels. Re-reads the file first, so labels saved meanwhile by
    another tool or person (the web page) are kept, never overwritten."""
    labels = load_labels()
    labels[clip] = entry
    save_labels(labels)
    return labels


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
    win = "BDD100K labelling  (1 normal, 2 risk, 3 unsure, 4 bad, arrows/a/d move, space replay, q quit)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, *SIZE)
    while 0 <= i < len(rows):
        r = rows[i]
        path = CLIPS / f"{r['rank']:04d}_{r['clip']}.mp4"
        if not path.exists():                # new cut not ready yet: fall back to the first cut
            path = OLD_CLIPS / path.name
        frames, fps = read_frames(path) if path.exists() else ([], 30.0)
        if not frames:                       # not prepared (or broken): show a message, allow moving on
            frames = [np.zeros((SIZE[1], SIZE[0], 3), np.uint8)]
            missing = True
        else:
            missing = False
        start = max(0.0, r["peak_s"] - BEFORE_S)
        labels = load_labels()               # fresh: include labels made on the web page meanwhile
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
            labels = set_label(r["clip"], {"rank": r["rank"], "label": KEYS[key], "max_risk": r["max_risk"],
                                           "peak_s": r["peak_s"], "by": "desktop",
                                           "at": time.strftime("%Y-%m-%d %H:%M:%S")})
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
