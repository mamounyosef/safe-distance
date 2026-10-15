"""Score a collision-risk model on our development sets, as it would run live (Modal GPU).

Sets (raw frames already cached in the Volume, 8 per second, 224x224):
    bdd_val        BDD100K val, 500 normal-driving clips: every warning is false
    nexar_public   Nexar test, Public half, 667 clips (334 crash, 333 normal)
    bdd_train      (--sets bdd_train) BDD100K train, our 3,000 clips: only to find possible real
                   near-misses for a person to review before training (no metrics)
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
    python -m modal run src\\risk\\eval_risk.py --sets bdd_train   # cleaning: rank BDD100K train clips by risk
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
CLIPS_PER_CONTAINER = 5                # clips handled at the same time in one container (keeps the GPU busy)
COMMIT_EVERY = 20                      # save to the Volume every N clips (each save took ~1.8 s per clip)
BADAS_REPO = "nexar-ai/BADAS-Open"
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"
HF_CACHE = "/data/models/hf"
SETS = {"bdd_val": ["cache/badas224/bdd100k_videos_100k_val"],
        "nexar_public": ["cache/badas224/nexar_test-public_positive", "cache/badas224/nexar_test-public_negative"],
        "bdd_train": ["cache/badas224/bdd100k_videos_100k_train"]}
SET_GROUPS = {"dev": ["bdd_val", "nexar_public"], "bdd_train": ["bdd_train"]}   # --sets picks one group
SAVE_DIR = "results/risk_eval_v3"      # in the Volume (v2: GPU preprocessing; all readings made the same way): <SAVE_DIR>/<model>/<set>/<clip>.json
RESIZE, CROP = 292, 256                # V-JEPA 2 video processor: shortest edge 292 (bilinear), centre crop 256
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
MAX_DIFF_OK = 0.03                     # worst reading gap allowed vs the exact reference (uncompiled, full precision, BADAS's processor)
MEAN_DIFF_OK = 0.005                   # average reading gap allowed vs the exact reference
COMPILE = True                         # torch.compile the model (2.6x faster on A100; about 4.5 min to compile)
FAST_PREP = True                       # BADAS's processor once per clip on the GPU (check() must match per-window)
STEP = 4                               # a reading every 4 frames at 8 per second = every 0.5 s
STEP_BY_SET = {"bdd_train": 8}         # cleaning only needs each clip's riskiest moment: every 1 s (half the cost)
BATCH = 32                             # windows per GPU pass
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
         # Compile cache on the container's own disk: several containers sharing one cache folder in the
         # Volume crashed ("FakeTensorMode" error). Each container copies the saved cache in at start (see load).
         .env({"HF_HOME": HF_CACHE, "TORCHINDUCTOR_CACHE_DIR": "/tmp/torchinductor",
               "TORCHINDUCTOR_FX_GRAPH_CACHE": "1", "TORCHINDUCTOR_AUTOGRAD_CACHE": "1",
               "TORCHINDUCTOR_COMPILE_THREADS": "1"}))
INDUCTOR_SAVED = "/data/cache/torchinductor"   # the compile cache kept in the Volume between runs


@app.function(image=image, volumes={"/data": volume})
def clip_list(limit: int, names: list[str]) -> list[tuple[str, str]]:
    """(set name, cached frames path inside the Volume) for every clip of the named sets; `limit` per folder if > 0."""
    jobs = []
    for name in names:
        folders = SETS[name]
        for f in folders:
            files = sorted(Path("/data", f).glob("*.npy"))
            files = [p for p in files if not p.name.endswith(".part.npy")]
            jobs += [(name, f"{f}/{p.name}") for p in (files[:limit] if limit else files)]
    return jobs


@app.cls(image=image, gpu=GPU, cpu=CPU_CORES, memory=32768, volumes={"/data": volume}, secrets=[secret],
         timeout=3600, max_containers=MAX_CONTAINERS, min_containers=MAX_CONTAINERS, retries=2)   # all GPUs start at once
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
        self.lock = threading.Lock()                    # one clip at a time on the model; others load/prep/save
        self.save_lock, self.unsaved = threading.Lock(), 0
        self.net = self.badas.model
        if COMPILE:
            # torch.compile fuses V-JEPA 2's ~60k tiny GPU operations per call (2.6x faster, readings within
            # 0.0025). Compiled once here for a fixed batch of BATCH windows (shorter batches are padded).
            import shutil

            import torch
            saved = Path(INDUCTOR_SAVED)
            if saved.exists():                          # private copy of the saved cache: no sharing while compiling
                shutil.copytree(saved, "/tmp/torchinductor", dirs_exist_ok=True)
            self.net = torch.compile(self.badas.model)
            t = time.time()
            dummy = torch.zeros(BATCH, 16, 3, CROP, CROP, device=self.badas.device)
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=FP16):
                for _ in range(2):
                    self.net(dummy)
            torch.cuda.synchronize()
            print(f"compiled in {time.time() - t:.0f} s", flush=True)
            if not saved.exists():                      # first compile ever: keep the cache for later runs
                shutil.copytree("/tmp/torchinductor", saved)
                volume.commit()

    @modal.exit()
    def flush(self) -> None:
        """Save what is left when the container stops."""
        volume.commit()

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
        tm = {"load_s": time.time() - t0}                         # where this clip's time goes
        out = self._readings(frames, fast=FAST_PREP, tm=tm, step=STEP_BY_SET.get(set_name, STEP))
        t1 = time.time()
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text(json.dumps(out))
        with self.save_lock:                            # Volume save every COMMIT_EVERY clips (resume points)
            self.unsaved += 1
            if self.unsaved >= COMMIT_EVERY:
                volume.commit()
                self.unsaved = 0
        tm["save_s"] = time.time() - t1
        busy = [u for t, u in list(self.util) if t >= t0]           # GPU busy % while this clip ran
        return {"set": set_name, "clip": clip, "series": out, "gpu_s": round(time.time() - t0, 2),
                "host": self.host, "up_s": round(time.time() - self.t_up, 1),
                "gpu_busy": round(sum(busy) / len(busy)) if busy else None,
                "times": {k: round(v, 2) for k, v in tm.items()}}

    def _prep_fast(self, frames):
        """BADAS's preprocessing (V-JEPA 2 video processor: resize to 292 bilinear, center crop 256,
        scale to 0..1, ImageNet normalize), done ONCE per frame on the GPU instead of per window on the CPU."""
        import torch

        # BADAS's own processor, run ONCE on all the clip's frames. It treats every frame
        # separately (resize, crop, scale, normalise), so slicing 16 frames out of the result gives the
        # same input as running it per window; check() verifies that on a real clip.
        # On the GPU: differs from the CPU version only by rounding (one brightness step out of 255 here and
        # there), moving readings by up to 0.003, the same size as half precision (FP16) which we already use.
        return self.badas.processor(videos=frames, return_tensors="pt",
                                    device=str(self.badas.device))["pixel_values_videos"][0]   # n, 3, 256, 256

    def _readings(self, frames, fast: bool, tm: dict | None = None, step: int = STEP) -> list:
        """Probability every `step` frames (+ one at the clip's end), each from the 16 frames ending there."""
        import torch

        ends = list(range(16, len(frames) + 1, step))
        if ends and ends[-1] != len(frames):
            ends.append(len(frames))                   # one reading at the very end of the clip
        tm = {} if tm is None else tm
        t = time.time()
        prepped = self._prep_fast(frames) if fast else None
        torch.cuda.synchronize()
        tm["prep_s"], tm["model_s"] = time.time() - t, 0.0
        out = []
        for i in range(0, len(ends), BATCH):
            if fast:
                batch = torch.stack([prepped[e - 16:e] for e in ends[i:i + BATCH]])          # B, 16, 3, 256, 256
            else:                                      # BADAS's own processor (slow, CPU), for --check
                batch = torch.stack([self.badas.processor(videos=frames[e - 16:e], return_tensors="pt")
                                     ["pixel_values_videos"].squeeze(0) for e in ends[i:i + BATCH]])
            n = len(batch)
            if COMPILE and fast and n < BATCH:          # pad to the compiled batch size (no recompiling)
                batch = torch.cat([batch, batch[-1:].expand(BATCH - n, *batch.shape[1:])])
            t = time.time()
            # Fast path: compiled model in half precision. Reference path (--check): plain model, full precision.
            net = self.net if fast else self.badas.model
            with self.lock, torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=FP16 and fast):
                logits = net(batch.to(self.badas.device)).float()[:n]
            probs = torch.softmax(logits / TEMPERATURE, dim=1)[:, 1].cpu()
            tm["model_s"] += time.time() - t
            out += [(round(e / 8.0, 3), round(float(p), 5)) for e, p in zip(ends[i:i + BATCH], probs)]
        return out

    @modal.method()
    def profile(self, frames_path: str) -> dict:
        """Time one model call per batch size, with the attention implementation in use (diagnosis only)."""
        import numpy as np
        import torch

        frames = np.load(f"/data/{frames_path}")
        x = self._prep_fast(frames)
        bb = self.badas.model.backbone
        res = {"attn_implementation": getattr(bb.config, "_attn_implementation", None),
               "model_dtype": str(next(self.badas.model.parameters()).dtype)}
        for b in (1, 8, 32):
            batch = torch.stack([x[i:i + 16] for i in range(b)])
            for _ in range(2):                                   # warm-up, then time
                torch.cuda.synchronize()
                t = time.time()
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=FP16):
                    self.badas.model(batch)
                torch.cuda.synchronize()
            res[f"batch_{b}_s"] = round(time.time() - t, 3)
            res[f"batch_{b}_windows_per_s"] = round(b / (time.time() - t), 1)
        with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
                                                torch.profiler.ProfilerActivity.CUDA]) as prof:
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=FP16):
                self.badas.model(torch.stack([x[i:i + 16] for i in range(32)]))
            torch.cuda.synchronize()
        res["top_ops"] = prof.key_averages().table(sort_by="cpu_time_total", row_limit=12)
        return res

    @modal.method()
    def speedtest(self, frames_path: str) -> dict:
        """Readings per second and readings on one clip for: current (fp32 weights + autocast), half-precision
        weights, and torch.compile of each. Diagnosis only; the model in this container is left unchanged."""
        import copy

        import numpy as np
        import torch

        frames = np.load(f"/data/{frames_path}")
        x = self._prep_fast(frames)
        ends = list(range(16, len(x) + 1, STEP))
        batch = torch.stack([x[e - 16:e] for e in ends[:32]])          # 32 windows of a real clip

        def run(model, half: bool, autocast: bool) -> tuple[float, np.ndarray]:
            inp = batch.half() if half else batch
            for i in range(4):                                         # 2 warm-up calls (compiles), 2 timed
                if i == 2:
                    torch.cuda.synchronize()
                    t = time.time()
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=autocast):
                    logits = model(inp).float()
            torch.cuda.synchronize()
            wps = 2 * len(inp) / (time.time() - t)
            return round(wps, 1), torch.softmax(logits / TEMPERATURE, dim=1)[:, 1].cpu().numpy()

        res = {}
        base_wps, base_p = run(self.badas.model, half=False, autocast=True)
        res["current"] = {"windows_per_s": base_wps}
        variants = {"half_weights": (False, True), "compile_current": (True, False), "compile_half": (True, True)}
        for name, (compiled, half) in variants.items():
            m = copy.deepcopy(self.badas.model)
            if half:
                m = m.half()
            if compiled:
                m = torch.compile(m)
            try:
                t = time.time()
                wps, p = run(m, half=half, autocast=not half)
                res[name] = {"windows_per_s": wps, "speedup": round(wps / base_wps, 2),
                             "max_prob_difference": round(float(np.abs(p - base_p).max()), 5),
                             "first_calls_s": round(time.time() - t, 1)}
            except Exception as e:  # noqa: BLE001
                res[name] = {"failed": repr(e)[:300]}
            del m
            torch.cuda.empty_cache()
        return res

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
        # Also compare the model inputs themselves for the last window.
        own = self.badas.processor(videos=frames[-16:], return_tensors="pt")["pixel_values_videos"][0]
        ours = self._prep_fast(frames)[-16:].float().cpu()
        return {"clip": frames_path, "readings": len(fast), "max_prob_difference": round(float(d.max()), 5),
                "max_input_difference": round(float((own - ours).abs().max()), 5),
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
def main(model: str = "baseline_badas_open", limit: int = 0, check: bool = False,
         profile: bool = False, speedtest: bool = False, sets: str = "dev") -> None:
    names = SET_GROUPS[sets]
    jobs = clip_list.remote(limit, names)
    per_set = {s: sum(j[0] == s for j in jobs) for s in names}
    print(f"model={model}  {len(jobs):,} clips {per_set}  {MAX_CONTAINERS} x {GPU}")
    scorer = Scorer(model_name=model)
    if speedtest:                                      # diagnosis only: faster model variants, then stop
        print(json.dumps(scorer.speedtest.remote(next(j for j in jobs if j[0] == "nexar_public")[1]), indent=1))
        return
    if profile:                                        # diagnosis only: time the model, then stop
        r = scorer.profile.remote(next(j for j in jobs if j[0] == "nexar_public")[1])
        print(r.pop("top_ops"))
        print(json.dumps(r, indent=1))
        return
    # Safety check first: once-per-clip GPU preprocessing must match BADAS's per-window CPU path.
    probe_clip = clip_list.remote(1, ["nexar_public"])[0] if jobs and jobs[0][0] != "nexar_public" else None
    for probe in ((probe_clip or next(j for j in jobs if j[0] == "nexar_public"),) if (check or FAST_PREP) else ()):
        c = scorer.check.remote(probe[1])
        print(f"check {c['clip']}: inputs differ by {c['max_input_difference']}, readings by {c['max_prob_difference']} at most, {c['mean_prob_difference']} on average, over {c['readings']} readings, "
              f"{c['seconds_badas_processor']} s -> {c['seconds_fast']} s ({c['speedup']}x faster)", flush=True)
        if c["max_prob_difference"] > MAX_DIFF_OK or c["mean_prob_difference"] > MEAN_DIFF_OK:
            raise SystemExit(f"fast path differs from the exact reference by more than {MAX_DIFF_OK} (worst) or {MEAN_DIFF_OK} (average): stopping")
    start, res, failed, gpu_s, new = time.time(), {s: {} for s in names}, [], 0.0, 0
    up = {}                                            # container -> its uptime so far (s): what Modal bills
    busy = []                                          # GPU busy % of each newly scored clip
    times = []                                         # per clip: seconds loading, preprocessing, model, saving
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
            if r.get("times"):
                times.append(r["times"])
        done = sum(len(v) for v in res.values()) + len(failed)
        if done % 25 == 0 or done == len(jobs):
            el = time.time() - start
            recent = busy[-25:]
            print(f"  {done:,}/{len(jobs):,} clips  new={new} failed={len(failed)}  elapsed={clock(el)}  "
                  f"ETA={clock((len(jobs) - done) * el / done)}  containers={len(up)}  "
                  f"GPU busy={sum(recent) / len(recent) if recent else 0:.0f}% (last {len(recent)} clips)  "
                  f"cost so far=${sum(up.values()) / 3600 * GPU_PRICE_H:.2f}", flush=True)
    out = REPO / "src/risk/runs" / model / "results" / (("eval_test" if limit else "eval") if sets == "dev" else sets)
    out.mkdir(parents=True, exist_ok=True)
    for s, v in res.items():
        (out / f"series_{s}.json").write_text(json.dumps(v))
    run = {"model": model, "clips": len(jobs), "failed": len(failed), "failures": failed,
           "wall_s": round(time.time() - start), "clip_seconds": round(gpu_s),
           "container_seconds": round(sum(up.values())), "containers": len(up),
           "gpu_busy_mean_pct": round(sum(busy) / len(busy)) if busy else None,
           "cost_usd_estimate": round(sum(up.values()) / 3600 * GPU_PRICE_H, 3)}
    if times:
        run["seconds_per_clip"] = {k: round(sum(x[k] for x in times) / len(times), 2) for k in times[0]}
        print("seconds per clip (mean):", run["seconds_per_clip"])
    print(f"GPU busy while scoring: {run['gpu_busy_mean_pct']}% on average; "
          f"{run['containers']} containers, {run['container_seconds']} s billed")
    if limit and new:
        # clip seconds overlap CLIPS_PER_CONTAINER-fold inside a container; GPU seconds per clip = that / overlap
        n_full = {"dev": 1167, "bdd_train": 3000}[sets]   # dev: 500 BDD val + 667 Nexar Public
        full = n_full * gpu_s / new / CLIPS_PER_CONTAINER
        run["full_run_estimate"] = {"cost_usd": round(full / 3600 * GPU_PRICE_H, 2),
                                    "wall_s": round(full / MAX_CONTAINERS)}
        print(f"full run estimate ({n_full:,} clips): ${run['full_run_estimate']['cost_usd']:.2f}, "
              f"about {clock(run['full_run_estimate']['wall_s'])} with {MAX_CONTAINERS} x {GPU} "
              f"(plus model loading)")
    (out / "run.json").write_text(json.dumps(run, indent=1))
    if sets == "bdd_train":
        # Cleaning: rank clips by their highest risk reading (candidates for a person to review, never auto-removed)
        top = sorted(((max(p for _, p in s), max(s, key=lambda r: r[1])[0], c) for c, s in res["bdd_train"].items() if s),
                     reverse=True)
        (out / "ranked.json").write_text(json.dumps([{"clip": c, "max_risk": p, "at_s": t} for p, t, c in top], indent=1))
        for thr in (0.9, 0.95, 0.98, 0.99):
            print(f"clips with a reading over {thr}: {sum(p > thr for p, _, _ in top)} of {len(top)}")
    elif not limit:
        m = metrics(res["bdd_val"], res["nexar_public"])
        (out / "metrics.json").write_text(json.dumps(m, indent=1))
        (out / "RESULTS.md").write_text(report(model, m))
        print(report(model, m))
    print(f"saved {out}")
