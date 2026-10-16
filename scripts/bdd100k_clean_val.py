"""Clean BDD100K val by the hand labels, then re-score the baseline on it (free: saved readings only, this PC).

Rule (same idea as train, decided with the person):
  val ranks 1-25    (plain BADAS-Open; same peak as train ranks 3-93, 23/23 real there): removed without labels
  val ranks 26-137  : kept only if hand-labelled "normal" in val_labels.json (risk / unsure / bad removed)
  val ranks 138-500 : kept (same peak as train ranks 703+, where no real dangers were found)

Writes:
  src/risk/data/bdd100k_ids/val_clean.txt                          one clip id per line
  src/risk/data/bdd100k_ids/val_clean_summary.json                 counts
  src/risk/runs/baseline_badas_open/results/eval_val_clean/        metrics.json + RESULTS.md on the cleaned val
  .../eval_val_clean/compare.json                                  old val vs cleaned val, key numbers

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe scripts\\bdd100k_clean_val.py
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/risk/data/data_code"))
sys.path.insert(0, str(ROOT / "src/risk"))
from bdd100k_review import rank  # noqa: E402
from eval_risk import metrics, report  # noqa: E402

# ---- CONFIG ----
IDS = ROOT / "src/risk/data/bdd100k_ids"
EVAL = ROOT / "src/risk/runs/baseline_badas_open/results/eval"
OUT = ROOT / "src/risk/runs/baseline_badas_open/results/eval_val_clean"
REMOVE_TOP, LABEL_LAST = 25, 137
# ----------------


def main() -> None:
    val = json.loads((EVAL / "series_bdd_val.json").read_text())
    nexar = json.loads((EVAL / "series_nexar_public.json").read_text())
    labels = json.loads((IDS / "val_labels.json").read_text())
    ranked = [r["clip"] for r in rank(val)]
    missing = [c for c in ranked[REMOVE_TOP:LABEL_LAST] if c not in labels]
    if missing:
        sys.exit(f"STOP: {len(missing)} clips in val ranks {REMOVE_TOP + 1}-{LABEL_LAST} have no label")

    # Apply the rule, rank by rank
    keep, removed = [], Counter()
    for i, clip in enumerate(ranked, 1):
        if i <= REMOVE_TOP:
            removed[f"ranks 1-{REMOVE_TOP}"] += 1
        elif i <= LABEL_LAST and labels[clip]["label"] != "normal":
            removed[f"ranks {REMOVE_TOP + 1}-{LABEL_LAST} labelled {labels[clip]['label']}"] += 1
        else:
            keep.append(clip)
    empty = [c for c, s in val.items() if not s]            # clips without readings never enter the ranking
    (IDS / "val_clean.txt").write_text("\n".join(keep) + "\n")
    summary = {"made": time.strftime("%Y-%m-%d %H:%M:%S"),
               "rule": f"ranks 1-{REMOVE_TOP} removed; {REMOVE_TOP + 1}-{LABEL_LAST} kept only if labelled normal; "
                       f"{LABEL_LAST + 1}+ kept",
               "val_clips": len(val), "clips_without_readings": len(empty), "kept": len(keep),
               "removed_total": sum(removed.values()), "removed": dict(removed),
               "labels": dict(Counter(labels[c]["label"] for c in ranked[REMOVE_TOP:LABEL_LAST]))}
    (IDS / "val_clean_summary.json").write_text(json.dumps(summary, indent=1))

    # Re-score the baseline on the cleaned val (same Nexar Public readings, same metric code)
    m = metrics({c: val[c] for c in keep}, nexar)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(m, indent=1))
    (OUT / "RESULTS.md").write_text(report("baseline_badas_open (BDD100K val cleaned)", m))
    old = json.loads((EVAL / "metrics.json").read_text())

    def row(mm, thr, c):
        return next(r for r in mm["rows"] if r["threshold"] == thr and r["in_a_row"] == c)

    cmp = {"val_hours": [old["bdd_val_hours"], m["bdd_val_hours"]],
           "budgets": {k: {"old": old["at_budget"][k], "clean": m["at_budget"][k]} for k in m["at_budget"]},
           "thresholds": [{"threshold": r["threshold"], "in_a_row": r["in_a_row"],
                           "false_per_hour_old": row(old, r["threshold"], r["in_a_row"])["false_per_hour"],
                           "false_per_hour_clean": r["false_per_hour"], "crashes_warned": r["crashes_warned"]}
                          for r in m["rows"]]}
    (OUT / "compare.json").write_text(json.dumps(cmp, indent=1))

    print(json.dumps(summary, indent=1))
    print(f"\nval hours: {old['bdd_val_hours']} -> {m['bdd_val_hours']}")
    print(f"{'budget':>22} {'old warned':>10} {'old thr':>8} {'clean warned':>12} {'clean thr':>9}")
    for k, v in cmp["budgets"].items():
        print(f"{k:>22} {v['old']['crashes_warned'] * 100:>9.1f}% {str(v['old']['threshold']):>8} "
              f"{v['clean']['crashes_warned'] * 100:>11.1f}% {str(v['clean']['threshold']):>9}")
    print(f"\n{'thr':>5} {'row':>3} {'false/h old':>11} {'false/h clean':>13} {'crashes warned':>14}")
    for r in cmp["thresholds"]:
        print(f"{r['threshold']:>5} {r['in_a_row']:>3} {r['false_per_hour_old']:>11} {r['false_per_hour_clean']:>13} "
              f"{r['crashes_warned'] * 100:>13.1f}%")


if __name__ == "__main__":
    main()
