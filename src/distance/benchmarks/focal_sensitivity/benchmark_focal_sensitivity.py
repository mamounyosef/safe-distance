"""How accurate is each method when the camera's focal length is wrong? No GPU.

On a new camera (a dashcam, a phone) the focal length is rarely known
exactly. Several methods use it to turn their output into metres:

    Metric3D v2         metres = network output * focal / 1000
    Depth Anything 3    metres = focal * network output / 300
    Depth Pro           metres = 1 / (network output * width / focal)
    known size          metres = focal * real height / height in pixels

In all four, the focal length only multiplies the result: the image the
network sees does not change. So if the focal length we give is off by a
factor s (s = 1.1 means 10% too high), every distance is off by exactly s,
and accuracy under that error can be computed from the saved estimates
without running anything.

Not covered here: UniDepth (it feeds the camera into the network, so the
effect is not a simple multiplication and needs its own GPU runs) and ground
plane (it depends on the focal length non-linearly, through the camera tilt).

Output: results/<RUN_NAME>/results.json (source of truth) and a generated
RESULTS.md next to this file.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\focal_sensitivity\\benchmark_focal_sensitivity.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2].parent))

from src.detection.benchmarks.common import md_table, provenance

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

RUN_NAME = "focal_scaling_v1"

# Focal length errors to simulate, as multipliers: 0.9 = given 10% too low.
SCALES = [0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2]

# Estimators whose distance is exactly proportional to the focal length.
PROPORTIONAL = [
    "metric3d-v2-small-fp16_p10",
    "metric3d-v2-large-fp16_p25",
    "da3-metric-large_p10",
    "depth-pro_median",
    "known_size",
]

# Where each benchmark's saved per-object estimates are, and how to read them:
# (label, run folder, file, truth column, row filter).
DISTANCE = HERE.parent
SOURCES = [
    ("KITTI, in path", "kitti/results", "objects.csv", "true_nearest_surface_m",
     lambda r: float(r["lateral_gap_m"]) <= 1.2),
    ("Lost and Found, under 20 m", "lost_and_found/results", "obstacles.csv", "true_m",
     lambda r: float(r["true_m"]) < 20),
    ("nuScenes, in path", "nuscenes/results", "objects.csv", "true_nearest_surface_m",
     lambda r: float(r["lateral_gap_m"]) <= 1.2),
]

# ----------------------------------------------------------------------------


def find_estimates(folder: Path, file_name: str, estimator: str) -> Path | None:
    """The largest run folder whose saved file has a column for this estimator."""
    best, best_rows = None, -1
    for run in sorted(p for p in folder.iterdir() if (p / file_name).exists()):
        with (run / file_name).open(newline="") as f:
            header = next(csv.reader(f))
            if estimator in header:
                n = sum(1 for _ in f)
                if n > best_rows:
                    best, best_rows = run, n
    return best


def main() -> None:
    results = {"benchmark": "focal_length_sensitivity", "provenance": provenance(),
               "config": {"run_name": RUN_NAME, "scales": SCALES, "estimators": PROPORTIONAL,
                          "assumption": "distance proportional to the focal length given (exact for these methods)"},
               "sources": {}}
    for label, rel, file_name, truth, keep in SOURCES:
        node = {}
        for est in PROPORTIONAL:
            run = find_estimates(DISTANCE / rel, file_name, est)
            if run is None:
                continue
            with (run / file_name).open(newline="") as f:
                rows = [r for r in csv.DictReader(f) if keep(r) and r[est] not in ("", "None") and float(r[truth]) > 0]
            t = np.array([float(r[truth]) for r in rows])
            e = np.array([float(r[est]) for r in rows])
            node[est] = {
                "run": run.name,
                "objects": len(rows),
                "within_10pct": {str(s): round(float(np.mean(np.abs(e * s - t) / t <= 0.10)), 4) for s in SCALES},
                "median_abs_error_m": {str(s): round(float(np.median(np.abs(e * s - t))), 2) for s in SCALES},
            }
        results["sources"][label] = node

    run_dir = HERE / "results" / RUN_NAME
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    write_report(run_dir)
    print(f"wrote {run_dir}")


def write_report(run_dir: Path) -> None:
    r = json.loads((run_dir / "results.json").read_text())
    cfg, prov = r["config"], r["provenance"]
    scales = [str(s) for s in cfg["scales"]]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""

    def label(s: str) -> str:
        v = float(s)
        return "exact" if v == 1.0 else f"{(v - 1) * 100:+.0f}%"

    out = [
        f"# Focal length sensitivity: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_focal_sensitivity.py`. Do not edit by hand.",
        "",
        "Share of objects within 10% of the true distance when the focal length given to each method",
        "is off by the stated amount. Computed from the saved estimates of the accuracy benchmarks: for",
        "these methods the distance is exactly proportional to the focal length, so no re-run is needed.",
        "",
        f"Git commit `{prov['git_commit']}`{dirty}, created {prov['created_utc']} UTC.",
        "",
    ]
    for source, node in r["sources"].items():
        out += [f"## {source}", "",
                *md_table(["Estimator", "Objects", "Run", *[f"Focal {label(s)}" for s in scales]],
                          [[f"`{e}`", n["objects"], f"`{n['run']}`",
                            *[f"{n['within_10pct'][s]:.0%}" for s in scales]] for e, n in node.items()])]
    out += [
        "## Known limitations",
        "",
        "- UniDepth is not included: it takes the camera as a network input, so its sensitivity is not",
        "  a simple scaling and needs its own runs (including its mode that estimates the camera itself).",
        "- Ground plane is not included: it depends on the focal length non-linearly.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
