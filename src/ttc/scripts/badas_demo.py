"""Watch BADAS-Open (Nexar's learned collision-risk model) predict on real crash videos (local GPU).

Picks a random clip, runs BADAS through it as it would run live in the car
(a new risk reading every STEP_S seconds, each from the last 2 s of video),
saves an annotated video and opens it in the viewer (seek bar, steps). When
the viewer is closed with Q, the next random clip starts; press ESC in the
viewer to stop.

What you see:
    risk bar      BADAS's collision probability right now (0 to 1)
    risk plot     the probability over the whole clip; red line = warning threshold
    WARNING       risk above THRESHOLD
    crash label   the dataset's crash time (red band), when the clip has one

RUN IT (from the repo root; uses your GPU, about 2 GB of its memory):

    .venv\\Scripts\\python.exe src\\ttc\\scripts\\badas_demo.py

Clip pools (POOLS below):
    "ccd"    CCD crashes where our own car crashes (801 clips): NEW to BADAS (not its training data)
    "nexar"  local Nexar collision clips: BADAS was TRAINED on these, so expect it to look good
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "src/ttc/benchmarks/nexar"))
from random_test import clip_pool  # noqa: E402  (CCD + local Nexar clips)
from run_pipeline_video import crash_labels  # noqa: E402

# ---- CONFIG ----
POOLS = ["ccd"]                   # "ccd" (new to BADAS) and/or "nexar" (BADAS's training data)
BADAS_DIR = Path(r"C:\safe-distance-data\models\badas-open")   # scripts/get_badas_source.py --weights
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"
STEP_S = 0.25                     # a new risk reading every 0.25 s (BADAS sees 8 frames per second)
THRESHOLD = 0.9                   # risk above this = warning
FP16 = True                       # half precision: about 2x faster, same readings (checked on Modal)
OUT_DIR = REPO / "out" / "badas"
SEED = None                       # None = different clips every run
# ----------------

TEMPERATURE = 2.0                 # BADAS's own output softening (models/vjepa.py)


def load_badas():
    """BADAS-Open as its loader builds it, from the local copy of the repo."""
    sys.path.insert(0, str(BADAS_DIR / "src"))
    from models.vjepa import VJEPAModel
    m = VJEPAModel(model_name=BASE_MODEL, checkpoint_path=str(BADAS_DIR / "weights" / "badas_open.pth"),
                   frame_count=16, img_size=224, target_fps=8.0, use_sliding_window=False)
    m.load()
    return m


def decode(video: Path):
    """All frames (for display) plus BADAS's frames: frame round(i x fps / 8), 224x224 RGB."""
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    full = []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        full.append(img)
    picks = [int(round(i * fps / 8.0)) for i in range(int(round(len(full) / fps * 8.0)))]
    small = np.stack([cv2.cvtColor(cv2.resize(full[p], (224, 224)), cv2.COLOR_BGR2RGB)
                      for p in picks if p < len(full)])
    return full, fps, small


def readings(model, small: np.ndarray) -> list[tuple[float, float]]:
    """(time in s, risk) every STEP_S, each from the 16 BADAS frames (2 s) ending then."""
    from utils.video import apply_temperature_scaling
    step = max(1, round(STEP_S * 8))
    out = []
    for e in range(16, len(small) + 1, step):
        x = model.processor(videos=small[e - 16:e], return_tensors="pt")["pixel_values_videos"]
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=FP16):
            logits = model.model(x.to(model.device)).float()
        p = torch.softmax(apply_temperature_scaling(logits, temperature=TEMPERATURE), dim=1)[0, 1]
        out.append((e / 8.0, float(p)))
    return out


def annotate(full, fps, risk, labels, name) -> list[np.ndarray]:
    """Draw risk bar, plot over time, warning and crash label on every frame."""
    h, w = full[0].shape[:2]
    dur = len(full) / fps
    plot_h = 120
    x_of = lambda t: int(10 + (w - 20) * min(max(t / dur, 0), 1))  # noqa: E731
    y_of = lambda p: int(plot_h - 10 - (plot_h - 20) * p)  # noqa: E731
    base = np.full((plot_h, w, 3), 25, np.uint8)
    if labels["crash_s"]:
        a, b = labels["crash_s"]
        cv2.rectangle(base, (x_of(a), 5), (max(x_of(b), x_of(a) + 3), plot_h - 5), (0, 0, 140), -1)
    cv2.line(base, (10, y_of(THRESHOLD)), (w - 10, y_of(THRESHOLD)), (0, 0, 255), 1)
    pts = np.array([[x_of(t), y_of(p)] for t, p in risk], np.int32)
    if len(pts) > 1:
        cv2.polylines(base, [pts], False, (0, 255, 255), 2)
    cv2.putText(base, f"BADAS risk over time (red line = warning at {THRESHOLD})", (12, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
    out = []
    for k, img in enumerate(full):
        t = k / fps
        now = [p for tt, p in risk if tt <= t]
        p = now[-1] if now else None
        img = img.copy()
        if p is not None:
            warn = p > THRESHOLD
            colour = (0, 0, 255) if warn else (0, 200, 0) if p < 0.5 else (0, 165, 255)
            cv2.rectangle(img, (20, 20), (20 + int(300 * p), 50), colour, -1)
            cv2.rectangle(img, (20, 20), (320, 50), (255, 255, 255), 2)
            cv2.putText(img, f"risk {p:.2f}", (330, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2,
                        cv2.LINE_AA)
            if warn:
                cv2.putText(img, "WARNING: collision likely", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                            (0, 0, 255), 3, cv2.LINE_AA)
        else:
            cv2.putText(img, "BADAS warming up (needs 2 s of video)", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2, cv2.LINE_AA)
        c = labels["crash_s"]
        if c and c[0] <= t <= max(c[1], c[0] + 0.3):
            cv2.putText(img, "CRASH (dataset label)", (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3,
                        cv2.LINE_AA)
        cv2.putText(img, name, (w - 260, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        plot = base.copy()
        cv2.line(plot, (x_of(t), 5), (x_of(t), plot_h - 5), (255, 255, 255), 1)
        out.append(np.vstack([img, plot]))
    return out


def main() -> None:
    import random_test
    random_test.POOLS = POOLS
    clips = clip_pool()
    rng = random.Random(SEED)
    print(f"{len(clips)} clips to draw from ({', '.join(POOLS)}); loading BADAS ...")
    model = load_badas()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    from view_video import view
    while True:
        clip = rng.choice(clips)
        name = f"{'CCD' if 'ccd' in str(clip).lower() else 'Nexar'} {clip.stem}"
        print(f"=== {name}: decoding and running BADAS ...", flush=True)
        full, fps, small = decode(clip)
        risk = readings(model, small)
        labels = crash_labels(clip)
        frames = annotate(full, fps, risk, labels, name)
        out = OUT_DIR / f"{name.replace(' ', '_')}.mp4"
        wr = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), fps, (frames[0].shape[1], frames[0].shape[0]))
        for f in frames:
            wr.write(f)
        wr.release()
        peak = max(risk, key=lambda r: r[1]) if risk else (None, None)
        first = next((t for t, p in risk if p > THRESHOLD), None)
        print(f"   peak risk {peak[1]:.2f} at {peak[0]:.1f} s; first warning at "
              f"{'never' if first is None else f'{first:.1f} s'}; crash label {labels['crash_s']}; saved {out}")
        print("   viewer: Q = next random clip, ESC = stop", flush=True)
        if view(str(out)) == "stop":
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
