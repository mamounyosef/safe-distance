"""Re-score the late validation with ONE window per Nexar clip: the last-frame window only (Nexar's own setup).

Uses the saved predictions (results/predictions/step<N>.npz), so no GPU: this PC, free, seconds.
Nexar crash and normal clips keep only their last-frame window (end_back 0): 334 crash + 333 normal.
BDD100K windows are unchanged (868 hard moments + 434 normal moments: false-alarm tests, not Nexar's clips).
Every score is the same shared_code.risk_scores as before; the official mAP is unchanged by construction.

Outputs: results/scores_last_frame.csv (one row per step) and results/scores_last_frame.json (+ settings)

RUN IT (from the repo root):
    python src\\risk\\runs\\stage1_lora\\late_validation\\rescore_last_frame.py
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import stage1_train as S  # noqa: E402            # stage 1's settings (RS, GROUP_SECONDS, THRESHOLDS)
import shared_code as ml  # noqa: E402

RES = HERE / "results"


def main() -> None:
    windows = json.loads((HERE / "windows.json").read_text())
    keep = [not (w["group"].startswith("nexar") and w["end_back"] != 0) for w in windows]   # drop Nexar 2nd windows
    win = ml.FixedWindows([w for w, k in zip(windows, keep) if k], S.RS)
    keep = np.array(keep)
    rows = []
    for f in sorted(RES.glob("predictions/step*.npz"), key=lambda p: int(p.stem[4:])):
        p = np.load(f, allow_pickle=True)
        assert len(p["ids"]) == len(windows), f"{f.name}: predictions do not match windows.json"
        z = p["logits"][keep]
        assert [str(i) for i in p["ids"][keep]] == win.ids, f"{f.name}: window order differs"
        risk = 1.0 / (1.0 + np.exp(-z))
        rows.append({"step": int(f.stem[4:]), **ml.risk_scores(risk, win, S.GROUP_SECONDS, S.THRESHOLDS)})
    counts = {g: int((win.group == g).sum()) for g in dict.fromkeys(win.group.tolist())}
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(RES / "scores_last_frame.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    (RES / "scores_last_frame.json").write_text(json.dumps(
        {"what": "late validation re-scored with one window per Nexar clip (last frame); BDD windows unchanged",
         "windows": counts, "rows": rows}, indent=2), encoding="utf-8")

    print(f"windows: {counts}")
    print(f"{'step':>5} {'AP all':>7} {'mAP':>6} {'AP NexN':>7} {'AP BDDh':>7} {'AP BDDn':>7} "
          f"{'crash@.9':>8} {'NexN@.9':>7} {'BDDh@.9':>7} {'BDDn@.9':>7} {'0.5s@.9':>7} {'1.0s@.9':>7} {'1.5s@.9':>7} {'calib':>6}")
    for r in rows:
        print(f"{r['step']:>5} {r['ap_crash_vs_all_normal']:7.3f} {r['nexar_official_map']:6.3f} "
              f"{r['ap_crash_vs_nexar_normal']:7.3f} {r['ap_crash_vs_bdd_hard']:7.3f} {r['ap_crash_vs_bdd_normal']:7.3f} "
              f"{r['crash_caught_pct_at_0.9']:8.1f} {r['nexar_normal_alarm_pct_at_0.9']:7.1f} "
              f"{r['bdd_hard_alarm_pct_at_0.9']:7.1f} {r['bdd_normal_alarm_pct_at_0.9']:7.1f} "
              f"{r['crash_0.5s_caught_pct_at_0.9']:7.1f} {r['crash_1.0s_caught_pct_at_0.9']:7.1f} "
              f"{r['crash_1.5s_caught_pct_at_0.9']:7.1f} {r['calibration_error']:6.3f}")
    print(f"saved {RES / 'scores_last_frame.csv'}")


if __name__ == "__main__":
    main()
