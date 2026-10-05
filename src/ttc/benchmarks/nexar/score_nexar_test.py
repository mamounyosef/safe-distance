"""Score our pipeline on Nexar's held-out TEST set, the official way (CPU only).

Nexar's test clips end 0.5, 1.0 or 1.5 s before the event (normal-driving clips
are cut the same way). Each clip gets ONE risk score; the official metric is
the average precision (AP) of those scores, per cut-off group, averaged over
the groups (mAP), separately for the Public and Private halves. This is the
same formula as Nexar's evaluate_submission.py (sklearn's average_precision_score),
re-implemented here so no extra packages are needed.

Our risk score per clip (SCORES): taken over the clip's last LAST_S seconds,
from objects in our path:
    inv_ttc      highest 1 / TTC seen (0 if no object ever had a TTC)
    warned       1 if the current warning rule fired, else 0
    inv_ttc+near like inv_ttc, but an object in our path closer than NEAR_M
                 and getting closer counts as at least 1 / NEAR_TTC_S
                 (a "safety net" for sudden braking right ahead)

RUN IT (from the repo root, after collect_modal.py with DATASET = "test" and
downloading results/test1 like score_nexar.py describes):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\score_nexar_test.py

Writes results/<RUN>/results.json, RESULTS.md and one submission CSV per score
(the format Nexar's own script reads: id,score).
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_nexar as sn  # noqa: E402  (filter replay, data folder)

# ---- CONFIG ----
RUN = "test1"
SOLUTION = Path(r"C:\safe-distance-data\nexar\meta\solution.csv")   # official labels: id,target,Usage,group
LAST_S = 1.0          # score uses the clip's last second (the moment the official metric asks about)
NEAR_M, NEAR_TTC_S = 5.0, 1.0
# Other systems' scores (submission CSVs: id,score), scored the same way, and
# each one combined with ours: the mean of the two RANKS (0 = lowest risk,
# 1 = highest), so neither system's number scale dominates.
OTHERS = {"badas_open": "submission_badas_open.csv",
          "op_brake3": "submission_op_brake3.csv",      # openpilot (openpilot_submissions.py)
          "op_brake5": "submission_op_brake5.csv",
          "op_fcw": "submission_op_fcw.csv"}
COMBINE_WITH = "inv_ttc"
OUT = Path(__file__).resolve().parent / "results" / RUN
# ----------------


def average_precision(labels: list[int], scores: list[float]) -> float:
    """Same as sklearn's average_precision_score: sum over thresholds of
    (recall step) x (precision at that threshold); tied scores form one step."""
    pairs = sorted(zip(scores, labels), key=lambda p: -p[0])
    total_pos = sum(labels)
    tp = fp = 0
    ap, prev_recall, i = 0.0, 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:   # all clips with this same score
            tp += pairs[j][1]
            fp += 1 - pairs[j][1]
            j += 1
        recall = tp / total_pos
        ap += (recall - prev_recall) * tp / (tp + fp)
        prev_recall, i = recall, j
    return ap


def ranks(values: dict[str, float]) -> dict[str, float]:
    """Each clip's rank from 0 (lowest score) to 1 (highest); tied scores share their average rank."""
    order = sorted(values, key=values.get)
    out, i = {}, 0
    while i < len(order):
        j = i
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        for k in range(i, j):
            out[order[k]] = ((i + j - 1) / 2) / max(len(order) - 1, 1)
        i = j
    return out


def clip_scores(clip: dict) -> dict:
    """Our risk scores for one test clip."""
    frames = sn.filter_clip(clip, clahe=True)
    end = frames[-1][0] if frames else 0.0
    warn = sn.warn_times(frames, sn.CURRENT)
    inv, near = 0.0, 0.0
    for t, objs in frames:
        if t < end - LAST_S:
            continue
        for o in objs:
            if o["gap"] > sn.CORRIDOR_M or o["ttc"] is None:
                continue
            r = 0.0 if math.isinf(o["ttc"]) else 1.0 / max(o["ttc"], 0.05)
            inv = max(inv, r)
            # Safety net: close ahead and getting closer (finite TTC) = at least 1 / NEAR_TTC_S.
            near = max(near, r, 1.0 / NEAR_TTC_S if o["distance"] < NEAR_M and r > 0 else 0.0)
    return {"inv_ttc": inv, "warned": 1.0 if any(t >= end - LAST_S for t in warn) else 0.0, "inv_ttc+near": near}


def main() -> None:
    solution = list(csv.DictReader(SOLUTION.open()))
    scores: dict[str, dict] = {}
    for p in sorted(sn.DATA.rglob(f"{RUN}/**/*.json.gz")):
        with gzip.open(p, "rt") as fh:           # one clip in memory at a time
            clip = json.load(fh)
        scores[clip["clip"]] = clip_scores(clip)
    names = ["inv_ttc", "warned", "inv_ttc+near"]
    for other, file in OTHERS.items():
        path = OUT / file
        if not path.exists():
            print(f"{path} not found, {other} skipped")
            continue
        theirs = {r["id"]: float(r["score"]) for r in csv.DictReader(path.open())}
        ours = {cid: s[COMBINE_WITH] for cid, s in scores.items()}
        r_theirs, r_ours = ranks(theirs), ranks(ours)
        for cid in scores:
            scores[cid][other] = theirs.get(cid, 0.0)
            scores[cid][f"{other}+ours"] = (r_theirs.get(cid, 0.0) + r_ours[cid]) / 2
        names += [other, f"{other}+ours"]
    missing = sum(1 for r in solution if r["id"] not in scores)
    results = {"run": RUN, "clips_scored": len(scores), "clips_missing": missing, "mAP": {}}
    for name in names:
        results["mAP"][name] = {}
        for usage in ("Public", "Private"):
            rows = [r for r in solution if r["Usage"] == usage]
            aps = []
            for g in sorted({r["group"] for r in rows}):
                sub = [r for r in rows if r["group"] == g]
                aps.append(average_precision([int(r["target"]) for r in sub],
                                             [scores.get(r["id"], {}).get(name, 0.0) for r in sub]))  # missing = 0, as Nexar's script
            results["mAP"][name][usage] = round(sum(aps) / len(aps), 4)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=1))
    for name in names:
        if name in OTHERS:          # their own file already exists; do not overwrite it
            continue
        with (OUT / f"submission_{name.replace('+', '_')}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "score"])
            for cid, s in sorted(scores.items()):
                w.writerow([cid, round(s[name], 5)])
    lines = [f"# Nexar test set (official metric), run {RUN}", "",
             "Generated by score_nexar_test.py from results.json. Do not edit by hand.", "",
             f"Clips scored: {len(scores)} (missing from the labels' list: {missing}, counted as score 0). "
             "mAP = mean average precision over the 0.5 / 1.0 / 1.5 s groups. A score that ranks at random "
             "gets about 0.5 (half the clips are collisions). Reference: BADAS-Open reports 0.86 on this set.", "",
             "| Score | mAP Public | mAP Private |", "|---|---|---|"]
    for name in names:
        lines.append(f"| {name} | {results['mAP'][name]['Public']} | {results['mAP'][name]['Private']} |")
    (OUT / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
