"""How plain BADAS-Open ranks the 500 BDD100K val clips (free, saved readings only).

Ranked the same way as train (bdd100k_review.rank: highest peak, then seconds at or above 0.99). Train readings were
every 1 s, val every 0.5 s, so val peaks can be slightly higher for the same clip.

Shows, per band of val ranks: the BADAS peak range, the train ranks with the same peak (and what the hand labels
found there), and how much of val's high-risk time (readings at or above 0.9 / 0.99, where false warnings come
from) sits in that band.

Writes src/risk/data/bdd100k_ids/val_flags.json (bands + the full val ranking).

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe scripts\\bdd100k_val_flags.py
"""

import bisect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/risk/data/data_code"))
from bdd100k_review import SERIES, rank  # noqa: E402

VAL = ROOT / "src/risk/runs/baseline_badas_open/results/eval/series_bdd_val.json"
LABELS = ROOT / "src/risk/data/bdd100k_ids/manual_labels.json"
OUT = ROOT / "src/risk/data/bdd100k_ids/val_flags.json"
BANDS = [(1, 25), (26, 49), (50, 75), (76, 100), (101, 137), (138, 200), (201, 300), (301, 400), (401, 500)]
STEP_S = 0.5                                # val reading interval


def train_rank_for(peak: float, train_peaks_desc: list[float]) -> int:
    """Train rank whose peak equals this val peak (number of train clips with a higher or equal peak)."""
    neg = [-p for p in train_peaks_desc]
    return bisect.bisect_right(neg, -peak)


val_series = json.loads(VAL.read_text())
val = rank(val_series)
train = rank(json.loads(SERIES.read_text()))
train_peaks = [r["max_risk"] for r in train]
labels = json.loads(LABELS.read_text())
train_rank_of = {r["clip"]: i for i, r in enumerate(train, 1)}

# Hand-label results by train rank, to say what the matching train ranks held
lab_by_rank = {train_rank_of[c]: v["label"] for c, v in labels.items() if c in train_rank_of}

total09 = sum(sum(p >= 0.9 for _, p in s) for s in val_series.values())
total099 = sum(sum(p >= 0.99 for _, p in s) for s in val_series.values())
bands = []
for lo, hi in BANDS:
    b = val[lo - 1:hi]
    s09 = sum(sum(p >= 0.9 for _, p in val_series[r["clip"]]) for r in b)
    s099 = sum(sum(p >= 0.99 for _, p in val_series[r["clip"]]) for r in b)
    t_hi, t_lo = train_rank_for(b[0]["max_risk"], train_peaks), train_rank_for(b[-1]["max_risk"], train_peaks)
    labs = [lab_by_rank[k] for k in range(max(1, t_hi), t_lo + 1) if k in lab_by_rank]
    bands.append({"val_ranks": f"{lo}-{hi}", "clips": len(b),
                  "peak": [round(b[-1]["max_risk"], 4), round(b[0]["max_risk"], 4)],
                  "same_peak_train_ranks": f"{max(1, t_hi)}-{t_lo}",
                  "train_labelled": len(labs),
                  "train_risk_pct": round(100 * labs.count("risk") / len(labs), 0) if labs else None,
                  "seconds_ge_0.9": s09 * STEP_S, "pct_of_val_time_ge_0.9": round(100 * s09 / total09, 1),
                  "seconds_ge_0.99": s099 * STEP_S, "pct_of_val_time_ge_0.99": round(100 * s099 / total099, 1)})
out = {"val_clips": len(val), "val_seconds_ge_0.9": total09 * STEP_S, "val_seconds_ge_0.99": total099 * STEP_S,
       "note": "train ranks 1-200 were removed without labels (reviews: 33/37 real); risk % only covers labelled ranks",
       "bands": bands,
       "ranking": [{"rank": i, "clip": r["clip"], "max_risk": round(r["max_risk"], 4),
                    "train_rank_same_peak": train_rank_for(r["max_risk"], train_peaks)}
                   for i, r in enumerate(val, 1)]}
OUT.write_text(json.dumps(out, indent=1))

print(f"val: {len(val)} clips; time at >=0.9: {total09 * STEP_S:.0f} s, at >=0.99: {total099 * STEP_S:.0f} s")
print(f"{'val ranks':>10} {'peak':>15} {'train ranks':>12} {'train risk%':>11} {'%time>=0.9':>10} {'%time>=0.99':>11}")
for b in bands:
    rp = "-" if b["train_risk_pct"] is None else f"{b['train_risk_pct']:.0f}% of {b['train_labelled']}"
    print(f"{b['val_ranks']:>10} {b['peak'][0]:.4f}-{b['peak'][1]:.4f} {b['same_peak_train_ranks']:>12} {rp:>11} "
          f"{b['pct_of_val_time_ge_0.9']:>10} {b['pct_of_val_time_ge_0.99']:>11}")
