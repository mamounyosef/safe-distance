"""Which objects cause the false warnings on Nexar? (CPU only, one clip at a time.)

Replays the current warning rule (as score_nexar.py, variant "as_now") and,
at the first frame of every warning episode, records the objects that raised
it: class, distance, closing speed, TTC, sideways gap, where the box is in the
image, how long it has been tracked, and how much its box grew in the last
second (a box that does not grow means the object is NOT really getting
closer, so the warning came from the distance readings drifting).

Two groups are compared:
    false  warnings in normal-driving clips (nothing about to happen)
    true   the warning that counted for a crash clip (started in the 4 s before the event)

RUN IT (from the repo root, after score_nexar.py's download step):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\diagnose_nexar.py

Writes results/<RUN>/diagnosis.json (every warning object) and DIAGNOSIS.md (generated summary).
"""

from __future__ import annotations

import gzip
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_nexar as sn  # noqa: E402  (same settings, data folder and helpers)
from score_nexar import ObjectState, lateral_gap_m  # noqa: E402

# Bins for the summary tables: (label, low, high), low <= value < high.
BINS = {
    "distance_m": [("< 5", 0, 5), ("5-10", 5, 10), ("10-20", 10, 20), ("20-40", 20, 40), (">= 40", 40, 1e9)],
    "closing_mps": [("< 3", 0, 3), ("3-6", 3, 6), ("6-10", 6, 10), (">= 10", 10, 1e9)],
    "box_growth_1s": [("shrank (< 0.95)", 0, 0.95), ("about same (0.95-1.05)", 0.95, 1.05),
                      ("grew a little (1.05-1.2)", 1.05, 1.2), ("grew a lot (>= 1.2)", 1.2, 1e9)],
    "age_s": [("< 0.5", 0, 0.5), ("0.5-1", 0.5, 1), ("1-2", 1, 2), (">= 2", 2, 1e9)],
    "lateral_gap_m": [("0 (box covers centre)", 0, 0.01), ("0-0.6", 0.01, 0.6), ("0.6-1.2", 0.6, 1.21)],
    "box_bottom_frac": [("upper half (< 0.5)", 0, 0.5), ("0.5-0.7", 0.5, 0.7), ("0.7-0.9", 0.7, 0.9),
                        ("bottom (>= 0.9)", 0.9, 1.01)],
}


def clip_warnings(clip: dict) -> list[dict]:
    """Warning objects at the first frame of each warning episode in one clip."""
    fx, cx, w, h = clip["focal_px"], clip["width"] / 2, clip["width"], clip["height"]
    use_clahe = clip.get("night", False)
    states: dict[int, ObjectState] = {}
    seen: dict[int, list] = {}          # track id -> [(t, box height)], for age and box growth
    found, last_warn = [], None
    for frame_no, f in enumerate(clip["frames"]):
        t, raised = f["t"], []
        for o in f["objects"]:
            d = o["d_clahe"] if use_clahe and o["d_clahe"] is not None else o["d"]
            if d is None:
                continue
            x1, y1, x2, y2 = o["box"]
            at_edge = x1 <= sn.EDGE_PX or y1 <= sn.EDGE_PX or x2 >= w - sn.EDGE_PX or y2 >= h - sn.EDGE_PX
            out = states.setdefault(o["id"], ObjectState()).step(frame_no, d, None if at_edge else y2 - y1)
            hist = seen.setdefault(o["id"], [])
            hist.append((t, y2 - y1))
            gap = lateral_gap_m(o["box"], out["distance"], fx, cx)
            if out["warning"] and gap <= sn.CORRIDOR_M:
                ago = [hh for tt, hh in hist if t - tt >= 1.0]       # box height about 1 s ago
                raised.append({
                    "t": t, "cls": o["cls"], "conf": o["conf"], "measured_m": round(d, 2),
                    "distance_m": round(out["distance"], 2), "closing_mps": round(out["closing"], 2),
                    "ttc_s": round(out["ttc"], 2), "lateral_gap_m": round(gap, 2),
                    "age_s": round(t - hist[0][0], 2), "at_edge": at_edge,
                    "box_growth_1s": round((y2 - y1) / ago[-1], 3) if ago and ago[-1] > 0 else None,
                    "box_h_frac": round((y2 - y1) / h, 3), "box_w_frac": round((x2 - x1) / w, 3),
                    "box_bottom_frac": round(y2 / h, 3), "brightness": f["brightness"]})
        if raised:
            if last_warn is None or t - last_warn > sn.EPISODE_GAP_S:   # first frame of a new episode
                found += raised
            last_warn = t
    return found


def table(rows: list[dict], key: str) -> list[tuple[str, int, float]]:
    """(bin label, count, share) for one feature."""
    vals = [r[key] for r in rows if r[key] is not None]
    out = []
    for label, lo, hi in BINS[key]:
        k = sum(1 for v in vals if lo <= v < hi)
        out.append((label, k, round(k / len(vals), 3) if vals else 0.0))
    return out


def summary(rows: list[dict]) -> dict:
    med = lambda k: round(statistics.median([r[k] for r in rows if r[k] is not None]), 2) if rows else None  # noqa: E731
    return {"objects": len(rows), "classes": dict(Counter(r["cls"] for r in rows).most_common()),
            "at_edge": sum(r["at_edge"] for r in rows),
            "medians": {k: med(k) for k in ("distance_m", "closing_mps", "ttc_s", "age_s", "box_growth_1s",
                                            "lateral_gap_m", "box_bottom_frac", "box_h_frac")},
            "bins": {k: table(rows, k) for k in BINS}}


def report(res: dict) -> str:
    f, t = res["false"], res["true"]
    lines = [f"# Nexar warning diagnosis, run {sn.RUN}", "",
             "Generated by diagnose_nexar.py from diagnosis.json. Do not edit by hand.", "",
             "Objects that raised a warning, at the first frame of each warning episode.", "",
             f"- false: warnings in normal-driving clips ({f['objects']} objects)",
             f"- true: the warning that counted in a crash clip ({t['objects']} objects)", "",
             "## Classes", "", "| Class | False | True |", "|---|---|---|"]
    for c in sorted(set(f["classes"]) | set(t["classes"]), key=lambda c: -f["classes"].get(c, 0)):
        lines.append(f"| {c} | {f['classes'].get(c, 0)} | {t['classes'].get(c, 0)} |")
    lines += ["", "## Medians", "", "| Feature | False | True |", "|---|---|---|"]
    for k in f["medians"]:
        lines.append(f"| {k} | {f['medians'][k]} | {t['medians'][k]} |")
    lines.append(f"| touching image edge (count) | {f['at_edge']} | {t['at_edge']} |")
    for k in BINS:
        lines += ["", f"## {k}", "", "| Bin | False | True |", "|---|---|---|"]
        for (lab, kf, sf), (_, kt, st) in zip(f["bins"][k], t["bins"][k]):
            lines.append(f"| {lab} | {kf} ({sf * 100:.0f}%) | {kt} ({st * 100:.0f}%) |")
    return "\n".join(lines) + "\n"


def main() -> None:
    meta = {r["file_name"][:-4]: r for r in sn.csv.DictReader(sn.METADATA.open())}
    false_rows, true_rows = [], []
    for p in sorted(sn.DATA.rglob("*.json.gz")):
        with gzip.open(p, "rt") as fh:            # one clip in memory at a time
            clip = json.load(fh)
        if clip.get("run") != sn.RUN:
            continue
        rows = clip_warnings(clip)
        for r in rows:
            r["clip"] = clip["clip"]
        if clip["split"].endswith("negative"):
            false_rows += rows
        else:
            e = float(meta[clip["clip"]]["time_of_event"])
            counted = [r for r in rows if e - sn.COUNT_WINDOW_S <= r["t"] < e]
            if counted:   # the first counted episode: all objects raising it at that frame
                true_rows += [r for r in counted if r["t"] == counted[0]["t"]]
    res = {"run": sn.RUN, "false": summary(false_rows), "true": summary(true_rows),
           "false_rows": false_rows, "true_rows": true_rows}
    sn.OUT.mkdir(parents=True, exist_ok=True)
    (sn.OUT / "diagnosis.json").write_text(json.dumps(res, indent=1))
    (sn.OUT / "DIAGNOSIS.md").write_text(report(res))
    print(report(res))


if __name__ == "__main__":
    main()
