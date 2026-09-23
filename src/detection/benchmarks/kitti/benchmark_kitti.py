"""Benchmark road-user detection on KITTI: cars, vans, trucks, pedestrians, cyclists.

KITTI labels every vehicle and person in each image, with its 3D position in
metres measured by a laser scanner. That gives three kinds of result:

    recall by distance   fraction of real objects found, per class and per
                         distance band. The safety view, same as the Lost
                         and Found benchmark: any predicted class counts.
    AP                   Average Precision, KITTI's official score, per class
                         (Car, Pedestrian, Cyclist) and difficulty (Easy,
                         Moderate, Hard). Class-aware and strict (IoU 0.7 for
                         cars), so it is comparable with published results.
    false alarms         vehicle or person detections where nothing is there.

Terms:
    IoU        Intersection over Union: overlap area of two boxes divided by
               their combined area. 1.0 is a perfect match, 0 is none.
    precision  fraction of detections that are real objects.
    AP         area under the precision-recall curve. Computed as KITTI's
               AP|R40: precision averaged over 40 evenly spaced recall levels.

Output: one folder per run under results/ next to this file, each with
results.json (source of truth), objects.csv (one row per object) and a
generated RESULTS.md; plus a generated COMPARISON.md across all runs.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_kitti.py
    .venv\\Scripts\\python.exe src\\detection\\benchmarks\\kitti\\benchmark_kitti.py

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

# Make the repo root importable, so "src.detection" resolves when this file
# is run directly. This file is at src/detection/benchmarks/kitti/, four
# levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.detection.benchmarks.common import best_row, iou, md_table, pct, provenance
from src.detection.detector import Detector

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Dataset root and the image subset, as written by scripts/download_kitti.py.
DATA = Path("data/kitti")
SUBSET = DATA / "subset.txt"

# Runs to perform, as (weights, run name). Each run writes results/<run name>/.
RUNS = [
    ("weights/yoloe-11s-seg.pt", "yoloe-11s-seg_prompts-v2"),
    ("weights/yolo26s-seg.pt", "yolo26s-seg_coco"),
]

# Longest side fed to the model. KITTI images are 1242x375.
IMGSZ = 1280

# The detector keeps everything down to this confidence, so the AP curve is
# complete. Recall and false alarms are then reported at CONF_THRESHOLDS.
DETECT_CONF = 0.01
CONF_THRESHOLDS = [0.05, 0.10, 0.25]

# For recall by distance, an object counts as found if any prediction of any
# class overlaps it with at least this IoU.
RECALL_MIN_IOU = 0.5

# Distance bands in metres.
BANDS = [(0, 10), (10, 20), (20, 30), (30, 50), (50, 1000)]

# Stop after this many images. 0 = the whole subset.
MAX_IMAGES = 0

# Where run folders are written: results/ next to this file.
OUT_DIR = Path(__file__).resolve().parent / "results"

# True: skip inference and only regenerate reports from existing results.json.
REPORT_ONLY = False

# ----------------------------------------------------------------------------

# KITTI label types -> the class names used in the recall tables. "Misc" and
# "DontCare" are not scored.
RECALL_CLASSES = {
    "Car": "car",
    "Van": "van",
    "Truck": "truck",
    "Pedestrian": "pedestrian",
    "Person_sitting": "pedestrian",
    "Cyclist": "cyclist",
    "Tram": "tram",
}

# Official AP setup, scored on detections converted to KITTI classes by
# to_kitti_classes(). "neighbours" are similar KITTI classes whose objects are
# ignored rather than counted as false alarms (a van detected on the Car task
# is not penalised), as in the official evaluation.
AP_CLASSES = {
    "Car": {"min_iou": 0.7, "preds": {"Car"}, "neighbours": {"Van"}},
    "Pedestrian": {"min_iou": 0.5, "preds": {"Pedestrian"}, "neighbours": {"Person_sitting"}},
    "Cyclist": {"min_iou": 0.5, "preds": {"Cyclist"}, "neighbours": set()},
}

# A person counts as riding a bicycle if at least this fraction of the person's
# box lies inside the bicycle's box.
RIDER_OVERLAP = 0.3

# Official difficulty levels: (minimum box height px, maximum occlusion level,
# maximum truncation). Occlusion: 0 fully visible, 1 partly, 2 largely hidden.
DIFFICULTIES = {
    "easy": (40, 0, 0.15),
    "moderate": (25, 1, 0.30),
    "hard": (25, 2, 0.50),
}

# Other road-user classes, kept under their own names. Together with the
# converted Car, Pedestrian and Cyclist detections, these are the ones judged
# for false alarms. Other predicted classes (cones, boxes, ...) are not
# labelled in KITTI at all, so they cannot be judged here and are left out.
OTHER_ROAD_PREDS = {"truck", "bus", "motorcycle", "train"}


def to_kitti_classes(preds: list[dict]) -> list[dict]:
    """Convert our detections into KITTI's road-user classes.

    KITTI labels a cyclist as ONE box around rider and bicycle, while our
    detector outputs a separate "person" and "bicycle". So each bicycle is
    merged with the person riding it into one Cyclist box (confidence = mean
    of the two), and that person is no longer counted as a pedestrian.

    A bicycle with no rider is dropped: KITTI's "Cyclist" means a person
    riding, and parked bicycles are not labelled at all, so scoring a lone
    bicycle would wrongly count every correctly seen parked bike as a false
    alarm.
    """
    people = [p for p in preds if p["class"] == "person"]
    ridden = set()
    out = []
    for b in (p for p in preds if p["class"] == "bicycle"):
        best, best_j = 0.0, -1
        for j, p in enumerate(people):
            if j in ridden:
                continue
            px1, py1, px2, py2 = p["box"]
            area = (px2 - px1) * (py2 - py1)
            ix = max(0.0, min(px2, b["box"][2]) - max(px1, b["box"][0]))
            iy = max(0.0, min(py2, b["box"][3]) - max(py1, b["box"][1]))
            frac = ix * iy / area if area > 0 else 0.0
            if frac > best:
                best, best_j = frac, j
        if best >= RIDER_OVERLAP:
            p = people[best_j]
            ridden.add(best_j)
            box = (min(b["box"][0], p["box"][0]), min(b["box"][1], p["box"][1]),
                   max(b["box"][2], p["box"][2]), max(b["box"][3], p["box"][3]))
            out.append({"class": "Cyclist", "conf": (b["conf"] + p["conf"]) / 2, "box": box})

    for j, p in enumerate(people):
        if j not in ridden:
            out.append({**p, "class": "Pedestrian"})
    for p in preds:
        if p["class"] in ("car", "van"):
            out.append({**p, "class": "Car"})
        elif p["class"] in OTHER_ROAD_PREDS:
            out.append(p)
    return out


def parse_labels(path: Path) -> list[dict]:
    """Read one KITTI label file into a list of objects."""
    objects = []
    for line in path.read_text().splitlines():
        f = line.split()
        if not f:
            continue
        x1, y1, x2, y2 = (float(v) for v in f[4:8])
        x, z = float(f[11]), float(f[13])
        objects.append({
            "type": f[0],
            "truncated": float(f[1]),
            "occluded": int(f[2]),
            "box": (x1, y1, x2, y2),
            # Ground distance from the camera, from the laser-measured position.
            "distance": math.hypot(x, z),
        })
    return objects


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
    return {
        name: {
            "objects": len(subset),
            "recall": {
                str(t): round(sum(r["best_conf"] >= t for r in subset) / len(subset), 4)
                for t in CONF_THRESHOLDS
            },
        }
        for name, subset in groups.items()
    }


def dontcare_overlap(box: tuple, dontcare: list[tuple]) -> bool:
    """True if at least half of a detection lies inside a DontCare region."""
    area = (box[2] - box[0]) * (box[3] - box[1])
    for d in dontcare:
        ix = max(0.0, min(box[2], d[2]) - max(box[0], d[0]))
        iy = max(0.0, min(box[3], d[3]) - max(box[1], d[1]))
        if area > 0 and ix * iy / area >= 0.5:
            return True
    return False


def average_precision(images: list[dict], cls: str, difficulty: str) -> dict:
    """KITTI-style AP|R40 for one class and difficulty.

    Greedy matching by descending confidence. Objects of the class that are
    too small, hidden or cut off for this difficulty, and objects of
    neighbouring classes, are ignored: detecting them is neither rewarded nor
    penalised. Detections below the minimum height or inside DontCare regions
    are ignored too. Close to, but not byte-identical with, the official devkit.
    """
    spec = AP_CLASSES[cls]
    min_h, max_occ, max_trunc = DIFFICULTIES[difficulty]
    dets = []
    n_valid = 0
    state = []
    for idx, img in enumerate(images):
        valid, ignored = [], []
        for g in img["gt"]:
            if g["type"] == cls:
                h = g["box"][3] - g["box"][1]
                ok = h >= min_h and g["occluded"] <= max_occ and g["truncated"] <= max_trunc
                (valid if ok else ignored).append(g["box"])
            elif g["type"] in spec["neighbours"]:
                ignored.append(g["box"])
        n_valid += len(valid)
        state.append({"valid": valid, "ignored": ignored, "used_v": [False] * len(valid),
                      "used_i": [False] * len(ignored), "dontcare": img["dontcare"]})
        for p in img["preds"]:
            if p["class"] in spec["preds"]:
                dets.append((p["conf"], idx, p["box"]))

    dets.sort(key=lambda d: -d[0])
    tp, fp = [], []
    for conf, idx, box in dets:
        s = state[idx]
        best, best_j = 0.0, -1
        for j, g in enumerate(s["valid"]):
            if not s["used_v"][j]:
                o = iou(box, g)
                if o > best:
                    best, best_j = o, j
        if best >= spec["min_iou"]:
            s["used_v"][best_j] = True
            tp.append(1)
            fp.append(0)
            continue
        best, best_j = 0.0, -1
        for j, g in enumerate(s["ignored"]):
            if not s["used_i"][j]:
                o = iou(box, g)
                if o > best:
                    best, best_j = o, j
        if best >= spec["min_iou"]:
            s["used_i"][best_j] = True
            continue
        if box[3] - box[1] < min_h or dontcare_overlap(box, s["dontcare"]):
            continue
        tp.append(0)
        fp.append(1)

    if n_valid == 0:
        return {"ap": None, "objects": 0}
    ctp, cfp = np.cumsum(tp), np.cumsum(fp)
    recall = ctp / n_valid if len(ctp) else np.array([])
    precision = ctp / np.maximum(ctp + cfp, 1) if len(ctp) else np.array([])
    points = [
        float(precision[recall >= r].max()) if np.any(recall >= r) else 0.0
        for r in np.linspace(1 / 40, 1.0, 40)
    ]
    return {"ap": round(float(np.mean(points)), 4), "objects": n_valid}


def evaluate(weights: str, run_name: str, ids: list[str]) -> None:
    print(f"\n=== {run_name} ===")
    detector = Detector(weights=weights, conf=DETECT_CONF, imgsz=IMGSZ)

    images = []
    rows = []
    false_alarms = {t: 0 for t in CONF_THRESHOLDS}
    times = []

    for i, image_id in enumerate(ids, 1):
        img = cv2.imread(str(DATA / "training" / "image_2" / f"{image_id}.png"))
        gt = parse_labels(DATA / "training" / "label_2" / f"{image_id}.txt")
        dontcare = [g["box"] for g in gt if g["type"] == "DontCare"]
        labelled = [g for g in gt if g["type"] != "DontCare"]

        t0 = time.perf_counter()
        preds = [
            {"class": p.class_name, "conf": p.confidence, "box": (p.x1, p.y1, p.x2, p.y2)}
            for p in detector.detect(img)
        ]
        times.append((time.perf_counter() - t0) * 1000.0)
        road = to_kitti_classes(preds)
        images.append({"gt": labelled, "dontcare": dontcare, "preds": road})

        # Recall: any raw prediction counts, plus the merged cyclist boxes.
        pool = preds + [p for p in road if p["class"] == "Cyclist"]
        for g in labelled:
            best_conf = 0.0
            for p in pool:
                if iou(g["box"], p["box"]) >= RECALL_MIN_IOU:
                    best_conf = max(best_conf, p["conf"])
            if g["type"] in RECALL_CLASSES:
                rows.append({
                    "image": image_id,
                    "type": g["type"],
                    "class": RECALL_CLASSES[g["type"]],
                    "distance_m": round(g["distance"], 2),
                    "box_height_px": round(g["box"][3] - g["box"][1], 1),
                    "occluded": g["occluded"],
                    "truncated": g["truncated"],
                    "best_conf": round(best_conf, 3),
                })

        # False alarms: road-user detections that overlap nothing labelled.
        for p in road:
            if any(iou(p["box"], g["box"]) >= RECALL_MIN_IOU for g in labelled):
                continue
            if dontcare_overlap(p["box"], dontcare):
                continue
            for t in CONF_THRESHOLDS:
                if p["conf"] >= t:
                    false_alarms[t] += 1

        if i % 100 == 0 or i == len(ids):
            print(f"  {i}/{len(ids)} images", flush=True)

    n = len(times)
    band_order = [band_name(lo, hi) for lo, hi in BANDS]
    by_band = recall_table(rows, lambda r: band_of(r["distance_m"]))
    classes = sorted({r["class"] for r in rows}, key=lambda c: -sum(r["class"] == c for r in rows))
    by_class_band = {}
    for c in classes:
        table = recall_table([r for r in rows if r["class"] == c], lambda r: band_of(r["distance_m"]))
        by_class_band[c] = {b: table[b] for b in band_order if b in table}

    print("  computing AP ...")
    ap = {cls: {d: average_precision(images, cls, d) for d in DIFFICULTIES} for cls in AP_CLASSES}

    results = {
        "benchmark": "kitti_road_user_detection",
        "provenance": provenance(),
        "dataset": {
            "name": "KITTI Object Detection",
            "source": "https://www.cvlibs.net/datasets/kitti/eval_object.php",
            "split": "training (the only split with public labels; models were not trained on KITTI)",
            "images": n,
            "subset": f"{SUBSET.as_posix()} (random, fixed seed, see scripts/download_kitti.py)",
            "objects": len(rows),
            "distance_source": "laser-measured 3D position, ground distance sqrt(x^2 + z^2)",
        },
        "config": {
            "run_name": run_name,
            "weights": weights,
            "prompts": detector.prompts,
            "imgsz": IMGSZ,
            "detect_conf": DETECT_CONF,
            "conf_thresholds": CONF_THRESHOLDS,
            "recall_min_iou": RECALL_MIN_IOU,
            "recall_matching": "any predicted class counts",
            "ap_classes": {
                c: {"min_iou": s["min_iou"], "ignored_neighbours": sorted(s["neighbours"])}
                for c, s in AP_CLASSES.items()
            },
            "class_conversion": (
                "car and van -> Car; person -> Pedestrian; bicycle merged with its rider "
                f"(person box >= {RIDER_OVERLAP:.0%} inside the bicycle box) -> Cyclist; "
                "rider-less bicycles dropped (parked bikes are unlabelled in KITTI)"
            ),
            "ap_method": "KITTI-style AP|R40, greedy matching",
            "difficulties": {
                d: {"min_height_px": h, "max_occlusion": o, "max_truncation": t}
                for d, (h, o, t) in DIFFICULTIES.items()
            },
            "distance_bands_m": BANDS,
        },
        "latency_ms": {
            "median": round(float(np.median(times)), 1),
            "p95": round(float(np.percentile(times, 95)), 1),
        },
        "recall_overall": recall_table(rows, lambda r: "all")["all"],
        "recall_by_class": {c: recall_table(rows, lambda r: r["class"])[c] for c in classes},
        "recall_by_distance": {b: by_band[b] for b in band_order if b in by_band},
        "recall_by_class_and_distance": by_class_band,
        "average_precision": ap,
        "false_alarms": {
            str(t): {"total": false_alarms[t], "per_image": round(false_alarms[t] / n, 4)}
            for t in CONF_THRESHOLDS
        },
    }

    run_dir = OUT_DIR / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    with (run_dir / "objects.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(run_dir)

    t = str(CONF_THRESHOLDS[0])
    print(f"recall@{t}: overall {results['recall_overall']['recall'][t]:.0%}")
    for c, v in results["recall_by_class"].items():
        print(f"  {c:>10}: {v['recall'][t]:.0%}  (n={v['objects']})")
    for c, v in ap.items():
        print(f"  AP {c:>10}: " + "  ".join(
            f"{d}={x['ap']:.1%}" if x["ap"] is not None else f"{d}=-" for d, x in v.items()))
    print(f"wrote {run_dir}")


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    thresholds = [str(t) for t in cfg["conf_thresholds"]]
    t0 = thresholds[0]
    rec_cols = [f"Recall @{t}" for t in thresholds]

    def recall_rows(table: dict, order: list[str]) -> list[list]:
        return [
            [name, table[name]["objects"], *(pct(table[name]["recall"][t]) for t in thresholds)]
            for name in order if name in table
        ]

    prompts = cfg.get("prompts")
    vocabulary = (
        f"open vocabulary, {len(prompts)} prompts: " + ", ".join(f"`{p}`" for p in prompts)
        if prompts else "fixed 80 COCO (Common Objects in Context) classes"
    )
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""
    bands = list(r["recall_by_distance"])
    classes = list(r["recall_by_class"])

    ap_rows = [
        [c, *(f"{v[d]['ap']:.1%}" if v[d]["ap"] is not None else "-" for d in cfg["difficulties"]),
         *(v[d]["objects"] for d in cfg["difficulties"])]
        for c, v in r["average_precision"].items()
    ]
    diffs = [d.capitalize() for d in cfg["difficulties"]]

    out = [
        f"# KITTI road-user benchmark: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_kitti.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Model weights", f"`{cfg['weights']}`"],
            ["Vocabulary", vocabulary],
            ["Input size", cfg["imgsz"]],
            ["Dataset", f"[{ds['name']}]({ds['source']}), {ds['split']}"],
            ["Images", f"{ds['images']}, {ds['subset']}"],
            ["Objects evaluated (recall)", ds["objects"]],
            ["Ground-truth distance", ds["distance_source"]],
            ["Recall match rule", f"IoU >= {cfg['recall_min_iou']}, {cfg['recall_matching']}"],
            ["AP method", cfg["ap_method"]],
            ["Class conversion", cfg["class_conversion"]],
            ["Hardware", f"{prov['gpu']}, FP16"],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "- **Recall**: fraction of real objects detected, any predicted class. A miss is what causes a collision.",
        "- **AP** (Average Precision): KITTI's official class-aware score, precision averaged over 40 recall levels.",
        "  IoU 0.7 for Car, 0.5 for Pedestrian and Cyclist.",
        "- **Difficulty**: Easy = fully visible, box at least 40 px tall; Moderate = partly hidden, at least 25 px;",
        "  Hard = largely hidden, at least 25 px. Moderate is the standard headline number.",
        "- **False alarms**: vehicle or person detections that match nothing labelled.",
        "- **Latency**: model inference time per image; p95 is the slowest 5%.",
        "",
        "## Average Precision (official metric)",
        "",
        *md_table(["Class", *diffs, *(f"Objects ({d})" for d in diffs)], ap_rows),
        "## Recall by class",
        "",
        *md_table(["Class", "Objects", *rec_cols], recall_rows(r["recall_by_class"], classes)),
        "## Recall by distance, all classes",
        "",
        *md_table(["Distance", "Objects", *rec_cols], recall_rows(r["recall_by_distance"], bands)),
        f"## Recall by class and distance (@{t0})",
        "",
        *md_table(["Distance", *classes], [
            [b, *(
                f"{pct(r['recall_by_class_and_distance'][c][b]['recall'][t0])} "
                f"(n={r['recall_by_class_and_distance'][c][b]['objects']})"
                if b in r["recall_by_class_and_distance"][c] else "-"
                for c in classes
            )]
            for b in bands
        ]),
        "## False alarms",
        "",
        *md_table(["Threshold", "Total", "Per image"], [
            [t, v["total"], f"{v['per_image']:.2f}"] for t, v in r["false_alarms"].items()
        ]),
        "## Latency",
        "",
        *md_table(["Median (ms)", "p95 (ms)"], [[r["latency_ms"]["median"], r["latency_ms"]["p95"]]]),
        *KNOWN_LIMITATIONS,
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


# Fixed text, not numbers, so it is safe to keep in the generator.
KNOWN_LIMITATIONS = [
    "## Known limitations",
    "",
    "- **False alarms are overstated.** KITTI does not label every vehicle: far or partly visible",
    "  ones are often left out, and parked bicycles are never labelled. A correct detection of such",
    "  an object counts as a false alarm. A model that sees more (higher recall far away) is",
    "  penalised more. Compare false alarms between runs, not as an absolute rate.",
    "- **Cyclist AP is approximate.** Our detector outputs separate person and bicycle boxes; they",
    "  are merged into one box to match KITTI's rider-plus-bicycle label, which only roughly",
    "  matches how KITTI draws it.",
    "- **AP is KITTI-style, not the official devkit.** Same IoU thresholds, difficulty levels and",
    "  ignore rules, but greedy matching; expect small differences from officially reported numbers.",
    "- **Daytime only**, Karlsruhe, 2011. No night, rain or snow.",
    "",
]


def write_comparison() -> None:
    """Generate COMPARISON.md: every run side by side, from their results.json."""
    runs = {
        p.name: json.loads((p / "results.json").read_text())
        for p in sorted(OUT_DIR.iterdir()) if (p / "results.json").exists()
    }
    if not runs:
        return
    names = list(runs)
    first = next(iter(runs.values()))
    t = str(min(first["config"]["conf_thresholds"]))

    def recall_section(key: str, order: list[str]) -> list[str]:
        rows = []
        for item in order:
            counts = {r[key][item]["objects"] for r in runs.values() if item in r[key]}
            values = [r[key][item]["recall"].get(t) if item in r[key] else None for r in runs.values()]
            rows.append(best_row(f"{item} (n={max(counts)})", values, True, pct))
        return md_table(["", *names], rows)

    ap_rows = []
    for cls in first["average_precision"]:
        for d in first["average_precision"][cls]:
            values = [r["average_precision"][cls][d]["ap"] for r in runs.values()]
            ap_rows.append(best_row(f"{cls}, {d}", values, True, lambda v: f"{v:.1%}"))

    out = [
        "# KITTI road-user benchmark: run comparison",
        "",
        "Generated automatically from every `results/<run>/results.json` by `benchmark_kitti.py`. "
        "Do not edit by hand. Each run's full setup and results are in its own `results/<run>/RESULTS.md`.",
        "",
        f"Recall and false alarms at confidence threshold {t}. Best value per row in bold.",
        "",
        "## Runs",
        "",
        *md_table(["Run", "Weights", "Vocabulary", "Input size", "Images", "Git commit"], [
            [
                f"`{n}`", f"`{r['config']['weights']}`",
                f"{len(r['config']['prompts'])} prompts" if r["config"].get("prompts") else "COCO 80",
                r["config"]["imgsz"], r["dataset"]["images"], f"`{r['provenance']['git_commit']}`",
            ]
            for n, r in runs.items()
        ]),
        "## Summary",
        "",
        *md_table(["", *names], [
            best_row("Recall, all objects", [r["recall_overall"]["recall"].get(t) for r in runs.values()], True, pct),
            best_row("False alarms per image",
                     [r["false_alarms"][t]["per_image"] for r in runs.values()], False, lambda v: f"{v:.2f}"),
            best_row("Latency median (ms)", [r["latency_ms"]["median"] for r in runs.values()], False, str),
            best_row("Latency p95 (ms)", [r["latency_ms"]["p95"] for r in runs.values()], False, str),
        ]),
        "## Average Precision (official metric)",
        "",
        *md_table(["", *names], ap_rows),
        "## Recall by class",
        "",
        *recall_section("recall_by_class", list(first["recall_by_class"])),
        "## Recall by distance, all classes",
        "",
        *recall_section("recall_by_distance", list(first["recall_by_distance"])),
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

    if not SUBSET.exists():
        raise SystemExit(f"{SUBSET} not found. Run scripts/download_kitti.py first.")
    ids = SUBSET.read_text().split()
    ids = [i for i in ids if (DATA / "training" / "image_2" / f"{i}.png").exists()]
    if MAX_IMAGES:
        ids = ids[:MAX_IMAGES]
    if not ids:
        raise SystemExit("No images found.")
    for weights, run_name in RUNS:
        evaluate(weights, run_name, ids)
    write_comparison()


if __name__ == "__main__":
    main()
