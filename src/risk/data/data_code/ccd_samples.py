"""20 random CCD crash clips with their labels drawn on, as ONE video (this PC, free).

CCD (Car Crash Dataset, Bao et al. 2020, MIT licence): 1,500 crash clips of 50 frames at
10 per second (5 s). Labels per clip (Crash-1500.txt): 50 per-frame flags (1 = accident
frames), whether our own car is involved, day/night, weather. Shown:
    time relative to the first accident frame, red frame from the accident on,
    a 1.5 s freeze at the first accident frame.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\ccd_samples.py

Output: C:\\Users\\mamou\\Downloads\\ccd_samples.mp4 (+ ccd_samples.json).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample_video import Writer, card, text  # noqa: E402

# ---- CONFIG ----
CCD = Path(r"C:\safe-distance-data\ccd")
OUT = Path.home() / "Downloads" / "ccd_samples.mp4"
N, SEED = 20, 5
SIZE = (1280, 720)
FREEZE_S, TITLE_S = 1.5, 1.5
LABEL_FPS = 10.0                  # CCD: 50 frames at 10 per second
# ----------------


def labels() -> list[dict]:
    """One dict per clip from Crash-1500.txt: id, per-frame flags, our car involved, day/night, weather."""
    out = []
    for ln in (CCD / "Crash-1500.txt").read_text().splitlines():
        if not ln.strip():
            continue
        vid, rest = ln.split(",", 1)
        flags, tail = rest.split("]", 1)
        flags = [int(x) for x in flags.strip("[").split(",")]
        _, start, yt, timing, weather, ego = tail.split(",")
        out.append({"id": vid, "flags": flags, "accident_frame": flags.index(1) if 1 in flags else None,
                    "our_car": ego.strip() == "Yes", "light": timing, "weather": weather})
    return out


def main() -> None:
    picks = random.Random(SEED).sample(labels(), N)
    wr, shown = Writer(OUT, SIZE, LABEL_FPS), []
    for k, c in enumerate(picks, 1):
        cap = cv2.VideoCapture(str(CCD / f"{c['id']}.mp4"))
        fps = cap.get(cv2.CAP_PROP_FPS) or LABEL_FPS
        frames = []
        while True:
            ok, img = cap.read()
            if not ok:
                break
            frames.append(img)
        cap.release()
        acc = c["accident_frame"]
        who = "OUR CAR CRASHES" if c["our_car"] else "OTHER ROAD USERS CRASH (our car only watches)"
        wr.write(card(SIZE, [f"CCD clip {k}/{N}   ({c['id']})", who,
                             f"accident at {acc / LABEL_FPS:.1f} s of {len(c['flags']) / LABEL_FPS:.0f} s   "
                             f"{c['light']}, {c['weather']}   (video: {len(frames)} frames at {fps:.0f} fps)"]),
                 TITLE_S)
        for j, img in enumerate(frames):
            lf = int(j * LABEL_FPS / fps)                 # this video frame's label frame
            img = cv2.resize(img, SIZE)
            t = (lf - acc) / LABEL_FPS
            text(img, f"{t:+.1f} s {'before' if t < 0 else 'after'} accident", (15, 40), 1.0)
            text(img, "OUR CAR" if c["our_car"] else "OTHERS", (15, SIZE[1] - 25), 0.8,
                 (0, 200, 255) if c["our_car"] else (255, 200, 0))
            if lf >= acc:
                cv2.rectangle(img, (0, 0), (SIZE[0] - 1, SIZE[1] - 1), (0, 0, 255), 10)
                text(img, "ACCIDENT (labelled)", (15, 85), 0.9, (0, 0, 255))
            first = lf == acc and int((j - 1) * LABEL_FPS / fps) < acc
            wr.write(img, FREEZE_S if first else 1.0 / LABEL_FPS * (LABEL_FPS / fps) if fps > LABEL_FPS else 0.0)
        shown.append({"n": k, "id": c["id"], "our_car": c["our_car"], "accident_s": acc / LABEL_FPS,
                      "light": c["light"], "weather": c["weather"], "video_frames": len(frames), "video_fps": fps})
        print(f"[{k}/{N}] {c['id']}: {'ours' if c['our_car'] else 'others'}, accident at {acc / LABEL_FPS:.1f} s, "
              f"video {len(frames)} frames at {fps:.0f} fps", flush=True)
    wr.close()
    OUT.with_suffix(".json").write_text(json.dumps(shown, indent=1))
    print(f"saved {OUT}; our car involved in {sum(s['our_car'] for s in shown)}/{N}")


if __name__ == "__main__":
    main()
