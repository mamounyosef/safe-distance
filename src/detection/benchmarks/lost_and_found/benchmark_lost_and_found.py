"""Benchmark obstacle detection on the Lost and Found test split.

For every labelled obstacle on the road, this finds its true distance from the
stereo disparity map, runs the detector, and records whether the obstacle was
found. Results are recall per distance band, per obstacle group and per
obstacle type, plus false alarms on free road and latency.

Terms:
    recall       fraction of real obstacles the detector found.
    false alarm  a detection on free road where there is no obstacle.
    IoU          Intersection over Union: overlap area of two boxes divided
                 by their combined area. 1.0 is a perfect match, 0 is none.

Output: one folder per run, named in RUNS below, under results/ next to this
file. Each holds:
    results.json    machine-readable results + provenance
    obstacles.csv   one row per obstacle, for digging into failures

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\detection\\benchmarks\\lost_and_found\\benchmark_lost_and_found.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Make the repo root importable, so "src.detection" resolves when this file
# is run directly. This file is at src/detection/benchmarks/lost_and_found/,
# four levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.detection.benchmarks.common import best_row, iou, md_table, pct, provenance
from src.detection.detector import Detector

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Dataset root, as written by scripts/download_lost_and_found.py.
DATA = Path("data/lost_and_found")

# The official test split scenes. Scenes whose images are missing are skipped.
SCENES = [
    "02_Hanns_Klemm_Str_44",
    "04_Maurener_Weg_8",
    "05_Schafgasse_1",
    "07_Festplatz_Flugfeld",
    "15_Rechbergstr_Deckenpfronn",
]

# Runs to perform, as (weights, run name). Each run writes its own folder
# results/<run name>/, so changing a setting under a new name keeps the old
# results for comparison instead of overwriting them. For YOLOE the name
# should say which prompt list was used, since the results depend on it.
RUNS = [
    ("weights/yoloe-11s-seg.pt", "yoloe-11s-seg_prompts-v2"),
]

# Longest side fed to the model, same meaning as in scripts/detect_video.py.
IMGSZ = 1280

# The detector runs once at the lowest threshold, and recall is then computed
# for each threshold here from the same predictions, so comparing them is free.
CONF_THRESHOLDS = [0.05, 0.10, 0.25]

# A prediction counts as finding an obstacle if its box overlaps the obstacle's
# box by at least this IoU. Any class counts: noticing that something is there
# matters more for collision avoidance than naming it correctly.
MIN_IOU = 0.3

# Distance bands in metres.
BANDS = [(0, 10), (10, 20), (20, 30), (30, 50), (50, 1000)]

# Stop after this many frames. 0 = all.
MAX_FRAMES = 0

# Where run folders are written: results/ next to this file.
OUT_DIR = Path(__file__).resolve().parent / "results"

# True: skip inference and only regenerate every run's RESULTS.md from its
# existing results.json. Use after changing the report layout.
REPORT_ONLY = False

# ----------------------------------------------------------------------------

# Obstacle types and groups, from the dataset's own table (laf_table.pdf).
TYPES: dict[str, tuple[str, str]] = {
    "01": ("crate (black)", "standard objects"),
    "02": ("crate (black, 2x stacked)", "standard objects"),
    "03": ("crate (black, upright)", "standard objects"),
    "04": ("crate (gray)", "standard objects"),
    "05": ("crate (gray, 2x stacked)", "standard objects"),
    "06": ("crate (gray, upright)", "standard objects"),
    "07": ("bumper", "random hazards"),
    "08": ("cardboard box", "random hazards"),
    "09": ("crate (blue)", "random hazards"),
    "10": ("crate (blue, small)", "random hazards"),
    "11": ("crate (green)", "random hazards"),
    "12": ("crate (green, small)", "random hazards"),
    "13": ("exhaust pipe", "random hazards"),
    "14": ("headlight", "random hazards"),
    "15": ("euro pallet", "random hazards"),
    "16": ("pylon", "random hazards"),
    "17": ("pylon (large)", "random hazards"),
    "18": ("pylon (white)", "random hazards"),
    "19": ("rearview mirror", "random hazards"),
    "20": ("tire", "random hazards"),
    "29": ("cardboard box", "random hazards"),
    "31": ("plastic bag (bloated)", "random hazards"),
    "34": ("styrofoam", "random hazards"),
    "21": ("ball", "emotional hazards"),
    "22": ("bicycle", "emotional hazards"),
    "23": ("dog (black)", "emotional hazards"),
    "24": ("dog (white)", "emotional hazards"),
    "25": ("kid dummy", "emotional hazards"),
    "26": ("bobby car (gray)", "emotional hazards"),
    "27": ("bobby car (red)", "emotional hazards"),
    "28": ("bobby car (yellow)", "emotional hazards"),
    "39": ("kid (walking)", "humans"),
    "40": ("kid (on a bobby car)", "humans"),
    "41": ("kid (on a small bobby car)", "humans"),
    "42": ("kid (crawling)", "humans"),
}

# The "random non-hazards" (lying poles, timber, wheel cap, thin wood) are ones
# a car can drive over, so the dataset excludes them and so do we: missing
# them is not a failure, and detecting them is not a false alarm.
NON_HAZARD_LABELS = {"30", "32", "33", "35", "36", "37", "38"}


def polygon_mask(polygon: list, shape: tuple[int, int]) -> np.ndarray:
    """Rasterise a label polygon into a boolean mask."""
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [np.asarray(polygon, dtype=np.int32)], 1)
    return mask.astype(bool)


def polygon_box(polygon: list) -> tuple[float, float, float, float]:
    pts = np.asarray(polygon, dtype=np.float32)
    return float(pts[:, 0].min()), float(pts[:, 1].min()), float(pts[:, 0].max()), float(pts[:, 1].max())


def disparity_to_depth(raw: np.ndarray, fx: float, baseline: float) -> np.ndarray:
    """Convert a stored disparity image to depth in metres.

    Stored as 16-bit: disparity in pixels = (value - 1) / 256, and 0 means
    no measurement. Depth then follows from stereo geometry:
    depth = focal length * camera separation / disparity.
    """
    disp = (raw.astype(np.float32) - 1.0) / 256.0
    depth = np.full(raw.shape, np.nan, dtype=np.float32)
    valid = (raw > 0) & (disp > 0)
    depth[valid] = fx * baseline / disp[valid]
    return depth


def band_name(lo: int, hi: int) -> str:
    return f"{lo}+ m" if hi >= 1000 else f"{lo}-{hi} m"


def band_of(distance: float) -> str:
    for lo, hi in BANDS:
        if lo <= distance < hi:
            return band_name(lo, hi)
    return "unknown"


def recall_table(rows: list[dict], key) -> dict:
    """Recall at every threshold, for each value of key(row)."""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(key(r), []).append(r)
    out = {}
    for name, subset in groups.items():
        out[name] = {
            "obstacles": len(subset),
            "recall": {
                str(t): round(sum(r["best_conf"] >= t for r in subset) / len(subset), 4)
                for t in CONF_THRESHOLDS
            },
        }
    return out


def list_frames() -> list[Path]:
    frames = []
    for scene in SCENES:
        img_dir = DATA / "leftImg8bit" / "test" / scene
        if not img_dir.exists():
            print(f"skipping {scene}: no images downloaded")
            continue
        frames.extend(sorted(img_dir.glob("*_leftImg8bit.png")))
    return frames[:MAX_FRAMES] if MAX_FRAMES else frames


def evaluate(weights: str, run_name: str, frames: list[Path]) -> None:
    print(f"\n=== {run_name} ===")
    detector = Detector(weights=weights, conf=min(CONF_THRESHOLDS), imgsz=IMGSZ)

    rows = []
    false_alarms = {t: 0 for t in CONF_THRESHOLDS}
    no_depth = 0
    times = []

    for i, img_path in enumerate(frames, 1):
        stem = img_path.name.replace("_leftImg8bit.png", "")
        scene = img_path.parent.name
        split_dir = img_path.parent.parent.name
        label_path = DATA / "gtCoarse" / split_dir / scene / f"{stem}_gtCoarse_polygons.json"
        disp_path = DATA / "disparity" / split_dir / scene / f"{stem}_disparity.png"
        cam_path = DATA / "camera" / split_dir / scene / f"{stem}_camera.json"
        if not (label_path.exists() and disp_path.exists() and cam_path.exists()):
            print(f"  missing label, disparity or camera for {stem}, skipped")
            continue

        img = cv2.imread(str(img_path))
        labels = json.loads(label_path.read_text())
        cam = json.loads(cam_path.read_text())
        depth = disparity_to_depth(
            cv2.imread(str(disp_path), cv2.IMREAD_UNCHANGED),
            cam["intrinsic"]["fx"], cam["extrinsic"]["baseline"],
        )
        shape = img.shape[:2]

        t0 = time.perf_counter()
        preds = detector.detect(img)
        times.append((time.perf_counter() - t0) * 1000.0)
        pred_boxes = [(p.x1, p.y1, p.x2, p.y2) for p in preds]

        free_mask = np.zeros(shape, dtype=bool)
        non_hazard_boxes = []
        matched = [False] * len(preds)

        for obj in labels["objects"]:
            label = obj["label"]
            if label == "free":
                free_mask |= polygon_mask(obj["polygon"], shape)
                continue
            if label in NON_HAZARD_LABELS:
                non_hazard_boxes.append(polygon_box(obj["polygon"]))
                continue
            if label not in TYPES:
                continue

            gt_box = polygon_box(obj["polygon"])
            values = depth[polygon_mask(obj["polygon"], shape)]
            values = values[np.isfinite(values)]
            if values.size == 0:
                no_depth += 1
                continue

            best_iou, best_conf = 0.0, 0.0
            for j, (p, box) in enumerate(zip(preds, pred_boxes)):
                o = iou(gt_box, box)
                if o >= MIN_IOU:
                    matched[j] = True
                    if p.confidence > best_conf:
                        best_iou, best_conf = o, p.confidence

            obstacle_type, group = TYPES[label]
            rows.append({
                "frame": stem,
                "label": label,
                "type": obstacle_type,
                "group": group,
                "distance_m": round(float(np.median(values)), 2),
                "box_height_px": round(gt_box[3] - gt_box[1], 1),
                "best_iou": round(best_iou, 3),
                "best_conf": round(best_conf, 3),
            })

        # A false alarm is an unmatched prediction whose road contact point
        # sits on free road, and which does not overlap a non-hazard either.
        for j, (p, box) in enumerate(zip(preds, pred_boxes)):
            if matched[j] or any(iou(box, nh) >= MIN_IOU for nh in non_hazard_boxes):
                continue
            cx, cy = p.contact_point
            x = int(min(max(cx, 0), shape[1] - 1))
            y = int(min(max(cy, 0), shape[0] - 1))
            if free_mask[y, x]:
                for t in CONF_THRESHOLDS:
                    if p.confidence >= t:
                        false_alarms[t] += 1

        if i % 100 == 0 or i == len(frames):
            print(f"  {i}/{len(frames)} frames")

    if not rows:
        raise SystemExit("No obstacles evaluated.")

    n_frames = len(times)
    band_order = [band_name(lo, hi) for lo, hi in BANDS]
    by_band = recall_table(rows, lambda r: band_of(r["distance_m"]))
    results = {
        "benchmark": "lost_and_found_obstacle_detection",
        "provenance": provenance(),
        "dataset": {
            "name": "Lost and Found",
            "source": "https://huggingface.co/datasets/kumuji/lost_and_found",
            "split": "test",
            "scenes": SCENES,
            "frames": n_frames,
            "obstacles": len(rows),
            "obstacles_skipped_no_depth": no_depth,
            "excluded_labels": "random non-hazards (30, 32, 33, 35-38), per the dataset definition",
            "distance_source": "median stereo depth inside the obstacle polygon",
        },
        "config": {
            "run_name": run_name,
            "weights": weights,
            "prompts": detector.prompts,
            "imgsz": IMGSZ,
            "conf_thresholds": CONF_THRESHOLDS,
            "min_iou": MIN_IOU,
            "matching": "any predicted class counts",
            "distance_bands_m": BANDS,
        },
        "latency_ms": {
            "median": round(float(np.median(times)), 1),
            "p95": round(float(np.percentile(times, 95)), 1),
        },
        "recall_overall": recall_table(rows, lambda r: "all")["all"],
        "recall_by_distance": {b: by_band[b] for b in band_order if b in by_band},
        "recall_by_group": recall_table(rows, lambda r: r["group"]),
        "recall_by_type": recall_table(rows, lambda r: r["type"]),
        "false_alarms_on_free_road": {
            str(t): {"total": false_alarms[t], "per_frame": round(false_alarms[t] / n_frames, 4)}
            for t in CONF_THRESHOLDS
        },
    }

    run_dir = OUT_DIR / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / "results.json"
    csv_path = run_dir / "obstacles.csv"
    json_path.write_text(json.dumps(results, indent=2))
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(run_dir)

    t = str(CONF_THRESHOLDS[0])
    print(f"recall@{t}: overall {results['recall_overall']['recall'][t]:.0%}")
    for name, v in results["recall_by_distance"].items():
        print(f"  {name:>8}: {v['recall'][t]:.0%}  (n={v['obstacles']})")
    for name, v in results["recall_by_group"].items():
        print(f"  {name:>18}: {v['recall'][t]:.0%}  (n={v['obstacles']})")
    print(f"wrote {json_path}, {csv_path} and RESULTS.md")


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json.

    The report is never edited by hand: every number in it comes from the
    JSON, so the two can never disagree. Re-run with REPORT_ONLY = True to
    regenerate reports after changing this function.
    """
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    thresholds = [str(t) for t in cfg["conf_thresholds"]]
    rec_cols = [f"Recall @{t}" for t in thresholds]

    def recall_rows(table: dict, order: list[str] | None = None) -> list[list]:
        names = order if order else sorted(table, key=lambda k: -table[k]["obstacles"])
        return [
            [name, table[name]["obstacles"], *(pct(table[name]["recall"][t]) for t in thresholds)]
            for name in names if name in table
        ]

    prompts = cfg.get("prompts")
    vocabulary = (
        f"open vocabulary, {len(prompts)} prompts: " + ", ".join(f"`{p}`" for p in prompts)
        if prompts else "fixed 80 COCO (Common Objects in Context) classes"
    )
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""

    out = [
        f"# Lost and Found obstacle benchmark: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by "
        "`benchmark_lost_and_found.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Model weights", f"`{cfg['weights']}`"],
            ["Vocabulary", vocabulary],
            ["Input size", cfg["imgsz"]],
            ["Dataset", f"[{ds['name']}]({ds['source']}), {ds['split']} split, {len(ds['scenes'])} scenes"],
            ["Frames", ds["frames"]],
            ["Obstacles evaluated", ds["obstacles"]],
            ["Excluded", ds["excluded_labels"]],
            ["Ground-truth distance", ds["distance_source"]],
            ["Match rule", f"IoU >= {cfg['min_iou']}, {cfg['matching']}"],
            ["Hardware", f"{prov['gpu']}, FP16"],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "- **Recall**: fraction of real obstacles detected. A miss is what causes a collision.",
        "- **False alarms per frame**: detections on free road where no obstacle exists.",
        "- **IoU** (Intersection over Union): box overlap area divided by combined area.",
        "- **Latency**: model inference time per frame; p95 is the slowest 5%.",
        "",
        "## Recall overall",
        "",
        *md_table(["", "Obstacles", *rec_cols], recall_rows({"All": r["recall_overall"]})),
        "## Recall by distance",
        "",
        *md_table(["Distance", "Obstacles", *rec_cols],
                  recall_rows(r["recall_by_distance"], list(r["recall_by_distance"]))),
        "## Recall by obstacle group",
        "",
        *md_table(["Group", "Obstacles", *rec_cols], recall_rows(r["recall_by_group"])),
        "## Recall by obstacle type",
        "",
        *md_table(["Type", "Obstacles", *rec_cols], recall_rows(r["recall_by_type"])),
        "## False alarms on free road",
        "",
        *md_table(["Threshold", "Total", "Per frame"], [
            [t, v["total"], f"{v['per_frame']:.2f}"]
            for t, v in r["false_alarms_on_free_road"].items()
        ]),
        "## Latency",
        "",
        *md_table(["Median (ms)", "p95 (ms)"],
                  [[r["latency_ms"]["median"], r["latency_ms"]["p95"]]]),
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


def write_comparison() -> None:
    """Generate COMPARISON.md: every run side by side, from their results.json.

    Numbers only, at the lowest confidence threshold. The best value in each
    row is bold: highest for recall, lowest for false alarms and latency.
    """
    runs = {
        p.name: json.loads((p / "results.json").read_text())
        for p in sorted(OUT_DIR.iterdir()) if (p / "results.json").exists()
    }
    if not runs:
        return
    names = list(runs)
    t = str(min(next(iter(runs.values()))["config"]["conf_thresholds"]))

    row = best_row

    def recall_section(key: str, order: list[str]) -> list[str]:
        rows = []
        for item in order:
            counts = {r[key][item]["obstacles"] for r in runs.values() if item in r[key]}
            values = [r[key][item]["recall"].get(t) if item in r[key] else None for r in runs.values()]
            rows.append(row(f"{item} (n={max(counts)})", values, True, pct))
        return md_table(["", *names], rows)

    first = next(iter(runs.values()))
    groups = sorted(first["recall_by_group"], key=lambda k: -first["recall_by_group"][k]["obstacles"])
    types = sorted(first["recall_by_type"], key=lambda k: -first["recall_by_type"][k]["obstacles"])

    out = [
        "# Lost and Found obstacle benchmark: run comparison",
        "",
        "Generated automatically from every `results/<run>/results.json` by "
        "`benchmark_lost_and_found.py`. Do not edit by hand. Each run's full "
        "setup and results are in its own `results/<run>/RESULTS.md`.",
        "",
        f"Recall and false alarms at confidence threshold {t}. Best value per row in bold.",
        "",
        "## Runs",
        "",
        *md_table(["Run", "Weights", "Vocabulary", "Input size", "Git commit"], [
            [
                f"`{n}`", f"`{r['config']['weights']}`",
                f"{len(r['config']['prompts'])} prompts" if r["config"].get("prompts") else "COCO 80",
                r["config"]["imgsz"], f"`{r['provenance']['git_commit']}`",
            ]
            for n, r in runs.items()
        ]),
        "## Summary",
        "",
        *md_table(["", *names], [
            row("Recall, all obstacles", [r["recall_overall"]["recall"].get(t) for r in runs.values()], True, pct),
            row("False alarms per frame",
                [r["false_alarms_on_free_road"][t]["per_frame"] for r in runs.values()], False, lambda v: f"{v:.2f}"),
            row("Latency median (ms)", [r["latency_ms"]["median"] for r in runs.values()], False, str),
            row("Latency p95 (ms)", [r["latency_ms"]["p95"] for r in runs.values()], False, str),
        ]),
        "## Recall by distance",
        "",
        *recall_section("recall_by_distance", list(first["recall_by_distance"])),
        "## Recall by obstacle group",
        "",
        *recall_section("recall_by_group", groups),
        "## Recall by obstacle type",
        "",
        *recall_section("recall_by_type", types),
    ]
    path = OUT_DIR.parent / "COMPARISON.md"
    path.write_text("\n".join(out))
    print(f"regenerated {path}")


def main() -> None:
    if REPORT_ONLY:
        for run_dir in sorted(p for p in OUT_DIR.iterdir() if (p / "results.json").exists()):
            write_report(run_dir)
            print(f"regenerated {run_dir / 'RESULTS.md'}")
        write_comparison()
        return

    frames = list_frames()
    if not frames:
        raise SystemExit("No frames found.")
    for weights, run_name in RUNS:
        evaluate(weights, run_name, frames)
    write_comparison()


if __name__ == "__main__":
    main()
