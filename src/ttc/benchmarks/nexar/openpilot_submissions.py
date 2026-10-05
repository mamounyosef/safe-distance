"""Turn openpilot's saved outputs (openpilot_modal.py) into one risk score per test clip (CPU only).

Scores, each taken over the clip's last LAST_S seconds (as for our pipeline):
    op_brake3   highest probability of braking harder than 3 m/s^2 within 2 s
    op_brake5   highest probability of braking harder than 5 m/s^2 within 2 s
    op_fcw      1 if openpilot's own collision warning fired, else 0

RUN IT (from the repo root, after openpilot_modal.py):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\openpilot_submissions.py

Writes results/test1/submission_op_*.csv (id,score), which score_nexar_test.py scores.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

# ---- CONFIG ----
RESULTS = Path(__file__).resolve().parent / "results" / "test1"
LAST_S = 1.0
# Columns of each saved step (see openpilot_modal.py)
COL = {"t": 0, "fcw": 1, "b3": 2, "b4": 3, "b5": 4}
# ----------------


def main() -> None:
    series = json.loads((RESULTS / "openpilot_series.json").read_text())
    scores = {"op_brake3": {}, "op_brake5": {}, "op_fcw": {}}
    for clip, rows in series.items():
        end = rows[-1][COL["t"]] if rows else 0.0
        last = [r for r in rows if r[COL["t"]] >= end - LAST_S]
        scores["op_brake3"][clip] = max((r[COL["b3"]] for r in last), default=0.0)
        scores["op_brake5"][clip] = max((r[COL["b5"]] for r in last), default=0.0)
        scores["op_fcw"][clip] = float(any(r[COL["fcw"]] for r in last))
    for name, s in scores.items():
        with (RESULTS / f"submission_{name}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "score"])
            for cid in sorted(s):
                w.writerow([cid, s[cid]])
    print(f"{len(series)} clips; wrote " + ", ".join(f"submission_{n}.csv" for n in scores))


if __name__ == "__main__":
    main()
