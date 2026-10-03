"""GPU part of the Nexar crash benchmark, on Modal: save raw per-frame results.

For each clip it runs detection (YOLO26s-seg) + tracking (BoT-SORT) + distance
(Metric3D v2 Small FP16, both on the plain image and with CLAHE) at 10 frames
per second, and saves everything per frame. NO warning logic runs here: the
filter, warning rules, day/night rule and scoring all run afterwards on the
local CPU from these files (score_nexar.py), so they can change without
re-running the GPU.

Saved per clip (Modal Volume, /data/results/<RUN>/<split>/<clip>.json.gz):
    clip info: size, fps, focal length assumed, time window processed
    per processed frame: time (s), mean brightness (0-255), and per tracked
    object: track ID, class, confidence, box (x1, y1, x2, y2), distance (m)
    from Metric3D plain and with CLAHE (10th percentile inside the mask).

Clips: every collision / near-miss clip (train/positive) from 6 s before its
event to 1 s after, and 100 random normal-driving clips (train/negative), 20 s
of each, to count false warnings. The CLAHE depth is only computed on darker
frames (mean brightness under 100), to save GPU time.

RUN IT (PowerShell, from the repo root; Modal account ahmad-yonis):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run src\\ttc\\benchmarks\\nexar\\collect_modal.py --limit 2     # test on 2 clips
    .venv\\Scripts\\modal.exe run src\\ttc\\benchmarks\\nexar\\collect_modal.py               # everything
"""

from __future__ import annotations

import modal

# ---- CONFIG ----
RUN = "v1"                       # results folder name; change to keep older results
VOLUME = "safe-distance-data"
GPU = "L4"                       # small GPU: Metric3D Small and YOLO need little memory
MAX_CONTAINERS = 4               # clips processed in parallel (at most 4 GPUs at once)
PROCESS_FPS = 10.0               # frames per second processed (the filter was tuned at 10)
# Collision clips: from 6 s before the event (2 s for the filter to settle, then
# the 4 s in which a warning matters) to 1 s after it.
BEFORE_EVENT_S, AFTER_EVENT_S = 6.0, 1.0
NEGATIVE_SAMPLE = 100            # normal-driving clips, to count false warnings ...
NEGATIVE_WINDOW_S = (10.0, 30.0)  # ... 20 s of each (100 x 20 s = 33 min of driving)
CLAHE_BELOW_BRIGHTNESS = 100     # run the CLAHE depth only on frames darker than this (0-255)
SEED = 0
HFOV_DEG = 110.0                 # assumed dashcam horizontal field of view (lens unknown)
# ----------------

app = modal.App("safe-distance-nexar-collect")
volume = modal.Volume.from_name(VOLUME)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install("torch==2.6.0", "torchvision==0.21.0", "xformers==0.0.29.post3",
                 index_url="https://download.pytorch.org/whl/cu124")
    .pip_install("ultralytics==8.4.155", "numpy==2.5.2", "timm==1.0.30", "mmengine==0.10.7",
                 "mmcv-lite==2.2.0", "einops==0.8.2", "lap==0.5.13", "scipy", "pyyaml")
    .env({"SAFE_DISTANCE_MODELS": "/data/models", "YOLO_CONFIG_DIR": "/tmp/ultralytics"})
    .add_local_dir("src", "/root/app/src", ignore=["**/__pycache__", "**/results*", "**/*.csv"])
    .add_local_file("weights/yolo26s-seg.pt", "/root/app/weights/yolo26s-seg.pt")
)


@app.function(image=image, gpu=GPU, volumes={"/data": volume}, timeout=3600, max_containers=MAX_CONTAINERS)
def collect(split: str, clip: str, t_start: float, t_end: float) -> dict:
    """Process one clip and save its per-frame results to the Volume."""
    import gzip
    import json
    import math
    import os
    import sys
    import time
    from pathlib import Path

    import cv2

    os.chdir("/root/app")
    sys.path.insert(0, "/root/app")
    from src.detection.detector import Detector
    from src.distance.camera import Camera
    from src.distance.depth_models import BACKENDS, DepthModelEstimator, EnhancedBackend
    from src.tracking.tracker import Tracker

    out = Path(f"/data/results/{RUN}/{split}/{clip}.json.gz")
    if out.exists():
        return {"clip": clip, "skipped": True}
    cap = cv2.VideoCapture(f"/data/nexar/{split}/{clip}.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w, h = int(cap.get(3)), int(cap.get(4))
    step = max(1, round(fps / PROCESS_FPS))
    fx = (w / 2) / math.tan(math.radians(HFOV_DEG) / 2)
    camera = Camera(fx=fx, fy=fx, cx=w / 2, cy=h / 2, height_m=1.3, pitch_rad=0.0)

    detector = Detector(weights="weights/yolo26s-seg.pt", conf=0.25, imgsz=1280)
    tracker = Tracker(detector, "botsort", track_low_thresh=0.05)
    base = BACKENDS["metric3d-v2-small-fp16"]()
    plain = DepthModelEstimator(base, "p10")
    clahe = DepthModelEstimator(EnhancedBackend(base, "clahe4"), "p10")

    frames, k, start = [], 0, time.time()
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(int(t_start * fps) - 1, 0))
    k = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    while True:
        ok, img = cap.read()
        if not ok:
            break
        t = k / fps
        k += 1
        if t > t_end:
            break
        if t < t_start or (k - 1) % step:
            continue
        dets = tracker.update(img)
        brightness = float(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).mean())
        d_plain = plain.estimate(img, dets, camera)
        # CLAHE (contrast boost) depth only on darker frames, where a night rule could use it.
        d_clahe = clahe.estimate(img, dets, camera) if brightness < CLAHE_BELOW_BRIGHTNESS else [None] * len(dets)
        frames.append({
            "t": round(t, 3),
            "brightness": round(brightness, 1),
            "objects": [{"id": d.track_id, "cls": d.class_name, "conf": round(d.confidence, 3),
                         "box": [round(v, 1) for v in (d.x1, d.y1, d.x2, d.y2)],
                         "d": None if a is None else round(a, 3), "d_clahe": None if b is None else round(b, 3)}
                        for d, a, b in zip(dets, d_plain, d_clahe) if d.track_id is not None],
        })
    result = {"clip": clip, "split": split, "run": RUN, "width": w, "height": h, "fps": fps, "step": step,
              "clahe_below_brightness": CLAHE_BELOW_BRIGHTNESS,
              "focal_px": round(fx, 2), "hfov_deg": HFOV_DEG, "window_s": [t_start, t_end],
              "frames": frames, "seconds": round(time.time() - start, 1)}
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt") as f:
        json.dump(result, f)
    volume.commit()
    return {"clip": clip, "frames": len(frames), "seconds": result["seconds"]}


@app.function(image=image, volumes={"/data": volume})
def clip_list(limit: int) -> list[tuple]:
    """(split, clip, start, end) for every clip to process, read from the metadata."""
    import csv
    import random

    jobs = []
    for r in csv.DictReader(open("/data/nexar/train/positive/metadata.csv")):
        if r["time_of_event"]:
            e = float(r["time_of_event"])
            jobs.append(("train/positive", r["file_name"][:-4], max(e - BEFORE_EVENT_S, 0.0), e + AFTER_EVENT_S))
    negatives = sorted(r["file_name"][:-4] for r in csv.DictReader(open("/data/nexar/train/negative/metadata.csv")))
    for clip in random.Random(SEED).sample(negatives, NEGATIVE_SAMPLE):
        jobs.append(("train/negative", clip, *NEGATIVE_WINDOW_S))
    if limit:   # test run: a few of each kind
        jobs = [j for j in jobs if j[0] == "train/positive"][:limit] + \
               [j for j in jobs if j[0] == "train/negative"][:limit]
    return jobs


@app.local_entrypoint()
def main(limit: int = 0) -> None:
    jobs = clip_list.remote(limit)
    print(f"{len(jobs)} clips to process")
    # One clip first, alone: it downloads the Metric3D weights into the Volume
    # once, so the parallel containers find them there instead of racing.
    first = collect.remote(*jobs[0])
    print(first)
    done = [first]
    for r in collect.starmap(jobs[1:], return_exceptions=True):
        done.append(r)
        print(r if isinstance(r, dict) else f"FAILED: {r}", flush=True)
    ok = [r for r in done if isinstance(r, dict) and not r.get("skipped")]
    if ok:
        frames = sum(r["frames"] for r in ok)
        secs = sum(r["seconds"] for r in ok)
        print(f"{len(ok)} clips, {frames} frames, {secs / max(frames, 1) * 1000:.0f} ms per frame on {GPU}")
