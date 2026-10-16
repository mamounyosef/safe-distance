"""Hand labels of BDD100K train ranks 201-638, counted per rank band, to see whether risk clips fade out by 638.

Writes src/risk/data/bdd100k_ids/label_bands.json and prints a table.

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe scripts\\bdd100k_label_bands.py
"""

import json
from collections import Counter
from pathlib import Path

IDS = Path(__file__).resolve().parents[1] / "src/risk/data/bdd100k_ids"
STEP = 50                                   # ranks per band

labels = json.loads((IDS / "manual_labels.json").read_text())
rows = sorted(labels.values(), key=lambda v: v["rank"])
bands = []
for lo in range(201, 639, STEP):
    hi = min(lo + STEP - 1, 638)
    b = [v for v in rows if lo <= v["rank"] <= hi]
    c = Counter(v["label"] for v in b)
    bands.append({"ranks": f"{lo}-{hi}", "clips": len(b), **{k: c[k] for k in ("normal", "risk", "unsure", "bad")},
                  "risk_pct": round(100 * c["risk"] / len(b), 1),
                  "max_risk_range": [round(min(v["max_risk"] for v in b), 4), round(max(v["max_risk"] for v in b), 4)]})
# Ranks of the last risk clips: how deep do real dangers still appear?
last_risk = [v["rank"] for v in rows if v["label"] == "risk"][-10:]
out = {"step": STEP, "bands": bands, "last_10_risk_ranks": last_risk}
(IDS / "label_bands.json").write_text(json.dumps(out, indent=1))

print(f"{'ranks':>9} {'clips':>5} {'normal':>6} {'risk':>5} {'unsure':>6} {'bad':>4} {'risk%':>6}  BADAS peak")
for b in bands:
    print(f"{b['ranks']:>9} {b['clips']:>5} {b['normal']:>6} {b['risk']:>5} {b['unsure']:>6} {b['bad']:>4} "
          f"{b['risk_pct']:>6}  {b['max_risk_range'][0]}-{b['max_risk_range'][1]}")
print("last 10 risk ranks:", last_risk)
