"""How many BDD100K val clips plain BADAS-Open flags, per peak-risk level (free, saved readings only).

Ranked the same way as train (bdd100k_review.rank). Train readings were every 1 s, val every 0.5 s, so val peaks
can be slightly higher for the same clip; the levels are still a fair guide to how much labelling val needs.
Also maps each val level to the train ranks with the same peak, and the share of real dangers found there.

Writes src/risk/data/bdd100k_ids/val_flags.json.

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe scripts\\bdd100k_val_flags.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/risk/data/data_code"))
from bdd100k_review import SERIES, rank  # noqa: E402

VAL = ROOT / "src/risk/runs/baseline_badas_open/results/eval/series_bdd_val.json"
OUT = ROOT / "src/risk/data/bdd100k_ids/val_flags.json"
LEVELS = [0.995, 0.994, 0.993, 0.992, 0.991, 0.99, 0.98, 0.95, 0.9]

val = rank(json.loads(VAL.read_text()))
train = rank(json.loads(SERIES.read_text()))
rows = []
for lv in LEVELS:
    rows.append({"peak_at_least": lv,
                 "val_clips": sum(r["max_risk"] >= lv for r in val),
                 "train_clips": sum(r["max_risk"] >= lv for r in train)})
out = {"val_clips": len(val), "train_clips": len(train), "levels": rows,
       "val_top20": [{"rank": i, "clip": r["clip"], "max_risk": round(r["max_risk"], 4)}
                     for i, r in enumerate(val[:20], 1)]}
OUT.write_text(json.dumps(out, indent=1))
print(f"{'peak >=':>8} {'val':>5} {'train':>6}")
for r in rows:
    print(f"{r['peak_at_least']:>8} {r['val_clips']:>5} {r['train_clips']:>6}")
