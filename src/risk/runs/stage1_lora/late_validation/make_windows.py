"""Build the NEW fixed validation windows for the late validation (this PC, free, seconds).

Four cases (2 s windows; settings in config.yaml):

    Nexar Public crash    groups 0 and 1 (clip stops 0.5 / 1.0 s before the crash): last frame + 0.5 s earlier
                          group 2 (stops 1.5 s before): last frame only (the 2.0 s window is dropped)        label 1
    Nexar Public normal   last frame + 4 s earlier (no overlap)                                               label 0
    BDD100K val, cleaned  "hard": the 2 moments plain BADAS-Open found riskiest (same as training's validation) label 0
    BDD100K val, cleaned  "normal": 1 random moment per clip (seed 42), at least 2 s from the hard ones        label 0

Every window's end frame is checked against the cached clip's length (wide_frame_counts.json): each needs 16 frames
of video before its end.

Inputs:  C:/safe-distance-data/nexar/meta/solution.csv          (Nexar's test labels: id, target, Usage, group)
         src/risk/data/bdd100k_ids/val_clean.txt                (the 434 clean val clips)
         src/risk/runs/baseline_badas_open/results/eval/series_bdd_val.json   (plain BADAS readings, every 0.5 s)
         src/risk/data/wide_frame_counts.json                   (frames per cached clip)
Outputs: late_validation/windows.json            (NOT in git: it holds Nexar's test labels; shipped to Modal)
         late_validation/results/windows_summary.json   (counts only, in git)

RUN IT (from the repo root):
    python src\\risk\\runs\\stage1_lora\\late_validation\\make_windows.py
"""

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent                            # late_validation/
RISK = HERE.parents[2]                                            # src/risk
CFG = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))["windows"]
TRAIN_CFG = yaml.safe_load((HERE.parent / "config.yaml").read_text(encoding="utf-8"))["data"]

# ---- CONFIG ----
SOLUTION = Path(r"C:\safe-distance-data\nexar\meta\solution.csv")
VAL_CLEAN = RISK / "data/bdd100k_ids/val_clean.txt"
BDD_SERIES = RISK / "runs/baseline_badas_open/results/eval/series_bdd_val.json"
FRAME_COUNTS = RISK / TRAIN_CFG["frame_counts"]
OUT = HERE / CFG["out"]
SUMMARY = HERE / "results" / "windows_summary.json"
FPS, WINDOW_FRAMES = TRAIN_CFG["fps"], TRAIN_CFG["window_frames"]   # 8 frames per second, 16-frame windows
BDD_FOLDER = "bdd100k_videos_100k_val"
# ----------------


def nexar_windows() -> list[dict]:
    """Nexar Public crash and normal windows. Given as frames before the clip's last frame ("end_back")."""
    out = []
    for r in csv.DictReader(SOLUTION.open()):
        if r["Usage"] != "Public":
            continue                                              # Private stays untouched for the final score
        crash, group = r["target"] == "1", int(r["group"])        # group 0/1/2 = stops 0.5 / 1.0 / 1.5 s before
        if crash:
            backs = CFG["nexar_crash_back_frames"]
            if group in CFG["nexar_crash_drop_second_for_groups"]:
                backs = backs[:1]                                 # group 2: last-frame window only
        else:
            backs = CFG["nexar_normal_back_frames"]
        for rank, back in enumerate(backs, 1):
            out.append({"group": "nexar_crash" if crash else "nexar_normal",
                        "folder": f"nexar_test-public_{'positive' if crash else 'negative'}",
                        "clip": r["id"], "end": None, "end_back": back, "rank": rank,
                        "label": 1.0 if crash else 0.0, "nexar_group": group})
    return out


def bdd_windows(rng: np.random.Generator) -> list[dict]:
    """BDD100K val windows: the 2 hard moments (exactly as training's validation picked them) + random normal ones."""
    series = json.loads(BDD_SERIES.read_text())
    gap = CFG["bdd_min_gap_s"]
    out = []
    for clip in VAL_CLEAN.read_text().split():
        readings = series[clip]                                   # (window end time s, risk) every 0.5 s
        by_risk = sorted(readings, key=lambda r: -r[1])
        hard = [by_risk[0][0]]                                    # the riskiest moment
        hard += [next(t for t, _ in by_risk if abs(t - hard[0]) >= gap)]   # the 2nd riskiest, far enough away
        # random normal moments: any reading time at least `gap` from every window already taken in this clip
        taken = list(hard)
        normal = []
        for _ in range(CFG["bdd_normal_per_clip"]):
            free = [t for t, _ in readings if all(abs(t - u) >= gap for u in taken)]
            if not free:
                raise SystemExit(f"{clip}: no moment left at least {gap} s from the others")
            t = float(free[rng.integers(len(free))])
            normal.append(t)
            taken.append(t)
        for kind, times in (("bdd_hard", hard), ("bdd_normal", normal)):
            for rank, t in enumerate(times, 1):
                out.append({"group": kind, "folder": BDD_FOLDER, "clip": clip, "end": int(round(t * FPS)),
                            "end_back": None, "rank": rank, "label": 0.0, "nexar_group": None})
    return out


def check_lengths(windows: list[dict]) -> None:
    """Stop if any window would need frames the cached clip does not have."""
    counts = json.loads(FRAME_COUNTS.read_text())
    bad = []
    for w in windows:
        n = counts[f"{w['folder']}/{w['clip']}"]                  # frames in this cached clip
        end = n - w["end_back"] if w["end"] is None else w["end"]
        if not WINDOW_FRAMES <= end <= n:
            bad.append((w["group"], end, n))
    if bad:
        raise SystemExit(f"{len(bad)} windows fall outside their clip, e.g. {bad[:3]}")


def main() -> None:
    rng = np.random.default_rng(CFG["seed"])
    windows = nexar_windows() + bdd_windows(rng)
    check_lengths(windows)
    OUT.write_text(json.dumps(windows, indent=1))

    # counts only (no clip names, no labels per clip): safe for git
    per_group = Counter(w["group"] for w in windows)
    crash_per_kind = Counter((w["nexar_group"], w["rank"]) for w in windows if w["group"] == "nexar_crash")
    summary = {"total": len(windows), "per_case": dict(per_group),
               "nexar_crash_per_group_and_window": {f"group{g}_win{r}": n for (g, r), n in sorted(crash_per_kind.items())},
               "settings": CFG}
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2))
    print(f"saved {OUT.name}: {len(windows)} windows {dict(per_group)}")
    print(f"crash windows per (group, window): {summary['nexar_crash_per_group_and_window']}")
    print(f"saved {SUMMARY}")


if __name__ == "__main__":
    main()
