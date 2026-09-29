"""Score combinations of depth models from saved results. No GPU.

Each distance benchmark saves every estimate per object (objects.csv /
obstacles.csv). Combining two models, for example taking the smaller of their
two distances, needs no new inference: this script joins the member runs'
saved estimates, writes them as a new run folder, and lets that benchmark's
own rescore code compute every statistic and generate the reports. So a
combination is documented exactly like any other run.

Rules:
    min    the smaller (nearer) of the members' distances. The cautious choice
           for braking: if either model sees the object close, trust that.
    mean   the average of the members' distances.

Before joining, the member runs are checked to contain exactly the same
objects in the same order (same images, same detector, same matching), so
every combined value compares like with like.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\combine_runs.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Combinations to score, as (display name, rule, member estimators).
COMBINATIONS = [
    ("min(metric3d-v2-small_p10,unidepth-v2-large_p10)", "min", ["metric3d-v2-small_p10", "unidepth-v2-large_p10"]),
    ("mean(metric3d-v2-small_p10,unidepth-v2-large_p10)", "mean", ["metric3d-v2-small_p10", "unidepth-v2-large_p10"]),
    ("min(metric3d-v2-large_p25,unidepth-v2-large_p10)", "min", ["metric3d-v2-large_p25", "unidepth-v2-large_p10"]),
    ("mean(metric3d-v2-large_p25,unidepth-v2-large_p10)", "mean", ["metric3d-v2-large_p25", "unidepth-v2-large_p10"]),
    ("min(metric3d-v2-small_p10,unidepth-v2-base_p10)", "min", ["metric3d-v2-small_p10", "unidepth-v2-base_p10"]),
    ("mean(metric3d-v2-small_p10,unidepth-v2-base_p10)", "mean", ["metric3d-v2-small_p10", "unidepth-v2-base_p10"]),
]

# Per benchmark: its script, per-object file, the columns that identify an
# object (checked to be identical across member runs), the member runs to
# read, and the name of the combined run to write.
BENCHMARKS = [
    {
        "script": HERE / "kitti" / "benchmark_kitti_distance.py",
        "objects_file": "objects.csv",
        "key_columns": ["image", "type", "occluded", "box_height_px", "true_centre_m"],
        "members": ["metric3d-v2-small_full", "metric3d-v2-large_full", "unidepth-v2-base_full", "unidepth-v2-large_full"],
        "run_name": "combinations_full",
    },
    {
        "script": HERE / "lost_and_found" / "benchmark_laf_distance.py",
        "objects_file": "obstacles.csv",
        "key_columns": ["frame", "label", "box_height_px", "true_m"],
        "members": ["metric3d-v2-small_full", "metric3d-v2-large_full", "unidepth-v2-base_full", "unidepth-v2-large_full"],
        "run_name": "combinations_full",
    },
    {
        "script": HERE / "nuscenes" / "benchmark_nuscenes_distance.py",
        "objects_file": "objects.csv",
        "key_columns": ["frame", "class", "box_height_px", "true_centre_m"],
        "members": ["metric3d-v2-small", "metric3d-v2-large", "unidepth-v2-base", "unidepth-v2-large"],
        "run_name": "combinations",
    },
]

# ----------------------------------------------------------------------------


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    return module


def value(x: str) -> float | None:
    return None if x in ("", "None") else float(x)


def combine(rule: str, values: list[float | None]) -> float | None:
    known = [v for v in values if v is not None]
    if not known:
        return None
    return round(min(known) if rule == "min" else sum(known) / len(known), 2)


def build(bench: dict) -> None:
    module = load_module(bench["script"])
    results_dir = bench["script"].parent / "results"
    member_rows = {}
    for run in bench["members"]:
        with (results_dir / run / bench["objects_file"]).open(newline="") as f:
            member_rows[run] = list(csv.DictReader(f))

    # Every member must describe the same objects, in the same order.
    reference = member_rows[bench["members"][0]]
    for run, rows in member_rows.items():
        if len(rows) != len(reference) or any(
            a[k] != b[k] for a, b in zip(rows, reference) for k in bench["key_columns"]
        ):
            raise SystemExit(f"{run} does not cover the same objects as {bench['members'][0]}")

    merged = [dict(r) for r in reference]
    for run, rows in member_rows.items():
        for target, row in zip(merged, rows):
            target.update({k: v for k, v in row.items() if k not in target})
    names = [name for name, _, _ in COMBINATIONS]
    for row in merged:
        for name, rule, members in COMBINATIONS:
            row[name] = combine(rule, [value(row[m]) for m in members])

    # A stub results.json (config and dataset facts of the first member, with
    # this run's name and estimators) lets the benchmark's rescore do the rest.
    first = json.loads((results_dir / bench["members"][0] / "results.json").read_text())
    first["config"]["run_name"] = bench["run_name"]
    first["config"]["estimators"] = names
    first["config"]["depth_model"] = {
        "name": "combination of saved runs: " + ", ".join(bench["members"]),
        "uses_our_focal_length": True,
        "inference_ms_median": "sum of members",
        "inference_ms_p95": "sum of members",
    }
    out_dir = results_dir / bench["run_name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(first, indent=2))
    keep = [k for k in reference[0] if k not in set(sum((m for _, _, m in COMBINATIONS), []))
            and not any(k.startswith(p) for p in ("metric3d", "unidepth"))]
    with (out_dir / bench["objects_file"]).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keep + names, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged)

    print(f"=== {bench['script'].parent.name}: {len(merged)} objects, {len(names)} combinations ===")
    module.rescore(out_dir)
    module.write_comparison()


def main() -> None:
    for bench in BENCHMARKS:
        build(bench)


if __name__ == "__main__":
    main()
