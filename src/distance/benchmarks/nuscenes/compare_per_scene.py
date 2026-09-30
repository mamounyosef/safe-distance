"""Paired, per-scene comparison of two nuScenes runs (e.g. no enhancement vs CLAHE).

Question it answers: is a gain real across many scenes, or carried by a few?
Frames within a scene are near-copies of each other (the same cars, seen 40
times), so the honest unit of evidence is the SCENE, not the object.

For in-path objects, vs the nearest-surface truth, it reports per scene how many
objects each run gets within 10%, then:
  - scenes better / worse / equal with the candidate,
  - a sign test over scenes (chance of that many "better" scenes if the
    enhancement did nothing),
  - a 95% confidence interval of the gain in "within 10%" share, by resampling
    whole scenes (cluster bootstrap).
No GPU: reads the objects.csv files the benchmark already wrote.

Output: per_scene.json (source of truth) and a generated PER_SCENE.md, in a
folder named after both runs next to them.

Run (from the repo root): .venv\\Scripts\\python.exe src\\distance\\benchmarks\\nuscenes\\compare_per_scene.py
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from src.detection.benchmarks.common import md_table, provenance  # noqa: E402

# ---- CONFIG ----
HERE = Path(__file__).resolve().parent
# (results folder, baseline run, candidate run). Each pair is compared by its "_p10" estimator.
PAIRS = [
    (HERE / "results_night_enhancement", "metric3d-v2-small-fp16_night", "metric3d-v2-small-fp16+clahe4_night"),
    (HERE / "results_night_confirm", "metric3d-v2-small-fp16_night", "metric3d-v2-small-fp16+clahe4_night"),
]
STATISTIC = "p10"
TRUTH = "true_nearest_surface_m"
TOLERANCE = 0.10
BOOTSTRAP = 10_000
SEED = 0
# ----------------


def load(run_dir: Path) -> dict:
    """In-path rows of one run, keyed by object, with 'within 10%' per row."""
    with (run_dir / "objects.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    column = next(c for c in rows[0] if c.endswith(f"_{STATISTIC}"))
    out = {}
    for r in rows:
        if r["in_path"] != "True":
            continue
        truth, est = float(r[TRUTH]), r[column]
        ok = est not in ("", "None") and abs(float(est) - truth) <= TOLERANCE * truth
        out[(r["frame"], r["true_centre_m"], r["true_nearest_surface_m"])] = (r["scene"], ok)
    return out, column


def sign_test(better: int, worse: int) -> float:
    """Two-sided binomial test over scenes that changed (ties dropped)."""
    n = better + worse
    if n == 0:
        return 1.0
    k = max(better, worse)
    tail = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(folder: Path, base_run: str, cand_run: str) -> None:
    if not (folder / base_run / "objects.csv").exists() or not (folder / cand_run / "objects.csv").exists():
        print(f"skip {folder.name}: runs not there yet")
        return
    base, base_col = load(folder / base_run)
    cand, cand_col = load(folder / cand_run)
    keys = sorted(set(base) & set(cand))
    scenes: dict[str, list[int]] = {}
    for k in keys:
        s = base[k][0]
        n, b, c = scenes.setdefault(s, [0, 0, 0]), base[k][1], cand[k][1]
        n[0] += 1
        n[1] += b
        n[2] += c
    names = sorted(scenes)
    arr = np.array([scenes[s] for s in names], dtype=float)
    total = arr.sum(0)
    gain = (total[2] - total[1]) / total[0]
    rng = np.random.default_rng(SEED)
    boot = []
    for _ in range(BOOTSTRAP):
        pick = arr[rng.integers(0, len(arr), len(arr))].sum(0)
        boot.append((pick[2] - pick[1]) / pick[0])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    better = int((arr[:, 2] > arr[:, 1]).sum())
    worse = int((arr[:, 2] < arr[:, 1]).sum())
    # Share of the total gain that comes from the single best scene.
    diffs = arr[:, 2] - arr[:, 1]
    top = float(diffs.max() / diffs.sum()) if diffs.sum() > 0 else None

    result = {
        "provenance": provenance(),
        "folder": folder.name, "baseline": base_col, "candidate": cand_col,
        "truth": TRUTH, "tolerance": TOLERANCE, "unit_of_evidence": "scene",
        "objects_in_path_paired": len(keys), "unpaired_objects": len(set(base) ^ set(cand)),
        "scenes": len(names),
        "baseline_within": int(total[1]), "candidate_within": int(total[2]),
        "baseline_share": round(total[1] / total[0], 4), "candidate_share": round(total[2] / total[0], 4),
        "gain_share": round(gain, 4),
        "gain_share_95ci_scene_bootstrap": [round(float(lo), 4), round(float(hi), 4)],
        "scenes_better": better, "scenes_worse": worse, "scenes_equal": len(names) - better - worse,
        "sign_test_p": round(sign_test(better, worse), 6),
        "share_of_gain_from_best_scene": None if top is None else round(top, 3),
        "per_scene": {s: {"objects": int(v[0]), "baseline_within": int(v[1]), "candidate_within": int(v[2])}
                      for s, v in zip(names, arr)},
    }
    out_dir = folder / f"per_scene_{base_run}_vs_{cand_run}"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "per_scene.json").write_text(json.dumps(result, indent=2))
    write_report(out_dir, result)
    print(f"{folder.name}: {len(names)} scenes, {len(keys)} objects, "
          f"{result['baseline_share']:.1%} -> {result['candidate_share']:.1%} "
          f"(gain {gain:+.1%}, 95% CI {lo:+.1%} .. {hi:+.1%}), "
          f"scenes better/worse/equal {better}/{worse}/{result['scenes_equal']}, "
          f"sign test p = {result['sign_test_p']:.4g}, best scene = {top if top is None else f'{top:.0%}'} of gain")


def write_report(out_dir: Path, r: dict) -> None:
    pct = lambda x: f"{x:.1%}"  # noqa: E731
    lo, hi = r["gain_share_95ci_scene_bootstrap"]
    lines = [
        f"# Per-scene comparison: `{r['candidate']}` vs `{r['baseline']}`", "",
        "Generated automatically from `per_scene.json` by `compare_per_scene.py`. Do not edit by hand.", "",
        f"In-path objects, within {r['tolerance']:.0%} of the {r['truth'].replace('true_', '').replace('_m', '').replace('_', ' ')}.",
        "The unit of evidence is the scene: frames of one scene show the same objects many times.", "",
        *md_table(["", ""], [
            ["Scenes / paired objects", f"{r['scenes']} / {r['objects_in_path_paired']}"],
            ["Baseline within 10%", f"{r['baseline_within']} ({pct(r['baseline_share'])})"],
            ["Candidate within 10%", f"{r['candidate_within']} ({pct(r['candidate_share'])})"],
            ["Gain", f"{r['gain_share']:+.1%} (95% CI {lo:+.1%} to {hi:+.1%}, resampling scenes)"],
            ["Scenes better / worse / equal", f"{r['scenes_better']} / {r['scenes_worse']} / {r['scenes_equal']}"],
            ["Sign test over scenes, p", f"{r['sign_test_p']:.4g}"],
            ["Share of the gain from the single best scene",
             "-" if r["share_of_gain_from_best_scene"] is None else pct(r["share_of_gain_from_best_scene"])],
            ["Git commit", f"`{r['provenance']['git_commit']}`"],
        ]),
        "## Per scene", "",
        *md_table(["Scene", "Objects", "Baseline within 10%", "Candidate within 10%", "Change"],
                  [[s, v["objects"], v["baseline_within"], v["candidate_within"],
                    f"{v['candidate_within'] - v['baseline_within']:+d}"] for s, v in r["per_scene"].items()]),
    ]
    (out_dir / "PER_SCENE.md").write_text("\n".join(lines))


def main() -> None:
    for folder, base_run, cand_run in PAIRS:
        compare(folder, base_run, cand_run)


if __name__ == "__main__":
    main()
