"""Stage 1: fine-tune BADAS-Open with LoRA on Nexar crashes + clean normal driving (Modal, one A100 80GB).

WHAT IT DOES
    BADAS-Open reads 2 s of dashcam video (16 frames at 8 per second) and gives a crash risk between 0 and 1.
    Here it learns from:
        danger : the 706 usable Nexar train crash clips (window inside the danger zone, label 1 or ramp >= 0.7)
        safe   : 750 Nexar normal clips + 2,576 clean BDD100K train clips + the part of every crash clip that ends
                 more than 4 s before the crash (label 0)
    One epoch = ONE window from every source (4,738 windows, 15% danger), at a new random end point each epoch.
    ml_utils.py runs the loop: bf16, AdamW, warmup + cosine, gradient clipping, CSV logs, checkpoints, resume, the
    Modal launch and the sync of results back to this PC.

THE CORE PARTS (read these first; each starts with a "CORE n" banner):
    CORE 1  TrainWindows.set_epoch   which window every source gives this epoch, and its label
    CORE 2  augment                  the augmentations, one draw per window, the same on all 16 frames
    CORE 3  add_lora                 LoRA on every layer + the checks that nothing is left out
    CORE 4  batched_predict_future   BADAS's future predictor run on the whole batch at once (checked equal)
    CORE 5  RiskModel.forward        the one risk number, and the loss it is trained with
    CORE 6  validation_scores        every validation number (what picks the best epoch)

RUN IT (see current_modal_commands.txt; run make_val_windows.py once before):
    python -m modal run src\\risk\\runs\\stage1_lora\\stage1_train.py --smoke   # short test: speed, memory, cost
    python -m modal run src\\risk\\runs\\stage1_lora\\stage1_train.py           # the real run (resumes if stopped)
(Not called train.py: BADAS's own code imports a package named "train", and the names would clash.)
Results come back to src/risk/runs/stage1_lora/results/ (smoke test: results_smoke/).
"""

import csv
import json
import os
import sys
import time
import types
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset

EXP_NAME = "stage1_lora"                  # MUST equal this folder's name


def _pkg_root() -> Path:
    """src/risk (holds ml_utils.py and stage1_labels.py): /root/runs on Modal, two folders up locally."""
    for c in (Path("/root/runs"), Path(__file__).resolve().parents[2]):
        if (c / "ml_utils.py").exists():
            return c
    raise FileNotFoundError("ml_utils.py not found")


PKG_ROOT = _pkg_root()
EXP_DIR = PKG_ROOT / "runs" / EXP_NAME
sys.path.insert(0, str(PKG_ROOT))
import ml_utils as ml  # noqa: E402
import stage1_labels as L  # noqa: E402   (the label rule; shared with the demo videos)

# =====================================================================================================================
# SETTINGS: every number this run uses
# =====================================================================================================================
# ---- data (paths inside the Modal data volume, mounted at /data) ----
DATA_VOLUME, RUNS_VOLUME = "safe-distance-data", "safe-distance-runs"
CACHE = "/data/cache/badas224"                      # frames BADAS sees: 8 per second, 224x224 RGB uint8, <clip>.npy
NEXAR_CRASH_DIR = f"{CACHE}/nexar_train_positive"
NEXAR_NORMAL_DIR = f"{CACHE}/nexar_train_negative"
BDD_TRAIN_DIR = f"{CACHE}/bdd100k_videos_100k_train"
NEXAR_CRASH_META = "/data/nexar/train/positive/metadata.csv"   # time_of_alert / time_of_event per crash clip
BDD_TRAIN_CLEAN = PKG_ROOT / "data/bdd100k_ids/train_clean.txt"  # 2,576 clean clips (person-reviewed)
NEXAR_EXCLUDED = PKG_ROOT / "data/nexar_excluded.json"           # clips the person removed (camera too high)
VAL_WINDOWS = EXP_DIR / "val_windows.json"                       # the 2,202 fixed validation windows
FPS, WINDOW_FRAMES = 8, 16                          # 16 frames = 2 s of video per window
FRAME_H, FRAME_W = 224, 224                         # cached size; BADAS's processor makes 256x256 from it

# ---- model ----
BADAS_REPO = "nexar-ai/BADAS-Open"
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"
HF_CACHE = "/data/models/hf"                        # Hugging Face downloads, kept in the data volume
TEMPERATURE = 2.0                                   # BADAS: risk = softmax(logits / 2)[crash]
PREDICTOR_CHECK_TOL = 1e-3                          # batched predictor must match BADAS's own loop to this
CHECK_INPUT_SIZE = 256                              # random test clips for the start-up checks (the real size)
GRAD_CHECKPOINTING = False                          # True = far less GPU memory, about 30% slower

# ---- LoRA (agreed: every layer; the coverage check stops the run if anything is left out) ----
LORA_RANK, LORA_ALPHA, LORA_DROPOUT = 16, 32, 0.1
# LoRA on: the Conv3d patch embedding, every attention (query/key/value/proj) and MLP (fc1/fc2) Linear of the
# encoder (24 blocks) and predictor (12 blocks), and the predictor's two width-changing Linears.
LORA_TARGETS = (r".*backbone\.(encoder\.(embeddings\.patch_embeddings\.proj|layer\.\d+\.(attention\.(query|key|value|proj)|mlp\.fc[12]))"
                r"|predictor\.(embeddings\.predictor_embeddings|proj|layer\.\d+\.(attention\.(query|key|value|proj)|mlp\.fc[12])))")
EXPECTED_LORA_LAYERS = 219                          # 218 Linear + 1 Conv3d (scripts/check_lora_coverage.py)
# Trained fully (small): time-attention and head. Exact name "classifier.classifier" (plain "classifier" matches
# the inner layer too). All LayerNorms and the predictor's mask tokens are switched on as well (see add_lora).
FULLY_TRAINED = ["temporal_processor", "classifier.classifier"]

# ---- training ----
EPOCHS = 10                                         # set from the smoke test's cost estimate
BATCH_SIZE = 8                                      # windows per GPU pass (smoke test checks the memory)
ACCUM_STEPS = 4                                     # passes per weight update: 8 x 4 = 32 windows per update
LR = 1.0e-4                                         # one learning rate for every trainable weight
WEIGHT_DECAY = 0.01                                 # not on biases / LayerNorms
WARMUP_FRAC, MIN_LR_MULT = 0.05, 0.01               # 5% linear warmup, then cosine down to 1% of LR
GRAD_CLIP = 3.0
EARLY_STOP_PATIENCE = 4                             # validations without a new best, then stop
NUM_WORKERS = 8                                     # CPU processes loading + augmenting windows
VAL_BATCH_SIZE = 16
SEED = 20261017
POS_WEIGHT = None                                   # e.g. 2.0 = crash windows count twice in the loss (not used)

# ---- augmentation (one random draw per window, the same on all 16 frames) ----
AUG_P = 0.6                                         # chance of each main augmentation
CROP_MAX = 0.05                                     # crop up to 5% off each edge (then back to 224x224)
ROTATE_DEG = 2.0                                    # rotate up to +-2 degrees
BRIGHTNESS, CONTRAST, SATURATION, GAMMA = 0.15, 0.15, 0.15, 0.15   # each +-15%
BLUR_P, SHARPEN_P = 0.2, 0.2                        # light blur OR light sharpen (never both)
NOISE_P, NOISE_SIGMA = 0.15, (2.0, 5.0)             # faint noise, strength in 0-255 brightness steps
JPEG_P, JPEG_QUALITY = 0.15, (70, 90)               # mild compression
# never: horizontal flip, speed changes, cutout, mixing clips, time reversal

# ---- validation ----
THRESHOLDS = [0.5, 0.8, 0.9, 0.93, 0.95, 0.97, 0.98, 0.99, 0.993, 0.995, 0.997]
MONITOR = "ap_crash_vs_all_normal"                  # picks best.pt (see validation_scores)
GROUP_SECONDS = {0: 0.5, 1: 1.0, 2: 1.5}            # Nexar test group -> seconds before the crash

# ---- checkpoints (each holds everything needed to continue: weights, optimizer, schedule, random states) ----
KEEP_LAST_N = 10                                    # rolling: the last 10 epoch-end checkpoints
KEEP_TOP_K = 3                                      # the 3 best validations (for the live check afterwards)

# ---- Modal (prices per hour, for the cost prints) ----
GPU, TIMEOUT_HOURS = "A100-80GB", 12
CPU_CORES, MEMORY_GB = 10, 48
PRICE_H = 0.000694 * 3600 + CPU_CORES * 0.0473 + MEMORY_GB * 0.008   # GPU + CPU + memory = about $3.35 / h

# ---- smoke test (--smoke): a short run that measures speed, memory and cost ----
SMOKE_STEPS = 20                                    # weight updates, then stop
PIP = ["torch==2.6.0", "torchvision==0.21.0", "transformers==4.53.0", "peft==0.21.2", "huggingface_hub",
       "opencv-python-headless", "numpy", "pandas", "scikit-learn", "pyyaml", "matplotlib", "psutil",
       "nvidia-ml-py", "albumentations"]
# =====================================================================================================================


def cfg_for(smoke: bool) -> dict:
    """The ml_utils config, built from the settings above. The smoke test writes to results_smoke/ (never mixed
    with the real run's checkpoints)."""
    cfg = {
        "experiment": {"name": EXP_NAME, "notes": "stage 1: BADAS-Open + LoRA, Nexar + clean BDD100K"},
        "task": {"type": "binary", "targets": ["crash_risk"]},
        "metrics": {"monitor": MONITOR, "mode": "max", "threshold": 0.5},
        "model": {"name": "BADAS-Open + LoRA r16", "pretrained": BADAS_REPO},
        "reproducibility": {"seed": SEED},
        "dataloader": {"batch_size": BATCH_SIZE, "accum_steps": ACCUM_STEPS, "num_workers": NUM_WORKERS,
                       "val_batch_size": VAL_BATCH_SIZE,
                       "persistent_workers": False},   # workers restart each epoch, so they see the new plan
        "training": {"epochs": EPOCHS, "amp": True, "amp_dtype": "bfloat16", "grad_clip": GRAD_CLIP,
                     "loss": {"name": "bce", "pos_weight": POS_WEIGHT},
                     "optimizer": {"name": "adamw", "lr": LR, "weight_decay": WEIGHT_DECAY},
                     "scheduler": {"name": "cosine", "warmup_frac": WARMUP_FRAC, "min_lr_mult": MIN_LR_MULT},
                     "early_stopping": {"enable": not smoke, "patience": EARLY_STOP_PATIENCE},
                     "stop_after_steps": SMOKE_STEPS if smoke else 0},
        "evaluation": {"eval_every_epochs": 1,
                       "validate_before_training": True},   # step 0 = plain BADAS-Open on our validation
        "logging": {"unit": "window", "console_log_every": 5 if smoke else 20, "diagnostics_every": 50},
        "output": {"run_dir": "results_smoke" if smoke else "results", "keep_last_n": KEEP_LAST_N,
                   "keep_top_k": KEEP_TOP_K, "checkpoint_every_steps": 0,   # set to one epoch in build_data
                   "commit_every_steps": 25, "make_plots": False},
        "modal": {"gpu": GPU, "timeout_hours": TIMEOUT_HOURS, "cpu": CPU_CORES, "memory_gb": MEMORY_GB,
                  "python_version": "3.12", "pip": PIP, "apt": ["libgl1", "libglib2.0-0"],
                  "runs_volume": RUNS_VOLUME, "runs_mount": "/runs", "data_volume": DATA_VOLUME,
                  "data_mount": "/data", "ship_data_dir": False},
        "resume": None if smoke else "last",
    }
    return ml.with_defaults(cfg)


CFG = cfg_for(False)


# =====================================================================================================================
# DATA
# =====================================================================================================================
@dataclass
class Source:
    """One thing that gives ONE window per epoch: a clip (or the safe part of a crash clip)."""
    kind: str                   # "crash_danger" | "crash_safe" | "nexar_normal" | "bdd_normal"
    clip: str
    path: str                   # its cached frames (.npy)
    ends: np.ndarray            # every allowed window END frame (window = frames end-16 .. end-1)
    alert: float | None = None  # crash clips: seconds from clip start
    event: float | None = None


def n_frames(path: str) -> int:
    """Number of cached frames, read from the .npy header only (no frames loaded)."""
    return int(np.load(path, mmap_mode="r").shape[0])


def training_sources() -> list[Source]:
    """Every source of the epoch, with its allowed window ends (from the label rule in stage1_labels.py)."""
    excluded = set(json.loads(NEXAR_EXCLUDED.read_text())["clips"])
    crash_meta = [r for r in csv.DictReader(open(NEXAR_CRASH_META)) if r["file_name"] not in excluded]
    normal_files = [p for p in sorted(Path(NEXAR_NORMAL_DIR).glob("*.npy")) if not p.name.endswith(".part.npy")]
    bdd_ids = BDD_TRAIN_CLEAN.read_text().split()
    paths = ([f"{NEXAR_CRASH_DIR}/{Path(r['file_name']).stem}.npy" for r in crash_meta]
             + [str(p) for p in normal_files] + [f"{BDD_TRAIN_DIR}/{c}.npy" for c in bdd_ids])
    with ThreadPoolExecutor(32) as ex:                       # headers only: about 4,000 small reads
        lengths = dict(zip(paths, ex.map(n_frames, paths)))

    sources, dropped = [], []
    for r in crash_meta:
        path = f"{NEXAR_CRASH_DIR}/{Path(r['file_name']).stem}.npy"
        alert, event, n = float(r["time_of_alert"]), float(r["time_of_event"]), lengths[path]
        # danger pool: label >= 0.7 (stage1_labels.danger_ends), as frame numbers inside the cached video
        danger = np.array([e for e in (int(round(t * FPS)) for t in L.danger_ends(alert, event))
                           if WINDOW_FRAMES <= e <= n])
        if len(danger) == 0:                                  # no danger window: the whole clip is not used
            dropped.append(r["file_name"])
            continue
        # safe pool: label 0 by the rule = before the alert AND more than 4 s before the crash
        safe = np.array([e for e in range(WINDOW_FRAMES, n + 1) if L.window_label(e / FPS, alert, event)[1] == L.ZERO])
        sources.append(Source("crash_danger", r["file_name"], path, danger, alert, event))
        if len(safe):
            sources.append(Source("crash_safe", r["file_name"], path, safe, alert, event))
    for p in normal_files:
        sources.append(Source("nexar_normal", p.stem, str(p), np.arange(WINDOW_FRAMES, lengths[str(p)] + 1)))
    for c in bdd_ids:
        path = f"{BDD_TRAIN_DIR}/{c}.npy"
        sources.append(Source("bdd_normal", c, path, np.arange(WINDOW_FRAMES, lengths[path] + 1)))

    ml._table("training sources (each gives ONE window per epoch)", ["source", "clips", "allowed window ends"],
              [[k, sum(s.kind == k for s in sources), f"{sum(len(s.ends) for s in sources if s.kind == k):,}"]
               for k in ("crash_danger", "crash_safe", "nexar_normal", "bdd_normal")], "📦")
    print(f"  crash clips: {len(crash_meta)} after the person's exclusions ({len(excluded)}), "
          f"{len(dropped)} dropped (no danger window), {sum(s.kind == 'crash_danger' for s in sources)} used")
    return sources


def window_label(s: Source, end: int) -> float:
    """The label of the window ending at frame `end` (stage1_labels.window_label; normal clips are always 0)."""
    if s.kind in ("nexar_normal", "bdd_normal"):
        return 0.0
    return float(L.window_label(end / FPS, s.alert, s.event)[0])


# ===== CORE 2: augmentation ==========================================================================================
def augment(frames: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Augment one window (16 x 224 x 224 x 3, uint8 RGB). Every random choice is made ONCE for the window and
    applied to all 16 frames, so the clip stays a consistent piece of video (only the faint noise grain differs
    frame to frame, like real sensor noise; its strength is the same)."""
    import cv2

    t, h, w, _ = frames.shape
    # 1) geometry: one crop box (up to 5% off each edge) + one small rotation, as ONE warp per frame
    m = np.eye(3)
    if rng.random() < AUG_P:
        x0, y0, x1, y1 = rng.uniform(0, CROP_MAX, 4) * [w, h, w, h]
        sx, sy = w / (w - x0 - x1), h / (h - y0 - y1)       # stretch the kept box back to 224 x 224
        m = np.array([[sx, 0, -x0 * sx], [0, sy, -y0 * sy], [0, 0, 1]]) @ m
    if rng.random() < AUG_P:
        rot = cv2.getRotationMatrix2D((w / 2, h / 2), rng.uniform(-ROTATE_DEG, ROTATE_DEG), 1.0)
        m = np.vstack([rot, [0, 0, 1]]) @ m
    if not np.allclose(m, np.eye(3)):
        frames = np.stack([cv2.warpAffine(f, m[:2], (w, h), flags=cv2.INTER_LINEAR,
                                          borderMode=cv2.BORDER_REFLECT_101) for f in frames])

    # 2) colour, on all frames at once (values 0..1)
    x = frames.astype(np.float32) / 255.0
    if rng.random() < AUG_P:                                    # brightness: scale every pixel
        x *= rng.uniform(1 - BRIGHTNESS, 1 + BRIGHTNESS)
    if rng.random() < AUG_P:                                    # contrast: stretch around the window's mean
        mean = x.mean()
        x = (x - mean) * rng.uniform(1 - CONTRAST, 1 + CONTRAST) + mean
    if rng.random() < AUG_P:                                    # saturation: towards / away from grey
        grey = (x @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
        x = grey + (x - grey) * rng.uniform(1 - SATURATION, 1 + SATURATION)
    x = np.clip(x, 0.0, 1.0)
    if rng.random() < AUG_P:                                    # gamma: brighten / darken the mid-tones
        x **= rng.uniform(1 - GAMMA, 1 + GAMMA)

    # 3) sharpness: light blur OR light sharpen (unsharp mask)
    u = rng.random()
    if u < BLUR_P:
        sigma = rng.uniform(0.5, 1.0)
        x = np.stack([cv2.GaussianBlur(f, (0, 0), sigma) for f in x])
    elif u < BLUR_P + SHARPEN_P:
        amount = rng.uniform(0.3, 0.7)
        x = np.clip(np.stack([f + amount * (f - cv2.GaussianBlur(f, (0, 0), 1.0)) for f in x]), 0.0, 1.0)

    # 4) faint noise
    if rng.random() < NOISE_P:
        x = np.clip(x + rng.normal(0.0, rng.uniform(*NOISE_SIGMA) / 255.0, x.shape).astype(np.float32), 0.0, 1.0)
    out = (x * 255.0 + 0.5).astype(np.uint8)

    # 5) mild JPEG compression, same quality on every frame (cv2 encodes BGR, so convert around it)
    if rng.random() < JPEG_P:
        q = int(rng.integers(JPEG_QUALITY[0], JPEG_QUALITY[1] + 1))
        out = np.stack([cv2.cvtColor(cv2.imdecode(cv2.imencode(".jpg", cv2.cvtColor(f, cv2.COLOR_RGB2BGR),
                                                               [cv2.IMWRITE_JPEG_QUALITY, q])[1], cv2.IMREAD_COLOR),
                                     cv2.COLOR_BGR2RGB) for f in out])
    return out


class TrainWindows(Dataset):
    """The training windows. Item i = this epoch's window of source i: (16 frames uint8, label, id)."""

    def __init__(self, sources: list[Source], seed: int):
        self.sources, self.seed = sources, seed
        self.ids = [f"{s.kind}|{s.clip}" for s in sources]
        self.set_epoch(1)                                        # a plan exists before the first epoch starts

    # ===== CORE 1: the epoch plan ====================================================================================
    def set_epoch(self, epoch: int) -> None:
        """Pick this epoch's window for EVERY source: one end frame drawn uniformly from its allowed ends.

        Drawn from a generator seeded with (seed, epoch), so the same epoch always gets the same windows, also after
        a crash and resume. ml_utils calls this before each epoch; the loader workers start after it, so they see it.
        """
        self.epoch = epoch
        rng = np.random.default_rng([self.seed, epoch])
        self.plan = np.array([int(rng.choice(s.ends)) for s in self.sources])
        self.labels = np.array([window_label(s, e) for s, e in zip(self.sources, self.plan)], np.float32)
        self.targets = self.labels[:, None]                     # ml_utils prints the label balance from this

    def plan_counts(self) -> dict:
        """How many windows of each kind this epoch has (printed and logged)."""
        kinds = np.array([s.kind for s in self.sources])
        danger = kinds == "crash_danger"
        return {"windows_total": len(self.sources), "windows_danger": int(danger.sum()),
                "windows_danger_label_1": int((danger & (self.labels == 1.0)).sum()),
                "windows_danger_ramp_0.7_to_1": int((danger & (self.labels < 1.0)).sum()),
                "windows_safe_crash_clip_part": int((kinds == "crash_safe").sum()),
                "windows_safe_nexar_normal": int((kinds == "nexar_normal").sum()),
                "windows_safe_bdd100k": int((kinds == "bdd_normal").sum()),
                "danger_share_pct": round(100.0 * danger.mean(), 1)}

    def __len__(self) -> int:
        return len(self.sources)

    def __getitem__(self, i: int):
        s, end = self.sources[i], int(self.plan[i])
        frames = np.ascontiguousarray(np.load(s.path, mmap_mode="r")[end - WINDOW_FRAMES:end])   # reads 16 frames
        rng = np.random.default_rng([self.seed, self.epoch, i])          # this window's augmentation draw
        frames = augment(frames, rng)
        return torch.from_numpy(frames), torch.tensor([self.labels[i]]), f"{self.ids[i]}|{end}"


class ValWindows(Dataset):
    """The 2,202 FIXED validation windows (val_windows.json): no augmentation, the same every epoch."""

    def __init__(self, windows: list[dict]):
        for w in windows:                                        # Nexar windows are counted from the clip's end
            w["path"] = f"{CACHE}/{w['folder']}/{w['clip']}.npy"
        with ThreadPoolExecutor(32) as ex:
            lengths = list(ex.map(n_frames, [w["path"] for w in windows]))
        for w, n in zip(windows, lengths):
            w["end"] = n - w["end_back"] if w["end"] is None else w["end"]
        self.windows = windows
        self.ids = [f"{w['group']}|{w['clip']}|{w['end']}" for w in windows]
        self.targets = np.array([[w["label"]] for w in windows], np.float32)
        # arrays the scores use (same order as the predictions: the val loader never shuffles)
        self.group = np.array([w["group"] for w in windows])
        self.rank = np.array([w["rank"] for w in windows])
        self.nexar_group = np.array([-1 if w["nexar_group"] is None else w["nexar_group"] for w in windows])

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, i: int):
        w = self.windows[i]
        frames = np.ascontiguousarray(np.load(w["path"], mmap_mode="r")[w["end"] - WINDOW_FRAMES:w["end"]])
        return torch.from_numpy(frames), torch.tensor([w["label"]], dtype=torch.float32), self.ids[i]


TRAIN: TrainWindows | None = None        # set in build_data; the hooks read them
VAL: ValWindows | None = None
STEPS_PER_EPOCH = [1]                    # weight updates per epoch (set in build_data)


def build_data(cfg: dict) -> dict:
    """The train and val datasets (runs on Modal). Also sets the rolling checkpoint to once per epoch."""
    global TRAIN, VAL
    ml._banner("STAGE 1 DATA", "📦")
    TRAIN = TrainWindows(training_sources(), SEED)
    VAL = ValWindows(json.loads(VAL_WINDOWS.read_text()))
    ml._table("validation windows (fixed, 2 per clip)", ["group", "windows", "label"],
              [[g, int((VAL.group == g).sum()), lab] for g, lab in
               (("nexar_crash", 1), ("nexar_normal", 0), ("bdd_hard", 0))], "🔎")
    n_micro = len(TRAIN) // BATCH_SIZE                            # drop_last: a ragged last batch is dropped
    steps = -(-n_micro // ACCUM_STEPS)
    STEPS_PER_EPOCH[0] = steps
    cfg["output"]["checkpoint_every_steps"] = steps               # rolling checkpoint at every epoch's last step
    print(f"  one epoch = {len(TRAIN):,} windows = {steps} weight updates; rolling checkpoint every {steps} "
          f"steps (keep last {KEEP_LAST_N})")
    return {"train": TRAIN, "val": VAL}


# =====================================================================================================================
# MODEL
# =====================================================================================================================
# ===== CORE 4: the batched predictor =================================================================================
def batched_predict_future(self, encoder_features: torch.Tensor) -> torch.Tensor:
    """BADAS's future prediction for the WHOLE batch in one predictor call.

    BADAS's own _predict_future_features loops over the batch, one clip at a time (slow in training). The predictor
    takes the encoder's 2,048 present tokens plus 512 empty "future" slots and fills those in. Here every clip gets
    the same slots at once: the context / target index lists are simply repeated for each clip of the batch.
    check_batched_predictor() proves the result equals the loop before training starts.
    """
    b, seq_len, d = encoder_features.shape
    future_s = getattr(self.config, "future_prediction_seconds", 1.0)
    present_s = self.config.frame_count / getattr(self.config, "original_fps", 4)
    n_future = max(int(seq_len * (future_s / present_s)), 1)               # 512 for BADAS-Open
    expanded = torch.cat([encoder_features, encoder_features.new_zeros(b, n_future, d)], dim=1)
    ctx = torch.arange(seq_len, device=encoder_features.device).unsqueeze(0).expand(b, -1)
    tgt = torch.arange(seq_len, seq_len + n_future, device=encoder_features.device).unsqueeze(0).expand(b, -1)
    return self.predictor(expanded, context_mask=[ctx], target_mask=[tgt]).last_hidden_state   # b, 512, 1024


def check_batched_predictor(net: nn.Module, device) -> float:
    """Stop the run unless the batched predictor gives the same output as BADAS's loop (4 clips, full precision)."""
    net.eval()
    x = torch.randn(4, WINDOW_FRAMES, 3, CHECK_INPUT_SIZE, CHECK_INPUT_SIZE, device=device)
    with torch.no_grad():
        feats = net._extract_video_features(x)
        loop = type(net)._predict_future_features(net, feats)             # BADAS's own code
        batched = batched_predict_future(net, feats)
    diff = float((loop - batched).abs().max())
    print(f"  ✅ batched predictor vs BADAS's per-clip loop: largest difference {diff:.2e} "
          f"(allowed {PREDICTOR_CHECK_TOL:g})")
    if not diff <= PREDICTOR_CHECK_TOL:
        raise SystemExit("batched predictor differs from BADAS's loop: stopping")
    return diff


# ===== CORE 3: LoRA on every layer ===================================================================================
def add_lora(net: nn.Module) -> nn.Module:
    """Wrap BADAS-Open with LoRA and switch on the small parts that train fully, then CHECK that nothing is left out.

    LoRA: each targeted weight W stays frozen and learns a small update B x A (rank 16, scaled by alpha / rank = 2).
    B starts at zero, so at step 0 the model is exactly BADAS-Open. Stops the run when:
      - the number of LoRA layers is not the 219 expected (a renamed layer would silently lose its LoRA),
      - any frozen weight is neither the base of a LoRA layer nor a backup copy (= left out of training),
      - the predictor stops being one shared object (BADAS lists it twice: predictor and backbone.predictor).
    """
    from peft import LoraConfig, get_peft_model

    model = get_peft_model(net, LoraConfig(r=LORA_RANK, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
                                           bias="none", target_modules=LORA_TARGETS, modules_to_save=FULLY_TRAINED))
    # peft leaves LayerNorms and the predictor's mask tokens frozen: switch them on (tiny, and they matter)
    for n, p in model.named_parameters():
        if ("norm" in n or n.endswith("mask_tokens")) and "lora_" not in n and "original_module" not in n:
            p.requires_grad_(True)

    lora = {n: m for n, m in model.named_modules() if hasattr(m, "base_layer") and hasattr(m, "lora_A")}
    bases = {f"{n}.base_layer.{pn}" for n, m in lora.items() for pn, _ in m.base_layer.named_parameters()}
    left_out = [n for n, p in model.named_parameters()
                if not p.requires_grad and n not in bases and "original_module" not in n]
    inner = model.base_model.model
    shared = inner.predictor is inner.backbone.predictor
    by_type = {}
    for m in lora.values():
        by_type[type(m.base_layer).__name__] = by_type.get(type(m.base_layer).__name__, 0) + 1
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    ml._kv("LoRA coverage check", [
        ("LoRA layers", f"{len(lora)} (expected {EXPECTED_LORA_LAYERS})  {by_type}"),
        ("weights left out", len(left_out)),
        ("predictor still shared", shared),
        ("trainable", f"{trainable / 1e6:.2f} M of {total / 1e6:.1f} M"),
    ], "🧩")
    if len(lora) != EXPECTED_LORA_LAYERS or left_out or not shared:
        raise SystemExit(f"LoRA coverage check failed: {len(lora)} layers, left out {left_out[:10]}, "
                         f"shared predictor {shared}")
    return model


def check_gradients_reach_everything(model: nn.Module, device) -> None:
    """One forward + backward on 2 random clips: every trainable weight must get a gradient (no dead path).

    drop_path (randomly skipping blocks in training) is paused for this check, else a skipped block would look dead.
    LoRA's A matrices get a zero gradient on this first pass (B is still zero): zero is fine, missing is not.
    """
    model.train()
    drop = [m for m in model.modules() if type(m).__name__ == "VJEPA2DropPath"]
    for m in drop:
        m.eval()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        out = model(torch.randn(2, WINDOW_FRAMES, 3, CHECK_INPUT_SIZE, CHECK_INPUT_SIZE, device=device))
    nn.functional.binary_cross_entropy_with_logits(out.float(), torch.tensor([[0.0], [1.0]], device=device)).backward()
    dead = [n for n, p in model.named_parameters() if p.requires_grad and p.grad is None]
    model.zero_grad(set_to_none=True)
    for m in drop:
        m.train()
    print(f"  ✅ gradient check: every trainable weight got a gradient ({len(dead)} without)")
    if dead:
        raise SystemExit(f"trainable weights with no gradient: {dead[:10]}")


PROCESSOR = None                          # BADAS's video processor (set in build_model, used by the prepare hook)


class RiskModel(nn.Module):
    """BADAS-Open + LoRA, giving ONE number per window: the crash-risk logit (sigmoid of it = BADAS's risk)."""

    def __init__(self, device):
        super().__init__()
        global PROCESSOR
        from huggingface_hub import snapshot_download

        repo = Path(snapshot_download(BADAS_REPO, allow_patterns=["src/*", "src/**/*", "weights/*"]))
        sys.path.insert(0, str(repo / "src"))
        from models.vjepa import VJEPAModel
        badas = VJEPAModel(model_name=BASE_MODEL, checkpoint_path=str(repo / "weights" / "badas_open.pth"),
                           device=str(device), frame_count=WINDOW_FRAMES, img_size=FRAME_H, target_fps=float(FPS),
                           use_sliding_window=False)
        badas.load()
        PROCESSOR = badas.processor
        net = badas.model                                       # BADAS's EnhancedVideoClassifier
        if GRAD_CHECKPOINTING and hasattr(net.backbone, "gradient_checkpointing_enable"):
            net.backbone.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            print("  🧮 gradient checkpointing ON (less memory, slower)")

        # CORE 4: prove the batched predictor equals BADAS's loop, then use it
        check_batched_predictor(net, device)
        x = torch.randn(2, WINDOW_FRAMES, 3, CHECK_INPUT_SIZE, CHECK_INPUT_SIZE, device=device)
        with torch.no_grad():
            before = net(x)                                     # plain BADAS-Open (loop predictor)
        net._predict_future_features = types.MethodType(batched_predict_future, net)

        # CORE 3: LoRA everywhere, coverage checked inside
        self.net = add_lora(net)
        self.net.eval()
        with torch.no_grad():
            diff = float((self.net(x) - before).abs().max())    # LoRA starts at zero: must still be BADAS-Open
        print(f"  ✅ start check: outputs after adding LoRA + batched predictor vs plain BADAS-Open differ by "
              f"{diff:.2e} (must be about 0)")
        if not diff <= PREDICTOR_CHECK_TOL:
            raise SystemExit("the model at step 0 is not BADAS-Open: stopping")
        check_gradients_reach_everything(self, device)
        self._trainable = {n for n, p in self.named_parameters() if p.requires_grad}

    # ===== CORE 5: the risk number and the loss =====================================================================
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: B x 16 x 3 x 256 x 256 (BADAS's processor already applied). Returns B x 1 risk logits.

        BADAS gives 2 scores per window (safe, crash) and its risk is softmax(scores / 2)[crash]. For two classes
        that equals sigmoid((crash - safe) / 2), so ONE logit z = (crash - safe) / 2 carries it exactly:
        sigmoid(z) is BADAS's risk. Training uses binary cross-entropy between sigmoid(z) and the label (1, a ramp
        value between 0.7 and 1, or 0), which is the same as BADAS's own 2-class cross-entropy with a soft target.
        """
        scores = self.net(x)                                     # B x 2: (safe, crash)
        return ((scores[:, 1] - scores[:, 0]) / TEMPERATURE).unsqueeze(1)

    # Checkpoints hold only what training changes (14 M weights, not the frozen 330 M): the frozen base is
    # reloaded from BADAS-Open every time. Loading checks that every trainable weight is present.
    def state_dict(self, *args, **kwargs):
        full = super().state_dict(*args, **kwargs)
        prefix = kwargs.get("prefix", "")
        return type(full)((k, v) for k, v in full.items() if k[len(prefix):] in self._trainable)

    def load_state_dict(self, state_dict, strict: bool = True, assign: bool = False):
        missing = sorted(self._trainable - set(state_dict))
        if strict and missing:
            raise RuntimeError(f"checkpoint is missing {len(missing)} trainable weights, e.g. {missing[:5]}")
        res = super().load_state_dict(state_dict, strict=False, assign=assign)
        if res.unexpected_keys:
            raise RuntimeError(f"checkpoint has unknown weights: {res.unexpected_keys[:5]}")
        return res


def build_model(cfg: dict) -> nn.Module:
    os.environ.setdefault("HF_HOME", HF_CACHE)
    ml._banner("STAGE 1 MODEL: BADAS-Open + LoRA", "🧠")
    return RiskModel(ml.pick_device(cfg))


# =====================================================================================================================
# HOOKS: GPU preprocessing, scores, prints
# =====================================================================================================================
def prepare(x: torch.Tensor, device, cfg) -> torch.Tensor:
    """B x 16 x 224 x 224 x 3 uint8 -> B x 16 x 3 x 256 x 256: BADAS's own processor (resize to 292, centre crop
    256, scale to 0..1, ImageNet normalise), run on the GPU on all B x 16 frames at once (it treats every frame on
    its own, exactly like eval_risk.py)."""
    b = x.shape[0]
    frames = x.reshape(b * WINDOW_FRAMES, FRAME_H, FRAME_W, 3).numpy()
    px = PROCESSOR(videos=frames, return_tensors="pt", device=str(device))["pixel_values_videos"][0]
    return px.reshape(b, WINDOW_FRAMES, *px.shape[1:])


def _ap(pos: np.ndarray, neg: np.ndarray) -> float:
    """Average precision (area under precision-recall): crash windows should all score above normal ones (1.0)."""
    from sklearn.metrics import average_precision_score
    if not len(pos) or not len(neg):
        return float("nan")
    return float(average_precision_score(np.r_[np.ones(len(pos)), np.zeros(len(neg))], np.r_[pos, neg]))


LAST_RISK = None                           # the last validation's risks, for the detailed table


# ===== CORE 6: the validation scores ================================================================================
def validation_scores(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    """The main validation numbers (ml_utils adds them to val_log.csv and prints them; MONITOR picks best.pt).

    AP = average precision: 1.0 when every crash window scores above every normal one. Three pairings:
      ap_crash_vs_all_normal    Nexar crash vs Nexar normal + BDD100K val hard moments   (picks best.pt)
      ap_crash_vs_nexar_normal  Nexar crash vs Nexar normal (same camera, same test moments)
      ap_crash_vs_bdd_hard      Nexar crash vs the BDD100K moments plain BADAS found riskiest (false-beep cases)
    nexar_official_map: Nexar's own score: AP per test group (0.5 / 1.0 / 1.5 s before the crash) on the clip's
    LAST-frame windows only, averaged (baseline BADAS-Open: 0.903). Plus the mean risk per group of windows.
    """
    global LAST_RISK
    risk = y_prob[:, 0]
    LAST_RISK = risk
    g, rank, ng = VAL.group, VAL.rank, VAL.nexar_group
    crash, nnorm, bdd = risk[g == "nexar_crash"], risk[g == "nexar_normal"], risk[g == "bdd_hard"]
    out = {"ap_crash_vs_all_normal": _ap(crash, np.r_[nnorm, bdd]),
           "ap_crash_vs_nexar_normal": _ap(crash, nnorm),
           "ap_crash_vs_bdd_hard": _ap(crash, bdd)}
    official = [_ap(risk[(g == "nexar_crash") & (rank == 1) & (ng == k)],
                    risk[(g == "nexar_normal") & (rank == 1) & (ng == k)]) for k in GROUP_SECONDS]
    out["nexar_official_map"] = float(np.mean(official))
    out.update({"mean_risk_nexar_crash": float(crash.mean()), "mean_risk_nexar_normal": float(nnorm.mean()),
                "mean_risk_bdd_hard": float(bdd.mean())})
    return out


def detailed_scores(risk: np.ndarray) -> dict:
    """Everything else, added to val_log.csv by on_validation: per Nexar group, and at every threshold."""
    g, rank, ng = VAL.group, VAL.rank, VAL.nexar_group
    crash_m, nnorm_m, bdd_m = g == "nexar_crash", g == "nexar_normal", g == "bdd_hard"
    out = {}
    for k, sec in GROUP_SECONDS.items():                        # per test group (seconds before the crash)
        c = risk[crash_m & (ng == k)]
        out[f"group_{sec}s_official_ap_crash_vs_nexar_normal"] = _ap(risk[crash_m & (rank == 1) & (ng == k)],
                                                                      risk[nnorm_m & (rank == 1) & (ng == k)])
        out[f"group_{sec}s_ap_crash_vs_bdd_hard"] = _ap(c, risk[bdd_m])
        out[f"group_{sec}s_mean_risk_crash"] = float(c.mean())
        for t in (0.9, 0.99):
            out[f"group_{sec}s_crash_caught_pct_at_{t}"] = round(100.0 * float((c > t).mean()), 2)
    for t in THRESHOLDS:                                        # share of windows above each threshold
        out[f"crash_caught_pct_at_{t}"] = round(100.0 * float((risk[crash_m] > t).mean()), 2)
        out[f"nexar_normal_alarm_pct_at_{t}"] = round(100.0 * float((risk[nnorm_m] > t).mean()), 2)
        out[f"bdd_hard_alarm_pct_at_{t}"] = round(100.0 * float((risk[bdd_m] > t).mean()), 2)
    # calibration error: does "risk 0.8" mean 80% of such windows are crashes? (10 equal-width bins)
    y = (crash_m).astype(float)
    bins = np.clip((risk * 10).astype(int), 0, 9)
    out["calibration_error"] = float(sum(abs(risk[bins == b].mean() - y[bins == b].mean()) * (bins == b).mean()
                                         for b in range(10) if (bins == b).any()))
    return out


VAL_SECS = [0.0]                           # validation time so far (for the cost estimate)


def on_epoch_start(epoch: int, model, loaders) -> None:
    """Print what this epoch trains on (the plan was just drawn by TrainWindows.set_epoch)."""
    c = TRAIN.plan_counts()
    ml._table(f"epoch {epoch}: training windows (one per source, new random end points)", ["windows", "count"],
              [[k.replace("windows_", "").replace("_", " "), v] for k, v in c.items()], "🎲")


def on_validation(row: dict, epoch: int, step: int) -> None:
    """Add the detailed numbers to the val_log.csv row, then print one clear summary block."""
    det = detailed_scores(LAST_RISK)
    row.update({f"val_{k}": v for k, v in det.items()})
    row.update({f"train_{k}": v for k, v in TRAIN.plan_counts().items()})
    VAL_SECS[0] += row.get("val_secs", 0.0)
    train_s = max(row.get("elapsed_s", 0.0) - VAL_SECS[0], 0.0)
    steps_per_epoch = STEPS_PER_EPOCH[0]
    row["cost_usd_so_far"] = round(row.get("elapsed_s", 0.0) / 3600 * PRICE_H, 3)
    if step:
        row["est_minutes_per_epoch"] = round((train_s / step * steps_per_epoch + row.get("val_secs", 0.0)) / 60, 1)
        row["est_cost_usd_per_epoch"] = round(row["est_minutes_per_epoch"] / 60 * PRICE_H, 2)

    v = lambda k: row.get(f"val_{k}", float("nan"))
    ml._banner(f"STAGE 1 VALIDATION SUMMARY  epoch {epoch}  step {step}"
               + ("  (plain BADAS-Open, before training)" if step == 0 else ""), "📋")
    ml._kv("ranking quality: average precision (1.0 = every crash window above every normal one)", [
        ("Nexar crash vs ALL normal  (picks best.pt)", f"{v('ap_crash_vs_all_normal'):.4f}"),
        ("Nexar crash vs Nexar normal", f"{v('ap_crash_vs_nexar_normal'):.4f}"),
        ("Nexar crash vs BDD100K val hard moments", f"{v('ap_crash_vs_bdd_hard'):.4f}"),
        ("Nexar official mAP (last frame, 3 groups)", f"{v('nexar_official_map'):.4f}   (baseline 0.903)"),
        ("calibration error (0 = risk values honest)", f"{v('calibration_error'):.4f}"),
    ], "🏁")
    ml._table("mean risk per window group", ["Nexar crash", "Nexar normal", "BDD100K val hard moments"],
              [[f"{v('mean_risk_nexar_crash'):.4f}", f"{v('mean_risk_nexar_normal'):.4f}",
                f"{v('mean_risk_bdd_hard'):.4f}"]], "📊")
    ml._table("by Nexar test group (how long before the crash the clip ends)",
              ["group", "official AP vs Nexar normal", "AP vs BDD hard", "mean risk (crash)",
               "crashes caught >0.9", "crashes caught >0.99"],
              [[f"{sec} s before", f"{v(f'group_{sec}s_official_ap_crash_vs_nexar_normal'):.4f}",
                f"{v(f'group_{sec}s_ap_crash_vs_bdd_hard'):.4f}", f"{v(f'group_{sec}s_mean_risk_crash'):.4f}",
                f"{v(f'group_{sec}s_crash_caught_pct_at_0.9'):.1f}%",
                f"{v(f'group_{sec}s_crash_caught_pct_at_0.99'):.1f}%"] for sec in GROUP_SECONDS.values()], "⏱️")
    ml._table("at each threshold: share of windows with risk above it",
              ["threshold", "crashes caught (Nexar crash)", "false alarms (Nexar normal)",
               "false alarms (BDD100K hard moments)"],
              [[t, f"{v(f'crash_caught_pct_at_{t}'):.1f}%", f"{v(f'nexar_normal_alarm_pct_at_{t}'):.1f}%",
                f"{v(f'bdd_hard_alarm_pct_at_{t}'):.1f}%"] for t in THRESHOLDS], "🎚️")
    cost = [("cost so far (GPU + CPU + memory)", f"${row['cost_usd_so_far']:.2f}  at ${PRICE_H:.2f}/h")]
    if step:
        cost += [("estimated time per epoch", f"{row['est_minutes_per_epoch']} min"),
                 ("estimated cost per epoch", f"${row['est_cost_usd_per_epoch']:.2f}"),
                 (f"estimated cost for {EPOCHS} epochs", f"${row['est_cost_usd_per_epoch'] * EPOCHS:.2f}")]
    ml._kv("cost", cost, "💰")


HOOKS = ml.Hooks(prepare=prepare, score=validation_scores, on_epoch_start=on_epoch_start,
                 on_validation=on_validation)
CFG_RUNTIME = CFG                          # the config this process trains with (set in train_remote)


# =====================================================================================================================
# MODAL
# =====================================================================================================================
import modal  # noqa: E402

app = modal.App(EXP_NAME)
VOLUMES = ml.modal_volumes(CFG)
try:                                       # this PC's Hugging Face login, passed for this run only
    from huggingface_hub import get_token
    _HF = modal.Secret.from_dict({"HF_TOKEN": get_token() or ""})
except Exception:
    _HF = modal.Secret.from_dict({})


@app.function(image=ml.modal_image(CFG, PKG_ROOT), volumes=VOLUMES, secrets=[_HF], **ml.modal_resources(CFG))
def train_remote(run_id: str = "", smoke: bool = False):
    """Runs inside the Modal container on the A100."""
    global CFG_RUNTIME
    os.environ["HF_HOME"] = HF_CACHE                       # before transformers is imported
    CFG_RUNTIME = cfg_for(smoke)
    ml.modal_train(CFG_RUNTIME, EXP_DIR, build_model, build_data, hooks=HOOKS, run_id=run_id, volumes=VOLUMES)


@app.local_entrypoint()
def main(smoke: bool = False):
    """`modal run stage1_train.py [--smoke]`: Ctrl+C stops the GPU first, then results are synced to this PC."""
    if not VAL_WINDOWS.exists():
        raise SystemExit(f"{VAL_WINDOWS} missing: run make_val_windows.py first")
    cfg = cfg_for(smoke)
    ml.sync_on_interrupt(cfg, EXP_DIR)
    run_id = ml.launch_run_id(cfg, EXP_DIR)
    status = "crashed"
    try:
        train_remote.remote(run_id, smoke)
        status = "finished"
    finally:
        ml.sync_back(cfg, EXP_DIR, status)
