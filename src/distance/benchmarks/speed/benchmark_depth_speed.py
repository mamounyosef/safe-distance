"""Benchmark the speed of each depth model (and the detector) on this GPU.

The accuracy benchmarks also record timings, but those can be distorted by
anything else using the GPU at the time. This benchmark measures speed on its
own, under controlled conditions:

    - one image at a time (batch size 1), as in the car: each camera frame
      must be processed as soon as it arrives;
    - after warm-up passes, which include loading and GPU start-up costs;
    - on real frames from each dataset, at their native size, since input
      size drives cost (KITTI 1242x375, nuScenes 1600x900, Lost and Found
      2048x1024);
    - timing covers the whole step from camera image to a depth map in
      metres at full resolution: preprocessing, the network, post-processing.

The GPU's state (utilisation, memory already in use by other processes) is
recorded at the start of every model, so a distorted run can be spotted.

This is PyTorch in FP16 (16-bit floating point) on the development GPU, not
TensorRT on a Jetson. It ranks the models and tells how far each is from a
real-time budget; the edge numbers need their own measurement later.

Output: results/<RUN_NAME>/results.json (source of truth) and a generated
RESULTS.md, next to this file.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\distance\\benchmarks\\speed\\benchmark_depth_speed.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import gc
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from src.detection.benchmarks.common import md_table, provenance
from src.detection.detector import Detector
from src.distance.camera import Camera
from src.distance.depth_models import BACKENDS

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

RUN_NAME = "rtx4060_pytorch_fp16"

# Depth models to time, by name from BACKENDS in src/distance/depth_models.py.
MODELS = [
    "metric3d-v2-small",
    "metric3d-v2-large",
    "metric3d-v2-small-fp16",
    "metric3d-v2-large-fp16",
    "unidepth-v2-small",
    "unidepth-v2-base",
    "unidepth-v2-large",
    "da3-metric-large",
    "depth-pro",
    "da2-metric-small",
    "da2-metric-base",
    "da2-metric-large",
    "yolo26s-depth",
]

# The detector is timed too, for the full per-frame budget.
DETECTOR_WEIGHTS = "weights/yolo26s-seg.pt"
DETECTOR_IMGSZ = 1280

# Untimed passes first, then timed passes, per model and image size.
WARMUP = 5
TIMED = 40

# Real-time budget for the verdict column: 30 frames per second = 33.3 ms per
# frame for the whole pipeline. A depth model alone must fit well inside it.
FRAME_BUDGET_MS = 1000.0 / 30.0

# ----------------------------------------------------------------------------

OUT_DIR = Path(__file__).resolve().parent / "results"


def dataset_frames() -> dict[str, tuple[list[np.ndarray], Camera]]:
    """TIMED + WARMUP distinct real frames and a camera per dataset."""
    n = TIMED + WARMUP
    out = {}

    kitti = REPO / "data/kitti"
    ids = (kitti / "subset.txt").read_text().split()[:n]
    out["KITTI 1242x375"] = (
        [cv2.imread(str(kitti / "training/image_2" / f"{i}.png")) for i in ids],
        Camera.from_kitti_calib(kitti / "training/calib" / f"{ids[0]}.txt"),
    )

    nus = Path(r"C:\safe-distance-data\nuscenes-mini")
    files = sorted((nus / "samples/CAM_FRONT").glob("*.jpg"))[:n]
    # nuScenes CAM_FRONT intrinsics are near-identical across its scenes; the
    # values of the first calibration are used (fx 1266.4, cx 816.3, cy 491.5).
    calib = json.loads((nus / "v1.0-mini/calibrated_sensor.json").read_text())
    K = next(c["camera_intrinsic"] for c in calib if c["camera_intrinsic"] and abs(c["camera_intrinsic"][0][2] - 816) < 20)
    out["nuScenes 1600x900"] = (
        [cv2.imread(str(f)) for f in files],
        Camera(fx=K[0][0], fy=K[1][1], cx=K[0][2], cy=K[1][2], height_m=1.5),
    )

    laf = REPO / "data/lost_and_found"
    files = sorted((laf / "leftImg8bit/test/04_Maurener_Weg_8").glob("*.png"))[:n]
    stem = files[0].name.replace("_leftImg8bit.png", "")
    out["Lost and Found 2048x1024"] = (
        [cv2.imread(str(f)) for f in files],
        Camera.from_lost_and_found(laf / "camera/test/04_Maurener_Weg_8" / f"{stem}_camera.json"),
    )
    return out


def gpu_state() -> dict:
    """GPU utilisation and memory in use right now, from the driver."""
    q = subprocess.run(
        ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,clocks.sm",
         "--format=csv,noheader,nounits"], capture_output=True, text=True,
    ).stdout.strip().split(", ")
    return {"utilization_pct": int(q[0]), "memory_used_mb": int(q[1]), "memory_total_mb": int(q[2]),
            "temperature_c": int(q[3]), "sm_clock_mhz": int(q[4])}


def time_calls(fn, frames: list[np.ndarray]) -> dict:
    """Median, p95 and mean of fn(frame) over the timed frames, after warm-up."""
    for f in frames[:WARMUP]:
        fn(f)
    times = []
    for f in frames[WARMUP:]:
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        fn(f)
        torch.cuda.synchronize()
        times.append((time.perf_counter() - t0) * 1000.0)
    t = np.array(times)
    return {"median_ms": round(float(np.median(t)), 1), "p95_ms": round(float(np.percentile(t, 95)), 1),
            "mean_ms": round(float(t.mean()), 1), "fps_at_median": round(1000.0 / float(np.median(t)), 1)}


def main() -> None:
    frames = dataset_frames()
    results = {"benchmark": "depth_model_speed", "provenance": provenance(),
               "config": {"run_name": RUN_NAME, "warmup": WARMUP, "timed": TIMED, "batch_size": 1,
                          "precision": "per model, see each model's precision (PyTorch, no TensorRT)", "frame_budget_ms": round(FRAME_BUDGET_MS, 1),
                          "timing_covers": "camera image in, full-resolution depth map in metres out"},
               "models": {}}

    print("=== detector ===", flush=True)
    detector = Detector(weights=DETECTOR_WEIGHTS, conf=0.25, imgsz=DETECTOR_IMGSZ)
    state = gpu_state()
    results["detector"] = {"weights": DETECTOR_WEIGHTS, "imgsz": DETECTOR_IMGSZ, "gpu_at_start": state,
                           "by_size": {k: time_calls(detector.detect, f) for k, (f, _) in frames.items()}}
    detector = None
    gc.collect()
    torch.cuda.empty_cache()

    for name in MODELS:
        print(f"=== {name} ===", flush=True)
        state = gpu_state()
        torch.cuda.reset_peak_memory_stats()
        try:
            backend = BACKENDS[name]()
            by_size = {}
            for k, (f, cam) in frames.items():
                by_size[k] = time_calls(lambda img, cam=cam: backend.predict(img, cam), f)
                print(f"  {k}: median {by_size[k]['median_ms']} ms", flush=True)
            results["models"][name] = {"gpu_at_start": state, "uses_our_focal_length": backend.uses_focal_length,
                                       "precision": backend.precision,
                                       "peak_gpu_memory_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                                       "by_size": by_size}
        except Exception as e:  # record the failure, keep timing the others
            results["models"][name] = {"gpu_at_start": state, "error": f"{type(e).__name__}: {e}"}
            print(f"  FAILED: {e}", flush=True)
        finally:
            backend = None
            gc.collect()
            torch.cuda.empty_cache()

    run_dir = OUT_DIR / RUN_NAME
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    write_report(run_dir)
    print(f"wrote {run_dir}")


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md entirely from results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, prov = r["config"], r["provenance"]
    sizes = list(r["detector"]["by_size"])
    budget = cfg["frame_budget_ms"]
    dirty = " (with uncommitted changes)" if prov.get("git_uncommitted_changes") else ""

    def verdict(ms: float) -> str:
        return "fits" if ms <= budget / 2 else ("tight" if ms <= budget else "too slow")

    rows = []
    for name, m in sorted(r["models"].items(), key=lambda kv: kv[1].get("by_size", {}).get(sizes[1], {}).get("median_ms", 1e9)):
        if "error" in m:
            rows.append([f"`{name}`", "-", *["failed"] * len(sizes), "-", "-", m["error"][:60]])
            continue
        rows.append([f"`{name}`", m.get("precision", "-"),
                     *[f"{m['by_size'][s]['median_ms']} / {m['by_size'][s]['p95_ms']}" for s in sizes],
                     m["peak_gpu_memory_gb"], verdict(m["by_size"][sizes[1]]["median_ms"]),
                     f"{m['gpu_at_start']['utilization_pct']}% busy, {m['gpu_at_start']['memory_used_mb']} MB used"])
    det = r["detector"]
    out = [
        f"# Depth model speed: `{cfg['run_name']}`",
        "",
        "Generated automatically from `results.json` by `benchmark_depth_speed.py`. Do not edit by hand.",
        "",
        "## Setup",
        "",
        *md_table(["", ""], [
            ["GPU", prov["gpu"]],
            ["Precision", cfg["precision"]],
            ["Detector precision", "fp16"],
            ["Batch size", cfg["batch_size"]],
            ["Timing covers", cfg["timing_covers"]],
            ["Passes", f"{cfg['warmup']} warm-up (untimed), then {cfg['timed']} timed, distinct real frames"],
            ["Software", f"Python {prov['python']}, torch {prov['torch']}, ultralytics {prov['ultralytics']}"],
            ["Git commit", f"`{prov['git_commit']}`{dirty}"],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## Depth models (median / p95 ms per frame)",
        "",
        f"Verdict uses the {sizes[1]} median against a 30 fps budget of {budget} ms per frame for the",
        "whole pipeline: `fits` = under half the budget, `tight` = under the budget, `too slow` = over.",
        "",
        *md_table(["Model", "Precision", *sizes, "Peak GPU memory (GB)", "Verdict", "GPU at start"], rows),
        "## Detector, for the full per-frame budget",
        "",
        *md_table(["Detector", *sizes], [[f"`{det['weights']}` at {det['imgsz']}",
                                          *[f"{det['by_size'][s]['median_ms']} / {det['by_size'][s]['p95_ms']}" for s in sizes]]]),
        "## Known limitations",
        "",
        "- PyTorch on an RTX 4060, not TensorRT on a Jetson Orin Nano: ranks the models and shows the",
        "  distance to a real-time budget; edge timings need their own measurement.",
        "- Includes pre- and post-processing done on the CPU, which differs per model's library.",
        "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
