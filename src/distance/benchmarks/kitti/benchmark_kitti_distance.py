"""Benchmark distance estimation on KITTI, against laser-measured distances.

Every labelled vehicle, pedestrian and cyclist in KITTI has a 3D position
measured by a laser scanner, accurate to a few centimetres. This runs the
detector, matches each real object to its detection, asks every distance
estimator for a distance, and compares it to the laser distance.

Metrics, per estimator, per class and per distance band:
    coverage        share of objects the estimator gave an answer for, rather
                    than "unknown". Low coverage is safe but less useful.
    median error    typical error in metres, half are better, half worse.
    mean abs error  average error in metres (MAE, Mean Absolute Error).
    relative error  average error as a percentage of the true distance.
    within 10%      share of answers within 10% of the true distance.
    bias            average signed error as a percentage: negative means the
                    estimator systematically says objects are CLOSER than they
                    are, positive FARTHER. Bias is correctable; spread is not.

Output: one folder per run under results/ next to this file, each with
results.json (source of truth), objects.csv (one row per object) and a
generated RESULTS.md; plus a generated COMPARISON.md across all runs.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_kitti.py
    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\kitti\\benchmark_kitti_distance.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Make the repo root importable, so "src" resolves when this file is run
# directly. This file is at src/distance/benchmarks/kitti/, four levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.detection.benchmarks.common import best_row, iou, md_table, pct, provenance
from src.detection.detector import Detector
from src.distance.camera import Camera
from src.distance.estimators import GroundPlaneEstimator, KnownSizeEstimator

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Dataset root and image subset, as written by scripts/download_kitti.py.
DATA = Path("data/kitti")
SUBSET = DATA / "subset.txt"

# Run name: results are written to results/<RUN_NAME>/. Use a new name when
# changing an estimator or a setting, so earlier results stay for comparison.
RUN_NAME = "yolo26s-seg_geometric-v1"

# Detector settings. Only detections matched to a real object are scored, so
# the confidence threshold mostly decides which objects get matched at all.
WEIGHTS = "weights/yolo26s-seg.pt"
IMGSZ = 1280
CONF = 0.25

# KITTI's camera mounting, from the dataset paper: 1.65 m above the road, level.
CAMERA_HEIGHT_M = 1.65
CAMERA_PITCH_RAD = 0.0

# A detection matches a real object if their IoU (Intersection over Union)
# is at least this. Each detection matches at most one object.
MIN_IOU = 0.5

# The driving corridor for "in path" results: an object is in our path if its
# footprint on the road comes within this many metres of our car's centre
# line, left or right: the objects we could actually hit head-on.
# 1.2 m = half our car's width (about 0.9 m) plus a 0.3 m margin. A first
# try with 1.75 m (half a lane) wrongly caught cars in the next lane driving
# alongside us: nearly out of view, nearest surface beside our own car.
CORRIDOR_HALF_WIDTH_M = 1.2

# Distance bands in metres.
BANDS = [(0, 10), (10, 20), (20, 30), (30, 50), (50, 1000)]

# Stop after this many images. 0 = the whole subset.
MAX_IMAGES = 0

# Where run folders are written: results/ next to this file.
OUT_DIR = Path(__file__).resolve().parent / "results"

# True: skip inference and only regenerate reports from existing results.json.
REPORT_ONLY = False

# True: skip the detector and recompute every statistic of RUN_NAME from its
# saved objects.csv plus the label files. For when only the scoring changes,
# not the detector or the estimators. Takes seconds and no GPU.
RESCORE_ONLY = False

# ----------------------------------------------------------------------------

# KITTI label types scored, and the class names used in the tables.
CLASSES = {
    "Car": "car",
    "Van": "van",
    "Truck": "truck",
    "Pedestrian": "pedestrian",
    "Person_sitting": "pedestrian",
    "Cyclist": "cyclist",
}

ESTIMATORS = [GroundPlaneEstimator(), KnownSizeEstimator()]

# Two definitions of the true distance, both scored:
#   centre           to the middle of the object, as KITTI records it.
#   nearest_surface  to the closest point of the object's footprint on the
#                    road, e.g. the rear bumper of the car ahead. This is the
#                    gap that matters for braking.
TRUTHS = ["nearest_surface", "centre"]


def footprint_corners(x: float, z: float, width: float, length: float,
                      rotation_y: float) -> list[tuple[float, float]]:
    """The four corners of an object's footprint on the road, as (x, z) points.

    KITTI gives each object's bottom-centre position (x to the right, z ahead),
    its width and length, and its heading rotation_y around the vertical axis.
    Corners are built in the object's own frame (length along its heading) and
    rotated into camera coordinates exactly as in the KITTI development kit.
    """
    c, s = math.cos(rotation_y), math.sin(rotation_y)
    local = [(length / 2, width / 2), (length / 2, -width / 2),
             (-length / 2, -width / 2), (-length / 2, width / 2)]
    return [(x + c * lx + s * lz, z - s * lx + c * lz) for lx, lz in local]


def lateral_gap(corners: list[tuple[float, float]]) -> float:
    """How far to the side of our car's centre line the footprint's nearest
    edge is, in metres. 0 if the footprint straddles the centre line."""
    xs = [cx for cx, _ in corners]
    if min(xs) <= 0.0 <= max(xs):
        return 0.0
    return min(abs(min(xs)), abs(max(xs)))


def label_geometry(f: list[str]) -> dict:
    """True distances and sideways gap of one KITTI label line.

    Label fields: 8-10 height, width, length; 11-13 position x, y, z;
    14 heading around the vertical axis.
    """
    width, length = float(f[9]), float(f[10])
    x, z, rotation_y = float(f[11]), float(f[13]), float(f[14])
    corners = footprint_corners(x, z, width, length, rotation_y)
    return {
        "true_centre_m": math.hypot(x, z),
        "true_nearest_surface_m": nearest_surface_distance(x, z, width, length, rotation_y),
        "lateral_gap_m": lateral_gap(corners),
    }


def nearest_surface_distance(x: float, z: float, width: float, length: float, rotation_y: float) -> float:
    """Ground distance from the camera to the nearest point of an object's footprint.

    The footprint is the object's rectangle on the road (see footprint_corners);
    the answer is the distance from the camera (the origin) to its closest
    edge, or 0 if the camera is inside it.
    """
    corners = footprint_corners(x, z, width, length, rotation_y)

    def to_segment(ax, az, bx, bz):
        dx, dz = bx - ax, bz - az
        t = max(0.0, min(1.0, -(ax * dx + az * dz) / (dx * dx + dz * dz)))
        return math.hypot(ax + t * dx, az + t * dz)

    # Inside test: the origin is on the same side of all four edges.
    signs = [
        (bx - ax) * (0 - az) - (bz - az) * (0 - ax)
        for (ax, az), (bx, bz) in zip(corners, corners[1:] + corners[:1])
    ]
    if all(v >= 0 for v in signs) or all(v <= 0 for v in signs):
        return 0.0
    return min(to_segment(ax, az, bx, bz)
               for (ax, az), (bx, bz) in zip(corners, corners[1:] + corners[:1]))


def band_name(lo: int, hi: int) -> str:
    return f"{lo}+ m" if hi >= 1000 else f"{lo}-{hi} m"


def band_of(distance: float) -> str:
    for lo, hi in BANDS:
        if lo <= distance < hi:
            return band_name(lo, hi)
    return "unknown"


def error_stats(rows: list[dict], method: str, truth: str) -> dict:
    """Error statistics of one estimator over a set of objects, against one truth."""
    answered = [r for r in rows if r[method] is not None and r[f"true_{truth}_m"] > 0]
    out = {"objects": len(rows), "answered": len(answered),
           "coverage": round(len(answered) / len(rows), 4) if rows else None}
    if not answered:
        return {**out, "median_abs_error_m": None, "mean_abs_error_m": None,
                "mean_rel_error": None, "within_10pct": None, "bias": None}
    true = np.array([r[f"true_{truth}_m"] for r in answered])
    est = np.array([r[method] for r in answered])
    err = est - true
    rel = err / true
    return {
        **out,
        "median_abs_error_m": round(float(np.median(np.abs(err))), 2),
        "mean_abs_error_m": round(float(np.mean(np.abs(err))), 2),
        "mean_rel_error": round(float(np.mean(np.abs(rel))), 4),
        "within_10pct": round(float(np.mean(np.abs(rel) <= 0.10)), 4),
        "bias": round(float(np.mean(rel)), 4),
    }


def match(labels: list[dict], boxes: list[tuple]) -> dict[int, int]:
    """Greedy one-to-one matching of labelled objects to detections by IoU."""
    pairs = sorted(
        ((iou(g["box"], b), gi, bi) for gi, g in enumerate(labels) for bi, b in enumerate(boxes)),
        reverse=True,
    )
    used_g, used_b, out = set(), set(), {}
    for o, gi, bi in pairs:
        if o < MIN_IOU:
            break
        if gi not in used_g and bi not in used_b:
            out[gi] = bi
            used_g.add(gi)
            used_b.add(bi)
    return out


def run(ids: list[str]) -> None:
    detector = Detector(weights=WEIGHTS, conf=CONF, imgsz=IMGSZ)
    methods = [e.name for e in ESTIMATORS]
    rows = []
    total_objects = 0
    times = {m: [] for m in methods}

    for i, image_id in enumerate(ids, 1):
        img = cv2.imread(str(DATA / "training" / "image_2" / f"{image_id}.png"))
        camera = Camera.from_kitti_calib(
            DATA / "training" / "calib" / f"{image_id}.txt",
            height_m=CAMERA_HEIGHT_M, pitch_rad=CAMERA_PITCH_RAD,
        )
        labels = []
        for line in (DATA / "training" / "label_2" / f"{image_id}.txt").read_text().splitlines():
            f = line.split()
            if f and f[0] in CLASSES:
                labels.append({
                    "type": f[0],
                    "box": tuple(float(v) for v in f[4:8]),
                    "occluded": int(f[2]),
                    "truncated": float(f[1]),
                    **label_geometry(f),
                })
        total_objects += len(labels)

        dets = detector.detect(img)
        estimates = {}
        for e in ESTIMATORS:
            t0 = time.perf_counter()
            estimates[e.name] = e.estimate(img, dets, camera)
            times[e.name].append((time.perf_counter() - t0) * 1000.0)

        for gi, bi in match(labels, [(d.x1, d.y1, d.x2, d.y2) for d in dets]).items():
            g, d = labels[gi], dets[bi]
            rows.append({
                "image": image_id,
                "type": g["type"],
                "class": CLASSES[g["type"]],
                "predicted_class": d.class_name,
                "occluded": g["occluded"],
                "truncated": g["truncated"],
                "box_height_px": round(g["box"][3] - g["box"][1], 1),
                "true_centre_m": round(g["true_centre_m"], 2),
                "true_nearest_surface_m": round(g["true_nearest_surface_m"], 2),
                "lateral_gap_m": round(g["lateral_gap_m"], 2),
                **{m: (None if estimates[m][bi] is None else round(estimates[m][bi], 2)) for m in methods},
            })

        if i % 250 == 0 or i == len(ids):
            print(f"  {i}/{len(ids)} images, {len(rows)} objects matched", flush=True)

    latency = {m: round(float(np.median(t)), 3) for m, t in times.items()}
    results = build_results(rows, methods, len(ids), total_objects, latency, provenance())
    save_run(results, rows)


def by_distance(rows: list[dict], method: str, truth: str) -> dict:
    """Error statistics per distance band. Bands use the same truth as the errors."""
    out = {}
    for lo, hi in BANDS:
        b = band_name(lo, hi)
        subset = [r for r in rows if band_of(r[f"true_{truth}_m"]) == b]
        if subset:
            out[b] = error_stats(subset, method, truth)
    return out


def build_results(rows: list[dict], methods: list[str], n_images: int, total_objects: int,
                  latency: dict, prov: dict) -> dict:
    """Every statistic, from the per-object rows. Shared by run and rescore."""
    for r in rows:
        r["in_path"] = r["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M
    in_path = [r for r in rows if r["in_path"]]
    beside = [r for r in rows if not r["in_path"]]
    classes = sorted({r["class"] for r in rows}, key=lambda c: -sum(r["class"] == c for r in rows))
    return {
        "benchmark": "kitti_distance",
        "provenance": prov,
        "dataset": {
            "name": "KITTI Object Detection",
            "source": "https://www.cvlibs.net/datasets/kitti/eval_object.php",
            "split": "training (public labels)",
            "images": n_images,
            "subset": f"{SUBSET.as_posix()} (random, fixed seed, see scripts/download_kitti.py)",
            "labelled_objects": total_objects,
            "matched_objects": len(rows),
            "in_path_objects": len(in_path),
            "distance_source": "laser-measured 3D boxes",
        },
        "config": {
            "run_name": RUN_NAME,
            "weights": WEIGHTS,
            "imgsz": IMGSZ,
            "conf": CONF,
            "camera_height_m": CAMERA_HEIGHT_M,
            "camera_pitch_rad": CAMERA_PITCH_RAD,
            "min_iou": MIN_IOU,
            "corridor_half_width_m": CORRIDOR_HALF_WIDTH_M,
            "estimators": methods,
            "distance_bands_m": BANDS,
        },
        "estimator_latency_ms_per_image": latency,
        # methods[estimator][truth] -> all objects, in-path only, and beside
        # the path; each overall and by distance, plus all objects by class.
        "methods": {
            m: {
                t: {
                    "overall": error_stats(rows, m, t),
                    "by_distance": by_distance(rows, m, t),
                    "by_class": {c: error_stats([r for r in rows if r["class"] == c], m, t) for c in classes},
                    "in_path": {"overall": error_stats(in_path, m, t), "by_distance": by_distance(in_path, m, t)},
                    "beside": {"overall": error_stats(beside, m, t), "by_distance": by_distance(beside, m, t)},
                }
                for t in TRUTHS
            }
            for m in methods
        },
    }


def save_run(results: dict, rows: list[dict]) -> None:
    run_dir = OUT_DIR / RUN_NAME
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    with (run_dir / "objects.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(run_dir)

    methods = results["config"]["estimators"]
    for t in TRUTHS:
        for scope in ("all", "in_path"):
            for m in methods:
                node = results["methods"][m][t]
                o = node["overall"] if scope == "all" else node["in_path"]["overall"]
                print(f"  vs {t:>15} | {scope:>7} | {m:>13}: median error {o['median_abs_error_m']} m, "
                      f"within 10% {o['within_10pct']:.0%}, bias {o['bias']:+.1%}")
    print(f"wrote {run_dir}")


def rescore() -> None:
    """Recompute all statistics of RUN_NAME from objects.csv and the labels.

    The detector and estimators are not run: their outputs are already in
    objects.csv. Geometry that is missing from an older objects.csv (such as
    the sideways gap) is recovered from the label files, by matching each row
    to its label line on object type and true centre distance.
    """
    run_dir = OUT_DIR / RUN_NAME
    old = json.loads((run_dir / "results.json").read_text())
    methods = old["config"]["estimators"]
    with (run_dir / "objects.csv").open(newline="") as f:
        raw = list(csv.DictReader(f))

    # Per image: (type, box height, occlusion, geometry) of every label line.
    geometry_cache: dict[str, list[tuple[str, float, int, dict]]] = {}
    rows = []
    for r in raw:
        image = r["image"]
        if image not in geometry_cache:
            lines = (DATA / "training" / "label_2" / f"{image}.txt").read_text().splitlines()
            geometry_cache[image] = [
                (f[0], float(f[7]) - float(f[5]), int(f[2]), label_geometry(f))
                for f in map(str.split, lines) if f and f[0] in CLASSES
            ]
        centre = float(r["true_centre_m"])
        candidates = [g for t, h, occ, g in geometry_cache[image]
                      if t == r["type"] and abs(g["true_centre_m"] - centre) < 0.006
                      and abs(h - float(r["box_height_px"])) < 0.06 and occ == int(r["occluded"])]
        if len(candidates) != 1:
            raise SystemExit(f"cannot uniquely match row to its label: image {image}, {r['type']} at {centre} m")
        g = candidates[0]
        rows.append({
            "image": image,
            "type": r["type"],
            "class": r["class"],
            "predicted_class": r["predicted_class"],
            "occluded": int(r["occluded"]),
            "truncated": float(r["truncated"]),
            "box_height_px": float(r["box_height_px"]),
            "true_centre_m": round(g["true_centre_m"], 2),
            "true_nearest_surface_m": round(g["true_nearest_surface_m"], 2),
            "lateral_gap_m": round(g["lateral_gap_m"], 2),
            **{m: (float(r[m]) if r[m] not in ("", "None") else None) for m in methods},
        })

    prov = {**old["provenance"], "rescored_utc": provenance()["created_utc"],
            "rescored_git_commit": provenance()["git_commit"]}
    results = build_results(rows, methods, old["dataset"]["images"], old["dataset"]["labelled_objects"],
                            old["estimator_latency_ms_per_image"], prov)
    save_run(results, rows)


def fmt_pct(v) -> str:
    return "-" if v is None else f"{v:.0%}"


def fmt_bias(v) -> str:
    return "-" if v is None else f"{v:+.1%}"


def fmt_m(v) -> str:
    return "-" if v is None else f"{v:.2f}"


def stat_rows(table: dict, order: list[str]) -> list[list]:
    return [
        [name, s["objects"], fmt_pct(s["coverage"]), fmt_m(s["median_abs_error_m"]),
         fmt_m(s["mean_abs_error_m"]), fmt_pct(s["mean_rel_error"]), fmt_pct(s["within_10pct"]),
         fmt_bias(s["bias"])]
        for name in order if name in table
        for s in [table[name]]
    ]


STAT_HEADER = ["Objects", "Coverage", "Median error (m)", "Mean error (m)",
               "Relative error", "Within 10%", "Bias"]


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""
    methods = cfg["estimators"]
    truths = list(r["methods"][methods[0]])

    out = [
        f"# KITTI distance benchmark: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Detector", f"`{cfg['weights']}`, input size {cfg['imgsz']}, confidence {cfg['conf']}"],
            ["Estimators", ", ".join(f"`{m}`" for m in methods)],
            ["Camera", f"height {cfg['camera_height_m']} m, pitch {cfg['camera_pitch_rad']} rad; "
                       "focal length and centre from each image's calibration file"],
            ["Dataset", f"[{ds['name']}]({ds['source']}), {ds['split']}"],
            ["Images", f"{ds['images']}, {ds['subset']}"],
            ["Objects", f"{ds['matched_objects']} matched to a detection (IoU >= {cfg['min_iou']}) "
                        f"of {ds['labelled_objects']} labelled"],
            ["Ground truth", "laser-measured 3D boxes; scored two ways, see below"],
            ["Hardware", f"{prov['gpu']}"],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "- **Nearest surface**: true distance to the closest point of the object's footprint on the road",
        "  (e.g. the rear bumper of the car ahead). The gap that matters for braking.",
        "- **Centre**: true distance to the middle of the object, as KITTI records it.",
        "- **Coverage**: share of objects the estimator answered for, rather than returning unknown.",
        "- **Median / mean error**: absolute distance error in metres (mean = MAE, Mean Absolute Error).",
        "- **Relative error**: average absolute error as a percentage of the true distance.",
        "- **Within 10%**: share of answers within 10% of the true distance.",
        "- **Bias**: average signed error; negative = estimates too close, positive = too far.",
        "  Bias is systematic and correctable; the spread around it is not.",
        "",
    ]
    for t in truths:
        out += [
            f"## Overall, vs {t.replace('_', ' ')}", "",
            *md_table(["Estimator", *STAT_HEADER], [
                [m, *stat_rows({"x": r["methods"][m][t]["overall"]}, ["x"])[0][1:]] for m in methods
            ]),
        ]
    if "in_path" in r["methods"][methods[0]][truths[0]]:
        half = cfg.get("corridor_half_width_m")
        out += [
            "## In our path vs beside it",
            "",
            f"In path: the object's footprint comes within {half} m of our car's centre line (it",
            "overlaps our lane), so these are the objects a forward collision warning must get right.",
            f"{ds.get('in_path_objects')} of {ds['matched_objects']} matched objects are in path.",
            "",
        ]
        for t in truths:
            rows_ = []
            for scope in ("in_path", "beside"):
                for m in methods:
                    s = r["methods"][m][t][scope]["overall"]
                    rows_.append([f"{scope.replace('_', ' ')} / {m}",
                                  *stat_rows({"x": s}, ["x"])[0][1:]])
            out += [f"### Overall, vs {t.replace('_', ' ')}", "",
                    *md_table(["Scope / estimator", *STAT_HEADER], rows_)]
            for m in methods:
                mr = r["methods"][m][t]["in_path"]["by_distance"]
                out += [f"### `{m}` in path, by distance, vs {t.replace('_', ' ')}", "",
                        *md_table(["Distance", *STAT_HEADER], stat_rows(mr, list(mr)))]
    for t in truths:
        for m in methods:
            mr = r["methods"][m][t]
            out += [
                f"## `{m}` by distance, vs {t.replace('_', ' ')}", "",
                *md_table(["Distance", *STAT_HEADER], stat_rows(mr["by_distance"], list(mr["by_distance"]))),
                f"## `{m}` by class, vs {t.replace('_', ' ')}", "",
                *md_table(["Class", *STAT_HEADER], stat_rows(mr["by_class"], list(mr["by_class"]))),
            ]
    out += [
        "## Estimator latency",
        "",
        *md_table(["Estimator", "Median ms per image"],
                  [[m, v] for m, v in r["estimator_latency_ms_per_image"].items()]),
        "## Known limitations",
        "",
        "- Only objects the detector found are scored; distance quality on missed objects is unknown.",
        "- Camera height and pitch are KITTI's published values, assumed constant; the car pitches",
        "  slightly when braking or on slopes, which the ground-plane method does not model.",
        "- Known-size heights are general real-world averages, not fitted to KITTI.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


def write_comparison() -> None:
    """Generate COMPARISON.md: every run and estimator side by side, per truth."""
    runs = {
        p.name: json.loads((p / "results.json").read_text())
        for p in sorted(OUT_DIR.iterdir()) if (p / "results.json").exists()
    }
    if not runs:
        return
    cols = [(run, m) for run, r in runs.items() for m in r["config"]["estimators"]]
    names = [f"{run} / {m}" for run, m in cols]
    first = next(iter(runs.values()))
    truths = list(first["methods"][first["config"]["estimators"][0]])

    out = [
        "# KITTI distance benchmark: comparison",
        "",
        "Generated automatically from every `results/<run>/results.json` by `benchmark_kitti_distance.py`. "
        "Do not edit by hand. Best value per row in bold.",
        "",
    ]
    for t in truths:
        def get(run, m, band=None):
            mr = runs[run]["methods"][m][t]
            return mr["overall"] if band is None else mr["by_distance"].get(band)

        bands = list(first["methods"][first["config"]["estimators"][0]][t]["by_distance"])
        rows = [
            best_row("Coverage", [get(r, m)["coverage"] for r, m in cols], True, fmt_pct),
            best_row("Median error (m), all", [get(r, m)["median_abs_error_m"] for r, m in cols], False, fmt_m),
            best_row("Within 10%, all", [get(r, m)["within_10pct"] for r, m in cols], True, fmt_pct),
            best_row("|Bias|, all", [None if get(r, m)["bias"] is None else abs(get(r, m)["bias"])
                                     for r, m in cols], False, fmt_bias),
        ]
        rows += [best_row(f"Median error (m), {b}",
                          [(get(r, m, b) or {}).get("median_abs_error_m") for r, m in cols], False, fmt_m)
                 for b in bands]
        rows += [best_row(f"Within 10%, {b}",
                          [(get(r, m, b) or {}).get("within_10pct") for r, m in cols], True, fmt_pct)
                 for b in bands]
        out += [f"## vs {t.replace('_', ' ')}", "", *md_table(["", *names], rows)]
    path = OUT_DIR.parent / "COMPARISON.md"
    path.write_text("\n".join(out))
    print(f"regenerated {path}")


def main() -> None:
    if RESCORE_ONLY:
        rescore()
        write_comparison()
        return
    if REPORT_ONLY:
        for run_dir in sorted(p for p in OUT_DIR.iterdir() if (p / "results.json").exists()):
            write_report(run_dir)
            print(f"regenerated {run_dir / 'RESULTS.md'}")
        write_comparison()
        return
    if not SUBSET.exists():
        raise SystemExit(f"{SUBSET} not found. Run scripts/download_kitti.py first.")
    ids = [i for i in SUBSET.read_text().split() if (DATA / "training" / "image_2" / f"{i}.png").exists()]
    if MAX_IMAGES:
        ids = ids[:MAX_IMAGES]
    print(f"=== {RUN_NAME} ===")
    run(ids)
    write_comparison()


if __name__ == "__main__":
    main()
