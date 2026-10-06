"""Does fusing BADAS-Open's risk with our physical checks cut false warnings? (CPU only.)

Uses ONLY the Public half of Nexar's test set (672 clips); the Private half is
kept untouched for the final, comparable test.

Every 0.5 s in the last WINDOW_S seconds of each clip (where both systems have
readings) we take:
    BADAS:  its collision probability at that moment (badas_series.json)
    ours:   over the last 0.5 s, for objects in our path: highest 1 / TTC,
            nearest distance, highest closing speed, and whether anything is in our path
A small model (logistic regression: a weighted sum of these numbers passed
through a sigmoid) learns from them when to warn. It is trained and tested
with 5-fold cross-validation by clip: the clips are split into 5 groups, it
learns on 4 and is tested on the 5th, rotating, so every clip is tested once
by a model that never saw it.

Compared on the same clips and moments: BADAS alone, ours alone, fusion.
    crashes warned  share of collision clips with a warning in the window
    false warnings  warning episodes per hour in normal-driving clips
For each system the threshold is swept; we report the share of crashes
warned at a few fixed false-warning rates.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\fusion_public.py

Writes results/test1/fusion_public.json and FUSION_PUBLIC.md (generated from it).
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_nexar as sn  # noqa: E402

# ---- CONFIG ----
RUN = "test1"
SOLUTION = Path(r"C:\safe-distance-data\nexar\meta\solution.csv")
WINDOW_S = 3.0               # last 3 s of each clip (our readings cover 5 s; the first 2 let the filter settle)
STEP_S = 0.5                 # BADAS reading interval
FOLDS, SEED = 5, 0
FALSE_RATES = [20, 50, 100, 200]   # false warnings per hour at which crashes warned are compared
MAX_DIST_M = 60.0            # "nothing in our path" counts as this far
OUT = Path(__file__).resolve().parent / "results" / RUN
FEATURES = ["badas_logit", "inv_ttc", "near_dist", "closing", "in_path"]
# ----------------


def steps_for_clip(clip: dict, badas: list) -> list[dict]:
    """One row per BADAS reading in the window: BADAS risk + our numbers over the preceding 0.5 s."""
    frames = sn.filter_clip(clip, clahe=True)
    end = frames[-1][0]
    rows = []
    for t, p in badas:
        if t < end - WINDOW_S or t > end + 1e-6:
            continue
        inv, dist, closing, n = 0.0, MAX_DIST_M, 0.0, 0
        for ft, objs in frames:
            if not (t - STEP_S < ft <= t):
                continue
            for o in objs:
                if o["gap"] > sn.CORRIDOR_M:
                    continue
                n += 1
                dist = min(dist, o["distance"])
                if o["ttc"] is not None and not math.isinf(o["ttc"]):
                    inv = max(inv, 1.0 / max(o["ttc"], 0.05))
                    closing = max(closing, o["distance"] / max(o["ttc"], 0.05))
        pc = min(max(p, 1e-4), 1 - 1e-4)
        rows.append({"t": t, "badas": p, "badas_logit": math.log(pc / (1 - pc)), "inv_ttc": min(inv, 5.0),
                     "near_dist": dist / MAX_DIST_M, "closing": min(closing, 30.0) / 30.0, "in_path": float(n > 0)})
    return rows


def fit_logistic(x: np.ndarray, y: np.ndarray, iters: int = 3000, lr: float = 0.1, l2: float = 1e-3):
    """Plain logistic regression by gradient descent (features already standardised)."""
    w, b = np.zeros(x.shape[1]), 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(x @ w + b)))
        g = p - y
        w -= lr * (x.T @ g / len(y) + l2 * w)
        b -= lr * g.mean()
    return w, b


def evaluate(clips: dict, score_key: str) -> list[tuple[float, float, float]]:
    """Sweep the threshold: (threshold, share of crashes warned, false warnings per hour)."""
    values = sorted({r[score_key] for c in clips.values() for r in c["rows"]})
    pos = [c for c in clips.values() if c["target"] == 1]
    neg = [c for c in clips.values() if c["target"] == 0]
    hours = sum(len(c["rows"]) * STEP_S for c in neg) / 3600
    curve = []
    for thr in values[::max(len(values) // 400, 1)]:
        warned = sum(1 for c in pos if any(r[score_key] > thr for r in c["rows"]))
        eps = 0
        for c in neg:
            above = [r[score_key] > thr for r in c["rows"]]
            eps += sum(1 for i, a in enumerate(above) if a and (i == 0 or not above[i - 1]))   # episode starts
        curve.append((thr, warned / len(pos), eps / hours))
    return curve


def at_rate(curve, rate: float) -> float:
    """Best share of crashes warned with at most `rate` false warnings per hour."""
    ok = [share for _, share, fr in curve if fr <= rate]
    return round(max(ok), 3) if ok else 0.0


def main() -> None:
    public = {r["id"]: int(r["target"]) for r in csv.DictReader(SOLUTION.open()) if r["Usage"] == "Public"}
    series = json.loads((OUT / "badas_series.json").read_text())
    clips = {}
    for p in sorted(sn.DATA.rglob(f"{RUN}/test-public/**/*.json.gz")):
        with gzip.open(p, "rt") as fh:
            clip = json.load(fh)
        cid = clip["clip"]
        if cid in public and clip["frames"] and series.get(cid):
            rows = steps_for_clip(clip, series[cid])
            if rows:
                clips[cid] = {"target": public[cid], "rows": rows}
    print(f"{len(clips)} Public clips with both systems' readings "
          f"({sum(c['target'] for c in clips.values())} collisions)")

    # 5-fold cross-validation by clip, both classes spread evenly over the folds.
    ids = sorted(clips)
    random.Random(SEED).shuffle(ids)
    ids.sort(key=lambda c: clips[c]["target"])
    fold_of = {cid: i % FOLDS for i, cid in enumerate(ids)}
    weights = []
    for k in range(FOLDS):
        train = [r | {"y": clips[c]["target"]} for c in clips if fold_of[c] != k for r in clips[c]["rows"]]
        x = np.array([[r[f] for f in FEATURES] for r in train])
        mu, sd = x.mean(0), x.std(0) + 1e-9
        w, b = fit_logistic((x - mu) / sd, np.array([r["y"] for r in train], float))
        weights.append(dict(zip(FEATURES, (w / sd).round(3).tolist())))
        for c in clips:
            if fold_of[c] == k:
                for r in clips[c]["rows"]:
                    z = (np.array([r[f] for f in FEATURES]) - mu) / sd
                    r["fusion"] = float(1 / (1 + np.exp(-(z @ w + b))))

    # Gates: BADAS's risk counts only when our physical check agrees (else the score is 0).
    for c in clips.values():
        for r in c["rows"]:
            r["gate_in_path"] = r["badas"] * r["in_path"]
            r["gate_closing"] = r["badas"] * (r["inv_ttc"] > 0)
            r["gate_near_20m"] = r["badas"] * (r["near_dist"] * MAX_DIST_M < 20)
            r["gate_ttc_4s"] = r["badas"] * (r["inv_ttc"] > 0.25)
    systems = {"BADAS alone": "badas", "Ours alone (1 / TTC in our path)": "inv_ttc", "Fusion": "fusion",
               "BADAS, only if something in our path": "gate_in_path",
               "BADAS, only if something in our path is closing in": "gate_closing",
               "BADAS, only if something in our path within 20 m": "gate_near_20m",
               "BADAS, only if TTC in our path < 4 s": "gate_ttc_4s"}
    curves = {name: evaluate(clips, key) for name, key in systems.items()}
    neg_hours = sum(len(c["rows"]) * STEP_S for c in clips.values() if c["target"] == 0) / 3600
    results = {"clips": len(clips), "collisions": sum(c["target"] for c in clips.values()),
               "normal_hours": round(neg_hours, 3), "fusion_weights_per_fold": weights,
               "crashes_warned_at_false_rate": {n: {str(r): at_rate(cv, r) for r in FALSE_RATES}
                                                for n, cv in curves.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fusion_public.json").write_text(json.dumps(results, indent=1))
    lines = [f"# Fusion test on Nexar test set, Public half only (run {RUN})", "",
             "Generated by fusion_public.py from fusion_public.json. Do not edit by hand.", "",
             f"{results['clips']} clips ({results['collisions']} collisions), the last {WINDOW_S:g} s of each, "
             f"a decision every {STEP_S:g} s; {neg_hours * 60:.0f} min of normal driving. Fusion = logistic "
             f"regression on {', '.join(FEATURES)}, {FOLDS}-fold cross-validation by clip.", "",
             "Share of crashes warned, at a given number of false warnings per hour:", "",
             "| System | " + " | ".join(f"<= {r}/h" for r in FALSE_RATES) + " |",
             "|---|" + "---|" * len(FALSE_RATES)]
    for n in systems:
        lines.append(f"| {n} | " + " | ".join(f"{results['crashes_warned_at_false_rate'][n][str(r)] * 100:.0f}%"
                                             for r in FALSE_RATES) + " |")
    lines += ["", "Fusion weights (per fold, on the original feature scales):", ""]
    lines += [f"- fold {i + 1}: {w}" for i, w in enumerate(weights)]
    (OUT / "FUSION_PUBLIC.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
