"""Show, step by step and as VIDEO, what happens to dashcam footage before BADAS-Open (and our stage 1 training) sees it.

The exact steps of the current pipeline, on 10 real clips (5 Nexar crash clips: the 4 s up to the crash; 5 BDD100K
normal clips: 4 s from the 20 s point):
    1. original video                      1280 x 720, 30 frames per second
    2. frame cache (frames.py)             8 frames per second, each squashed to 224 x 224 (cv2.resize, bilinear):
                                           the 16:9 picture becomes square
    3. BADAS's processor, step 1           enlarged to 292 x 292 (bilinear)
    4. BADAS's processor, step 2           the middle 256 x 256 is kept  = what the model sees
Panels 2-4 change only 8 times per second, like the model's input (frame round(i x fps / 8), as in frames.py).
Every panel is drawn at the same height with pixels enlarged as blocks, so the real detail of each step is visible.
Steps 3-4 use BADAS's real video processor (V-JEPA 2's, from Hugging Face): exactly what training does.

RUN IT (from the repo root, this PC, free, about a minute):
    .venv\\Scripts\\python.exe scripts\\preprocess_demo.py

Output: Downloads\\safe-distance-testing\\preprocessing\\preprocessing_steps.mp4
"""

import csv
import random
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/risk/data/data_code"))
from sample_video import Writer, card  # noqa: E402   (title cards + one H.264 video)

# ---- CONFIG ----
NEXAR_DIR = Path(r"C:\safe-distance-data\nexar\samples")          # local Nexar crash clips (+ metadata.csv)
BDD_DIR = Path(r"C:\safe-distance-data\bdd100k\samples")          # local BDD100K clips
OUT = Path.home() / "Downloads" / "safe-distance-testing" / "preprocessing" / "preprocessing_steps.mp4"
OUT_WIDE = OUT.with_name("now_vs_256x448.mp4")                   # --wide: current input vs the 16:9 proposal
WIDE_H, WIDE_W = 256, 448                                        # proposal: 16:9 kept, both multiples of 16
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"                # BADAS's processor comes from this model
N_EACH, SEED = 5, 3                                               # 5 Nexar + 5 BDD100K clips, fixed pick
SEGMENT_S = 4.0                                                   # seconds shown per clip
BDD_START_S = 20.0                                                # BDD100K clips: start here
SHOW_H = 360                                                      # every panel drawn at this height
CACHE_SIZE, CACHE_FPS = 224, 8                                    # frames.py: 224 x 224, 8 per second
MEAN, STD = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])   # ImageNet (undone for display)
VIDEO_FPS, TITLE_S = 30.0, 2.5
# ----------------


def label(img: np.ndarray, lines: list[str]) -> np.ndarray:
    """Put lines of text in a dark bar ABOVE the image (never over the picture)."""
    bar = np.full((24 * len(lines) + 10, img.shape[1], 3), 20, np.uint8)
    for i, s in enumerate(lines):
        cv2.putText(bar, s, (8, 22 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    return np.vstack([bar, img])


def blocks(img: np.ndarray, h: int) -> np.ndarray:
    """Enlarge to height h with NEAREST pixels: each real pixel shows as a block (no smoothing hides the loss)."""
    w = int(round(img.shape[1] * h / img.shape[0]))
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_NEAREST)


def model_views(cache_frames: np.ndarray, proc) -> list[tuple[np.ndarray, np.ndarray]]:
    """For cached 224 frames: (step-3 picture 292 with the crop box, step-4 model input 256) per frame, using
    BADAS's processor for the model input (one call on all frames, as in training)."""
    px = proc(videos=cache_frames, return_tensors="pt")["pixel_values_videos"][0]          # n x 3 x 256 x 256
    off = (292 - 256) // 2
    out = []
    for c, p in zip(cache_frames, px):
        model_in = ((p.permute(1, 2, 0).numpy() * STD + MEAN).clip(0, 1) * 255).round().astype(np.uint8)
        enlarged = cv2.resize(c, (292, 292), interpolation=cv2.INTER_LINEAR)
        cv2.rectangle(enlarged, (off, off), (off + 256, off + 256), (255, 220, 0), 2)
        out.append((enlarged, model_in))
    return out


def wide_input(orig: np.ndarray) -> np.ndarray:
    """The 16:9 proposal: shrink the original 1280 x 720 frame to 455 x 256 (shape kept, no squash), then cut
    448 x 256 out of the middle (only about 3 px off each side) so both sides are multiples of the 16-pixel patch."""
    w = int(round(orig.shape[1] * WIDE_H / orig.shape[0]))                     # 1280 x 256 / 720 = 455
    small = cv2.resize(orig, (w, WIDE_H), interpolation=cv2.INTER_AREA)       # INTER_AREA: best for shrinking
    x0 = (w - WIDE_W) // 2
    return small[:, x0:x0 + WIDE_W]


def clip_frames(path: Path, t0: float, t1: float):
    """Every original frame between t0 and t1 (RGB), with its time, plus the video's frame rate."""
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames, f = [], 0
    while True:
        ok, img = cap.read()
        if not ok:
            break
        t = f / fps
        f += 1
        if t0 <= t < t1:
            frames.append((t, cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
        if t >= t1:
            break
    cap.release()
    return frames, fps


def main() -> None:
    wide = "--wide" in sys.argv                                  # compare the current input with 256 x 448
    out_path = OUT_WIDE if wide else OUT
    from transformers import AutoVideoProcessor
    proc = AutoVideoProcessor.from_pretrained(BASE_MODEL)         # the processor BADAS uses
    OUT.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)
    meta = [r for r in csv.DictReader((NEXAR_DIR / "metadata.csv").open()) if (NEXAR_DIR / r["file_name"]).exists()]
    picks = []
    for r in rng.sample(meta, N_EACH):                            # Nexar: the 4 s up to the crash
        ev = float(r["time_of_event"])
        picks.append(("Nexar crash clip", NEXAR_DIR / r["file_name"], ev - SEGMENT_S, ev, "the 4 s up to the crash"))
    for p in rng.sample(sorted(BDD_DIR.glob("*.mov")), N_EACH):   # BDD100K: 4 s from 20 s in
        picks.append(("BDD100K normal clip", p, BDD_START_S, BDD_START_S + SEGMENT_S, "4 s of normal driving"))

    wr = None
    for k, (kind, path, t0, t1, what) in enumerate(picks, 1):
        frames, fps = clip_frames(path, t0, t1)
        # the frames the cache keeps: frame round(i x fps / 8), i.e. 8 per second (frames.py)
        keep = sorted({int(round(i * fps / CACHE_FPS)) for i in range(int(t0 * CACHE_FPS), int(t1 * CACHE_FPS) + 1)})
        first = int(round(t0 * fps))
        kept = {i: frames[i - first][1] for i in keep if 0 <= i - first < len(frames)}
        cache = {i: cv2.resize(img, (CACHE_SIZE, CACHE_SIZE)) for i, img in kept.items()}      # step 2
        views = dict(zip(cache, model_views(np.stack(list(cache.values())), proc)))            # steps 3-4

        rows = []
        for j, (t, orig) in enumerate(frames):
            idx = max(i for i in cache if i <= first + j) if any(i <= first + j for i in cache) else min(cache)
            enlarged, model_in = views[idx]                      # the latest 8-per-second frame (what the model has)
            orig_box = cv2.resize(orig, (int(SHOW_H * 16 / 9), SHOW_H))
            off, fx, fy = 18, orig_box.shape[1] / 292, orig_box.shape[0] / 292       # the kept area on the original
            cv2.rectangle(orig_box, (int(off * fx), int(off * fy)), (int((off + 256) * fx), int((off + 256) * fy)),
                          (255, 220, 0), 2)
            if wide:                                             # current input vs the 16:9 proposal
                new_in = wide_input(kept[idx])                   # from the same 8-per-second frame
                panels = [label(orig_box, ["original 1280 x 720", "yellow = what the CURRENT input keeps"]),
                          label(blocks(model_in, SHOW_H), ["NOW: 256 x 256", "squashed 1.8x sideways"]),
                          label(blocks(new_in, SHOW_H), ["PROPOSAL: 256 x 448 (true 16:9)",
                                                         "shapes kept, almost the whole width"])]
            else:
              panels = [label(orig_box, ["1) original 1280 x 720, 30 fps", "yellow = area the model keeps"]),
                      label(blocks(cache[idx], SHOW_H), ["2) cache: 8 fps,", "squashed to 224 x 224"]),
                      label(blocks(enlarged, SHOW_H), ["3) enlarged to 292", "yellow = 256 crop"]),
                      label(blocks(model_in, SHOW_H), ["4) model input", "256 x 256"])]
            gap = np.full((panels[0].shape[0], 8, 3), 30, np.uint8)
            row = np.hstack(sum([[p, gap] for p in panels], [])[:-1])
            title = np.full((44, row.shape[1], 3), 20, np.uint8)
            cv2.putText(title, f"{k}/10  {kind} {path.name}: {what}   t = {t:.2f} s", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            rows.append(np.vstack([title, row]))
        if wr is None:                                             # size from the first frame (even numbers)
            size = (rows[0].shape[1] // 2 * 2, rows[0].shape[0] // 2 * 2)
            wr = Writer(out_path, size, VIDEO_FPS)
            intro = (["The current model input vs the 16:9 proposal",
                      "NOW: squashed to a square, then the middle 256 x 256 kept",
                      "PROPOSAL: shape kept, 256 x 448 (about the whole width)"] if wide else
                     ["How a dashcam frame becomes BADAS's input (the current pipeline)",
                      "1) original 1280 x 720  ->  2) 8 fps, squashed to 224 x 224",
                      "3) enlarged to 292 x 292  ->  4) middle 256 x 256 = model input"])
            wr.write(card(size, intro), 5.0)
        wr.write(card(size, [f"{k}/10  {kind}", f"{path.name}: {what}"]), TITLE_S)
        for r in rows:
            wr.write(cv2.cvtColor(r, cv2.COLOR_RGB2BGR))          # Writer expects BGR (OpenCV order)
        print(f"[{k}/10] {kind} {path.name}: {len(rows)} frames", flush=True)
    wr.close()
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
