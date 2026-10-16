"""Build the cleaned BDD100K train list (the normal clips stage 1 trains on). Free, runs on this PC.

Rule (decided with the person, from the reviews in review_decisions.json):
  ranks 1-200   (riskiest by plain BADAS-Open): removed, mostly real near-misses
  ranks 201-638 : kept only if hand-labelled "normal" in manual_labels.json (risk / unsure / bad removed)
  ranks 639-700 : kept only if spot-checked "normal" (unchecked removed: dangers still common here)
  ranks 701+    : kept as normal (unless a spot check labelled it otherwise; 0/20 risk found in 701-1107)

Writes:
  src/risk/data/bdd100k_ids/train_clean.txt           one clip id per line
  src/risk/data/bdd100k_ids/train_clean_summary.json  counts per rank band and label

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_clean_train.py
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bdd100k_review import SERIES, rank  # noqa: E402

# ---- CONFIG ----
IDS = Path(__file__).resolve().parents[1] / "bdd100k_ids"
LABELS = IDS / "manual_labels.json"
TRAIN = IDS / "train_3000.txt"
REMOVE_TOP, LABEL_LAST = 200, 638          # ranks 1-200 removed; 201-638 decided by hand labels
UNCHECKED_REMOVE_LAST = 700                 # 639-700: spot checks found 4/20 risk, so unchecked clips are removed;
                                            # 701-1107 spot check found 0/20 risk, so unchecked clips below 700 stay
# ----------------


def main() -> None:
    ranked = rank(json.loads(SERIES.read_text()))
    labels = json.loads(LABELS.read_text())
    train = TRAIN.read_text().split()

    # Every train clip must have a BADAS reading, and every clip in 201-638 a hand label: stop otherwise
    ranked_ids = [r["clip"] for r in ranked]
    missing_series = sorted(set(train) - set(ranked_ids))
    band = ranked_ids[REMOVE_TOP:LABEL_LAST]
    missing_labels = [c for c in band if c not in labels]
    if missing_series or missing_labels:
        sys.exit(f"STOP: {len(missing_series)} train clips without readings, {len(missing_labels)} unlabelled in "
                 f"ranks {REMOVE_TOP + 1}-{LABEL_LAST}")

    # Apply the rule, rank by rank
    keep, removed = [], Counter()
    for i, clip in enumerate(ranked_ids, 1):
        if i <= REMOVE_TOP:
            removed["ranks 1-200"] += 1
        elif i <= LABEL_LAST:
            lab = labels[clip]["label"]
            if lab == "normal":
                keep.append(clip)
            else:
                removed[f"ranks 201-638 labelled {lab}"] += 1
        elif i <= UNCHECKED_REMOVE_LAST and clip not in labels:          # dangers still common here: unchecked out
            removed[f"ranks 639-{UNCHECKED_REMOVE_LAST} not checked"] += 1
        elif labels.get(clip, {}).get("label", "normal") == "normal":   # spot-checked clips can be removed too
            keep.append(clip)
        else:
            removed[f"ranks 639+ spot check labelled {labels[clip]['label']}"] += 1

    (IDS / "train_clean.txt").write_text("\n".join(keep) + "\n")
    band_labels = Counter(labels[c]["label"] for c in band)
    summary = {
        "made": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rule": "ranks 1-200 removed; 201-700 kept only if labelled normal; 701+ kept unless spot-checked as not normal",
        "train_clips": len(train),
        "kept": len(keep),
        "removed_total": sum(removed.values()),
        "removed": dict(removed),
        "ranks_201_638_labels": dict(band_labels),
        "ranks_201_638_labelled_by": dict(Counter(labels[c].get("by", "?") for c in band)),
        "kept_from_ranks_201_638": band_labels["normal"],
        "kept_from_ranks_639_plus": len(keep) - band_labels["normal"],
        # Spot checks below 638, per band (labels by rank, so each check's result can be read separately)
        "spot_checks": {f"{lo}-{hi}": dict(Counter(labels[c]["label"] for c in ranked_ids[lo - 1:hi] if c in labels))
                        for lo, hi in ((639, 700), (701, 900), (901, 1107))},
        # Open limit: risk share fell 70% -> 5% across 201-638 (label_bands.json), 639-700 still had dangers
        # (unchecked clips there removed), 701-1107 had none in 20 clips; tilted cameras below 700 may remain.
        "known_limit": "ranks 701+ mostly unlabelled; spot check 701-1107 found 0/20 risk but 4/10 tilted cameras in 901-1107",
    }
    (IDS / "train_clean_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
