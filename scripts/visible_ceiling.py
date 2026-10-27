"""The "visible ceiling": how many crashes could be caught at all, at each warning timing (this PC, free).

Nexar's test clips have no alert time (the moment the danger first becomes visible), so a crash window that ends
before the danger appears still counts as a miss. Nexar's TRAIN crash clips do have alert times. From them:

    visible share at t  = share of train crash clips whose alert comes at least t seconds before the crash
                          (a window ending t s before the crash already shows the danger)
    catch / visible     = the model's catch rate on the validation windows ending t s before the crash, divided by
                          the visible share: roughly "how much of what can be seen, the model catches"

An ESTIMATE (assumes test clips are like train clips), reported NEXT TO the official scores, never instead of them.
Nothing is removed or relabelled.

Inputs:  C:/safe-distance-data/nexar/train/positive/metadata.csv    (time_of_event, time_of_alert per crash clip)
         late_validation/results/scores.csv                         (crash_<t>s_caught_pct_at_<thr> per step)
Output:  late_validation/results/visible_ceiling.json

RUN IT (from the repo root):
    python scripts\\visible_ceiling.py
"""

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
META = Path(r"C:\safe-distance-data\nexar\train\positive\metadata.csv")
SCORES = REPO / "src/risk/runs/stage1_lora/late_validation/results/scores.csv"
OUT = REPO / "src/risk/runs/stage1_lora/late_validation/results/visible_ceiling.json"
TIMINGS = [0.5, 1.0, 1.5]                         # seconds before the crash the scored windows end
THRESHOLDS = [0.5, 0.9]                           # the thresholds late_validate.py scores per timing


def main() -> None:
    # alert lead per train crash clip = crash time - alert time (seconds the danger is visible before the crash)
    leads = [float(r["time_of_event"]) - float(r["time_of_alert"]) for r in csv.DictReader(META.open())]
    visible = {t: 100.0 * sum(lead >= t for lead in leads) / len(leads) for t in TIMINGS}

    rows = list(csv.DictReader(SCORES.open()))
    per_step = []
    for r in rows:
        entry = {"step": int(r["step"])}
        for thr in THRESHOLDS:
            for t in TIMINGS:
                caught = float(r[f"crash_{t}s_caught_pct_at_{thr}"]) if f"crash_{t}s_caught_pct_at_{thr}" in r else None
                if caught is None:
                    continue
                entry[f"caught_pct_{t}s_at_{thr}"] = caught
                entry[f"caught_over_visible_{t}s_at_{thr}"] = round(caught / visible[t], 3)
        per_step.append(entry)

    report = {"what": "estimated share of crashes visible at each timing (from Nexar train alert times) and the "
                      "model's catch rate relative to it; an estimate next to the official scores",
              "train_crash_clips": len(leads),
              "visible_pct_by_timing_s": {str(t): round(v, 1) for t, v in visible.items()},
              "per_step": per_step}
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"{len(leads)} train crash clips; danger visible by: " +
          ", ".join(f"{t} s before = {v:.1f}%" for t, v in visible.items()))
    s1000 = next(e for e in per_step if e["step"] == 1000)
    for thr in THRESHOLDS:
        print(f"step 1000 at {thr}: " + ", ".join(
            f"{t} s: caught {s1000[f'caught_pct_{t}s_at_{thr}']}% / visible {visible[t]:.0f}% = "
            f"{s1000[f'caught_over_visible_{t}s_at_{thr}']:.2f}" for t in TIMINGS))
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
