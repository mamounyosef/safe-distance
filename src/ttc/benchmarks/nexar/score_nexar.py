"""Score the collision warning on real Nexar dashcam clips (CPU only, no GPU).

Replays the warning logic (combined Kalman filter -> TTC under 2.5 s for 2
frames in a row, objects in our path only) on the per-frame readings that
collect_modal.py saved, and measures:
    crash clips:   share warned before the event, share warned by Nexar's
                   "warning due by" time, how many seconds of warning we gave
    normal clips:  false warnings per hour of driving

Several variants of the rules are scored on the same readings (VARIANTS), so a
fix can be checked in seconds without re-running the GPU.

RUN IT (PowerShell, from the repo root):

    # 1. download the readings from Modal (once, after collect_modal.py has finished)
    #    (the target folder must exist and end with a backslash, or Windows refuses it)
    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe volume get safe-distance-data results/v2 C:\\safe-distance-data\\nexar\\results\\
    # 2. score
    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\score_nexar.py

Writes results/<RUN>/results.json (all numbers) and results/<RUN>/RESULTS.md (generated from it).
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src/ttc/scripts"))
import ttc_demo  # noqa: E402  (the filter settings used everywhere: ObjectState, WARN_TTC_S, ...)
from ttc_demo import ObjectState  # noqa: E402

# ---- CONFIG ----
RUN = sys.argv[1] if len(sys.argv) > 1 else "v2"     # must match collect_modal.py (or give it on the command line)
DATA = Path(r"C:\safe-distance-data\nexar\results")   # where the readings were downloaded (searched recursively)
METADATA = Path(r"C:\safe-distance-data\nexar\train\positive\metadata.csv")   # event and "due by" times
CORRIDOR_M = 1.2            # "in our path" = within 1.2 m of our centre line
EDGE_PX = 3                 # boxes touching the image edge: box height not used (object cut off)
COUNT_WINDOW_S = 4.0        # a warning counts for the crash if it starts at most 4 s before the event
EPISODE_GAP_S = 0.5         # warnings closer than this belong to the same episode
# Rule variants to compare. min_age_s: ignore objects tracked for less than this
# (against false warnings on newly seen objects). clahe: use the CLAHE distance
# on clips Nexar labels as night.
VARIANTS = {
    "as_now":        {"min_age_s": 0.0, "clahe": True},
    "min_age_0.5s":  {"min_age_s": 0.5, "clahe": True},
    "min_age_1.0s":  {"min_age_s": 1.0, "clahe": True},
    "no_clahe":      {"min_age_s": 0.0, "clahe": False},
}
OUT = Path(__file__).resolve().parent / "results" / RUN
# ----------------


def lateral_gap_m(box, distance: float, fx: float, cx: float) -> float:
    """Sideways gap (m) between our centre line and the object's nearest side."""
    x1, _, x2, _ = box
    if x1 <= cx <= x2:
        return 0.0
    return min(abs(x1 - cx), abs(x2 - cx)) / fx * distance


def episodes(times: list[float]) -> list[float]:
    """Start time of each warning episode (a stretch of warnings with no gap over EPISODE_GAP_S)."""
    starts, last = [], None
    for t in times:
        if last is None or t - last > EPISODE_GAP_S:
            starts.append(t)
        last = t
    return starts


def replay(clip: dict, min_age_s: float, clahe: bool) -> list[float]:
    """Run the warning logic over one clip's saved readings; return the times with a warning."""
    fx, cx, w, h = clip["focal_px"], clip["width"] / 2, clip["width"], clip["height"]
    use_clahe = clahe and clip.get("night", False)
    states: dict[int, ObjectState] = {}
    first_seen: dict[int, float] = {}
    warn_times = []
    # Frames are numbered in the order they were processed (about 10 per second),
    # as in the live pipeline; numbering from the time would skip or repeat a
    # number when the video's frame rate is not exactly 30.
    for frame_no, f in enumerate(clip["frames"]):
        t = f["t"]
        warning = False
        for o in f["objects"]:
            d = o["d_clahe"] if use_clahe and o["d_clahe"] is not None else o["d"]
            if d is None:
                continue
            first_seen.setdefault(o["id"], t)
            x1, y1, x2, y2 = o["box"]
            at_edge = x1 <= EDGE_PX or y1 <= EDGE_PX or x2 >= w - EDGE_PX or y2 >= h - EDGE_PX
            out = states.setdefault(o["id"], ObjectState()).step(frame_no, d, None if at_edge else y2 - y1)
            old_enough = t - first_seen[o["id"]] >= min_age_s
            in_path = lateral_gap_m(o["box"], out["distance"], fx, cx) <= CORRIDOR_M
            warning |= out["warning"] and in_path and old_enough
        if warning:
            warn_times.append(t)
    return warn_times


def wilson(k: int, n: int) -> list[float]:
    """95% confidence interval for a share k/n (Wilson score interval)."""
    if n == 0:
        return [math.nan, math.nan]
    z, p = 1.96, k / n
    mid = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(mid - half, 3), round(mid + half, 3)]


def load_clips() -> tuple[list[dict], list[dict]]:
    """All saved clips of this run, split into collision clips and normal clips."""
    meta = {r["file_name"][:-4]: r for r in csv.DictReader(METADATA.open())}
    pos, neg = [], []
    for p in sorted(DATA.rglob("*.json.gz")):
        clip = json.loads(gzip.open(p, "rt").read())
        if clip.get("run") != RUN:
            continue
        if clip["split"].endswith("positive"):
            r = meta[clip["clip"]]
            clip["event_s"] = float(r["time_of_event"])
            clip["due_s"] = float(r["time_of_alert"]) if r["time_of_alert"] else None
            clip["light"] = r["light_conditions"]
            pos.append(clip)
        else:
            neg.append(clip)
    return pos, neg


def score(pos: list[dict], neg: list[dict], rules: dict) -> dict:
    """All numbers for one rule variant."""
    per_clip, leads = [], []
    for c in pos:
        starts = episodes(replay(c, **rules))
        e = c["event_s"]
        counted = [s for s in starts if e - COUNT_WINDOW_S <= s < e]   # a warning AT the event is too late
        lead = round(e - counted[0], 2) if counted else None
        per_clip.append({"clip": c["clip"], "night": c.get("night", False), "light": c["light"], "event_s": e,
                         "due_s": c["due_s"], "first_warning_s": None if lead is None else counted[0],
                         "lead_s": lead, "by_due": lead is not None and c["due_s"] is not None
                         and counted[0] <= c["due_s"],
                         "early_warnings": sum(1 for s in starts if s < e - COUNT_WINDOW_S)})
        if lead is not None:
            leads.append(lead)

    def share(rows, key):
        k = sum(1 for r in rows if r[key])
        return {"k": k, "n": len(rows), "share": round(k / len(rows), 3) if rows else None, "ci95": wilson(k, len(rows))}

    for r in per_clip:
        r["warned"] = r["lead_s"] is not None
    due_rows = [r for r in per_clip if r["due_s"] is not None]
    false_eps = sum(len(episodes(replay(c, **rules))) for c in neg)
    hours = sum(c["window_s"][1] - c["window_s"][0] for c in neg) / 3600
    return {
        "rules": rules,
        "crash_clips": len(per_clip),
        "warned_before_event": share(per_clip, "warned"),
        "warned_by_due_time": share(due_rows, "by_due"),
        "warned_before_event_day": share([r for r in per_clip if not r["night"]], "warned"),
        "warned_before_event_night": share([r for r in per_clip if r["night"]], "warned"),
        "lead_s": {"median": round(statistics.median(leads), 2) if leads else None,
                   "p25": round(statistics.quantiles(leads, n=4)[0], 2) if len(leads) > 1 else None,
                   "p75": round(statistics.quantiles(leads, n=4)[2], 2) if len(leads) > 1 else None},
        "early_warnings_per_crash_clip": round(sum(r["early_warnings"] for r in per_clip) / max(len(per_clip), 1), 3),
        "normal_clips": len(neg), "normal_hours": round(hours, 3),
        "false_warnings": false_eps, "false_warnings_per_hour": round(false_eps / hours, 1) if hours else None,
        "per_clip": per_clip,
    }


def report(results: dict) -> str:
    """RESULTS.md, generated from results.json."""
    pct = lambda s: "n/a" if s["share"] is None else f"{s['share'] * 100:.0f}% ({s['k']}/{s['n']}, 95% CI {s['ci95'][0] * 100:.0f} to {s['ci95'][1] * 100:.0f}%)"  # noqa: E731
    lines = [f"# Nexar real-crash benchmark, run {RUN}", "",
             "Generated by score_nexar.py from results.json. Do not edit by hand.", "",
             f"Warning rule: TTC under {ttc_demo.WARN_TTC_S} s for {ttc_demo.WARN_FRAMES} frames in a row, "
             f"objects within {CORRIDOR_M} m of our centre line. A warning counts for a crash if it starts "
             f"in the {COUNT_WINDOW_S:g} s before the event.", "",
             "| Variant | Warned before event | Warned by Nexar's due time | Day | Night | Median lead (s) | "
             "Early warnings per crash clip | False warnings per hour (normal driving) |",
             "|---|---|---|---|---|---|---|---|"]
    for name, r in results["variants"].items():
        lines.append(f"| {name} | {pct(r['warned_before_event'])} | {pct(r['warned_by_due_time'])} | "
                     f"{pct(r['warned_before_event_day'])} | {pct(r['warned_before_event_night'])} | "
                     f"{r['lead_s']['median']} | {r['early_warnings_per_crash_clip']} | "
                     f"{r['false_warnings_per_hour']} ({r['false_warnings']} in {r['normal_hours'] * 60:.0f} min) |")
    first = next(iter(results["variants"].values()))
    lines += ["", f"Clips: {first['crash_clips']} collision / near-miss clips, {first['normal_clips']} normal clips."]
    return "\n".join(lines) + "\n"


def main() -> None:
    pos, neg = load_clips()
    print(f"{len(pos)} collision clips, {len(neg)} normal clips")
    results = {"run": RUN, "variants": {name: score(pos, neg, rules) for name, rules in VARIANTS.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=1))
    (OUT / "RESULTS.md").write_text(report(results))
    print(report(results))


if __name__ == "__main__":
    main()
