"""Benchmark multi-object tracking on the KITTI tracking sequences.

KITTI tracking labels every car, van, pedestrian and cyclist with its true ID
in every frame of 21 continuous driving sequences. Running our detector plus
tracker over them and comparing IDs gives the standard tracking metrics:

    ID switches   how often a tracked object's ID wrongly changes. Lower is better.
    IDF1          ID F1 score: how consistently each real object keeps ONE ID over
                  its whole life, 0 to 100%. Higher is better. The best single
                  number for "does the same car stay the same car".
    MOTA          Multiple Object Tracking Accuracy: 1 minus (misses + false
                  alarms + ID switches) divided by the number of real objects.
                  Can go negative. Higher is better.
    mostly tracked / mostly lost
                  share of real objects followed for at least 80% / at most 20%
                  of their life.

Scoring is done by py-motmetrics, the standard open-source implementation.
Evaluated classes are Car and Pedestrian, as in the official KITTI benchmark.

Output: one folder per run under results/ next to this file, each with
results.json (source of truth) and a generated RESULTS.md; plus a generated
COMPARISON.md across all runs.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_kitti_tracking.py
    .venv\\Scripts\\python.exe src\\tracking\\benchmarks\\kitti_tracking\\benchmark_kitti_tracking.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import motmetrics as mm
import numpy as np

# Make the repo root importable, so "src" resolves when this file is run
# directly. This file is at src/tracking/benchmarks/kitti_tracking/, four
# levels down.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src.detection.benchmarks.common import best_row, iou, md_table, provenance
from src.detection.detector import Detector
from src.tracking.tracker import Tracker

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Dataset root, as written by scripts/download_kitti_tracking.py.
DATA = Path("data/kitti_tracking/training")

# Sequences to evaluate, "0000" to "0020". None = all 21.
SEQUENCES = None

# Runs to perform, as (tracker method, run name). Each writes results/<run name>/.
RUNS = [
    ("bytetrack", "yolo26s-seg_bytetrack"),
    ("botsort", "yolo26s-seg_botsort"),
]

# Detector settings, same meaning as in src/tracking/scripts/track_video.py.
WEIGHTS = "weights/yolo26s-seg.pt"
IMGSZ = 1280
CONF = 0.05

# Tracker settings, same values and meaning as in track_video.py. Note that
# KITTI is recorded at 10 frames per second, so TRACK_BUFFER = 30 frames
# keeps a lost track alive for 3 seconds here (1 second on a 30 fps video).
TRACKER_SETTINGS = {
    "track_high_thresh": 0.25,
    "track_low_thresh": 0.05,
    "new_track_thresh": 0.25,
    "track_buffer": 30,
    "match_thresh": 0.8,
}

# A tracked box matches a real object if their IoU (Intersection over Union)
# is at least this. 0.5 is the standard for tracking benchmarks.
MIN_IOU = 0.5

# Objects and tracked boxes shorter than this are ignored, as in the official
# KITTI evaluation: too small to judge reliably.
MIN_HEIGHT = 25

# Stop each sequence after this many frames. 0 = whole sequence.
MAX_FRAMES_PER_SEQ = 0

# Where run folders are written: results/ next to this file.
OUT_DIR = Path(__file__).resolve().parent / "results"

# True: skip inference and only regenerate reports from existing results.json.
REPORT_ONLY = False

# ----------------------------------------------------------------------------

# For each evaluated class: which KITTI labels are the real objects, which
# similar labels are ignored (tracking them is neither rewarded nor penalised),
# and which of our predicted class names count as tracking that class.
# Pedestrian also ignores Cyclist: our detector sees a rider as a "person", and
# KITTI labels riders as Cyclist, so a correct person box on a cyclist would
# otherwise count as a false alarm. This is stricter than nothing and more
# lenient than the official devkit; it is stated in every report.
EVAL_CLASSES = {
    "Car": {"gt": {"Car"}, "ignore": {"Van"}, "preds": {"car", "van"}},
    "Pedestrian": {"gt": {"Pedestrian"}, "ignore": {"Person", "Cyclist"}, "preds": {"person", "pedestrian"}},
}

METRICS = [
    "num_frames", "num_unique_objects", "num_objects", "mota", "motp", "idf1",
    "num_switches", "num_fragmentations", "mostly_tracked", "partially_tracked",
    "mostly_lost", "num_false_positives", "num_misses", "recall", "precision",
]


def read_labels(path: Path) -> dict[int, list[dict]]:
    """Read one KITTI tracking label file, grouped by frame number."""
    frames: dict[int, list[dict]] = defaultdict(list)
    for line in path.read_text().splitlines():
        f = line.split()
        if not f:
            continue
        frames[int(f[0])].append({
            "id": int(f[1]),
            "type": f[2],
            "box": tuple(float(v) for v in f[6:10]),
        })
    return frames


def height(box: tuple) -> float:
    return box[3] - box[1]


def inside_fraction(box: tuple, region: tuple) -> float:
    """Fraction of box's area that lies inside region."""
    area = (box[2] - box[0]) * (box[3] - box[1])
    ix = max(0.0, min(box[2], region[2]) - max(box[0], region[0]))
    iy = max(0.0, min(box[3], region[3]) - max(box[1], region[1]))
    return ix * iy / area if area > 0 else 0.0


def frame_update(acc: mm.MOTAccumulator, labels: list[dict], tracked: list, spec: dict) -> None:
    """Score one frame for one class."""
    dontcare = [g["box"] for g in labels if g["type"] == "DontCare"]
    valid = [g for g in labels if g["type"] in spec["gt"] and height(g["box"]) >= MIN_HEIGHT]
    ignored = [g["box"] for g in labels
               if g["type"] in spec["ignore"]
               or (g["type"] in spec["gt"] and height(g["box"]) < MIN_HEIGHT)]

    hyps = []
    for d in tracked:
        if d.track_id is None or d.class_name not in spec["preds"]:
            continue
        box = (d.x1, d.y1, d.x2, d.y2)
        if height(box) < MIN_HEIGHT:
            continue
        # A box that does not match a real object, but mostly sits inside an
        # ignored object or a DontCare region, is left out entirely. "Mostly
        # inside" rather than IoU, because a person box on a cyclist covers
        # only the rider, the top part of KITTI's rider-plus-bicycle box: on
        # sequence 0000 IoU caught 51 such boxes, "mostly inside" caught 214.
        if not any(iou(box, g["box"]) >= MIN_IOU for g in valid):
            if any(iou(box, b) >= MIN_IOU or inside_fraction(box, b) >= 0.5 for b in ignored):
                continue
            if any(inside_fraction(box, r) >= 0.5 for r in dontcare):
                continue
        hyps.append((d.track_id, box))

    # Distance for py-motmetrics: 1 - IoU, or NaN where the pair cannot match.
    dist = np.full((len(valid), len(hyps)), np.nan)
    for i, g in enumerate(valid):
        for j, (_, box) in enumerate(hyps):
            o = iou(g["box"], box)
            if o >= MIN_IOU:
                dist[i, j] = 1.0 - o
    acc.update([g["id"] for g in valid], [h[0] for h in hyps], dist)


def to_plain(value):
    """numpy scalars -> plain Python numbers, for JSON."""
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else round(float(value), 4)
    return value


def evaluate(method: str, run_name: str, sequences: list[str]) -> None:
    print(f"\n=== {run_name} ===")
    detector = Detector(weights=WEIGHTS, conf=CONF, imgsz=IMGSZ)
    accs = {cls: [] for cls in EVAL_CLASSES}
    times = []

    for seq in sequences:
        labels = read_labels(DATA / "label_02" / f"{seq}.txt")
        frames = sorted((DATA / "image_02" / seq).glob("*.png"))
        if MAX_FRAMES_PER_SEQ:
            frames = frames[:MAX_FRAMES_PER_SEQ]
        tracker = Tracker(detector, method=method, **TRACKER_SETTINGS)  # fresh IDs per sequence
        seq_accs = {cls: mm.MOTAccumulator(auto_id=True) for cls in EVAL_CLASSES}

        for path in frames:
            img = cv2.imread(str(path))
            t0 = time.perf_counter()
            tracked = tracker.update(img)
            times.append((time.perf_counter() - t0) * 1000.0)
            frame_labels = labels.get(int(path.stem), [])
            for cls, spec in EVAL_CLASSES.items():
                frame_update(seq_accs[cls], frame_labels, tracked, spec)

        for cls in EVAL_CLASSES:
            accs[cls].append(seq_accs[cls])
        print(f"  sequence {seq}: {len(frames)} frames", flush=True)

    mh = mm.metrics.create()
    by_class = {}
    for cls in EVAL_CLASSES:
        summary = mh.compute_many(accs[cls], metrics=METRICS, names=sequences, generate_overall=True)
        table = {name: {m: to_plain(summary.loc[name, m]) for m in METRICS} for name in summary.index}
        # motp here is the mean (1 - IoU) of matched pairs; report the mean IoU instead.
        for row in table.values():
            row["mean_match_iou"] = None if row["motp"] is None else round(1.0 - row.pop("motp"), 4)
        by_class[cls] = {"overall": table.pop("OVERALL"), "per_sequence": table}

    results = {
        "benchmark": "kitti_tracking",
        "provenance": provenance(),
        "dataset": {
            "name": "KITTI Tracking",
            "source": "https://www.cvlibs.net/datasets/kitti/eval_tracking.php",
            "split": "training (the only split with public labels)",
            "sequences": sequences,
            "frames": len(times),
            "frame_rate_fps": 10,
        },
        "config": {
            "run_name": run_name,
            "weights": WEIGHTS,
            "prompts": detector.prompts,
            "imgsz": IMGSZ,
            "conf": CONF,
            "tracker": method,
            "tracker_settings": TRACKER_SETTINGS,
            "min_iou": MIN_IOU,
            "min_height_px": MIN_HEIGHT,
            "classes": {c: {k: sorted(v) for k, v in s.items()} for c, s in EVAL_CLASSES.items()},
            "scoring": f"py-motmetrics {mm.__version__}",
        },
        "latency_ms": {
            "median": round(float(np.median(times)), 1),
            "p95": round(float(np.percentile(times, 95)), 1),
        },
        "metrics": by_class,
    }

    run_dir = OUT_DIR / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    write_report(run_dir)

    for cls, v in by_class.items():
        o = v["overall"]
        print(f"  {cls:>10}: IDF1 {o['idf1']:.1%}  MOTA {o['mota']:.1%}  "
              f"ID switches {o['num_switches']}  recall {o['recall']:.1%}")
    print(f"  latency median {results['latency_ms']['median']} ms")
    print(f"wrote {run_dir}")


def fmt_pct(v) -> str:
    return "-" if v is None else f"{v:.1%}"


def mt_ml(o: dict) -> tuple[str, str]:
    """Mostly tracked / mostly lost as a share of unique objects."""
    n = o["num_unique_objects"] or 1
    return f"{o['mostly_tracked'] / n:.0%}", f"{o['mostly_lost'] / n:.0%}"


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md for one run, entirely from its results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov = r["config"], r["dataset"], r["provenance"]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""
    settings = ", ".join(f"{k}={v}" for k, v in cfg["tracker_settings"].items())

    overall_rows = []
    for cls, v in r["metrics"].items():
        o = v["overall"]
        mt, ml = mt_ml(o)
        overall_rows.append([
            cls, fmt_pct(o["idf1"]), fmt_pct(o["mota"]), o["num_switches"], fmt_pct(o["recall"]),
            fmt_pct(o["precision"]), mt, ml, o["num_unique_objects"], o["num_objects"],
        ])

    out = [
        f"# KITTI tracking benchmark: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_kitti_tracking.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["Detector", f"`{cfg['weights']}`, input size {cfg['imgsz']}, confidence {cfg['conf']}"],
            ["Tracker", f"{cfg['tracker']} ({settings})"],
            ["Dataset", f"[{ds['name']}]({ds['source']}), {ds['split']}"],
            ["Sequences / frames", f"{len(ds['sequences'])} / {ds['frames']} at {ds['frame_rate_fps']} fps"],
            ["Match rule", f"IoU >= {cfg['min_iou']}; objects and boxes under {cfg['min_height_px']} px ignored"],
            ["Ignored labels", "; ".join(f"{c}: {', '.join(s['ignore'])}" for c, s in cfg["classes"].items())],
            ["Scoring", cfg["scoring"]],
            ["Hardware", f"{prov['gpu']}, FP16"],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Metrics",
        "",
        "- **IDF1**: how consistently each real object keeps one ID over its whole life. Best single number.",
        "- **MOTA**: 1 minus (misses + false alarms + ID switches) / real objects. Can be negative.",
        "- **ID switches**: times a tracked object's ID wrongly changed. Lower is better.",
        "- **Mostly tracked / lost**: share of real objects followed for at least 80% / at most 20% of their life.",
        "- **Latency**: detection plus tracking per frame; p95 is the slowest 5%.",
        "",
        "## Overall",
        "",
        *md_table(["Class", "IDF1", "MOTA", "ID switches", "Recall", "Precision",
                   "Mostly tracked", "Mostly lost", "Unique objects", "Object-frames"], overall_rows),
    ]
    for cls, v in r["metrics"].items():
        rows = []
        for seq, o in v["per_sequence"].items():
            rows.append([seq, o["num_frames"], fmt_pct(o["idf1"]), fmt_pct(o["mota"]),
                         o["num_switches"], o["num_unique_objects"]])
        out += [f"## Per sequence: {cls}", "",
                *md_table(["Sequence", "Frames", "IDF1", "MOTA", "ID switches", "Unique objects"], rows)]
    out += [
        "## Latency",
        "",
        *md_table(["Median (ms)", "p95 (ms)"], [[r["latency_ms"]["median"], r["latency_ms"]["p95"]]]),
        "## Known limitations",
        "",
        "- Not the official KITTI devkit: same classes, IoU and height rules, scored with py-motmetrics.",
        "- Pedestrian also ignores Cyclist labels (see Setup), which is more lenient than the official rules.",
        "- The detector was not trained on KITTI; tracking quality is bounded by detection quality.",
        "- Daytime only, Karlsruhe, 2011.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


def write_comparison() -> None:
    """Generate COMPARISON.md: every run side by side, from their results.json."""
    runs = {
        p.name: json.loads((p / "results.json").read_text())
        for p in sorted(OUT_DIR.iterdir()) if (p / "results.json").exists()
    }
    if not runs:
        return
    names = list(runs)
    rows = []
    for cls in next(iter(runs.values()))["metrics"]:
        ov = [r["metrics"][cls]["overall"] for r in runs.values()]
        rows += [
            best_row(f"{cls}: IDF1", [o["idf1"] for o in ov], True, fmt_pct),
            best_row(f"{cls}: MOTA", [o["mota"] for o in ov], True, fmt_pct),
            best_row(f"{cls}: ID switches", [o["num_switches"] for o in ov], False, str),
            best_row(f"{cls}: recall", [o["recall"] for o in ov], True, fmt_pct),
            best_row(f"{cls}: precision", [o["precision"] for o in ov], True, fmt_pct),
        ]
    rows += [
        best_row("Latency median (ms)", [r["latency_ms"]["median"] for r in runs.values()], False, str),
        best_row("Latency p95 (ms)", [r["latency_ms"]["p95"] for r in runs.values()], False, str),
    ]
    out = [
        "# KITTI tracking benchmark: run comparison",
        "",
        "Generated automatically from every `results/<run>/results.json` by `benchmark_kitti_tracking.py`. "
        "Do not edit by hand. Each run's full setup and per-sequence results are in `results/<run>/RESULTS.md`.",
        "",
        "Best value per row in bold.",
        "",
        "## Runs",
        "",
        *md_table(["Run", "Detector", "Tracker", "Frames", "Git commit"], [
            [f"`{n}`", f"`{r['config']['weights']}`", r["config"]["tracker"], r["dataset"]["frames"],
             f"`{r['provenance']['git_commit']}`"]
            for n, r in runs.items()
        ]),
        "## Results",
        "",
        *md_table(["", *names], rows),
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

    sequences = SEQUENCES or sorted(p.name for p in (DATA / "image_02").iterdir() if p.is_dir())
    if not sequences:
        raise SystemExit(f"No sequences found in {DATA}. Run scripts/download_kitti_tracking.py first.")
    for method, run_name in RUNS:
        evaluate(method, run_name, sequences)
    write_comparison()


if __name__ == "__main__":
    main()
