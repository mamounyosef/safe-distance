"""Benchmark distance estimation on nuScenes mini: a second driving dataset.

nuScenes was recorded in Boston and Singapore, with a different car, camera
and lens than KITTI, and includes NIGHT scenes. Every object carries a 3D box
from LiDAR (laser), so the same object-level scoring as the KITTI benchmark
applies: does each method get the distance to each real object right?

Mini is the 10-scene sample of nuScenes: 404 labelled front-camera frames,
7 scenes by day and 3 at night. Enough to expose a model that only works on
KITTI; too few scenes to prove anything statistically about night on its own.
Its barriers and traffic cones also give an obstacle test with laser ground
truth (Lost and Found uses stereo).

Distances are ground distances in a level frame on the road, measured from
the point directly below our camera, like the KITTI benchmark:
    centre           to the middle of the object.
    nearest_surface  to the closest point of the object's footprint, e.g. the
                     rear bumper of the car ahead. The gap that matters.

The nuScenes label files are read directly (JSON tables plus quaternion
rotations), without the official devkit, whose pinned dependencies could
clash with this environment.

Output: one folder per run under results/ next to this file, each with
results.json (source of truth), objects.csv (one row per object) and a
generated RESULTS.md; plus a generated, ranked COMPARISON.md.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\nuscenes\\benchmark_nuscenes_distance.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import gc
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

# Make the repo root importable. This file is at src/distance/benchmarks/nuscenes/.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kitti"))

from benchmark_kitti_distance import (  # shared scoring, same rules as KITTI
    BANDS, STAT_HEADER, band_name, band_of, error_stats, estimator_set, fmt_m, fmt_pct, match, stat_rows,
)
from src.detection.benchmarks.common import md_table, provenance
from src.detection.detector import Detector
from src.distance.camera import Camera

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# nuScenes mini, unpacked (see the dataset's LICENSE; non-commercial use).
DATA = Path(r"C:\safe-distance-data\nuscenes-mini")
VERSION = "v1.0-mini"
CAMERA = "CAM_FRONT"

# Runs, as (run name, estimator set): "geometric", or a depth model name from
# src/distance/depth_models.py BACKENDS. Every run uses all 404 frames.
RUNS = [
    ("geometric", "geometric"),
    ("metric3d-v2-small", "metric3d-v2-small"),
    ("metric3d-v2-large", "metric3d-v2-large"),
    ("metric3d-v2-small-fp16", "metric3d-v2-small-fp16"),
    ("metric3d-v2-large-fp16", "metric3d-v2-large-fp16"),
    ("unidepth-v2-small", "unidepth-v2-small"),
    ("unidepth-v2-base", "unidepth-v2-base"),
    ("unidepth-v2-large", "unidepth-v2-large"),
    ("unidepth-v2-base-nocam", "unidepth-v2-base-nocam"),
    ("unidepth-v2-large-nocam", "unidepth-v2-large-nocam"),
    ("da3-metric-large", "da3-metric-large"),
    ("depth-pro", "depth-pro"),
    ("da2-metric-small", "da2-metric-small"),
    ("da2-metric-base", "da2-metric-base"),
    ("da2-metric-large", "da2-metric-large"),
    ("yolo26s-depth", "yolo26s-depth"),
]

# Detector settings, same as the KITTI distance benchmark.
WEIGHTS = "weights/yolo26s-seg.pt"
IMGSZ = 1280
CONF = 0.25

# In-path corridor, same as KITTI: footprint within this many metres of our
# car's centre line.
CORRIDOR_HALF_WIDTH_M = 1.2

# Labelled objects are scored only if at least this share of them is visible
# in the camera image, per nuScenes' own visibility label (levels 0-40%,
# 40-60%, 60-80%, 80-100%). Mostly hidden objects cannot be detected fairly.
MIN_VISIBILITY = "v40-60"

# Objects whose projected box is smaller than this (pixels tall) are skipped.
MIN_BOX_HEIGHT_PX = 10

OUT_DIR = Path(__file__).resolve().parent / "results"

# Obstacle runs: traffic cones and barriers, scored at their LABELLED box
# (projected into the image) instead of a detection, because the detector's
# COCO classes do not include them. Measures distance quality alone, like the
# Lost and Found benchmark. Written to their own folder and comparison.
OBSTACLE_CLASSES = {"traffic cone", "barrier"}
OBSTACLE_RUNS = [
    ("geometric", "geometric"),
    ("metric3d-v2-small", "metric3d-v2-small"),
    ("metric3d-v2-small-fp16", "metric3d-v2-small-fp16"),
    ("metric3d-v2-large", "metric3d-v2-large"),
    ("metric3d-v2-large-fp16", "metric3d-v2-large-fp16"),
    ("unidepth-v2-base", "unidepth-v2-base"),
    ("unidepth-v2-large", "unidepth-v2-large"),
]
OBSTACLE_OUT_DIR = Path(__file__).resolve().parent / "results_obstacles"
SKIP_EXISTING = True
RESCORE_ONLY = False
REPORT_ONLY = False

# ----------------------------------------------------------------------------

TRUTHS = ["nearest_surface", "centre"]
VISIBILITY_ORDER = ["v0-40", "v40-60", "v60-80", "v80-100"]


def class_of(category: str, attributes: set[str]) -> str | None:
    """nuScenes category -> the class names used in our tables (None = not scored)."""
    if category == "vehicle.car":
        return "car"
    if category in ("vehicle.truck", "vehicle.trailer", "vehicle.construction"):
        return "truck"
    if category.startswith("vehicle.bus"):
        return "bus"
    if category.startswith("human.pedestrian"):
        return "pedestrian"
    if category in ("vehicle.bicycle", "vehicle.motorcycle"):
        # A bicycle or motorcycle with a rider is a cyclist; a parked one is
        # still something in the road we must not hit.
        return "cyclist" if "cycle.with_rider" in attributes else "parked two-wheeler"
    if category == "movable_object.trafficcone":
        return "traffic cone"
    if category == "movable_object.barrier":
        return "barrier"
    return None


def quat_to_matrix(q: list[float]) -> np.ndarray:
    """Rotation matrix of a (w, x, y, z) quaternion."""
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def box_corners(center: list[float], size: list[float], rotation: list[float]) -> np.ndarray:
    """The 8 corners (3 x 8) of a nuScenes box; size is (width, length, height).

    The first 4 are the bottom face, the one touching the road.
    """
    w, l, h = size
    x = np.array([1, 1, -1, -1, 1, 1, -1, -1]) * l / 2
    y = np.array([1, -1, -1, 1, 1, -1, -1, 1]) * w / 2
    z = np.array([-1, -1, -1, -1, 1, 1, 1, 1]) * h / 2
    return quat_to_matrix(rotation) @ np.vstack([x, y, z]) + np.array(center).reshape(3, 1)


def nearest_point_distance(polygon: np.ndarray, point: np.ndarray) -> float:
    """Distance from point (2,) to a convex polygon (2 x N), 0 if inside."""
    pts = polygon.T
    edges = list(zip(pts, np.roll(pts, -1, axis=0)))
    cross = [(b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0]) for a, b in edges]
    if all(c >= 0 for c in cross) or all(c <= 0 for c in cross):
        return 0.0
    best = math.inf
    for a, b in edges:
        d = b - a
        t = max(0.0, min(1.0, float(np.dot(point - a, d) / np.dot(d, d))))
        best = min(best, float(np.linalg.norm(a + t * d - point)))
    return best


class NuScenesMini:
    """Minimal reader for the nuScenes tables this benchmark needs."""

    def __init__(self, root: Path, version: str) -> None:
        def table(name):
            return json.loads((root / version / f"{name}.json").read_text())

        self.root = root
        self.scenes = {s["token"]: s for s in table("scene")}
        logs = {l["token"]: l for l in table("log")}
        self.samples = {s["token"]: s for s in table("sample")}
        self.calib = {c["token"]: c for c in table("calibrated_sensor")}
        self.poses = {p["token"]: p for p in table("ego_pose")}
        self.visibility = {v["token"]: v["level"] for v in table("visibility")}
        attributes = {a["token"]: a["name"] for a in table("attribute")}
        categories = {c["token"]: c["name"] for c in table("category")}
        instances = {i["token"]: categories[i["category_token"]] for i in table("instance")}
        self.location = {t: logs[s["log_token"]]["location"] for t, s in self.scenes.items()}

        self.annotations: dict[str, list[dict]] = {}
        for a in table("sample_annotation"):
            a["category"] = instances[a["instance_token"]]
            a["attributes"] = {attributes[t] for t in a["attribute_tokens"]}
            self.annotations.setdefault(a["sample_token"], []).append(a)

        # Key frames of the chosen camera, in time order.
        self.frames = sorted(
            (d for d in table("sample_data")
             if d["is_key_frame"] and d["filename"].startswith(f"samples/{CAMERA}/")),
            key=lambda d: d["timestamp"],
        )

    def is_night(self, frame: dict) -> bool:
        scene = self.scenes[self.samples[frame["sample_token"]]["scene_token"]]
        return "night" in scene["description"].lower()

    def scene_name(self, frame: dict) -> str:
        return self.scenes[self.samples[frame["sample_token"]]["scene_token"]]["name"]


def frame_geometry(ds: NuScenesMini, frame: dict) -> tuple[Camera, dict]:
    """Our Camera for one frame, plus the transforms needed for its labels.

    nuScenes' vehicle frame has x forward, y left, z up, with its origin on the
    road below the rear axle, so the camera's z position is its height.
    """
    cal = ds.calib[frame["calibrated_sensor_token"]]
    K = np.array(cal["camera_intrinsic"])
    R_cam = quat_to_matrix(cal["rotation"])
    t_cam = np.array(cal["translation"])
    axis = R_cam @ np.array([0.0, 0.0, 1.0])  # optical axis in the vehicle frame
    pitch = math.asin(max(-1.0, min(1.0, -axis[2])))  # positive = looking down
    camera = Camera(fx=K[0, 0], fy=K[1, 1], cx=K[0, 2], cy=K[1, 2], height_m=float(t_cam[2]), pitch_rad=pitch)
    pose = ds.poses[frame["ego_pose_token"]]
    return camera, {"K": K, "R_cam": R_cam, "t_cam": t_cam,
                    "R_ego": quat_to_matrix(pose["rotation"]), "t_ego": np.array(pose["translation"])}


def frame_labels(ds: NuScenesMini, frame: dict, geo: dict) -> list[dict]:
    """Scored objects of one frame, with their 2D box and true distances."""
    width, height = frame["width"], frame["height"]
    cam_ground = geo["t_cam"][:2]  # the road point below the camera, vehicle frame
    min_vis = VISIBILITY_ORDER.index(MIN_VISIBILITY)
    out = []
    for a in ds.annotations.get(frame["sample_token"], []):
        cls = class_of(a["category"], a["attributes"])
        vis = ds.visibility[a["visibility_token"]]
        if cls is None or VISIBILITY_ORDER.index(vis) < min_vis:
            continue
        corners = box_corners(a["translation"], a["size"], a["rotation"])
        ego = geo["R_ego"].T @ (corners - geo["t_ego"].reshape(3, 1))   # world -> vehicle
        cam = geo["R_cam"].T @ (ego - geo["t_cam"].reshape(3, 1))       # vehicle -> camera
        if (cam[2] < 0.5).any():
            continue  # partly behind the camera: no clean image box
        uv = geo["K"] @ cam
        uv = uv[:2] / uv[2]
        x1, y1 = max(0.0, uv[0].min()), max(0.0, uv[1].min())
        x2, y2 = min(width - 1.0, uv[0].max()), min(height - 1.0, uv[1].max())
        if x2 <= x1 or y2 - y1 < MIN_BOX_HEIGHT_PX:
            continue

        footprint = ego[:2, :4]  # bottom face, vehicle x-y plane
        centre = ego[:2].mean(axis=1)
        ys = footprint[1]
        lateral = 0.0 if ys.min() <= 0.0 <= ys.max() else float(min(abs(ys.min()), abs(ys.max())))
        hull = cv2.convexHull(np.stack([np.clip(uv[0], 0, width - 1), np.clip(uv[1], 0, height - 1)], axis=1)
                              .astype(np.float32)).reshape(-1, 2)
        out.append({
            "outline": hull,
            "class": cls,
            "category": a["category"],
            "visibility": vis,
            "box": (float(x1), float(y1), float(x2), float(y2)),
            "true_centre_m": float(np.linalg.norm(centre - cam_ground)),
            "true_nearest_surface_m": nearest_point_distance(footprint, cam_ground),
            "lateral_gap_m": lateral,
        })
    return out


def by_distance(rows: list[dict], m: str, t: str) -> dict:
    out = {}
    for lo, hi in BANDS:
        b = band_name(lo, hi)
        subset = [r for r in rows if band_of(r[f"true_{t}_m"]) == b]
        if subset:
            out[b] = error_stats(subset, m, t)
    return out


def build_results(rows: list[dict], methods: list[str], n_frames: int, n_labelled: int, prov: dict,
                  run_name: str, depth_model: dict | None,
                  estimator_input: str = "detections matched to labels (IoU >= 0.5)") -> dict:
    for r in rows:
        r["in_path"] = r["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M
    classes = sorted({r["class"] for r in rows}, key=lambda c: -sum(r["class"] == c for r in rows))

    def stats_for(subset, m, t):
        return {"overall": error_stats(subset, m, t), "by_distance": by_distance(subset, m, t)}

    in_path = [r for r in rows if r["in_path"]]
    return {
        "benchmark": "nuscenes_distance",
        "provenance": prov,
        "dataset": {
            "name": f"nuScenes {VERSION}",
            "source": "https://www.nuscenes.org/nuscenes",
            "camera": CAMERA,
            "frames": n_frames,
            "night_frames": len({r["frame"] for r in rows if r["condition"] == "night"}),
            "labelled_objects": n_labelled,
            "matched_objects": len(rows),
            "in_path_objects": len(in_path),
            "min_visibility": MIN_VISIBILITY,
            "ground_truth": "LiDAR 3D boxes; ground distance from the road point below the camera",
            "estimator_input": estimator_input,
        },
        "config": {
            "run_name": run_name,
            "depth_model": depth_model,
            "weights": WEIGHTS,
            "imgsz": IMGSZ,
            "conf": CONF,
            "camera_height_and_pitch": "from each frame's calibration",
            "corridor_half_width_m": CORRIDOR_HALF_WIDTH_M,
            "estimators": methods,
            "distance_bands_m": BANDS,
        },
        "methods": {
            m: {
                t: {
                    **stats_for(rows, m, t),
                    "by_class": {c: error_stats([r for r in rows if r["class"] == c], m, t) for c in classes},
                    "in_path": stats_for(in_path, m, t),
                    "by_condition": {
                        cond: {
                            "overall": error_stats([r for r in rows if r["condition"] == cond], m, t),
                            "in_path": error_stats([r for r in in_path if r["condition"] == cond], m, t),
                        }
                        for cond in ("day", "night")
                    },
                }
                for t in TRUTHS
            }
            for m in methods
        },
    }


def save_run(results: dict, rows: list[dict], out_dir: Path = OUT_DIR) -> None:
    run_dir = out_dir / results["config"]["run_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    with (run_dir / "objects.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(run_dir)
    for m in results["config"]["estimators"]:
        n = results["methods"][m]["nearest_surface"]
        print(f"  {m:>26}: in path within 10% {n['in_path']['overall']['within_10pct'] or 0:.0%}, "
              f"night in path {n['by_condition']['night']['in_path']['within_10pct'] or 0:.0%}, "
              f"all {n['overall']['within_10pct'] or 0:.0%}")
    print(f"wrote {run_dir}")


def run(ds: NuScenesMini, run_name: str, estimators: list) -> None:
    detector = Detector(weights=WEIGHTS, conf=CONF, imgsz=IMGSZ)
    methods = [e.name for e in estimators]
    rows, n_labelled = [], 0
    for i, frame in enumerate(ds.frames, 1):
        img = cv2.imread(str(ds.root / frame["filename"]))
        camera, geo = frame_geometry(ds, frame)
        labels = frame_labels(ds, frame, geo)
        n_labelled += len(labels)
        dets = detector.detect(img)
        estimates = {e.name: e.estimate(img, dets, camera) for e in estimators}
        for gi, bi in match(labels, [(d.x1, d.y1, d.x2, d.y2) for d in dets]).items():
            g, d = labels[gi], dets[bi]
            rows.append({
                "frame": frame["token"],
                "scene": ds.scene_name(frame),
                "condition": "night" if ds.is_night(frame) else "day",
                "class": g["class"],
                "category": g["category"],
                "predicted_class": d.class_name,
                "visibility": g["visibility"],
                "box_height_px": round(g["box"][3] - g["box"][1], 1),
                "true_centre_m": round(g["true_centre_m"], 2),
                "true_nearest_surface_m": round(g["true_nearest_surface_m"], 2),
                "lateral_gap_m": round(g["lateral_gap_m"], 2),
                **{m: (None if estimates[m][bi] is None else round(estimates[m][bi], 2)) for m in methods},
            })
        if i % 100 == 0 or i == len(ds.frames):
            print(f"  {i}/{len(ds.frames)} frames, {len(rows)} objects matched of {n_labelled}", flush=True)

    backends = {id(e.backend): e.backend for e in estimators if hasattr(e, "backend")}
    depth_model = None
    for b in backends.values():
        t = b.times_ms[1:] or b.times_ms
        depth_model = {"name": b.name, "uses_our_focal_length": b.uses_focal_length, "precision": b.precision,
                       "inference_ms_median": round(float(np.median(t)), 1),
                       "inference_ms_p95": round(float(np.percentile(t, 95)), 1)}
        if getattr(b, "estimated_fx", None):
            depth_model["estimated_focal_px_median"] = round(float(np.median(b.estimated_fx)), 1)
            depth_model["estimated_focal_px_p10_p90"] = [round(float(np.percentile(b.estimated_fx, q)), 1) for q in (10, 90)]
    save_run(build_results(rows, methods, len(ds.frames), n_labelled, provenance(), run_name, depth_model), rows)


def run_outlines(ds: NuScenesMini, run_name: str, estimators: list) -> None:
    """Score estimators on every labelled cone and barrier, given its outline."""
    from src.detection.detector import Detection

    methods = [e.name for e in estimators]
    rows, n_labelled = [], 0
    for i, frame in enumerate(ds.frames, 1):
        img = cv2.imread(str(ds.root / frame["filename"]))
        camera, geo = frame_geometry(ds, frame)
        labels = [g for g in frame_labels(ds, frame, geo) if g["class"] in OBSTACLE_CLASSES]
        n_labelled += len(labels)
        dets = [Detection(x1=g["box"][0], y1=g["box"][1], x2=g["box"][2], y2=g["box"][3], class_id=-1,
                          class_name="obstacle", confidence=1.0, mask=g["outline"]) for g in labels]
        estimates = {e.name: e.estimate(img, dets, camera) for e in estimators}
        for k, g in enumerate(labels):
            rows.append({
                "frame": frame["token"],
                "scene": ds.scene_name(frame),
                "condition": "night" if ds.is_night(frame) else "day",
                "class": g["class"],
                "category": g["category"],
                "predicted_class": "labelled outline",
                "visibility": g["visibility"],
                "box_height_px": round(g["box"][3] - g["box"][1], 1),
                "true_centre_m": round(g["true_centre_m"], 2),
                "true_nearest_surface_m": round(g["true_nearest_surface_m"], 2),
                "lateral_gap_m": round(g["lateral_gap_m"], 2),
                **{m: (None if estimates[m][k] is None else round(estimates[m][k], 2)) for m in methods},
            })
        if i % 100 == 0 or i == len(ds.frames):
            print(f"  {i}/{len(ds.frames)} frames, {len(rows)} obstacles", flush=True)

    backends = {id(e.backend): e.backend for e in estimators if hasattr(e, "backend")}
    depth_model = None
    for b in backends.values():
        t = b.times_ms[1:] or b.times_ms
        depth_model = {"name": b.name, "uses_our_focal_length": b.uses_focal_length, "precision": b.precision,
                       "inference_ms_median": round(float(np.median(t)), 1),
                       "inference_ms_p95": round(float(np.percentile(t, 95)), 1)}
        if getattr(b, "estimated_fx", None):
            depth_model["estimated_focal_px_median"] = round(float(np.median(b.estimated_fx)), 1)
            depth_model["estimated_focal_px_p10_p90"] = [round(float(np.percentile(b.estimated_fx, q)), 1) for q in (10, 90)]
    save_run(build_results(rows, methods, len(ds.frames), n_labelled, provenance(), run_name, depth_model,
                           "labelled 3D box projected into the image (convex hull of its corners)"),
             rows, OBSTACLE_OUT_DIR)


def rescore(run_dir: Path) -> None:
    """Recompute all statistics of one run from its objects.csv. No GPU."""
    old = json.loads((run_dir / "results.json").read_text())
    methods = old["config"]["estimators"]
    num = ("box_height_px", "true_centre_m", "true_nearest_surface_m", "lateral_gap_m")
    with (run_dir / "objects.csv").open(newline="") as f:
        rows = [{**r, **{k: float(r[k]) for k in num},
                 **{m: (float(r[m]) if r[m] not in ("", "None") else None) for m in methods}}
                for r in csv.DictReader(f)]
    prov = {**old["provenance"], "rescored_utc": provenance()["created_utc"],
            "rescored_git_commit": provenance()["git_commit"]}
    save_run(build_results(rows, methods, old["dataset"]["frames"], old["dataset"]["labelled_objects"], prov,
                           old["config"]["run_name"], old["config"].get("depth_model"),
                           old["dataset"].get("estimator_input", "detections matched to labels (IoU >= 0.5)")),
             rows, run_dir.parent)


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""
    dm = cfg.get("depth_model")
    methods = cfg["estimators"]
    out = [
        f"# nuScenes distance benchmark: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Detector", f"`{cfg['weights']}`, input size {cfg['imgsz']}, confidence {cfg['conf']}"],
            ["Estimators", ", ".join(f"`{m}`" for m in methods)],
            *([["Depth model", f"`{dm['name']}`, {'given' if dm['uses_our_focal_length'] else 'not given'} "
                               f"our focal length; inference {dm['inference_ms_median']} ms median, "
                               f"{dm['inference_ms_p95']} ms p95 per frame"]] if dm else []),
            ["Dataset", f"[{ds['name']}]({ds['source']}), camera {ds['camera']}"],
            ["Frames", f"{ds['frames']} ({ds['night_frames']} at night)"],
            ["Objects", f"{ds['matched_objects']} matched to a detection of {ds['labelled_objects']} labelled "
                        f"(visibility at least {ds['min_visibility']}); {ds['in_path_objects']} in path"],
            ["Ground truth", ds["ground_truth"]],
            ["Camera", cfg["camera_height_and_pitch"]],
            ["Hardware", prov["gpu"]],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,",
        "share within 10% of the truth, and bias (negative = too close). In path = footprint within",
        f"{cfg['corridor_half_width_m']} m of our car's centre line.",
        "",
    ]
    for t in TRUTHS:
        title = t.replace("_", " ")
        out += [f"## In path, vs {title}", "",
                *md_table(["Estimator", *STAT_HEADER],
                          [[m, *stat_rows({"x": r["methods"][m][t]["in_path"]["overall"]}, ["x"])[0][1:]]
                           for m in methods]),
                f"## Day vs night, in path, vs {title}", "",
                *md_table(["Estimator / condition", *STAT_HEADER],
                          [[f"{m} / {c}", *stat_rows({"x": r["methods"][m][t]["by_condition"][c]["in_path"]}, ["x"])[0][1:]]
                           for m in methods for c in ("day", "night")]),
                f"## All objects, vs {title}", "",
                *md_table(["Estimator", *STAT_HEADER],
                          [[m, *stat_rows({"x": r["methods"][m][t]["overall"]}, ["x"])[0][1:]] for m in methods])]
        for m in methods:
            node = r["methods"][m][t]
            out += [f"### `{m}` in path by distance, vs {title}", "",
                    *md_table(["Distance", *STAT_HEADER], stat_rows(node["in_path"]["by_distance"], list(node["in_path"]["by_distance"]))),
                    f"### `{m}` by class, vs {title}", "",
                    *md_table(["Class", *STAT_HEADER], stat_rows(node["by_class"], list(node["by_class"])))]
    out += [
        "## Known limitations",
        "",
        "- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition",
        "  results (especially night, 3 scenes) are indicative, not statistically conclusive.",
        "- Only objects the detector found are scored; objects under the visibility threshold are skipped.",
        "- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


def write_comparison(out_dir: Path = OUT_DIR, file_name: str = "COMPARISON.md",
                     title: str = "nuScenes distance benchmark: comparison") -> None:
    runs = {p.name: json.loads((p / "results.json").read_text())
            for p in sorted(out_dir.iterdir()) if (p / "results.json").exists()}
    if not runs:
        return
    band_names = [band_name(lo, hi) for lo, hi in BANDS]
    out = [
        f"# {title}",
        "",
        "Generated automatically from every `results/<run>/results.json` by `benchmark_nuscenes_distance.py`. "
        "Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.",
        "",
        "Ranked by **in path, within 10%** of the true distance. `_median`, `_p10`, `_p25` mark how a",
        "depth model's per-pixel depth inside the object's mask is summarised.",
        "",
    ]
    for t in TRUTHS:
        rows = []
        for run, r in runs.items():
            dm = r["config"].get("depth_model") or {}
            for m in r["config"]["estimators"]:
                n = r["methods"][m][t]
                ip = n["in_path"]
                rows.append((ip["overall"]["within_10pct"] or 0.0, [
                    f"`{run}`", f"`{m}`", fmt_pct(ip["overall"]["within_10pct"]), fmt_m(ip["overall"]["median_abs_error_m"]),
                    fmt_pct(n["by_condition"]["day"]["in_path"]["within_10pct"]),
                    fmt_pct(n["by_condition"]["night"]["in_path"]["within_10pct"]),
                    *[fmt_pct((ip["by_distance"].get(b) or {}).get("within_10pct")) for b in band_names],
                    fmt_pct(n["overall"]["within_10pct"]), dm.get("inference_ms_median", "-"),
                ]))
        rows.sort(key=lambda x: -x[0])
        header = ["Rank", "Run", "Estimator", "In path within 10%", "In path median error (m)",
                  "In path, day", "In path, night", *[f"In path, {b}" for b in band_names],
                  "All objects within 10%", "Depth model ms"]
        out += [f"## vs {t.replace('_', ' ')}", "", *md_table(header, [[i, *row] for i, (_, row) in enumerate(rows, 1)])]
    path = out_dir.parent / file_name
    path.write_text("\n".join(out))
    print(f"regenerated {path}")


def main() -> None:
    folders = [(OUT_DIR, "COMPARISON.md", "nuScenes distance benchmark: comparison"),
               (OBSTACLE_OUT_DIR, "COMPARISON_OBSTACLES.md",
                "nuScenes distance benchmark: traffic cones and barriers (labelled outlines)")]
    if RESCORE_ONLY or REPORT_ONLY:
        for out_dir, file_name, title in folders:
            if not out_dir.exists():
                continue
            for run_dir in sorted(p for p in out_dir.iterdir() if (p / "results.json").exists()):
                if RESCORE_ONLY:
                    rescore(run_dir)
                else:
                    write_report(run_dir)
            write_comparison(out_dir, file_name, title)
        return

    import torch

    ds = NuScenesMini(DATA, VERSION)
    groups = [(RUNS, OUT_DIR, run, folders[0]), (OBSTACLE_RUNS, OBSTACLE_OUT_DIR, run_outlines, folders[1])]
    for runs, out_dir, runner, (_, file_name, title) in groups:
        for run_name, set_name in runs:
            if SKIP_EXISTING and (out_dir / run_name / "results.json").exists():
                print(f"=== {out_dir.name}/{run_name}: already done, skipped ===")
                continue
            print(f"=== {out_dir.name}/{run_name} ({len(ds.frames)} frames) ===", flush=True)
            estimators = estimator_set(set_name)
            runner(ds, run_name, estimators)
            estimators = None
            gc.collect()
            torch.cuda.empty_cache()
            write_comparison(out_dir, file_name, title)


if __name__ == "__main__":
    main()
