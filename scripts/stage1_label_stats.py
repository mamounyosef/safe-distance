"""Counts of the stage 1 label rule over all Nexar train crash clips (free, metadata only).

Uses src/risk/stage1_labels.py (the rule training uses) and src/risk/data/nexar_excluded.json.
Per clip: is it used, how many danger / safe / skipped window end points it has (0.125 s frame grid).

Writes src/risk/runs/stage1_lora/results/label_stats.json and prints a summary.

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe scripts\\stage1_label_stats.py
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/risk"))
import stage1_labels as L  # noqa: E402

META = Path(r"C:\safe-distance-data\nexar\samples\metadata.csv")     # Nexar train crash clips (positive)
EXCLUDED = ROOT / "src/risk/data/nexar_excluded.json"
OUT = ROOT / "src/risk/runs/stage1_lora/results/label_stats.json"

excluded = set(json.loads(EXCLUDED.read_text())["clips"])
rows = list(csv.DictReader(META.open()))
used, dropped, zones = 0, [], Counter()
for r in rows:
    if r["file_name"] in excluded:
        continue
    alert, event = float(r["time_of_alert"]), float(r["time_of_event"])
    if not L.crash_clip_used(alert, event):            # no danger window: whole clip dropped
        dropped.append(r["file_name"])
        continue
    used += 1
    for k in range(int(event / L.FRAME_S + 1e-9) + 1):  # every end point up to the crash
        zones[L.window_label(k * L.FRAME_S, alert, event)[1]] += 1

out = {"crash_clips": len(rows), "excluded_by_person": len(excluded), "dropped_no_danger_window": len(dropped),
       "used": used, "end_points_in_used_clips": dict(zones),
       "danger_end_points_drawn": sum(len(L.danger_ends(float(r["time_of_alert"]), float(r["time_of_event"]))) for r in rows if r["file_name"] not in excluded), "ramp_end_points_all": zones[L.RAMP], "label_1_end_points": zones[L.ONE], "safe_end_points": zones[L.ZERO],
       "rule": {"hard_s": L.HARD_S, "ramp_start": L.RAMP_START, "margin_s": L.MARGIN_S,
                "safe_before_s": L.SAFE_BEFORE_S, "danger_min_label": L.DANGER_MIN_LABEL}, "dropped_clips": dropped}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "dropped_clips"}, indent=1))
