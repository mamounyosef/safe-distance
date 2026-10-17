"""Show, step by step, what happens to a dashcam frame before BADAS-Open (and our stage 1 training) sees it.

The exact steps of the current pipeline, on 10 real frames (5 Nexar crash clips at 1 s before the crash, 5 BDD100K
normal clips at their middle):
    1. original video frame                1280 x 720
    2. frame cache (frames.py)             squashed to 224 x 224 (cv2.resize, bilinear): the 16:9 picture becomes square
    3. BADAS's processor, step 1           enlarged to 292 x 292 (bilinear)
    4. BADAS's processor, step 2           the middle 256 x 256 is kept  = what the model sees
Each output image shows the 4 steps side by side, every step drawn at the same height (pixels enlarged as blocks, so
the real detail of each step is visible), plus the area that survives the crop drawn on the original.

Uses BADAS's real video processor (V-JEPA 2's, from Hugging Face) for steps 3-4, so it is exactly what training does.

RUN IT (from the repo root, this PC, free):
    .venv\\Scripts\\python.exe scripts\\preprocess_demo.py

Output: Downloads\\safe-distance-testing\\preprocessing\\01_... .png ... 10_... .png
"""

import csv
import random
from pathlib import Path

import cv2
import numpy as np
import torch

# ---- CONFIG ----
NEXAR_DIR = Path(r"C:\safe-distance-data\nexar\samples")          # local Nexar crash clips (+ metadata.csv)
BDD_DIR = Path(r"C:\safe-distance-data\bdd100k\samples")          # local BDD100K clips
OUT = Path.home() / "Downloads" / "safe-distance-testing" / "preprocessing"
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"                # BADAS's processor comes from this model
N_EACH, SEED = 5, 3
SHOW_H = 360                                                      # every panel drawn at this height
CACHE_SIZE = 224                                                  # frames.py: cv2.resize(img, (224, 224))
MEAN, STD = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])   # ImageNet (to undo for display)
# ----------------


def read_frame(path: Path, t: float) -> np.ndarray:
    """The video frame at time t (seconds), as RGB."""
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, img = cap.read()
    cap.release()
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def label(img: np.ndarray, lines: list[str]) -> np.ndarray:
    """Write lines of text on the top of an image (with a dark outline so it reads on any picture)."""
    img = img.copy()
    for i, s in enumerate(lines):
        y = 26 + 26 * i
        cv2.putText(img, s, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, s, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def blocks(img: np.ndarray, h: int) -> np.ndarray:
    """Enlarge to height h with NEAREST pixels, so each real pixel shows as a block (no smoothing hides the loss)."""
    w = int(round(img.shape[1] * h / img.shape[0]))
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_NEAREST)


def main() -> None:
    from transformers import AutoVideoProcessor
    proc = AutoVideoProcessor.from_pretrained(BASE_MODEL)         # the processor BADAS uses
    OUT.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)
    meta = list(csv.DictReader((NEXAR_DIR / "metadata.csv").open()))
    meta = [r for r in meta if (NEXAR_DIR / r["file_name"]).exists()]
    picks = [("Nexar crash clip", NEXAR_DIR / r["file_name"], float(r["time_of_event"]) - 1.0, "1 s before the crash")
             for r in rng.sample(meta, N_EACH)]
    bdd = sorted(BDD_DIR.glob("*.mov"))
    picks += [("BDD100K normal clip", p, 20.0, "20 s into the clip") for p in rng.sample(bdd, N_EACH)]

    for k, (kind, path, t, when) in enumerate(picks, 1):
        orig = read_frame(path, t)                                         # 1) 1280 x 720
        cache = cv2.resize(orig, (CACHE_SIZE, CACHE_SIZE))                  # 2) frames.py: squash to 224 x 224
        # 3-4) BADAS's processor on the cached frame: enlarge (shortest edge 292), then centre crop 256
        px = proc(videos=cache[None], return_tensors="pt")["pixel_values_videos"][0, 0]   # 3 x 256 x 256, normalised
        model_in = ((px.permute(1, 2, 0).numpy() * STD + MEAN).clip(0, 1) * 255).round().astype(np.uint8)
        enlarged = cv2.resize(cache, (292, 292), interpolation=cv2.INTER_LINEAR)          # the step-3 picture

        # where the 256 crop sits inside the 292 picture, and the same area on the original frame
        off = (292 - 256) // 2
        enl_box = enlarged.copy()
        cv2.rectangle(enl_box, (off, off), (off + 256, off + 256), (255, 220, 0), 2)
        orig_box = orig.copy()
        fx, fy = orig.shape[1] / 292, orig.shape[0] / 292
        cv2.rectangle(orig_box, (int(off * fx), int(off * fy)), (int((off + 256) * fx), int((off + 256) * fy)),
                      (255, 220, 0), 4)

        panels = [label(cv2.resize(orig_box, (int(SHOW_H * 16 / 9), SHOW_H)),
                        ["1) original frame 1280 x 720", "yellow = area the model keeps"]),
                  label(blocks(cache, SHOW_H), ["2) cache: squashed", "to 224 x 224"]),
                  label(blocks(enl_box, SHOW_H), ["3) enlarged to 292", "yellow = 256 crop"]),
                  label(blocks(model_in, SHOW_H), ["4) model input", "256 x 256"])]
        gap = np.full((SHOW_H, 8, 3), 30, np.uint8)
        row = np.hstack(sum([[p, gap] for p in panels], [])[:-1])
        title = np.full((40, row.shape[1], 3), 20, np.uint8)
        cv2.putText(title, f"{k}/10  {kind} {path.name}, frame at {when}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2, cv2.LINE_AA)
        out = OUT / f"{k:02d}_{'nexar' if 'Nexar' in kind else 'bdd'}_{path.stem}.png"
        cv2.imwrite(str(out), cv2.cvtColor(np.vstack([title, row]), cv2.COLOR_RGB2BGR))
        print(f"saved {out}")


if __name__ == "__main__":
    main()
