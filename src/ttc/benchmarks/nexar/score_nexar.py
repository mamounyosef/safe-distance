"""Score the collision warning on real Nexar dashcam clips (CPU only, no GPU).

Replays the warning logic (combined Kalman filter -> TTC under a threshold for
2 frames in a row, objects in our path only) on the per-frame readings that
collect_modal.py saved, and measures:
    crash clips:   share warned before the event, share warned by Nexar's
                   "warning due by" time, how many seconds of warning we gave
    normal clips:  false warnings per hour of driving

Several variants of the rules are scored on the same readings (VARIANTS), so a
fix can be checked in seconds without re-running the GPU. Clips are read one
at a time (little memory).

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
import ttc_demo  # noqa: E402  (the filter settings used everywhere: ObjectState, WARN_FRAMES, ...)
from ttc_demo import ObjectState  # noqa: E402

# ---- CONFIG ----
RUN = sys.argv[1] if len(sys.argv) > 1 else "v2"     # must match collect_modal.py (or give it on the command line)
DATA = Path(r"C:\safe-distance-data\nexar\results")   # where the readings were downloaded (searched recursively)
METADATA = Path(r"C:\safe-distance-data\nexar\train\positive\metadata.csv")   # event and "due by" times
CORRIDOR_M = 1.2            # current rule: "in our path" = within 1.2 m of our centre line
EDGE_PX = 3                 # boxes touching the image edge: box height not used (object cut off)
COUNT_WINDOW_S = 4.0        # a warning counts for the crash if it starts at most 4 s before the event
EPISODE_GAP_S = 0.5         # warnings closer than this belong to the same episode
# Rule variants to compare (each key can be left out to keep the current value):
#   ttc_s       warn when TTC is under this (current 2.5 s)
#   corridor_m  "in our path" = nearest side within this of our centre line (current 1.2 m)
#   min_bottom  ignore boxes whose bottom edge is above this share of the image
#               height (0 = top); against traffic lights and signs (current 0 = off)
#   min_age_s   ignore objects tracked for less than this (current 0 = off)
#   clahe       use the CLAHE distance on clips Nexar labels as night (current on)
CURRENT = {"ttc_s": 2.5, "corridor_m": CORRIDOR_M, "min_bottom": 0.0, "min_age_s": 0.0, "clahe": True}
VARIANTS = {
    "as_now":                  {},
    "no_clahe":                {"clahe": False},
    "min_age_1.0s":            {"min_age_s": 1.0},
    "no_high_boxes":           {"min_bottom": 0.35},
    "ttc_2.0":                 {"ttc_s": 2.0},
    "ttc_1.5":                 {"ttc_s": 1.5},
    "path_1.0m":               {"corridor_m": 1.0},
    "path_0.8m":               {"corridor_m": 0.8},
    "ttc_2.0+path_1.0m+high":  {"ttc_s": 2.0, "corridor_m": 1.0, "min_bottom": 0.35},
    "ttc_2.0+path_0.8m+high":  {"ttc_s": 2.0, "corridor_m": 0.8, "min_bottom": 0.35},
    "ttc_1.5+path_1.0m+high":  {"ttc_s": 1.5, "corridor_m": 1.0, "min_bottom": 0.35},
    "ttc_1.5+path_0.8m+high":  {"ttc_s": 1.5, "corridor_m": 0.8, "min_bottom": 0.35},
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


def filter_clip(clip: dict, clahe: bool) -> list[list[dict]]:
    """Run the Kalman filter over one clip. Per frame: every object's filter output
    and position, so the warning rules can then be applied cheaply."""
    fx, cx, w, h = clip["focal_px"], clip["width"] / 2, clip["width"], clip["height"]
    use_clahe = clahe and clip.get("night", False)
    states: dict[int, ObjectState] = {}
    first_seen: dict[int, float] = {}
    frames = []
    # Frames are numbered in the order they were processed (about 10 per second),
    # as in the live pipeline; numbering from the time would skip or repeat a
    # number when the video's frame rate is not exactly 30.
    for frame_no, f in enumerate(clip["frames"]):
        t, objs = f["t"], []
        for o in f["objects"]:
            d = o["d_clahe"] if use_clahe and o["d_clahe"] is not None else o["d"]
            if d is None:
                continue
            first_seen.setdefault(o["id"], t)
            x1, y1, x2, y2 = o["box"]
            at_edge = x1 <= EDGE_PX or y1 <= EDGE_PX or x2 >= w - EDGE_PX or y2 >= h - EDGE_PX
            out = states.setdefault(o["id"], ObjectState()).step(frame_no, d, None if at_edge else y2 - y1)
            objs.append({"id": o["id"], "frame": frame_no, "ttc": out["ttc"],
                         "gap": lateral_gap_m(o["box"], out["distance"], fx, cx),
                         "bottom": y2 / h, "age": t - first_seen[o["id"]]})
        frames.append((t, objs))
    return frames


def warn_times(frames: list, rules: dict) -> list[float]:
    """Times with a warning under one rule variant: an object in our path whose
    TTC has been under the threshold for WARN_FRAMES frames in a row."""
    run: dict[int, tuple[int, int]] = {}          # track id -> (last frame, frames in a row under threshold)
    times = []
    for t, objs in frames:
        warning = False
        for o in objs:
            last, n = run.get(o["id"], (None, 0))
            if last is None or o["frame"] - last != 1:   # new, or a frame was missed: count again
                n = 0
            n = n + 1 if (o["ttc"] is not None and o["ttc"] < rules["ttc_s"]) else 0
            run[o["id"]] = (o["frame"], n)
            warning |= (n >= ttc_demo.WARN_FRAMES and o["gap"] <= rules["corridor_m"]
                        and o["bottom"] >= rules["min_bottom"] and o["age"] >= rules["min_age_s"])
        if warning:
            times.append(t)
    return times


def wilson(k: int, n: int) -> list[float]:
    """95% confidence interval for a share k/n (Wilson score interval)."""
    if n == 0:
        return [math.nan, math.nan]
    z, p = 1.96, k / n
    mid = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(mid - half, 3), round(mid + half, 3)]


def collect(rules_by_name: dict) -> tuple[dict, dict, float, int]:
    """Read the clips one at a time and record, per variant, every crash clip's
    outcome and every normal clip's false-warning count."""
    meta = {r["file_name"][:-4]: r for r in csv.DictReader(METADATA.open())}
    per_clip = {name: [] for name in rules_by_name}
    false_eps = {name: 0 for name in rules_by_name}
    hours, n_neg = 0.0, 0
    for p in sorted(DATA.rglob("*.json.gz")):
        with gzip.open(p, "rt") as fh:
            clip = json.load(fh)
        if clip.get("run") != RUN:
            continue
        filtered = {c: filter_clip(clip, c) for c in {r["clahe"] for r in rules_by_name.values()}}
        negative = clip["split"].endswith("negative")
        if negative:
            hours += (clip["window_s"][1] - clip["window_s"][0]) / 3600
            n_neg += 1
        else:
            r = meta[clip["clip"]]
            e = float(r["time_of_event"])
            due = float(r["time_of_alert"]) if r["time_of_alert"] else None
        for name, rules in rules_by_name.items():
            starts = episodes(warn_times(filtered[rules["clahe"]], rules))
            if negative:
                false_eps[name] += len(starts)
                continue
            counted = [s for s in starts if e - COUNT_WINDOW_S <= s < e]   # a warning AT the event is too late
            per_clip[name].append({
                "clip": clip["clip"], "night": clip.get("night", False), "light": r["light_conditions"],
                "event_s": e, "due_s": due, "first_warning_s": counted[0] if counted else None,
                "lead_s": round(e - counted[0], 2) if counted else None, "warned": bool(counted),
                "by_due": bool(counted) and due is not None and counted[0] <= due,
                "early_warnings": sum(1 for s in starts if s < e - COUNT_WINDOW_S)})
    return per_clip, false_eps, hours, n_neg


def summarise(rules: dict, rows: list[dict], false_eps: int, hours: float, n_neg: int) -> dict:
    """All numbers for one rule variant."""
    def share(sub, key):
        k = sum(1 for r in sub if r[key])
        return {"k": k, "n": len(sub), "share": round(k / len(sub), 3) if sub else None, "ci95": wilson(k, len(sub))}

    leads = [r["lead_s"] for r in rows if r["lead_s"] is not None]
    rate = false_eps / hours if hours else None
    return {
        "rules": rules,
        "crash_clips": len(rows),
        "warned_before_event": share(rows, "warned"),
        "warned_by_due_time": share([r for r in rows if r["due_s"] is not None], "by_due"),
        "warned_before_event_day": share([r for r in rows if not r["night"]], "warned"),
        "warned_before_event_night": share([r for r in rows if r["night"]], "warned"),
        # Share of crash clips that would show a warning in the 4 s window by pure
        # chance, at this false-warning rate (random warnings: 1 - e^(-rate x 4 s)).
        "warned_by_chance": round(1 - math.exp(-rate / 3600 * COUNT_WINDOW_S), 3) if rate is not None else None,
        "lead_s": {"median": round(statistics.median(leads), 2) if leads else None,
                   "p25": round(statistics.quantiles(leads, n=4)[0], 2) if len(leads) > 1 else None,
                   "p75": round(statistics.quantiles(leads, n=4)[2], 2) if len(leads) > 1 else None},
        "early_warnings_per_crash_clip": round(sum(r["early_warnings"] for r in rows) / max(len(rows), 1), 3),
        "normal_clips": n_neg, "normal_hours": round(hours, 3),
        "false_warnings": false_eps, "false_warnings_per_hour": round(rate, 1) if rate is not None else None,
        "per_clip": rows,
    }


def report(results: dict) -> str:
    """RESULTS.md, generated from results.json."""
    pct = lambda s: "n/a" if s["share"] is None else f"{s['share'] * 100:.0f}% ({s['k']}/{s['n']})"  # noqa: E731
    first = next(iter(results["variants"].values()))
    lines = [f"# Nexar real-crash benchmark, run {RUN}", "",
             "Generated by score_nexar.py from results.json. Do not edit by hand.", "",
             f"Clips: {first['crash_clips']} collision / near-miss clips, {first['normal_clips']} normal clips "
             f"({first['normal_hours'] * 60:.0f} min of driving).", "",
             f"Current rule: {json.dumps(CURRENT)}. Warning = TTC under ttc_s for {ttc_demo.WARN_FRAMES} frames "
             f"in a row, object in our path. A warning counts for a crash if it starts in the "
             f"{COUNT_WINDOW_S:g} s before the event. 'By chance' = share of crash clips that would show a "
             "warning in that window from false warnings alone.", "",
             "| Variant | Warned before event | 95% CI | By chance | Warned by Nexar's due time | Day | Night | "
             "Median lead (s) | False warnings per hour |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, r in results["variants"].items():
        ci = r["warned_before_event"]["ci95"]
        lines.append(f"| {name} | {pct(r['warned_before_event'])} | {ci[0] * 100:.0f} to {ci[1] * 100:.0f}% | "
                     f"{r['warned_by_chance'] * 100:.0f}% | {pct(r['warned_by_due_time'])} | "
                     f"{pct(r['warned_before_event_day'])} | {pct(r['warned_before_event_night'])} | "
                     f"{r['lead_s']['median']} | {r['false_warnings_per_hour']} ({r['false_warnings']}) |")
    return "\n".join(lines) + "\n"


def main() -> None:
    rules_by_name = {name: {**CURRENT, **v} for name, v in VARIANTS.items()}
    per_clip, false_eps, hours, n_neg = collect(rules_by_name)
    results = {"run": RUN, "current": CURRENT, "variants": {
        name: summarise(rules, per_clip[name], false_eps[name], hours, n_neg) for name, rules in rules_by_name.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=1))
    (OUT / "RESULTS.md").write_text(report(results))
    print(report(results))


if __name__ == "__main__":
    main()
