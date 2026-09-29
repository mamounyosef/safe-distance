"""Benchmark how STABLE each distance method is over time, on KITTI tracking.

Accuracy benchmarks judge every frame on its own. But the next stage computes
closing speed from the CHANGE in distance between frames, so a method that is
accurate yet jumpy creates fake speed, a wrong Time To Collision (TTC) and
phantom braking. This benchmark measures that wobble.

KITTI tracking labels every car, van, pedestrian and cyclist with a fixed ID
and a laser-measured 3D box in every frame of 21 continuous sequences. Each
real object is followed through time by its labelled ID (matched to the
detector's box in each frame), so this measures the distance method's
stability alone, not tracking mistakes.

Metrics, per method (a pair = the same object in two frames):
    jitter        |change in estimate - true change| between consecutive
                  frames, in metres and as a percentage of the distance.
                  0 = the estimate moves exactly as the object really does.
    speed error   |speed from the estimates - true speed|, in metres per
                  second, over a window of W frames. W = 1 is raw frame-to-
                  frame speed; W = 5 (half a second at 10 fps) is closer to
                  what a smoothed TTC stage would use.
    within 10%    per-frame accuracy on this dataset, as a cross-check.

Every observation is saved (observations.csv), so any statistic, window or
combination can be recomputed later without a GPU.

Output: one folder per run under results/ next to this file, each with
results.json (source of truth), observations.csv and a generated RESULTS.md;
plus a generated, ranked COMPARISON.md.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_kitti_tracking.py
    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\kitti_tracking\\benchmark_distance_stability.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import gc
import json
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src/distance/benchmarks/kitti"))

from benchmark_kitti_distance import (  # same geometry and matching as the KITTI accuracy benchmark
    BANDS, band_name, band_of, estimator_set, label_geometry, match,
)
from src.detection.benchmarks.common import md_table, provenance
from src.detection.detector import Detector
from src.distance.camera import Camera

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

DATA = REPO / "data/kitti_tracking/training"

# Use the first this-many frames of every sequence (all 21). 150 frames is
# 15 seconds per sequence, about 3150 frames in total: every scene, at a
# sensible cost. 0 = every frame (8008).
FRAMES_PER_SEQUENCE = 150

# Runs, as (run name, estimator set, as in the KITTI distance benchmark).
RUNS = [
    ("geometric_f150", "geometric"),
    ("metric3d-v2-small-fp16_f150", "metric3d-v2-small-fp16"),
    ("metric3d-v2-large-fp16_f150", "metric3d-v2-large-fp16"),
    ("unidepth-v2-base_f150", "unidepth-v2-base"),
    ("unidepth-v2-large_f150", "unidepth-v2-large"),
]

# Detector settings, same as the KITTI distance benchmark.
WEIGHTS = "weights/yolo26s-seg.pt"
IMGSZ = 1280
CONF = 0.25

# KITTI's camera: 1.65 m above the road, level; recorded at 10 frames per second.
CAMERA_HEIGHT_M = 1.65
FPS = 10.0

# Speed windows, in frames.
SPEED_WINDOWS = [1, 5, 10, 20]

# In-path corridor, same as the accuracy benchmarks.
CORRIDOR_HALF_WIDTH_M = 1.2

OUT_DIR = Path(__file__).resolve().parent / "results"
SKIP_EXISTING = True
RESCORE_ONLY = False

# ----------------------------------------------------------------------------

# KITTI tracking label types scored, and the class names used in the tables.
CLASSES = {"Car": "car", "Van": "van", "Truck": "truck", "Pedestrian": "pedestrian",
           "Person": "pedestrian", "Cyclist": "cyclist", "Tram": "tram"}
TRUTH = "true_nearest_surface_m"


def read_labels(path: Path) -> dict[int, list[dict]]:
    """KITTI tracking labels by frame, with true distances from the 3D boxes.

    A tracking label line is an object label line with two extra leading
    fields (frame, track ID), so the object-label geometry is reused on f[2:].
    """
    frames: dict[int, list[dict]] = defaultdict(list)
    for line in path.read_text().splitlines():
        f = line.split()
        if len(f) < 17 or f[2] not in CLASSES:
            continue
        geo = label_geometry(f[2:])
        frames[int(f[0])].append({
            "track_id": int(f[1]),
            "type": f[2],
            "box": tuple(float(v) for v in f[6:10]),
            **geo,
        })
    return frames


def run(run_name: str, estimators: list) -> None:
    detector = Detector(weights=WEIGHTS, conf=CONF, imgsz=IMGSZ)
    methods = [e.name for e in estimators]
    rows, n_frames = [], 0
    sequences = sorted(p.name for p in (DATA / "image_02").iterdir() if p.is_dir())
    for seq in sequences:
        labels = read_labels(DATA / "label_02" / f"{seq}.txt")
        camera = Camera.from_kitti_calib(DATA / "calib" / f"{seq}.txt", height_m=CAMERA_HEIGHT_M)
        frames = sorted((DATA / "image_02" / seq).glob("*.png"))
        if FRAMES_PER_SEQUENCE:
            frames = frames[:FRAMES_PER_SEQUENCE]
        for path in frames:
            frame_no = int(path.stem)
            gt = labels.get(frame_no, [])
            img = cv2.imread(str(path))
            dets = detector.detect(img)
            estimates = {e.name: e.estimate(img, dets, camera) for e in estimators}
            for gi, bi in match(gt, [(d.x1, d.y1, d.x2, d.y2) for d in dets]).items():
                g = gt[gi]
                rows.append({
                    "sequence": seq,
                    "frame": frame_no,
                    "track_id": g["track_id"],
                    "class": CLASSES[g["type"]],
                    "true_centre_m": round(g["true_centre_m"], 3),
                    "true_nearest_surface_m": round(g["true_nearest_surface_m"], 3),
                    "lateral_gap_m": round(g["lateral_gap_m"], 3),
                    **{m: (None if estimates[m][bi] is None else round(estimates[m][bi], 3)) for m in methods},
                })
            n_frames += 1
        print(f"  sequence {seq}: {len(frames)} frames, {len(rows)} observations so far", flush=True)

    backends = {id(e.backend): e.backend for e in estimators if hasattr(e, "backend")}
    depth_model = None
    for b in backends.values():
        t = b.times_ms[1:] or b.times_ms
        depth_model = {"name": b.name, "uses_our_focal_length": b.uses_focal_length, "precision": b.precision,
                       "inference_ms_median": round(float(np.median(t)), 1)}
    save_run(build_results(rows, methods, n_frames, len(sequences), provenance(), run_name, depth_model), rows)


def pairs(rows: list[dict], method: str, window: int) -> list[tuple[dict, dict]]:
    """(earlier, later) observations of the same object, `window` frames apart,
    both with an estimate."""
    by_track = defaultdict(dict)
    for r in rows:
        if r[method] is not None:
            by_track[(r["sequence"], r["track_id"])][r["frame"]] = r
    out = []
    for obs in by_track.values():
        for f, later in obs.items():
            earlier = obs.get(f - window)
            if earlier is not None:
                out.append((earlier, later))
    return out


def stability_stats(rows: list[dict], method: str) -> dict:
    """Jitter, speed errors and per-frame accuracy of one method."""
    out = {"observations": len(rows)}
    answered = [r for r in rows if r[method] is not None and r[TRUTH] > 0]
    if answered:
        true = np.array([r[TRUTH] for r in answered])
        est = np.array([r[method] for r in answered])
        out["within_10pct"] = round(float(np.mean(np.abs(est - true) / true <= 0.10)), 4)
    else:
        out["within_10pct"] = None

    p1 = [(a, b) for a, b in pairs(rows, method, 1) if b[TRUTH] > 0]
    out["pairs"] = len(p1)
    if p1:
        jitter = np.array([abs((b[method] - a[method]) - (b[TRUTH] - a[TRUTH])) for a, b in p1])
        rel = jitter / np.array([b[TRUTH] for _, b in p1])
        out.update({
            "jitter_median_m": round(float(np.median(jitter)), 3),
            "jitter_p90_m": round(float(np.percentile(jitter, 90)), 3),
            "jitter_median_pct": round(float(np.median(rel)), 4),
            "jitter_p90_pct": round(float(np.percentile(rel, 90)), 4),
        })
    else:
        out.update({"jitter_median_m": None, "jitter_p90_m": None, "jitter_median_pct": None, "jitter_p90_pct": None})

    for w in SPEED_WINDOWS:
        pw = pairs(rows, method, w)
        if pw:
            dt = w / FPS
            err = np.array([abs((b[method] - a[method]) / dt - (b[TRUTH] - a[TRUTH]) / dt) for a, b in pw])
            out[f"speed_error_w{w}_median_mps"] = round(float(np.median(err)), 3)
            out[f"speed_error_w{w}_p90_mps"] = round(float(np.percentile(err, 90)), 3)
        else:
            out[f"speed_error_w{w}_median_mps"] = out[f"speed_error_w{w}_p90_mps"] = None
    return out


def build_results(rows: list[dict], methods: list[str], n_frames: int, n_sequences: int, prov: dict,
                  run_name: str, depth_model: dict | None) -> dict:
    for r in rows:
        r["in_path"] = r["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M
    in_path = [r for r in rows if r["in_path"]]
    classes = sorted({r["class"] for r in rows}, key=lambda c: -sum(r["class"] == c for r in rows))

    def by_band(subset, m):
        out = {}
        for lo, hi in BANDS:
            b = band_name(lo, hi)
            s = [r for r in subset if band_of(r[TRUTH]) == b]
            if s:
                out[b] = stability_stats(s, m)
        return out

    return {
        "benchmark": "kitti_tracking_distance_stability",
        "provenance": prov,
        "dataset": {
            "name": "KITTI Tracking",
            "source": "https://www.cvlibs.net/datasets/kitti/eval_tracking.php",
            "split": "training (public labels)",
            "sequences": n_sequences,
            "frames": n_frames,
            "frames_per_sequence": FRAMES_PER_SEQUENCE,
            "fps": FPS,
            "observations": len(rows),
            "tracks": len({(r["sequence"], r["track_id"]) for r in rows}),
            "ground_truth": "laser-measured 3D boxes, distance to the nearest surface of the footprint",
            "association": "each labelled object followed by its labelled track ID; detections matched per frame",
        },
        "config": {
            "run_name": run_name,
            "depth_model": depth_model,
            "weights": WEIGHTS,
            "imgsz": IMGSZ,
            "conf": CONF,
            "camera_height_m": CAMERA_HEIGHT_M,
            "speed_windows_frames": SPEED_WINDOWS,
            "corridor_half_width_m": CORRIDOR_HALF_WIDTH_M,
            "estimators": methods,
            "distance_bands_m": BANDS,
        },
        "methods": {
            m: {
                "overall": stability_stats(rows, m),
                "in_path": stability_stats(in_path, m),
                "in_path_by_distance": by_band(in_path, m),
                "by_class": {c: stability_stats([r for r in rows if r["class"] == c], m) for c in classes},
            }
            for m in methods
        },
    }


def save_run(results: dict, rows: list[dict]) -> None:
    run_dir = OUT_DIR / results["config"]["run_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    with (run_dir / "observations.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(run_dir)
    for m in results["config"]["estimators"]:
        o = results["methods"][m]["in_path"]
        print(f"  {m:>26}: in path jitter {o['jitter_median_pct'] or 0:.1%} median, "
              f"speed error w1 {o['speed_error_w1_median_mps']} m/s, w5 {o['speed_error_w5_median_mps']} m/s, "
              f"within 10% {o['within_10pct'] or 0:.0%}")
    print(f"wrote {run_dir}")


def rescore(run_dir: Path) -> None:
    """Recompute all statistics of one run from observations.csv. No GPU."""
    old = json.loads((run_dir / "results.json").read_text())
    methods = old["config"]["estimators"]
    num = ("true_centre_m", "true_nearest_surface_m", "lateral_gap_m")
    with (run_dir / "observations.csv").open(newline="") as f:
        rows = [{**r, "frame": int(r["frame"]), "track_id": int(r["track_id"]), **{k: float(r[k]) for k in num},
                 **{m: (float(r[m]) if r[m] not in ("", "None") else None) for m in methods}}
                for r in csv.DictReader(f)]
    prov = {**old["provenance"], "rescored_utc": provenance()["created_utc"],
            "rescored_git_commit": provenance()["git_commit"]}
    save_run(build_results(rows, methods, old["dataset"]["frames"], old["dataset"]["sequences"], prov,
                           old["config"]["run_name"], old["config"].get("depth_model")), rows)


def fmt(v, kind: str) -> str:
    if v is None:
        return "-"
    return {"pct": f"{v:.1%}", "pct0": f"{v:.0%}", "m": f"{v:.2f}", "mps": f"{v:.2f}"}[kind]


STAB_HEADER = ["Observations", "Pairs", "Jitter median", "Jitter p90", "Jitter median (m)",
               "Speed error, 1 frame (m/s)", "Speed error, 5 frames (m/s)", "Within 10%"]


def stab_row(name: str, s: dict) -> list:
    return [name, s["observations"], s.get("pairs", "-"), fmt(s.get("jitter_median_pct"), "pct"),
            fmt(s.get("jitter_p90_pct"), "pct"), fmt(s.get("jitter_median_m"), "m"),
            fmt(s.get("speed_error_w1_median_mps"), "mps"), fmt(s.get("speed_error_w5_median_mps"), "mps"),
            fmt(s.get("within_10pct"), "pct0")]


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""
    dm = cfg.get("depth_model")
    methods = cfg["estimators"]
    out = [
        f"# Distance stability benchmark (KITTI tracking): `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_distance_stability.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Detector", f"`{cfg['weights']}`, input size {cfg['imgsz']}, confidence {cfg['conf']}"],
            ["Estimators", ", ".join(f"`{m}`" for m in methods)],
            *([["Depth model", f"`{dm['name']}`, precision {dm.get('precision', '-')}, "
                               f"{'given' if dm['uses_our_focal_length'] else 'not given'} our focal length"]] if dm else []),
            ["Dataset", f"[{ds['name']}]({ds['source']}), {ds['split']}"],
            ["Frames", f"{ds['frames']}: first {ds['frames_per_sequence']} of each of {ds['sequences']} sequences, {ds['fps']:.0f} fps"],
            ["Objects", f"{ds['observations']} observations of {ds['tracks']} tracked objects"],
            ["Ground truth", ds["ground_truth"]],
            ["Association", ds["association"]],
            ["Hardware", prov["gpu"]],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "- **Jitter**: |change in estimate - true change| between consecutive frames, as a percentage",
        "  of the distance (and in metres). 0 means the estimate moves exactly like the real object.",
        "- **Speed error**: |speed from estimates - true speed| in m/s, from distances 1 frame (0.1 s)",
        "  or 5 frames (0.5 s) apart. This is the error the Time To Collision stage would inherit.",
        "- **Within 10%**: per-frame accuracy on this dataset, as a cross-check.",
        "",
        "## In path",
        "",
        *md_table(["Estimator", *STAB_HEADER], [stab_row(m, r["methods"][m]["in_path"]) for m in methods]),
        "## All objects",
        "",
        *md_table(["Estimator", *STAB_HEADER], [stab_row(m, r["methods"][m]["overall"]) for m in methods]),
    ]
    for m in methods:
        node = r["methods"][m]
        out += [f"## `{m}` in path, by distance", "",
                *md_table(["Distance", *STAB_HEADER], [stab_row(b, s) for b, s in node["in_path_by_distance"].items()]),
                f"## `{m}` by class", "",
                *md_table(["Class", *STAB_HEADER], [stab_row(c, s) for c, s in node["by_class"].items()])]
    out += [
        "## Known limitations",
        "",
        "- The labels themselves are not perfectly steady frame to frame (each box is fitted to the laser",
        "  scan separately), so part of every method's measured jitter is label noise, a floor none can beat.",
        "- Objects are followed by their labelled ID; a real tracker's ID switches would add error on top.",
        "- First 150 frames of each sequence only.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


def write_comparison() -> None:
    runs = {p.name: json.loads((p / "results.json").read_text())
            for p in sorted(OUT_DIR.iterdir()) if (p / "results.json").exists()}
    if not runs:
        return
    rows = []
    for run, r in runs.items():
        for m in r["config"]["estimators"]:
            s = r["methods"][m]["in_path"]
            rows.append((s.get("speed_error_w5_median_mps") or 1e9, [
                f"`{run}`", f"`{m}`", fmt(s.get("jitter_median_pct"), "pct"), fmt(s.get("jitter_p90_pct"), "pct"),
                fmt(s.get("speed_error_w1_median_mps"), "mps"), fmt(s.get("speed_error_w1_p90_mps"), "mps"),
                fmt(s.get("speed_error_w5_median_mps"), "mps"), fmt(s.get("speed_error_w5_p90_mps"), "mps"),
                fmt(s.get("within_10pct"), "pct0"), s.get("pairs", "-"),
            ]))
    rows.sort(key=lambda x: x[0])
    out = [
        "# Distance stability benchmark (KITTI tracking): comparison",
        "",
        "Generated automatically from every `results/<run>/results.json` by `benchmark_distance_stability.py`. "
        "Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.",
        "",
        "In-path objects. Ranked by **speed error over 5 frames (0.5 s)**, lowest first: the error in",
        "closing speed that the Time To Collision stage would inherit.",
        "",
        *md_table(["Rank", "Run", "Estimator", "Jitter median", "Jitter p90", "Speed error 1 frame, median (m/s)",
                   "1 frame, p90", "Speed error 5 frames, median (m/s)", "5 frames, p90", "Within 10%", "Pairs"],
                  [[i, *row] for i, (_, row) in enumerate(rows, 1)]),
    ]
    path = OUT_DIR.parent / "COMPARISON.md"
    path.write_text("\n".join(out))
    print(f"regenerated {path}")


def main() -> None:
    if RESCORE_ONLY:
        for run_dir in sorted(p for p in OUT_DIR.iterdir() if (p / "observations.csv").exists()):
            rescore(run_dir)
        write_comparison()
        return

    import torch

    for run_name, set_name in RUNS:
        if SKIP_EXISTING and (OUT_DIR / run_name / "results.json").exists():
            print(f"=== {run_name}: already done, skipped ===")
            continue
        print(f"=== {run_name} ===", flush=True)
        estimators = estimator_set(set_name)
        run(run_name, estimators)
        estimators = None
        gc.collect()
        torch.cuda.empty_cache()
        write_comparison()


if __name__ == "__main__":
    main()
