"""Benchmark distance estimation on Lost and Found obstacles.

Lost and Found shows real obstacles lying on the road (crates, tires, pallets,
dog and child dummies, ...), with stereo depth for every frame. KITTI cannot
test this: it has no obstacles, and known size cannot measure an obstacle at
all (there is no typical height for "debris"), so only ground plane and depth
models are candidates here.

Each estimator is given the obstacle's LABELLED outline, not a detection. That
measures distance quality alone: whether the detector would have found the
obstacle is a separate question, answered by the detection benchmark.

Ground truth: the median stereo depth inside the outline. Stereo depth gets
noisy far away, so the near bands are the trustworthy ones, and they are also
the range where the detector reliably finds obstacles (see
src/detection/benchmarks/lost_and_found/COMPARISON.md). Runs are therefore
ranked by accuracy under 20 m.

Metrics, per estimator, per distance band and obstacle group:
    coverage        share of obstacles the estimator gave an answer for.
    median error    typical absolute error in metres.
    mean abs error  MAE (Mean Absolute Error), in metres.
    relative error  average absolute error as a percentage of the true distance.
    within 10%      share of answers within 10% of the true distance.
    bias            average signed error; negative = estimates too close.

Output: one folder per run under results/ next to this file, each with
results.json (source of truth), obstacles.csv (one row per obstacle) and a
generated RESULTS.md; plus a generated, ranked COMPARISON.md.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_lost_and_found.py
    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\lost_and_found\\benchmark_laf_distance.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import gc
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Make the repo root importable. This file is at
# src/distance/benchmarks/lost_and_found/, four levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.detection.benchmarks.common import md_table, provenance
from src.detection.benchmarks.lost_and_found.benchmark_lost_and_found import (
    NON_HAZARD_LABELS,
    TYPES,
    disparity_to_depth,
    polygon_mask,
)
from src.detection.detector import Detection
from src.distance.camera import Camera
from src.distance.estimators import FallbackEstimator, GroundPlaneEstimator

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Dataset root, as written by scripts/download_lost_and_found.py.
DATA = Path("data/lost_and_found")

# The official test split scenes.
SCENES = [
    "02_Hanns_Klemm_Str_44",
    "04_Maurener_Weg_8",
    "05_Schafgasse_1",
    "07_Festplatz_Flugfeld",
    "15_Rechbergstr_Deckenpfronn",
]

# Runs to perform, in order, as (run name, estimator set, frame step: use every
# N-th frame of the 1203, 1 = all). "geometric" is
# ground plane plus the known-size / ground-plane combination (known size
# alone is omitted: it cannot measure obstacles). Any depth model name from
# src/distance/depth_models.py BACKENDS gives that model read three ways.
RUNS = [
    # Screening: every model on every 4th frame (about 300).
    ("geometric_n300", "geometric", 4),
    ("da2-metric-small_n300", "da2-metric-small", 4),
    ("da2-metric-base_n300", "da2-metric-base", 4),
    ("da2-metric-large_n300", "da2-metric-large", 4),
    ("da3-metric-large_n300", "da3-metric-large", 4),
    ("metric3d-v2-small_n300", "metric3d-v2-small", 4),
    ("metric3d-v2-large_n300", "metric3d-v2-large", 4),
    ("unidepth-v2-small_n300", "unidepth-v2-small", 4),
    ("unidepth-v2-base_n300", "unidepth-v2-base", 4),
    ("unidepth-v2-large_n300", "unidepth-v2-large", 4),
    ("depth-pro_n300", "depth-pro", 4),
    ("yolo26s-depth_n300", "yolo26s-depth", 4),
    # Finalists on all 1203 frames.
    ("geometric_full", "geometric", 1),
    ("metric3d-v2-small_full", "metric3d-v2-small", 1),
    ("metric3d-v2-large_full", "metric3d-v2-large", 1),
    ("unidepth-v2-base_full", "unidepth-v2-base", 1),
    ("unidepth-v2-large_full", "unidepth-v2-large", 1),
    ("metric3d-v2-small-fp16_full", "metric3d-v2-small-fp16", 1),
    ("metric3d-v2-large-fp16_full", "metric3d-v2-large-fp16", 1),
]

# Distance bands in metres, and the range runs are ranked by.
BANDS = [(0, 10), (10, 20), (20, 30), (30, 50), (50, 1000)]
RANK_RANGE_M = (0, 20)

# Where run folders are written: results/ next to this file.
OUT_DIR = Path(__file__).resolve().parent / "results"

# True: skip runs whose results.json already exists (resume a batch).
SKIP_EXISTING = True

# True: recompute every statistic from each run's obstacles.csv, no GPU.
RESCORE_ONLY = False

# True: only regenerate reports from existing results.json files.
REPORT_ONLY = False

# ----------------------------------------------------------------------------

# Stereo camera separation of the Lost and Found rig, in metres.
BASELINE_M = 0.222126


def estimator_set(name: str) -> list:
    if name == "geometric":
        return [GroundPlaneEstimator(), FallbackEstimator()]
    from src.distance.depth_models import depth_estimators

    return depth_estimators(name)


def band_name(lo: int, hi: int) -> str:
    return f"{lo}+ m" if hi >= 1000 else f"{lo}-{hi} m"


def band_of(d: float) -> str:
    for lo, hi in BANDS:
        if lo <= d < hi:
            return band_name(lo, hi)
    return "unknown"


def error_stats(rows: list[dict], method: str) -> dict:
    """Error statistics of one estimator over a set of obstacles."""
    answered = [r for r in rows if r[method] is not None]
    out = {"obstacles": len(rows), "answered": len(answered),
           "coverage": round(len(answered) / len(rows), 4) if rows else None}
    if not answered:
        return {**out, "median_abs_error_m": None, "mean_abs_error_m": None,
                "mean_rel_error": None, "within_10pct": None, "bias": None}
    true = np.array([r["true_m"] for r in answered])
    err = np.array([r[method] for r in answered]) - true
    rel = err / true
    return {
        **out,
        "median_abs_error_m": round(float(np.median(np.abs(err))), 2),
        "mean_abs_error_m": round(float(np.mean(np.abs(err))), 2),
        "mean_rel_error": round(float(np.mean(np.abs(rel))), 4),
        "within_10pct": round(float(np.mean(np.abs(rel) <= 0.10)), 4),
        "bias": round(float(np.mean(rel)), 4),
    }


def list_frames(step: int) -> list[Path]:
    frames = []
    for scene in SCENES:
        frames += sorted((DATA / "leftImg8bit" / "test" / scene).glob("*_leftImg8bit.png"))
    return frames[::step]


def outline_detection(polygon: list) -> Detection:
    """A labelled obstacle outline, presented to estimators as if detected."""
    pts = np.asarray(polygon, dtype=np.float32)
    return Detection(x1=float(pts[:, 0].min()), y1=float(pts[:, 1].min()),
                     x2=float(pts[:, 0].max()), y2=float(pts[:, 1].max()),
                     class_id=-1, class_name="obstacle", confidence=1.0, mask=pts)


def run(frames: list[Path], run_name: str, estimators: list, frame_step: int) -> None:
    methods = [e.name for e in estimators]
    rows, skipped_no_depth = [], 0

    for i, path in enumerate(frames, 1):
        stem = path.name.replace("_leftImg8bit.png", "")
        scene = path.parent.name
        img = cv2.imread(str(path))
        camera = Camera.from_lost_and_found(DATA / "camera" / "test" / scene / f"{stem}_camera.json")
        labels = json.loads((DATA / "gtCoarse" / "test" / scene / f"{stem}_gtCoarse_polygons.json").read_text())
        stereo = disparity_to_depth(
            cv2.imread(str(DATA / "disparity" / "test" / scene / f"{stem}_disparity.png"), cv2.IMREAD_UNCHANGED),
            camera.fx, BASELINE_M,
        )

        objects, dets = [], []
        for obj in labels["objects"]:
            if obj["label"] not in TYPES or obj["label"] in NON_HAZARD_LABELS:
                continue
            truth = stereo[polygon_mask(obj["polygon"], img.shape[:2])]
            truth = truth[np.isfinite(truth)]
            if truth.size == 0:
                skipped_no_depth += 1
                continue
            objects.append((obj, float(np.median(truth))))
            dets.append(outline_detection(obj["polygon"]))

        estimates = {e.name: e.estimate(img, dets, camera) for e in estimators}
        for k, (obj, true_m) in enumerate(objects):
            obstacle_type, group = TYPES[obj["label"]]
            rows.append({
                "frame": stem,
                "label": obj["label"],
                "type": obstacle_type,
                "group": group,
                "box_height_px": round(dets[k].y2 - dets[k].y1, 1),
                "true_m": round(true_m, 2),
                **{m: (None if estimates[m][k] is None else round(estimates[m][k], 2)) for m in methods},
            })
        if i % 50 == 0 or i == len(frames):
            print(f"  {i}/{len(frames)} frames, {len(rows)} obstacles", flush=True)

    backends = {id(e.backend): e.backend for e in estimators if hasattr(e, "backend")}
    depth_model = None
    for b in backends.values():
        t = b.times_ms[1:] or b.times_ms
        depth_model = {"name": b.name, "uses_our_focal_length": b.uses_focal_length, "precision": b.precision,
                       "inference_ms_median": round(float(np.median(t)), 1),
                       "inference_ms_p95": round(float(np.percentile(t, 95)), 1)}
    results = build_results(rows, methods, len(frames), skipped_no_depth, provenance(), run_name,
                            depth_model, frame_step)
    save_run(results, rows)


def build_results(rows: list[dict], methods: list[str], n_frames: int, skipped: int, prov: dict,
                  run_name: str, depth_model: dict | None, frame_step: int) -> dict:
    band_order = [band_name(lo, hi) for lo, hi in BANDS]
    lo, hi = RANK_RANGE_M
    ranked = [r for r in rows if lo <= r["true_m"] < hi]
    groups = sorted({r["group"] for r in rows}, key=lambda g: -sum(r["group"] == g for r in rows))
    return {
        "benchmark": "lost_and_found_distance",
        "provenance": prov,
        "dataset": {
            "name": "Lost and Found",
            "source": "https://huggingface.co/datasets/kumuji/lost_and_found",
            "split": "test",
            "scenes": SCENES,
            "frames": n_frames,
            "frame_step": frame_step,
            "obstacles": len(rows),
            "obstacles_skipped_no_stereo_depth": skipped,
            "excluded_labels": "random non-hazards (30, 32, 33, 35-38), per the dataset definition",
            "ground_truth": "median stereo depth inside the labelled outline",
            "estimator_input": "the labelled outline (distance quality only, independent of detection)",
        },
        "config": {
            "run_name": run_name,
            "depth_model": depth_model,
            "estimators": methods,
            "distance_bands_m": BANDS,
            "rank_range_m": list(RANK_RANGE_M),
        },
        "methods": {
            m: {
                "overall": error_stats(rows, m),
                "rank_range": error_stats(ranked, m),
                "by_distance": {b: error_stats([r for r in rows if band_of(r["true_m"]) == b], m)
                                for b in band_order if any(band_of(r["true_m"]) == b for r in rows)},
                "by_group": {g: error_stats([r for r in rows if r["group"] == g], m) for g in groups},
            }
            for m in methods
        },
    }


def save_run(results: dict, rows: list[dict]) -> None:
    run_dir = OUT_DIR / results["config"]["run_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    with (run_dir / "obstacles.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(run_dir)
    lo, hi = RANK_RANGE_M
    for m in results["config"]["estimators"]:
        o = results["methods"][m]["rank_range"]
        print(f"  {m:>26}: {lo}-{hi} m within 10% {o['within_10pct'] or 0:.0%}, "
              f"median error {o['median_abs_error_m']} m, coverage {o['coverage'] or 0:.0%}")
    print(f"wrote {run_dir}")


def rescore(run_dir: Path) -> None:
    """Recompute all statistics of one run from its obstacles.csv. No GPU."""
    old = json.loads((run_dir / "results.json").read_text())
    methods = old["config"]["estimators"]
    with (run_dir / "obstacles.csv").open(newline="") as f:
        rows = [{**r, "true_m": float(r["true_m"]), "box_height_px": float(r["box_height_px"]),
                 **{m: (float(r[m]) if r[m] not in ("", "None") else None) for m in methods}}
                for r in csv.DictReader(f)]
    prov = {**old["provenance"], "rescored_utc": provenance()["created_utc"],
            "rescored_git_commit": provenance()["git_commit"]}
    results = build_results(rows, methods, old["dataset"]["frames"],
                            old["dataset"]["obstacles_skipped_no_stereo_depth"], prov,
                            old["config"]["run_name"], old["config"].get("depth_model"),
                            old["dataset"]["frame_step"])
    save_run(results, rows)


def fmt_pct(v) -> str:
    return "-" if v is None else f"{v:.0%}"


def fmt_bias(v) -> str:
    return "-" if v is None else f"{v:+.1%}"


def fmt_m(v) -> str:
    return "-" if v is None else f"{v:.2f}"


STAT_HEADER = ["Obstacles", "Coverage", "Median error (m)", "Mean error (m)", "Relative error", "Within 10%", "Bias"]


def stat_row(name: str, s: dict) -> list:
    return [name, s["obstacles"], fmt_pct(s["coverage"]), fmt_m(s["median_abs_error_m"]),
            fmt_m(s["mean_abs_error_m"]), fmt_pct(s["mean_rel_error"]), fmt_pct(s["within_10pct"]),
            fmt_bias(s["bias"])]


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""
    dm = cfg.get("depth_model")
    lo, hi = cfg["rank_range_m"]
    methods = cfg["estimators"]
    out = [
        f"# Lost and Found distance benchmark: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Estimators", ", ".join(f"`{m}`" for m in methods)],
            *([["Depth model", f"`{dm['name']}`, {'given' if dm['uses_our_focal_length'] else 'not given'} "
                               f"our focal length; inference {dm['inference_ms_median']} ms median, "
                               f"{dm['inference_ms_p95']} ms p95 per frame"]] if dm else []),
            ["Dataset", f"[{ds['name']}]({ds['source']}), {ds['split']} split, {len(ds['scenes'])} scenes"],
            ["Frames", f"{ds['frames']} (every {ds['frame_step']}th frame)"],
            ["Obstacles", f"{ds['obstacles']} ({ds['obstacles_skipped_no_stereo_depth']} skipped: no stereo depth)"],
            ["Excluded", ds["excluded_labels"]],
            ["Ground truth", ds["ground_truth"]],
            ["Estimator input", ds["estimator_input"]],
            ["Hardware", prov["gpu"]],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "- **Coverage**: share of obstacles the estimator answered for, rather than returning unknown.",
        "- **Median / mean error**: absolute distance error in metres (mean = MAE, Mean Absolute Error).",
        "- **Relative error**: average absolute error as a percentage of the true distance.",
        "- **Within 10%**: share of answers within 10% of the true distance.",
        "- **Bias**: average signed error; negative = estimates too close, positive = too far.",
        f"- **{lo} to {hi} m**: the range where the detector reliably finds obstacles, and where",
        "  stereo ground truth is most trustworthy. Runs are ranked by it.",
        "",
        f"## {lo} to {hi} m",
        "",
        *md_table(["Estimator", *STAT_HEADER], [stat_row(m, r["methods"][m]["rank_range"]) for m in methods]),
        "## All distances",
        "",
        *md_table(["Estimator", *STAT_HEADER], [stat_row(m, r["methods"][m]["overall"]) for m in methods]),
    ]
    for m in methods:
        mr = r["methods"][m]
        out += [f"## `{m}` by distance", "",
                *md_table(["Distance", *STAT_HEADER], [stat_row(b, s) for b, s in mr["by_distance"].items()]),
                f"## `{m}` by obstacle group", "",
                *md_table(["Group", *STAT_HEADER], [stat_row(g, s) for g, s in mr["by_group"].items()])]
    out += [
        "## Known limitations",
        "",
        "- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.",
        "- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.",
        "- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


def write_comparison() -> None:
    """Generate COMPARISON.md: every (run, estimator), ranked by accuracy under 20 m."""
    runs = {p.name: json.loads((p / "results.json").read_text())
            for p in sorted(OUT_DIR.iterdir()) if (p / "results.json").exists()}
    if not runs:
        return
    band_names = [band_name(lo, hi) for lo, hi in BANDS]
    lo, hi = RANK_RANGE_M
    rows = []
    for run, r in runs.items():
        dm = r["config"].get("depth_model") or {}
        for m in r["config"]["estimators"]:
            node = r["methods"][m]
            rows.append((node["rank_range"]["within_10pct"] or 0.0, [
                f"`{run}`", f"`{m}`", r["dataset"]["frames"], fmt_pct(node["overall"]["coverage"]),
                fmt_pct(node["rank_range"]["within_10pct"]), fmt_m(node["rank_range"]["median_abs_error_m"]),
                *[fmt_pct((node["by_distance"].get(b) or {}).get("within_10pct")) for b in band_names],
                fmt_pct(node["overall"]["within_10pct"]), dm.get("inference_ms_median", "-"),
            ]))
    rows.sort(key=lambda x: -x[0])
    header = ["Rank", "Run", "Estimator", "Frames", "Coverage", f"Within 10%, {lo}-{hi} m",
              f"Median error (m), {lo}-{hi} m", *[f"Within 10%, {b}" for b in band_names],
              "Within 10%, all", "Depth model ms"]
    out = [
        "# Lost and Found distance benchmark: comparison",
        "",
        "Generated automatically from every `results/<run>/results.json` by `benchmark_laf_distance.py`. "
        "Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.",
        "",
        f"Ranked by **within 10%, {lo} to {hi} m**: obstacles whose estimated distance is within 10% of",
        "the stereo ground truth, in the range where the detector reliably finds them. `_median`,",
        "`_p10`, `_p25` mark how a depth model's per-pixel depth inside the outline is summarised.",
        "",
        *md_table(header, [[i, *row] for i, (_, row) in enumerate(rows, 1)]),
    ]
    path = OUT_DIR.parent / "COMPARISON.md"
    path.write_text("\n".join(out))
    print(f"regenerated {path}")


def main() -> None:
    if RESCORE_ONLY:
        for run_dir in sorted(p for p in OUT_DIR.iterdir() if (p / "obstacles.csv").exists()):
            rescore(run_dir)
        write_comparison()
        return
    if REPORT_ONLY:
        for run_dir in sorted(p for p in OUT_DIR.iterdir() if (p / "results.json").exists()):
            write_report(run_dir)
        write_comparison()
        return

    import torch

    for run_name, set_name, frame_step in RUNS:
        if SKIP_EXISTING and (OUT_DIR / run_name / "results.json").exists():
            print(f"=== {run_name}: already done, skipped ===")
            continue
        frames = list_frames(frame_step)
        print(f"=== {run_name} ({len(frames)} frames) ===", flush=True)
        t0 = time.perf_counter()
        estimators = estimator_set(set_name)
        run(frames, run_name, estimators, frame_step)
        estimators = None
        gc.collect()
        torch.cuda.empty_cache()
        write_comparison()
        print(f"  took {time.perf_counter() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
