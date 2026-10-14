"""20 random BDD100K TRAIN clips (from our drawn 3,000, the normal driving we train on), as ONE video (this PC, free).

BDD100K videos have no event labels: they are ordinary driving, used as "no danger" examples.
Each clip is about 40 s, so only SHOW_S seconds from the middle are shown, to keep the video short.
Videos come from the Modal Volume (modal volume get: a file copy, no container, no cost).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_samples.py
    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_samples.py --seed 22 --out "%USERPROFILE%\\Downloads\\bdd100k_samples_2.mp4"

Output: C:\\Users\\mamou\\Downloads\\bdd100k_samples.mp4 (+ bdd100k_samples.json).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nexar_samples import volume_get  # noqa: E402
from sample_video import Writer, card, text  # noqa: E402

# ---- CONFIG ----
IDS = Path(__file__).resolve().parents[1] / "bdd100k_ids" / "train_3000.txt"
CACHE = Path(r"C:\safe-distance-data\bdd100k\samples")
OUT = Path.home() / "Downloads" / "bdd100k_samples.mp4"
N, SEED = 20, 21
SHOW_S = 15.0                      # seconds shown per clip (from the middle)
SIZE, FPS = (1280, 720), 30.0
TITLE_S = 1.5
# ----------------


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    ids = IDS.read_text().split()
    picks = random.Random(a.seed).sample(ids, N)
    wr, shown = Writer(a.out, SIZE, FPS), []
    for k, cid in enumerate(picks, 1):
        path = volume_get(f"bdd100k/videos/100k/train/{cid}.mov", CACHE / f"{cid}.mov")
        cap = cv2.VideoCapture(str(path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
        start = max(0.0, length / 2 - SHOW_S / 2)            # middle of the clip
        wr.write(card(SIZE, [f"BDD100K clip {k}/{N}   ({cid})",
                             f"normal driving (no label)   {w}x{h} at {fps:.0f} fps, {length:.0f} s long",
                             f"showing {start:.0f} s to {start + SHOW_S:.0f} s"]), TITLE_S)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(start * fps))
        f = int(start * fps)
        while f < (start + SHOW_S) * fps:
            ok, img = cap.read()
            if not ok:
                break
            img = cv2.resize(img, SIZE)
            text(img, f"{cid}   {f / fps:.1f} s", (15, 40), 0.9)
            wr.write(img)
            f += 1
        cap.release()
        shown.append({"n": k, "clip": cid, "width": w, "height": h, "fps": round(fps, 2), "length_s": round(length, 1)})
        print(f"[{k}/{N}] {cid}: {w}x{h} at {fps:.1f} fps, {length:.1f} s", flush=True)
    wr.close()
    a.out.with_suffix(".json").write_text(json.dumps(shown, indent=1))
    print(f"saved {a.out}")


if __name__ == "__main__":
    main()
