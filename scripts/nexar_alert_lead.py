"""How long before the crash Nexar's human alert comes, over the 750 Nexar train crash clips (this PC, free).

alert lead = time_of_event - time_of_alert (seconds). Used to choose the stage 1 labels
(hard 1 for the last 2.4 s, a ramp for earlier alerts, 0 beyond 4 s).

Output: src/risk/data/nexar_alert_lead.json (all numbers written by this script).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\nexar_alert_lead.py
"""

import csv
import json
from pathlib import Path

import numpy as np

# ---- CONFIG ----
META = Path(r"C:\safe-distance-data\nexar\samples\metadata.csv")      # Nexar train positive metadata (copied from Modal)
OUT = Path(__file__).resolve().parents[1] / "src/risk/data/nexar_alert_lead.json"
BINS = [(0, 1), (1, 1.5), (1.5, 2), (2, 2.4), (2.4, 3), (3, 4), (4, 99)]
# ----------------

rows = list(csv.DictReader(META.open()))
lead = np.array([float(r["time_of_event"]) - float(r["time_of_alert"]) for r in rows])
pct = [0, 10, 25, 50, 75, 90, 100]
res = {"clips": len(lead),
       "percentiles_s": {str(p): round(float(v), 2) for p, v in zip(pct, np.percentile(lead, pct))},
       "mean_s": round(float(lead.mean()), 2),
       "bins_s": {f"{lo}-{hi}": int(((lead >= lo) & (lead < hi)).sum()) for lo, hi in BINS},
       "alert_more_than_2.4s_early": int((lead > 2.4).sum()),
       "alert_at_least_3s_early": int((lead >= 3).sum()),
       "alert_at_least_4s_early": int((lead >= 4).sum())}
OUT.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
print(f"saved {OUT}")
