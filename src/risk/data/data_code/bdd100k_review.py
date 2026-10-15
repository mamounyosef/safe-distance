"""Review video for cleaning BDD100K train: the clips plain BADAS-Open finds riskiest, for a PERSON to judge (this PC, free).

BDD100K is used as "normal driving" (label 0). If a clip holds a real near-miss, that label is wrong,
so the person watching decides which clips to remove. BADAS only orders the list (never removes anything).

Ranking: highest risk reading first; ties (many clips reach 0.99+) broken by how long the risk stays
at or above HIGH, since a real near-miss usually stays high for a while, and many false alarms are short spikes.
Each clip: title card with its rank, then BEFORE_S before to AFTER_S after its riskiest moment, with the
live risk reading drawn on the frame (red when >= HIGH).

Needs the scan first (src/risk/runs/baseline_badas_open/results/bdd_train/series_bdd_train.json):

    python -m modal run src\\risk\\eval_risk.py --sets bdd_train

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_review.py

Output: C:\\Users\\mamou\\Downloads\\bdd100k_review.mp4 + bdd100k_review.json (rank -> clip id, to note your decisions).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nexar_samples import volume_get  # noqa: E402
from sample_video import Writer, card, text  # noqa: E402

# ---- CONFIG ----
SERIES = Path(__file__).resolve().parents[2] / "runs/baseline_badas_open/results/bdd_train/series_bdd_train.json"
CACHE = Path(r"C:\safe-distance-data\bdd100k\samples")
OUT = Path.home() / "Downloads" / "bdd100k_review.mp4"
TOP = 60                         # clips to review
HIGH = 0.99                      # "very high" risk level used for the tie-break and the red marking
BEFORE_S, AFTER_S = 6.0, 2.0     # seconds shown around the riskiest moment
# --bands: a few random clips from each risk band, to estimate how many real near-misses each band holds.
# Band = (name, first rank, last rank) in the ranked list (rank 1 = riskiest). Ranks 1-15 were already reviewed.
BANDS = [("ranks 16-100", 16, 100), ("ranks 101-638 (peak over 0.99)", 101, 638),
         ("peak 0.98-0.99", 639, 1107), ("peak 0.95-0.98", 1108, 1685), ("peak 0.90-0.95", 1686, 2049)]
PER_BAND, SEED = 8, 7
# --boundary: where do real near-misses stop? Ranks 16-100 were all real (8/8), 101-638 almost all normal (0/8).
BOUNDARY = [("ranks 101-200", 101, 200), ("ranks 201-638", 201, 638)]
BOUNDARY_PER_BAND = 10
BAND_BEFORE_S, BAND_AFTER_S = 2.5, 1.0     # short: enough to identify the moment and move on
BAND_OUT = Path.home() / "Downloads" / "safe-distance-testing" / "bdd100k" / "4_cleaning_bands.mp4"
SIZE, FPS = (1280, 720), 30.0
# ----------------


def rank(series: dict) -> list[dict]:
    """Clips ordered by (highest risk, seconds at or above HIGH), riskiest first."""
    rows = []
    for clip, s in series.items():
        if not s:
            continue
        t_peak, p_peak = max(s, key=lambda r: r[1])
        times = [t for t, _ in s]
        step = min((b - a for a, b in zip(times, times[1:]) if b > a), default=1.0)
        rows.append({"clip": clip, "max_risk": p_peak, "peak_s": t_peak,
                     "seconds_high": round(sum(p >= HIGH for _, p in s) * step, 1)})
    return sorted(rows, key=lambda r: (r["max_risk"], r["seconds_high"]), reverse=True)


def risk_at(s: list, t: float) -> float | None:
    """The latest reading at or before time t (what the system would show live)."""
    past = [p for tt, p in s if tt <= t]
    return past[-1] if past else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bands", action="store_true", help="random clips per risk band (short) instead of the top 60")
    ap.add_argument("--boundary", action="store_true", help="more clips from ranks 101-638 (short)")
    a = ap.parse_args()
    series = json.loads(SERIES.read_text())
    full = rank(series)
    for i, r in enumerate(full, 1):
        r["rank"] = i
    if a.bands or a.boundary:
        rng = random.Random(SEED + (1 if a.boundary else 0))
        bands, per = (BOUNDARY, BOUNDARY_PER_BAND) if a.boundary else (BANDS, PER_BAND)
        ranked = []
        for name, lo, hi in bands:
            for r in sorted(rng.sample(full[lo - 1:hi], per), key=lambda r: r["rank"]):
                ranked.append({**r, "band": name})
        out = BAND_OUT.with_name("5_cleaning_boundary.mp4") if a.boundary else BAND_OUT
        before, after = BAND_BEFORE_S, BAND_AFTER_S
    else:
        ranked, out, before, after = full[:TOP], OUT, BEFORE_S, AFTER_S
    print(f"{len(series)} clips scanned; reviewing {len(ranked)}")
    out.parent.mkdir(parents=True, exist_ok=True)
    wr = Writer(out, SIZE, FPS)
    for k, r in enumerate(ranked, 1):
        path = volume_get(f"bdd100k/videos/100k/train/{r['clip']}.mov", CACHE / f"{r['clip']}.mov")
        cap = cv2.VideoCapture(str(path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        wr.write(card(SIZE, [f"#{k}/{len(ranked)}   {r.get('band', '')}",
                             f"rank {r['rank']}, highest risk {r['max_risk']:.3f}",
                             "Real near-miss? Note the number."]), 0.8 if (a.bands or a.boundary) else 1.5)
        start = max(0.0, r["peak_s"] - before)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(start * fps))
        f = int(start * fps)
        while f < (r["peak_s"] + after) * fps:
            ok, img = cap.read()
            if not ok:
                break
            t = f / fps
            img = cv2.resize(img, SIZE)
            p = risk_at(series[r["clip"]], t)
            colour = (0, 0, 255) if p is not None and p >= HIGH else (255, 255, 255)
            text(img, f"#{k}   {t - r['peak_s']:+.1f} s from riskiest moment", (15, 40), 0.9)
            text(img, f"BADAS risk: {'-' if p is None else f'{p:.3f}'}", (15, 85), 1.0, colour)
            if p is not None and p >= HIGH:
                cv2.rectangle(img, (0, 0), (SIZE[0] - 1, SIZE[1] - 1), (0, 0, 255), 8)
            wr.write(img)
            f += 1
        cap.release()
        print(f"[{k}/{len(ranked)}] {r['clip']}: max {r['max_risk']:.3f}, {r['seconds_high']} s high", flush=True)
    wr.close()
    out.with_suffix(".json").write_text(json.dumps([{"n": k, **r} for k, r in enumerate(ranked, 1)], indent=1))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
