"""Generate the distance-stage summary: every benchmark, every candidate, one table.

Reads the results.json files written by the individual distance benchmarks
and assembles them per candidate method: accuracy on each dataset, at night,
on obstacles, stability over time, speed, sensitivity to a wrong focal length,
and licence. Nothing here is measured or typed by hand: every number is read
from a benchmark's results.json, and the source file of each is recorded in
summary.json. Missing results show as "-".

Output (next to this file):
    SUMMARY.md     the generated overview
    summary.json   the same numbers, with their source files

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\summarize_distance.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

from src.detection.benchmarks.common import md_table, provenance

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Candidates, as (label, estimator, run names per benchmark, speed model name,
# licence). A run name of None means that benchmark has no such run.
CANDIDATES = [
    {"label": "Metric3D v2 Small FP16", "laf_detected": "metric3d-v2-small-fp16_detected", "estimator": "metric3d-v2-small-fp16_p10",
     "kitti": "metric3d-v2-small-fp16_full", "laf": "metric3d-v2-small-fp16_full",
     "nuscenes": "metric3d-v2-small-fp16", "nuscenes_obstacles": "metric3d-v2-small-fp16",
     "stability": "metric3d-v2-small-fp16_f150", "speed": "metric3d-v2-small-fp16", "licence": "BSD-2-Clause"},
    {"label": "Metric3D v2 Large FP16", "laf_detected": "metric3d-v2-large-fp16_detected", "estimator": "metric3d-v2-large-fp16_p25",
     "kitti": "metric3d-v2-large-fp16_full", "laf": "metric3d-v2-large-fp16_full",
     "nuscenes": "metric3d-v2-large-fp16", "nuscenes_obstacles": "metric3d-v2-large-fp16",
     "stability": "metric3d-v2-large-fp16_f150", "speed": "metric3d-v2-large-fp16", "licence": "BSD-2-Clause"},
    {"label": "UniDepth v2 Base", "laf_detected": "unidepth-v2-base_detected", "estimator": "unidepth-v2-base_p10",
     "kitti": "unidepth-v2-base_full", "laf": "unidepth-v2-base_full",
     "nuscenes": "unidepth-v2-base", "nuscenes_obstacles": "unidepth-v2-base",
     "stability": "unidepth-v2-base_f150", "speed": "unidepth-v2-base", "licence": "CC BY-NC 4.0 (non-commercial)"},
    {"label": "UniDepth v2 Large", "laf_detected": "unidepth-v2-large_detected", "estimator": "unidepth-v2-large_p10",
     "kitti": "unidepth-v2-large_full", "laf": "unidepth-v2-large_full",
     "nuscenes": "unidepth-v2-large", "nuscenes_obstacles": "unidepth-v2-large",
     "stability": "unidepth-v2-large_f150", "speed": "unidepth-v2-large", "licence": "CC BY-NC 4.0 (non-commercial)"},
    {"label": "UniDepth v2 Base, camera not given", "estimator": "unidepth-v2-base-nocam_p10",
     "kitti": "unidepth-v2-base-nocam_full", "laf": "unidepth-v2-base-nocam_full",
     "nuscenes": "unidepth-v2-base-nocam", "nuscenes_obstacles": None,
     "stability": None, "speed": "unidepth-v2-base", "licence": "CC BY-NC 4.0 (non-commercial)"},
    {"label": "UniDepth v2 Large, camera not given", "estimator": "unidepth-v2-large-nocam_p10",
     "kitti": "unidepth-v2-large-nocam_full", "laf": "unidepth-v2-large-nocam_full",
     "nuscenes": "unidepth-v2-large-nocam", "nuscenes_obstacles": None,
     "stability": None, "speed": "unidepth-v2-large", "licence": "CC BY-NC 4.0 (non-commercial)"},
    {"label": "min(Metric3D v2 Large, UniDepth v2 Large)",
     "estimator": "min(metric3d-v2-large_p25,unidepth-v2-large_p10)",
     "kitti": "combinations_full", "laf": "combinations_full",
     "nuscenes": "combinations", "nuscenes_obstacles": "combinations",
     "stability": None, "speed": ["metric3d-v2-large-fp16", "unidepth-v2-large"],
     "licence": "CC BY-NC 4.0 (UniDepth part)"},
    {"label": "Known size (geometric)", "estimator": "known_size",
     "kitti": "geometric_full", "laf": None, "nuscenes": "geometric", "nuscenes_obstacles": None,
     "stability": "geometric_f150", "speed": None, "licence": "own code"},
    {"label": "Ground plane (geometric)", "laf_detected": "geometric_detected", "estimator": "ground_plane",
     "kitti": "geometric_full", "laf": "geometric_full", "nuscenes": "geometric",
     "nuscenes_obstacles": "geometric", "stability": "geometric_f150", "speed": None, "licence": "own code"},
]

SPEED_RUN = "rtx4060_pytorch_fp16"
SPEED_SIZE = "nuScenes 1600x900"
FOCAL_RUN = "focal_scaling_v1"

# ----------------------------------------------------------------------------

PATHS = {
    "kitti": HERE / "kitti" / "results",
    "laf": HERE / "lost_and_found" / "results",
    "laf_detected": HERE / "lost_and_found" / "results_detected",
    "nuscenes": HERE / "nuscenes" / "results",
    "nuscenes_obstacles": HERE / "nuscenes" / "results_obstacles",
    "stability": HERE / "kitti_tracking" / "results",
    "speed": HERE / "speed" / "results",
    "focal": HERE / "focal_sensitivity" / "results",
}


def load(kind: str, run: str | None) -> tuple[dict | None, str | None]:
    if run is None:
        return None, None
    path = PATHS[kind] / run / "results.json"
    if not path.exists():
        return None, None
    return json.loads(path.read_text()), str(path.relative_to(HERE.parents[2])).replace("\\", "/")


def dig(d, *keys):
    for k in keys:
        if d is None or k not in d:
            return None
        d = d[k]
    return d


def collect(c: dict) -> dict:
    e = c["estimator"]
    row, sources = {"label": c["label"], "estimator": e, "licence": c["licence"]}, {}

    r, src = load("kitti", c["kitti"])
    row["kitti_in_path_within_10pct"] = dig(r, "methods", e, "nearest_surface", "in_path", "overall", "within_10pct")
    row["kitti_in_path_median_error_m"] = dig(r, "methods", e, "nearest_surface", "in_path", "overall", "median_abs_error_m")
    sources["kitti"] = src

    r, src = load("laf", c["laf"])
    row["laf_under_20m_within_10pct"] = dig(r, "methods", e, "rank_range", "within_10pct")
    sources["laf"] = src

    r, src = load("laf_detected", c.get("laf_detected"))
    row["laf_real_pipeline_under_20m_within_10pct"] = dig(r, "methods", e, "rank_range", "within_10pct")
    sources["laf_detected"] = src

    r, src = load("nuscenes", c["nuscenes"])
    n = dig(r, "methods", e, "nearest_surface")
    row["nuscenes_in_path_within_10pct"] = dig(n, "in_path", "overall", "within_10pct")
    row["nuscenes_day_in_path_within_10pct"] = dig(n, "by_condition", "day", "in_path", "within_10pct")
    row["nuscenes_night_in_path_within_10pct"] = dig(n, "by_condition", "night", "in_path", "within_10pct")
    row["estimated_focal_px_median"] = dig(r, "config", "depth_model", "estimated_focal_px_median")
    sources["nuscenes"] = src

    r, src = load("nuscenes_obstacles", c["nuscenes_obstacles"])
    row["nuscenes_cones_barriers_within_10pct"] = dig(r, "methods", e, "nearest_surface", "overall", "within_10pct")
    sources["nuscenes_obstacles"] = src

    r, src = load("stability", c["stability"])
    s = dig(r, "methods", e, "in_path")
    row["jitter_median_pct"] = dig(s, "jitter_median_pct")
    row["speed_error_0_5s_p90_mps"] = dig(s, "speed_error_w5_p90_mps")
    row["speed_error_2s_p90_mps"] = dig(s, "speed_error_w20_p90_mps")
    sources["stability"] = src

    r, src = load("speed", SPEED_RUN)
    models = c["speed"] if isinstance(c["speed"], list) else ([c["speed"]] if c["speed"] else [])
    times = [dig(r, "models", m, "by_size", SPEED_SIZE, "median_ms") for m in models]
    row["ms_per_frame"] = round(sum(times), 1) if times and None not in times else (0.0 if not models else None)
    sources["speed"] = src if models else None

    r, src = load("focal", FOCAL_RUN)
    f = dig(r, "sources", "KITTI, in path", e, "within_10pct")
    row["kitti_within_10pct_focal_minus10"] = dig(f, "0.9")
    row["kitti_within_10pct_focal_plus10"] = dig(f, "1.1")
    sources["focal"] = src if f else None

    row["sources"] = sources
    return row


def pct(v) -> str:
    return "-" if v is None else f"{v:.0%}"


def num(v, unit: str = "") -> str:
    if v is None:
        return "-"
    return f"{v:.2f}{unit}" if isinstance(v, float) and unit else f"{v}{unit}"


def main() -> None:
    rows = [collect(c) for c in CANDIDATES]
    summary = {"provenance": provenance(), "candidates": rows,
               "speed": {"run": SPEED_RUN, "image_size": SPEED_SIZE}, "focal_run": FOCAL_RUN}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2))

    prov = summary["provenance"]
    out = [
        "# Distance stage: summary of all benchmarks",
        "",
        "Generated automatically by `summarize_distance.py` from each benchmark's `results.json`",
        "(the exact source file of every number is listed in `summary.json`). Do not edit by hand.",
        f"Generated at git commit `{prov['git_commit']}`, {prov['created_utc']} UTC.",
        "",
        "All accuracy figures are the share of objects whose estimated distance is within 10% of the",
        "true distance to their nearest surface (laser ground truth; stereo for Lost and Found).",
        "",
        "## Accuracy",
        "",
        *md_table(["Candidate", "KITTI road users, in path", "Lost and Found obstacles, under 20 m",
                   "Lost and Found, real pipeline (detector masks), under 20 m",
                   "nuScenes in path", "nuScenes day", "nuScenes night", "nuScenes cones and barriers"],
                  [[r["label"], pct(r["kitti_in_path_within_10pct"]), pct(r["laf_under_20m_within_10pct"]),
                    pct(r["laf_real_pipeline_under_20m_within_10pct"]),
                    pct(r["nuscenes_in_path_within_10pct"]), pct(r["nuscenes_day_in_path_within_10pct"]),
                    pct(r["nuscenes_night_in_path_within_10pct"]), pct(r["nuscenes_cones_barriers_within_10pct"])]
                   for r in rows]),
        "## Stability, speed, robustness, licence",
        "",
        "Stability: KITTI tracking, in path. Speed: median per frame on an RTX 4060 in PyTorch at",
        f"{SPEED_SIZE} (sum of both models for a combination). Focal: KITTI in path, within 10% when",
        "the focal length given is 10% too low / too high.",
        "",
        *md_table(["Candidate", "Jitter, median", "Speed error p90, 0.5 s", "Speed error p90, 2 s",
                   "ms per frame", "Focal -10%", "Focal +10%", "Estimated focal (px), nuScenes", "Licence"],
                  [[r["label"], "-" if r["jitter_median_pct"] is None else f"{r['jitter_median_pct']:.1%}",
                    num(r["speed_error_0_5s_p90_mps"], " m/s"), num(r["speed_error_2s_p90_mps"], " m/s"),
                    num(r["ms_per_frame"]), pct(r["kitti_within_10pct_focal_minus10"]),
                    pct(r["kitti_within_10pct_focal_plus10"]), num(r["estimated_focal_px_median"]), r["licence"]]
                   for r in rows]),
        "## Where each benchmark is",
        "",
        "- KITTI accuracy: `src/distance/benchmarks/kitti/COMPARISON.md`",
        "- Lost and Found obstacles: `src/distance/benchmarks/lost_and_found/COMPARISON.md` (labelled outlines)",
        "  and `COMPARISON_DETECTED.md` (real pipeline: YOLOE detections and masks)",
        "- nuScenes: `src/distance/benchmarks/nuscenes/COMPARISON.md` and `COMPARISON_OBSTACLES.md`",
        "- Stability: `src/distance/benchmarks/kitti_tracking/COMPARISON.md`",
        "- Speed: `src/distance/benchmarks/speed/results/`",
        "- Focal length sensitivity: `src/distance/benchmarks/focal_sensitivity/results/`",
        "",
    ]
    (HERE / "SUMMARY.md").write_text("\n".join(out))
    print(f"wrote {HERE / 'SUMMARY.md'} and summary.json")


if __name__ == "__main__":
    main()
