"""Keep testing the full pipeline on randomly chosen crash clips, live (GPU).

Picks a random clip, runs the whole pipeline on it in a window, and when the
clip ends picks the next one, until you quit. Each clip's result (saved video +
summary .json) goes to out/pipeline, and one line per clip is added to
out/pipeline/random_test_log.jsonl.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\ttc\\scripts\\random_test.py

Keys: R next random clip now, SPACE pause / play, Q quit.

Clip pools (set POOLS below):
    "ccd"    CCD crashes where OUR car crashes (801 clips, 5 s each, real crashes)
    "nexar"  every Nexar collision / near-miss clip downloaded locally (about 40 s each)
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_pipeline_video import OUT_DIR, Models, run_clip  # noqa: E402

# ---- CONFIG ----
POOLS = ["ccd", "nexar"]          # which clips to draw from
CCD_DIR = Path(r"C:\safe-distance-data\ccd")
NEXAR_DIR = Path(r"C:\safe-distance-data\nexar\train\positive")
SEED = None                       # None = different order every run; a number = repeatable order
# ----------------


def clip_pool() -> list[Path]:
    """All clips to draw from: CCD clips where our own car crashes, plus local Nexar clips."""
    clips = []
    if "ccd" in POOLS:
        for line in (CCD_DIR / "Crash-1500.txt").read_text().splitlines():
            if line.strip().endswith("Yes"):              # egoinvolve = Yes: our car crashes
                clips.append(CCD_DIR / f"{line.split(',')[0]}.mp4")
    if "nexar" in POOLS:
        clips += sorted(NEXAR_DIR.glob("*.mp4"))
    return [c for c in clips if c.exists()]


def main() -> None:
    clips = clip_pool()
    rng = random.Random(SEED)
    print(f"{len(clips)} clips to draw from; R = next clip, SPACE = pause, Q = quit")
    models = Models()
    window = "Safe distance: random clips (R next, SPACE pause, Q quit)"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    log = OUT_DIR / "random_test_log.jsonl"
    while True:
        clip = rng.choice(clips)
        print(f"=== {clip} ===", flush=True)
        result = run_clip(clip, models, window, allow_skip=True)
        summary = OUT_DIR / f"{'CCD' if clip.parent == CCD_DIR else 'Nexar'}_{clip.stem}.json"
        if summary.exists():
            with log.open("a") as f:
                f.write(json.dumps({**json.loads(summary.read_text()), "ended_by": result}) + "\n")
        if result == "quit":
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
