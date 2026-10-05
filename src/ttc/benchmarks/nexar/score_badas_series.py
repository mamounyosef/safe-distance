"""Warnings as they would happen live: BADAS-Open vs our pipeline on Nexar's TEST set (CPU only).

BADAS-Open gives a collision probability every 0.5 s (badas_modal.py --series).
A warning = probability over THRESHOLD for CONFIRM readings in a row. For each
threshold we measure:
    normal-driving clips:  false warnings per hour
    collision clips:       share warned before the event, and how early
Our pipeline (current rule) is measured on the same clips from its saved
readings (collect_modal.py, run test1: the last 5 s of each clip; the first
2 s let the filter settle and are not counted, as BADAS needs 2 s too).

Test clips end 0.5, 1.0 or 1.5 s before the event (time_to_accident in the
metadata), so the event time is the clip's end plus that.

RUN IT (from the repo root, after badas_modal.py --series and collect_modal.py test1):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\score_badas_series.py

Writes results/test1/live_warnings.json and LIVE_WARNINGS.md (generated from it).
"""

from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_nexar as sn  # noqa: E402

# ---- CONFIG ----
RUN = "test1"
META = Path(r"C:\safe-distance-data\nexar\meta")           # test-*_*.csv metadata (time_to_accident)
THRESHOLDS = [0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99]
CONFIRMS = [1, 2]             # readings in a row over the threshold (1 reading = 0.5 s)
COUNT_WINDOW_S = 4.0          # a warning counts for the collision if it starts at most 4 s before the event
OURS_SETTLE_S = 2.0           # our readings: first 2 s of the 5 s window not counted
OUT = Path(__file__).resolve().parent / "results" / RUN
# ----------------


def metadata() -> dict[str, dict]:
    """Clip id -> {"positive": bool, "tta": seconds from clip end to event}."""
    out = {}
    for p in META.glob("test-*_*.csv"):
        for r in csv.DictReader(p.open()):
            out[r["file_name"][:-4]] = {"positive": p.stem.endswith("positive"), "tta": float(r["time_to_accident"])}
    return out


def badas_episodes(series: list, thr: float, confirm: int) -> list[float]:
    """Start times of warning episodes: `confirm` readings in a row over `thr`."""
    starts, run = [], 0
    for t, p in series:
        run = run + 1 if p > thr else 0
        if run == confirm:               # just confirmed: a new episode starts here
            starts.append(t)
    return starts


def summarise(per_clip: dict, meta: dict, hours: float) -> dict:
    """per_clip: id -> (episode start times, clip end time). Shares and rates."""
    warned, leads, false_eps, n_pos = 0, [], 0, 0
    for cid, (starts, end) in per_clip.items():
        m = meta[cid]
        if not m["positive"]:
            false_eps += len(starts)
            continue
        n_pos += 1
        event = end + m["tta"]
        counted = [s for s in starts if event - COUNT_WINDOW_S <= s <= end]
        if counted:
            warned += 1
            leads.append(event - counted[0])
    return {"warned": warned, "positives": n_pos, "warned_share": round(warned / max(n_pos, 1), 3),
            "median_lead_s": round(statistics.median(leads), 2) if leads else None,
            "false_warnings": false_eps, "normal_hours": round(hours, 3),
            "false_per_hour": round(false_eps / hours, 1) if hours else None}


def main() -> None:
    meta = metadata()
    series = json.loads((OUT / "badas_series.json").read_text())
    neg_hours = sum(s[-1][0] for cid, s in series.items() if s and not meta[cid]["positive"]) / 3600 if series else 0
    # (BADAS readings cover each clip from 2 s to its end; the first 2 s fill its first window, as in the car.)
    neg_hours_badas = sum(s[-1][0] - s[0][0] + 0.5 for cid, s in series.items()
                          if s and not meta[cid]["positive"]) / 3600
    results = {"run": RUN, "badas": {}, "ours": None}
    for thr in THRESHOLDS:
        for c in CONFIRMS:
            per_clip = {cid: (badas_episodes(s, thr, c), s[-1][0] if s else 0.0) for cid, s in series.items()}
            results["badas"][f"p>{thr}, {c} in a row"] = summarise(per_clip, meta, neg_hours_badas)

    # Our pipeline, current rule, from its saved readings (one clip in memory at a time).
    per_clip, ours_hours = {}, 0.0
    for p in sorted(sn.DATA.rglob(f"{RUN}/**/*.json.gz")):
        with gzip.open(p, "rt") as fh:
            clip = json.load(fh)
        if not clip["frames"]:
            continue
        start, end = clip["frames"][0]["t"], clip["frames"][-1]["t"]
        starts = [s for s in sn.episodes(sn.warn_times(sn.filter_clip(clip, True), sn.CURRENT))
                  if s >= start + OURS_SETTLE_S]
        per_clip[clip["clip"]] = (starts, end)
        if not meta[clip["clip"]]["positive"]:
            ours_hours += max(end - start - OURS_SETTLE_S, 0.0) / 3600
    results["ours"] = summarise(per_clip, meta, ours_hours)
    results["note"] = (f"BADAS hours counted: {neg_hours_badas:.2f} (normal clips, from 2 s in); "
                       f"ours: {ours_hours:.2f} (last 3 s of each normal clip); all normal-clip time: {neg_hours:.2f}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "live_warnings.json").write_text(json.dumps(results, indent=1))
    lines = [f"# Live warnings on the Nexar test set, run {RUN}", "",
             "Generated by score_badas_series.py from live_warnings.json. Do not edit by hand.", "",
             results["note"] + ".", "",
             "| System | Crashes warned before event | Median warning time (s before event) | "
             "False warnings per hour (normal driving) |", "|---|---|---|---|"]
    o = results["ours"]
    lines.append(f"| Ours (current rule) | {o['warned_share'] * 100:.0f}% ({o['warned']}/{o['positives']}) | "
                 f"{o['median_lead_s']} | {o['false_per_hour']} ({o['false_warnings']}) |")
    for name, r in results["badas"].items():
        lines.append(f"| BADAS {name} | {r['warned_share'] * 100:.0f}% ({r['warned']}/{r['positives']}) | "
                     f"{r['median_lead_s']} | {r['false_per_hour']} ({r['false_warnings']}) |")
    (OUT / "LIVE_WARNINGS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
