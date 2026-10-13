"""Score a collision-risk model on our development sets, as it would run live (Modal GPU).

Sets (raw frames already cached in the Volume, 8 per second, 224x224):
    bdd_val        BDD100K val, 500 normal-driving clips: every warning is false
    nexar_public   Nexar test, Public half, 667 clips (334 crash, 333 normal)
A reading every 0.5 s, each from the 16 frames (2 s) ending then, plus one at the
very end of each clip (the moment Nexar's official metric asks about).

Metrics (computed on this PC from the saved readings):
    false warnings per hour on bdd_val, and crashes warned on nexar_public
    (a warning starting at most 4 s before the crash, before the clip ends),
    for each threshold and 1 or 2 readings in a row; crashes warned at a fixed
    false-warning budget; and Nexar's official mAP on Public (end-of-clip reading).

Models (--model):
    baseline_badas_open   BADAS-Open as published (the number to beat)

Resume-safe: each clip's readings are saved to the Volume when done, a re-run skips
them. Results go to src/risk/runs/<model>/results/eval/ (metrics.json + RESULTS.md).

RUN IT (see current_modal_commands.txt):

    python -m modal run src\\risk\\eval_risk.py --limit 4       # timed test: 4 clips per set
    python -m modal run src\\risk\\eval_risk.py                 # everything
"""

# (No "from __future__ import annotations": Modal needs real types for its class parameters.)
import csv
import json
import sys
import time
from pathlib import Path

import modal

LOCAL = modal.is_local()
REPO = Path(__file__).resolve().parents[2] if LOCAL else Path("/root")

# ---- CONFIG ----
VOLUME = "safe-distance-data"
GPU, GPU_PRICE_H = "A100-40GB", 2.10
MAX_CONTAINERS = 4
CPU_CORES = 8                          # per container: room for CLIPS_PER_CONTAINER preprocessing at once
CLIPS_PER_CONTAINER = 3                # clips handled at the same time in one container (keeps the GPU busy)
BADAS_REPO = "nexar-ai/BADAS-Open"
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"
HF_CACHE = "/data/models/hf"
SETS = {"bdd_val": ["cache/badas224/bdd100k_videos_100k_val"],
        "nexar_public": ["cache/badas224/nexar_test-public_positive", "cache/badas224/nexar_test-public_negative"]}
SAVE_DIR = "results/risk_eval"         # in the Volume: <SAVE_DIR>/<model>/<set>/<clip>.json
RESIZE, CROP = 292, 256                # V-JEPA 2 video processor: shortest edge 292 (bilinear), centre crop 256
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
MAX_DIFF_OK = 0.01                     # fast preprocessing must give readings within this of BADAS's own
FAST_PREP = False                      # GPU preprocessing: only 1.2x faster and up to 0.04 off, so BADAS's own is used
STEP = 4                               # a reading every 4 frames at 8 per second = every 0.5 s
BATCH = 16                             # windows per GPU pass
FP16 = True
TEMPERATURE = 2.0                      # BADAS's output softening
THRESHOLDS = [0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99]
CONFIRMS = [1, 2]                      # readings in a row over the threshold
COUNT_WINDOW_S = 4.0                   # a warning counts for a crash if it starts at most 4 s before it
BUDGETS = [10, 30, 60]                 # false warnings per hour: crashes warned at this budget
SOLUTION = Path(r"C:\safe-distance-data\nexar\meta\solution.csv")    # official labels (id,target,Usage,group)
# ----------------

app = modal.App("safe-distance-risk-eval")
volume = modal.Volume.from_name(VOLUME)
from huggingface_hub import get_token  # noqa: E402  (this PC's Hugging Face login, passed for this run only)

secret = modal.Secret.from_dict({"HF_TOKEN": get_token() or ""})
image = (modal.Image.debian_slim(python_version="3.12").apt_install("libgl1", "libglib2.0-0")
         .pip_install("torch==2.6.0", "torchvision==0.21.0", index_url="https://download.pytorch.org/whl/cu124")
         .pip_install("transformers==4.53.0", "huggingface_hub", "opencv-python-headless", "numpy", "pillow",
                      "albumentations", "psutil", "nvidia-ml-py")
         .env({"HF_HOME": HF_CACHE}))


@app.function(image=image, volumes={"/data": volume})
def clip_list(limit: int) -> list[tuple[str, str]]:
    """(set name, cached frames path inside the Volume) for every clip; `limit` per folder if > 0."""
    jobs = []
    for name, folders in SETS.items():
        for f in folders:
            files = sorted(Path("/data", f).glob("*.npy"))
            files = [p for p in files if not p.name.endswith(".part.npy")]
            jobs += [(name, f"{f}/{p.name}") for p in (files[:limit] if limit else files)]
    return jobs


@app.cls(image=image, gpu=GPU, cpu=CPU_CORES, memory=32768, volumes={"/data": volume}, secrets=[secret],
         timeout=3600, max_containers=MAX_CONTAINERS, retries=2)
@modal.concurrent(max_inputs=CLIPS_PER_CONTAINER)   # several clips at once: CPU preprocessing overlaps GPU work
class Scorer:
    model_name: str = modal.parameter()

    @modal.enter()
    def load(self) -> None:
        """Load the model once per container, and start sampling how busy the GPU is."""
        import socket
        import threading

        import pynvml
        from huggingface_hub import snapshot_download

        self.host, self.t_up, self.util = socket.gethostname(), time.time(), []
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)

        def sample():                                   # GPU busy % every 0.5 s: (time, percent)
            while True:
                self.util.append((time.time(), pynvml.nvmlDeviceGetUtilizationRates(h).gpu))
                time.sleep(0.5)
        threading.Thread(target=sample, daemon=True).start()

        if self.model_name != "baseline_badas_open":
            raise ValueError(f"unknown model {self.model_name}")
        repo = Path(snapshot_download(BADAS_REPO, allow_patterns=["src/*", "src/**/*", "weights/*"]))
        sys.path.insert(0, str(repo / "src"))
        from models.vjepa import VJEPAModel
        self.badas = VJEPAModel(model_name=BASE_MODEL, checkpoint_path=str(repo / "weights" / "badas_open.pth"),
                                frame_count=16, img_size=224, target_fps=8.0, use_sliding_window=False)
        self.badas.load()

    @modal.method()
    def series(self, set_name: str, frames_path: str) -> dict:
        """Readings through one clip: [(time in s at the window's end, probability), ...]."""
        import numpy as np
        import torch

        clip = Path(frames_path).stem
        saved = Path("/data", SAVE_DIR, self.model_name, set_name, f"{clip}.json")
        if saved.exists():
            return {"set": set_name, "clip": clip, "series": json.loads(saved.read_text()), "gpu_s": 0.0,
                    "host": self.host, "up_s": round(time.time() - self.t_up, 1), "gpu_busy": None}
        t0 = time.time()
        frames = np.load(f"/data/{frames_path}")
        out = self._readings(frames, fast=FAST_PREP)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text(json.dumps(out))
        volume.commit()
        busy = [u for t, u in list(self.util) if t >= t0]           # GPU busy % while this clip ran
        return {"set": set_name, "clip": clip, "series": out, "gpu_s": round(time.time() - t0, 2),
                "host": self.host, "up_s": round(time.time() - self.t_up, 1),
                "gpu_busy": round(sum(busy) / len(busy)) if busy else None}

    def _prep_fast(self, frames):
        """BADAS's preprocessing (V-JEPA 2 video processor: resize to 292 bilinear, center crop 256,
        scale to 0..1, ImageNet normalize), done ONCE per frame on the GPU instead of per window on the CPU."""
        import torch
        import torch.nn.functional as F

        x = torch.from_numpy(frames).to(self.badas.device).permute(0, 3, 1, 2).float()   # n, 3, 224, 224
        x = F.interpolate(x, size=(RESIZE, RESIZE), mode="bilinear", align_corners=False, antialias=True)
        o = (RESIZE - CROP) // 2
        x = x[:, :, o:o + CROP, o:o + CROP] / 255.0
        mean = torch.tensor(MEAN, device=x.device).view(1, 3, 1, 1)
        std = torch.tensor(STD, device=x.device).view(1, 3, 1, 1)
        return (x - mean) / std                                                               # n, 3, 256, 256

    def _readings(self, frames, fast: bool) -> list:
        """Probability every STEP frames (+ one at the clip's end), each from the 16 frames ending there."""
        import torch

        ends = list(range(16, len(frames) + 1, STEP))
        if ends and ends[-1] != len(frames):
            ends.append(len(frames))                   # one reading at the very end of the clip
        prepped = self._prep_fast(frames) if fast else None
        out = []
        for i in range(0, len(ends), BATCH):
            if fast:
                batch = torch.stack([prepped[e - 16:e] for e in ends[i:i + BATCH]])          # B, 16, 3, 256, 256
            else:                                      # BADAS's own processor (slow, CPU), for --check
                batch = torch.stack([self.badas.processor(videos=frames[e - 16:e], return_tensors="pt")
                                     ["pixel_values_videos"].squeeze(0) for e in ends[i:i + BATCH]])
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=FP16):
                logits = self.badas.model(batch.to(self.badas.device)).float()
            probs = torch.softmax(logits / TEMPERATURE, dim=1)[:, 1]
            out += [(round(e / 8.0, 3), round(float(p), 5)) for e, p in zip(ends[i:i + BATCH], probs)]
        return out

    @modal.method()
    def check(self, frames_path: str) -> dict:
        """Fast GPU preprocessing vs BADAS's own processor on one clip: same readings? how much faster?"""
        import numpy as np
        import torch

        frames = np.load(f"/data/{frames_path}")
        torch.cuda.synchronize()
        t = time.time()
        slow = self._readings(frames, fast=False)
        t_slow = time.time() - t
        t = time.time()
        fast = self._readings(frames, fast=True)
        torch.cuda.synchronize()
        t_fast = time.time() - t
        d = np.abs(np.array([p for _, p in slow]) - np.array([p for _, p in fast]))
        return {"clip": frames_path, "readings": len(fast), "max_prob_difference": round(float(d.max()), 5),
                "mean_prob_difference": round(float(d.mean()), 6), "seconds_badas_processor": round(t_slow, 1),
                "seconds_fast": round(t_fast, 1), "speedup": round(t_slow / max(t_fast, 1e-6), 1)}


# ---------------------------------------------------------------- metrics (this PC)

def episodes(series: list, thr: float, confirm: int) -> list[float]:
    """Start times of warnings: `confirm` readings in a row over `thr` (a run counts once)."""
    starts, run = [], 0
    for t, p in series:
        run = run + 1 if p > thr else 0
        if run == confirm:
            starts.append(t)
    return starts


def average_precision(labels: list[int], scores: list[float]) -> float:
    """Same as sklearn's average_precision_score (tied scores form one step)."""
    pairs = sorted(zip(scores, labels), key=lambda p: -p[0])
    total, tp, fp, ap, prev, i = sum(labels), 0, 0, 0.0, 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            tp += pairs[j][1]
            fp += 1 - pairs[j][1]
            j += 1
        recall = tp / total
        ap += (recall - prev) * tp / (tp + fp)
        prev, i = recall, j
    return ap


def metrics(bdd: dict, nexar: dict) -> dict:
    """All numbers, from the readings of both sets."""
    sys.path.insert(0, str(REPO / "src/ttc/benchmarks/nexar"))
    from score_badas_series import metadata                # clip id -> positive, seconds from clip end to crash
    meta = metadata()
    solution = [r for r in csv.DictReader(SOLUTION.open()) if r["Usage"] == "Public"]
    hours = sum(s[-1][0] - s[0][0] + 0.5 for s in bdd.values() if s) / 3600
    crashes = {c: s for c, s in nexar.items() if meta[c]["positive"]}

    def point(thr: float, confirm: int) -> tuple[int, int]:
        false = sum(len(episodes(s, thr, confirm)) for s in bdd.values())
        warned = 0
        for c, s in crashes.items():
            end = s[-1][0]
            event = end + meta[c]["tta"]
            warned += any(event - COUNT_WINDOW_S <= t <= end for t in episodes(s, thr, confirm))
        return false, warned

    rows = []
    for thr in THRESHOLDS:
        for c in CONFIRMS:
            false, warned = point(thr, c)
            rows.append({"threshold": thr, "in_a_row": c, "false_warnings": false,
                         "false_per_hour": round(false / hours, 1), "crashes_warned": round(warned / len(crashes), 4)})
    # Best share of crashes warned while staying within each false-warning budget (fine threshold grid).
    budget = {}
    grid = [round(0.5 + 0.001 * k, 3) for k in range(500)]
    for c in CONFIRMS:
        pts = [(thr, *point(thr, c)) for thr in grid]
        for b in BUDGETS:
            ok = [(w, thr, f) for thr, f, w in pts if f / hours <= b]
            w, thr, f = max(ok) if ok else (0, None, None)
            budget[f"{b}_per_hour_{c}_in_a_row"] = {"crashes_warned": round(w / len(crashes), 4), "threshold": thr,
                                                    "false_per_hour": round(f / hours, 1) if f is not None else None}
    # Nexar's official metric on Public: AP per time-before-crash group, averaged (end-of-clip reading).
    aps = []
    for g in sorted({r["group"] for r in solution}):
        sub = [r for r in solution if r["group"] == g]
        aps.append(average_precision([int(r["target"]) for r in sub],
                                     [nexar[r["id"]][-1][1] if nexar.get(r["id"]) else 0.0 for r in sub]))
    return {"bdd_val_clips": len(bdd), "bdd_val_hours": round(hours, 2), "nexar_public_clips": len(nexar),
            "nexar_public_crashes": len(crashes), "nexar_public_map": round(sum(aps) / len(aps), 4),
            "nexar_public_missing": sum(1 for r in solution if r["id"] not in nexar),
            "at_budget": budget, "rows": rows}


def report(model: str, m: dict) -> str:
    """RESULTS.md text (generated from metrics.json; never edited by hand)."""
    lines = [f"# {model}: live readings on the development sets", "",
             "Generated by src/risk/eval_risk.py from metrics.json. Do not edit by hand.", "",
             f"BDD100K val: {m['bdd_val_clips']} normal clips, {m['bdd_val_hours']} h. Nexar Public: "
             f"{m['nexar_public_clips']} clips ({m['nexar_public_crashes']} crashes; a warning counts if it starts at "
             f"most {COUNT_WINDOW_S:g} s before the crash).", "",
             f"**Nexar official mAP (Public, end-of-clip reading): {m['nexar_public_map']}**", "",
             "## Crashes warned at a fixed false-warning budget", "",
             "| Budget (false per hour) | Readings in a row | Crashes warned | Threshold | False per hour |",
             "|---|---|---|---|---|"]
    for k, v in m["at_budget"].items():
        b, c = k.split("_per_hour_")
        lines.append(f"| {b} | {c.split('_')[0]} | {v['crashes_warned'] * 100:.1f}% | {v['threshold']} | "
                     f"{v['false_per_hour']} |")
    lines += ["", "## Every threshold", "",
              "| Warn when risk > | Readings in a row | Crashes warned (Nexar Public) | False per hour (BDD100K val) |",
              "|---|---|---|---|"]
    for r in m["rows"]:
        lines.append(f"| {r['threshold']} | {r['in_a_row']} | {r['crashes_warned'] * 100:.1f}% | "
                     f"{r['false_per_hour']} ({r['false_warnings']}) |")
    return "\n".join(lines) + "\n"


def clock(sec: float) -> str:
    """Seconds as 1h02m03s / 2m03s / 3s."""
    sec = int(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s" if m else f"{s}s"


@app.local_entrypoint()
def main(model: str = "baseline_badas_open", limit: int = 0, check: bool = False) -> None:
    jobs = clip_list.remote(limit)
    per_set = {s: sum(j[0] == s for j in jobs) for s in SETS}
    print(f"model={model}  {len(jobs):,} clips {per_set}  {MAX_CONTAINERS} x {GPU}")
    scorer = Scorer(model_name=model)
    # Safety check first: the fast GPU preprocessing must match BADAS's own on a crash and a normal clip.
    for probe in ((next(j for j in jobs if j[0] == "nexar_public"),) if check else ()):
        c = scorer.check.remote(probe[1])
        print(f"check {c['clip']}: max difference {c['max_prob_difference']} over {c['readings']} readings, "
              f"{c['seconds_badas_processor']} s -> {c['seconds_fast']} s ({c['speedup']}x faster)", flush=True)
        if c["max_prob_difference"] > MAX_DIFF_OK:
            raise SystemExit(f"fast preprocessing differs by more than {MAX_DIFF_OK}: stopping")
    start, res, failed, gpu_s, new = time.time(), {s: {} for s in SETS}, [], 0.0, 0
    up = {}                                            # container -> its uptime so far (s): what Modal bills
    busy = []                                          # GPU busy % of each newly scored clip
    for r in scorer.series.starmap(jobs, return_exceptions=True, order_outputs=False):
        if isinstance(r, Exception):
            failed.append(repr(r))
            print(f"  FAILED: {r!r}", flush=True)
        else:
            res[r["set"]][r["clip"]] = r["series"]
            gpu_s += r["gpu_s"]
            new += r["gpu_s"] > 0
            up[r["host"]] = max(up.get(r["host"], 0.0), r["up_s"])
            if r["gpu_busy"] is not None:
                busy.append(r["gpu_busy"])
        done = sum(len(v) for v in res.values()) + len(failed)
        if done % 25 == 0 or done == len(jobs):
            el = time.time() - start
            recent = busy[-25:]
            print(f"  {done:,}/{len(jobs):,} clips  new={new} failed={len(failed)}  elapsed={clock(el)}  "
                  f"ETA={clock((len(jobs) - done) * el / done)}  containers={len(up)}  "
                  f"GPU busy={sum(recent) / len(recent) if recent else 0:.0f}% (last {len(recent)} clips)  "
                  f"cost so far=${sum(up.values()) / 3600 * GPU_PRICE_H:.2f}", flush=True)
    out = REPO / "src/risk/runs" / model / "results" / ("eval_test" if limit else "eval")
    out.mkdir(parents=True, exist_ok=True)
    for s, v in res.items():
        (out / f"series_{s}.json").write_text(json.dumps(v))
    run = {"model": model, "clips": len(jobs), "failed": len(failed), "failures": failed,
           "wall_s": round(time.time() - start), "clip_seconds": round(gpu_s),
           "container_seconds": round(sum(up.values())), "containers": len(up),
           "gpu_busy_mean_pct": round(sum(busy) / len(busy)) if busy else None,
           "cost_usd_estimate": round(sum(up.values()) / 3600 * GPU_PRICE_H, 3)}
    print(f"GPU busy while scoring: {run['gpu_busy_mean_pct']}% on average; "
          f"{run['containers']} containers, {run['container_seconds']} s billed")
    if limit and new:
        # clip seconds overlap CLIPS_PER_CONTAINER-fold inside a container; GPU seconds per clip = that / overlap
        full = 1167 * gpu_s / new / CLIPS_PER_CONTAINER   # 500 BDD val + 667 Nexar Public
        run["full_run_estimate"] = {"cost_usd": round(full / 3600 * GPU_PRICE_H, 2),
                                    "wall_s": round(full / MAX_CONTAINERS)}
        print(f"full run estimate (1,167 clips): ${run['full_run_estimate']['cost_usd']:.2f}, "
              f"about {clock(run['full_run_estimate']['wall_s'])} with {MAX_CONTAINERS} x {GPU} "
              f"(plus model loading)")
    (out / "run.json").write_text(json.dumps(run, indent=1))
    if not limit:
        m = metrics(res["bdd_val"], res["nexar_public"])
        (out / "metrics.json").write_text(json.dumps(m, indent=1))
        (out / "RESULTS.md").write_text(report(model, m))
        print(report(model, m))
    print(f"saved {out}")
