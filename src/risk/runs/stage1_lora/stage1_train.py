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

WORDS USED BELOW
    window      2 s of video = 16 consecutive frames. Named by its END frame e: it holds frames e-16 ... e-1 and
                "happens" at time e / 8 seconds.
    source      something that gives ONE window per epoch: a normal clip, or the danger / safe part of a crash clip.
    label       the answer the model should give for a window: 1 = crash coming, 0 = safe, or a ramp value 0.7-1.
    alert       Nexar's label: the moment a person could first see the danger (seconds from the clip's start).
    event       Nexar's label: the moment of the crash itself.
    step        one weight update (= 4 GPU passes of 8 windows = 32 windows).

RUN IT (see current_modal_commands.txt; run make_val_windows.py once before):
    python -m modal run src\\risk\\runs\\stage1_lora\\stage1_train.py --smoke   # short test: speed, memory, cost
    python -m modal run src\\risk\\runs\\stage1_lora\\stage1_train.py           # the real run (resumes if stopped)
(Not called train.py: BADAS's own code imports a package named "train", and the names would clash.)
Results come back to src/risk/runs/stage1_lora/results/ (smoke test: results_smoke/).
"""

import csv                                            # reads Nexar's metadata.csv (alert / crash times)
import json                                           # reads the small JSON lists (excluded clips, val windows)
import os                                             # environment variables (where Hugging Face keeps downloads)
import sys                                            # lets Python find ml_utils.py and BADAS's own code
import types                                          # attaches our batched predictor to BADAS's model object
from dataclasses import dataclass                     # a short way to define the Source record
from pathlib import Path                              # file paths

import numpy as np                                    # arrays (frames, labels, scores)
import torch                                          # the deep-learning library
import torch.nn as nn                                 # its neural-network parts
from torch.utils.data import Dataset                  # the "list of training examples" interface ml_utils expects

EXP_NAME = "stage1_lora"                  # MUST equal this folder's name (it names the Modal app and results folder)


def _pkg_root() -> Path:
    """Find the folder holding ml_utils.py and stage1_labels.py (src/risk).
    On Modal the code is copied to /root/runs; on this PC it is two folders above this file."""
    here = Path(__file__).resolve()
    candidates = [Path("/root/runs")]                 # Modal: the code folder is copied here
    if len(here.parents) > 2:                         # this PC: src/risk (on Modal the file sits at /root, too shallow)
        candidates.append(here.parents[2])
    for candidate in candidates:
        if (candidate / "ml_utils.py").exists():
            return candidate
    raise FileNotFoundError("ml_utils.py not found")


PKG_ROOT = _pkg_root()                                # src/risk (or /root/runs on Modal)
EXP_DIR = PKG_ROOT / "runs" / EXP_NAME                # this run's folder: src/risk/runs/stage1_lora
sys.path.insert(0, str(PKG_ROOT))                     # so the two imports below are found
import ml_utils as ml  # noqa: E402                   # the shared training engine (loop, logs, checkpoints, Modal)
import stage1_labels as L  # noqa: E402               # the label rule (also used by the demo videos)
import wide_input as W  # noqa: E402                  # the 16:9 input: frame shape, normalising, position patch

# =====================================================================================================================
# SETTINGS: every number lives in config.yaml (next to this script); here they are only read into named constants
# =====================================================================================================================
import yaml  # noqa: E402                             # reads .yaml files (PyYAML)

_C = yaml.safe_load((EXP_DIR / "config.yaml").read_text(encoding="utf-8"))   # the whole file, as nested dicts
_D, _M, _LO, _T, _A = _C["data"], _C["model"], _C["lora"], _C["training"], _C["augment"]
_V, _K, _MO = _C["validation"], _C["checkpoints"], _C["modal"]

# ---- data ----
DATA_VOLUME, RUNS_VOLUME = _D["data_volume"], _D["runs_volume"]
CACHE = _D["cache"]
NEXAR_CRASH_DIR = f"{CACHE}/{_D['nexar_crash_folder']}"
NEXAR_NORMAL_DIR = f"{CACHE}/{_D['nexar_normal_folder']}"
BDD_TRAIN_DIR = f"{CACHE}/{_D['bdd_train_folder']}"
NEXAR_CRASH_META = _D["nexar_crash_meta"]
BDD_TRAIN_CLEAN = PKG_ROOT / _D["bdd_train_clean"]
NEXAR_EXCLUDED = PKG_ROOT / _D["nexar_excluded"]
FRAME_COUNTS = PKG_ROOT / _D["frame_counts"]
VAL_WINDOWS = EXP_DIR / _D["val_windows"]
FPS, WINDOW_FRAMES = _D["fps"], _D["window_frames"]
FRAME_H, FRAME_W = W.WIDE_H, W.WIDE_W                 # 256 x 448: from wide_input.py (what the cache was built with)
CHECK_H, CHECK_W = W.WIDE_H, W.WIDE_W                 # size of the random test clips used by the start-up checks

# ---- model ----
BADAS_REPO, BASE_MODEL, HF_CACHE = _M["badas_repo"], _M["base_model"], _M["hf_cache"]
TEMPERATURE = _M["temperature"]
PREDICTOR_CHECK_TOL = _M["predictor_check_tol"]
GRAD_CHECKPOINTING = _M["grad_checkpointing"]

# ---- LoRA ----
LORA_RANK, LORA_ALPHA, LORA_DROPOUT = _LO["rank"], _LO["alpha"], _LO["dropout"]
LORA_TARGETS = _LO["targets"]
EXPECTED_LORA_LAYERS = _LO["expected_layers"]
FULLY_TRAINED = _LO["fully_trained"]

# ---- training ----
EPOCHS, BATCH_SIZE, ACCUM_STEPS = _T["epochs"], _T["batch_size"], _T["accum_steps"]
LR, WEIGHT_DECAY = _T["lr"], _T["weight_decay"]
WARMUP_FRAC, MIN_LR_MULT = _T["warmup_frac"], _T["min_lr_mult"]
GRAD_CLIP = _T["grad_clip"]
COMPILE = _T["compile"]                               # torch.compile on / off
EARLY_STOP_PATIENCE = _T["early_stop_patience"]
NUM_WORKERS, VAL_BATCH_SIZE = _T["num_workers"], _T["val_batch_size"]
SEED = _T["seed"]
POS_WEIGHT = _T["pos_weight"]                         # null in the file = not used

# ---- augmentation ----
CROP_P, CROP_MAX = _A["crop_p"], _A["crop_max"]
ROTATE_P, ROTATE_DEG = _A["rotate_p"], _A["rotate_deg"]
BRIGHTNESS_P, BRIGHTNESS = _A["brightness_p"], _A["brightness"]
CONTRAST_P, CONTRAST = _A["contrast_p"], _A["contrast"]
SATURATION_P, SATURATION = _A["saturation_p"], _A["saturation"]
GAMMA_P, GAMMA = _A["gamma_p"], _A["gamma"]
BLUR_P, BLUR_SIGMA = _A["blur_p"], tuple(_A["blur_sigma"])
SHARPEN_P, SHARPEN_AMOUNT = _A["sharpen_p"], tuple(_A["sharpen_amount"])
NOISE_P, NOISE_SIGMA = _A["noise_p"], tuple(_A["noise_sigma"])
JPEG_P, JPEG_QUALITY = _A["jpeg_p"], tuple(_A["jpeg_quality"])

# ---- validation ----
THRESHOLDS = _V["thresholds"]
MONITOR = _V["monitor"]
VALS_PER_EPOCH = _V["vals_per_epoch"]                # validations per epoch (from MORE_OFTEN_FROM_EPOCH on)
MORE_OFTEN_FROM_EPOCH = _V["more_often_from_epoch"]
GROUP_SECONDS = dict(enumerate(_V["group_seconds"]))  # Nexar test group 0, 1, 2 -> seconds before the crash

# ---- checkpoints ----
KEEP_LAST_N, KEEP_TOP_K = _K["keep_last_n"], _K["keep_top_k"]
CHECKPOINT_EVERY = _K["every_steps"]                 # a rolling checkpoint every N updates

# ---- Modal ----
GPU, TIMEOUT_HOURS = _MO["gpu"], _MO["timeout_hours"]
CPU_CORES, MEMORY_GB = _MO["cpu_cores"], _MO["memory_gb"]
PRICE_H = _MO["gpu_price_s"] * 3600 + CPU_CORES * 0.0473 + MEMORY_GB * 0.008   # GPU + CPU + memory, $ per hour
PIP = _MO["pip"]

# ---- smoke test ----
SMOKE_STEPS = _C["smoke"]["steps"]
# =====================================================================================================================


def cfg_for(smoke: bool) -> dict:
    """The settings above, in the form ml_utils reads (a nested dictionary). Anything not given here keeps
    ml_utils's default (listed in ml_utils.DEFAULTS_YAML). The smoke test writes to results_smoke/, so it never
    mixes with the real run's checkpoints.

    Arguments:
        smoke: True = the short smoke test (20 updates, results_smoke/), False = the real run.
    """
    cfg = {
        "experiment": {"name": EXP_NAME, "notes": "stage 1: BADAS-Open + LoRA, Nexar + clean BDD100K"},
        "task": {"type": "binary", "targets": ["crash_risk"]},          # one yes/no answer per window
        "metrics": {"monitor": MONITOR, "mode": "max",                    # higher MONITOR = better
                    "threshold": 0.5},                                    # ml_utils's own F1 etc. cut at 0.5
        "model": {"name": "BADAS-Open + LoRA r16", "pretrained": BADAS_REPO},   # only for the prints
        "reproducibility": {"seed": SEED},
        "dataloader": {"batch_size": BATCH_SIZE, "accum_steps": ACCUM_STEPS, "num_workers": NUM_WORKERS,
                       "val_batch_size": VAL_BATCH_SIZE,
                       "persistent_workers": False},   # workers restart each epoch, so they see the new plan
        "training": {"epochs": EPOCHS,
                     "amp": True, "amp_dtype": "bfloat16",               # 16-bit maths on the GPU (faster)
                     "compile": COMPILE,                                 # torch.compile (config.yaml)
                     "grad_clip": GRAD_CLIP,
                     "loss": {"name": "bce", "pos_weight": POS_WEIGHT},  # binary cross-entropy (see forward)
                     "optimizer": {"name": "adamw", "lr": LR, "weight_decay": WEIGHT_DECAY},
                     "scheduler": {"name": "cosine", "warmup_frac": WARMUP_FRAC, "min_lr_mult": MIN_LR_MULT},
                     "early_stopping": {"enable": not smoke, "patience": EARLY_STOP_PATIENCE},
                     "stop_after_steps": SMOKE_STEPS if smoke else 0},    # 0 = run all epochs
        "evaluation": {"eval_every_epochs": 1,                            # validate after every epoch
                       "validate_before_training": True},   # step 0 = plain BADAS-Open on our validation
        "logging": {"unit": "window",                                     # speed is printed in windows per second
                    "console_log_every": 5 if smoke else 20,              # a progress line every N updates
                    "diagnostics_every": 50},                             # update/weight ratio etc. every 50
        "output": {"run_dir": "results_smoke" if smoke else "results",
                   "keep_last_n": KEEP_LAST_N, "keep_top_k": KEEP_TOP_K,
                   "checkpoint_every_steps": 0,                           # set in build_data (config.yaml)
                   "commit_every_steps": 25,                              # save logs to the volume every 25 updates
                   "make_plots": False},                                  # plots are drawn on this PC afterwards
        "modal": {"gpu": GPU, "timeout_hours": TIMEOUT_HOURS, "cpu": CPU_CORES, "memory_gb": MEMORY_GB,
                  "python_version": "3.12", "pip": PIP, "apt": ["libgl1", "libglib2.0-0"],   # apt: for OpenCV
                  "runs_volume": RUNS_VOLUME, "runs_mount": "/runs",
                  "data_volume": DATA_VOLUME, "data_mount": "/data",
                  "ship_data_dir": False},                                # data comes from the volume, not the image
        "resume": None if smoke else "last",              # the real run continues from its last checkpoint if stopped
    }
    return ml.with_defaults(cfg)                          # fill in every setting not given above


CFG = cfg_for(False)                                      # the real run's settings (also used to build the image)


# =====================================================================================================================
# DATA
# =====================================================================================================================
@dataclass
class Source:
    """One thing that gives ONE window per epoch: a normal clip, or the danger part or safe part of a crash clip."""
    kind: str                   # "crash_danger" | "crash_safe" | "nexar_normal" | "bdd_normal"
    clip: str                   # the clip's name
    path: str                   # its cached frames (.npy file)
    ends: np.ndarray            # every frame a window of this source is allowed to END on
    alert: float | None = None  # crash clips: when the danger became visible (seconds from the clip's start)
    event: float | None = None  # crash clips: when the crash happened


_COUNTS: dict | None = None                # clip -> number of frames, read once from FRAME_COUNTS


def n_frames(path: str) -> int:
    """Number of frames in a cached clip, looked up in FRAME_COUNTS (counted once by wide_frame_counts.py).

    Why not read the file: opening about 5,000 cache files on the Modal volume at start-up choked the GPU
    container (no progress for 9 minutes). The counts file ships with the code, so this reads nothing from the volume.

    Arguments:
        path: a cached clip's .npy file (.../<cache folder>/<clip>.npy).
    """
    
    global _COUNTS
    if _COUNTS is None:
        _COUNTS = json.loads(FRAME_COUNTS.read_text())
    p = Path(path)
    key = f"{p.parent.name}/{p.stem}"                                 # e.g. nexar_train_positive/00266
    if key not in _COUNTS:
        raise SystemExit(f"{key} is not in {FRAME_COUNTS.name}: re-run wide_frame_counts.py")
    return _COUNTS[key]


def training_sources() -> list[Source]:
    """Every source of the epoch, each with the list of frames its window is allowed to END on.

    How a window is named: by its END frame e. The window is the 16 frames before it (frames e-16 ... e-1), and it
    "happens" at time e / 8 seconds (8 frames per second). So e = 16 is the earliest window (the clip's first 2 s).
    """
    # --- 1) which clips we use ---
    excluded = set(json.loads(NEXAR_EXCLUDED.read_text())["clips"])           # the clips you removed
    crash_meta = []                                                           # Nexar crash clips + their times
    for r in csv.DictReader(open(NEXAR_CRASH_META)):                          # one row per crash clip
        if r["file_name"] not in excluded:                                    # skip the removed ones
            crash_meta.append(r)
    normal_files = []                                                         # Nexar normal clips
    folder = Path(NEXAR_NORMAL_DIR).name                                      # nexar_train_negative
    for key in sorted(json.loads(FRAME_COUNTS.read_text())):                  # every cached clip (no volume listing)
        if key.startswith(folder + "/"):
            normal_files.append(Path(NEXAR_NORMAL_DIR) / f"{key.split('/')[1]}.npy")
    bdd_ids = BDD_TRAIN_CLEAN.read_text().split()                             # the 2,576 clean BDD100K clips

    # --- 2) how many frames each clip has (a window can only end inside the clip) ---
    crash_path = {r["file_name"]: f"{NEXAR_CRASH_DIR}/{Path(r['file_name']).stem}.npy" for r in crash_meta}
    bdd_path = {c: f"{BDD_TRAIN_DIR}/{c}.npy" for c in bdd_ids}
    all_paths = list(crash_path.values()) + [str(p) for p in normal_files] + list(bdd_path.values())
    n_of = {p: n_frames(p) for p in all_paths}                                # path -> number of frames

    sources = []                                                              # what we build here
    dropped = []                                                              # crash clips with no danger window

    # --- 3) Nexar crash clips: one DANGER source and one SAFE source per clip ---
    for r in crash_meta:
        path = crash_path[r["file_name"]]
        alert = float(r["time_of_alert"])                     # seconds from the clip's start: danger first visible
        event = float(r["time_of_event"])                     # seconds from the clip's start: the crash itself
        n = n_of[path]                                        # frames in this clip

        # DANGER pool: the end frames where the label is at least 0.7 (stage1_labels.danger_ends gives them as
        # times in seconds; times x 8 = frame numbers). Keep only frames inside the clip with 2 s of video before.
        danger = []
        for t in L.danger_ends(alert, event):                 # every allowed danger end time (0.125 s apart)
            e = int(round(t * FPS))                           # the same moment as a frame number
            if WINDOW_FRAMES <= e <= n:                       # 16 frames before it exist, and it is inside the clip
                danger.append(e)
        if not danger:                                        # no danger window at all: drop the whole clip
            dropped.append(r["file_name"])
            continue

        # SAFE pool: the end frames the rule labels 0 (before the alert AND more than 4 s before the crash)
        safe = []
        for e in range(WINDOW_FRAMES, n + 1):                 # every possible end frame of the clip
            if L.window_label(e / FPS, alert, event)[1] == L.ZERO:   # the rule's zone for that moment is "0"
                safe.append(e)

        sources.append(Source("crash_danger", r["file_name"], path, np.array(danger), alert, event))
        if safe:                                              # a clip that starts close to the crash has none
            sources.append(Source("crash_safe", r["file_name"], path, np.array(safe), alert, event))

    # --- 4) normal clips (no crash): a window may end on any frame from 16 to the clip's last frame ---
    for p in normal_files:
        sources.append(Source("nexar_normal", p.stem, str(p), np.arange(WINDOW_FRAMES, n_of[str(p)] + 1)))
    for c in bdd_ids:
        sources.append(Source("bdd_normal", c, bdd_path[c], np.arange(WINDOW_FRAMES, n_of[bdd_path[c]] + 1)))

    # --- 5) print what we got ---
    rows = []
    for k in ("crash_danger", "crash_safe", "nexar_normal", "bdd_normal"):
        of_kind = [s for s in sources if s.kind == k]
        rows.append([k, len(of_kind), f"{sum(len(s.ends) for s in of_kind):,}"])
    ml._table("training sources (each gives ONE window per epoch)", ["source", "clips", "allowed window ends"],
              rows, "📦")
    print(f"  crash clips: {len(crash_meta)} after your exclusions ({len(excluded)} removed), "
          f"{len(dropped)} dropped (no danger window), {sum(s.kind == 'crash_danger' for s in sources)} used")
    return sources


def window_label(s: Source, end: int) -> float:
    """The label of the window of source s that ends at frame `end` (normal clips: always 0).

    Arguments:
        s:   the source the window comes from (its kind tells normal from crash; crash clips carry alert / event).
        end: the window's end frame (the window is frames end-16 ... end-1, at time end / 8 s).
    """
    if s.kind in ("nexar_normal", "bdd_normal"):
        return 0.0
    return float(L.window_label(end / FPS, s.alert, s.event)[0])   # the shared rule, at time end / 8 seconds


# ===== CORE 2: augmentation ==========================================================================================
def augment(frames: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Augment one window: 16 frames, each 256 x 448 x 3 (RGB, values 0-255).

    Every random choice (crop box, angle, brightness, ...) is drawn ONCE for the window and applied to all 16 frames,
    so the window stays one consistent piece of video. Only the faint noise grain differs from frame to frame (like
    real camera noise); its strength is the same for all 16.

    Arguments:
        frames: the window's 16 frames, 16 x 256 x 448 x 3, uint8 RGB.
        rng:    this window's own random generator (the same window + epoch always gets the same draw).
    """
    import cv2                                                      # OpenCV: image operations

    h, w = frames.shape[1], frames.shape[2]                         # 256, 448

    # --- 1) geometry: crop + rotate, combined into ONE warp so each frame is resampled only once ---
    # A warp is a 3 x 3 matrix that moves pixels. We start with "no change" (the identity) and add steps to it.
    warp = np.eye(3)
    if rng.random() < CROP_P:
        # CROP: cut 0-5% off each edge (left, top, right, bottom drawn separately), then stretch what is left
        # back to the full 256 x 448 (the same share of height and width, so shapes stay right).
        left, top, right, bottom = rng.uniform(0, CROP_MAX, 4) * [w, h, w, h]   # in pixels
        stretch_x = w / (w - left - right)                          # e.g. 448 / 420 = 1.07
        stretch_y = h / (h - top - bottom)
        crop = np.array([[stretch_x, 0, -left * stretch_x],         # x -> (x - left) x stretch_x
                         [0, stretch_y, -top * stretch_y],          # y -> (y - top) x stretch_y
                         [0, 0, 1]])
        warp = crop @ warp                                          # add the crop to the warp
    if rng.random() < ROTATE_P:
        # ROTATE: turn the picture by -2 .. +2 degrees around its centre
        angle = rng.uniform(-ROTATE_DEG, ROTATE_DEG)
        rotate = np.vstack([cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0), [0, 0, 1]])
        warp = rotate @ warp                                        # add the rotation after the crop
    if not np.allclose(warp, np.eye(3)):                            # only if crop or rotate was drawn
        # apply the same warp to every frame; edges that come into view are filled by mirroring the picture
        warped = []
        for f in frames:
            warped.append(cv2.warpAffine(f, warp[:2], (w, h), flags=cv2.INTER_LINEAR,
                                         borderMode=cv2.BORDER_REFLECT_101))
        frames = np.stack(warped)

    # --- 2) colour: on all 16 frames at once, with pixel values as 0.0 .. 1.0 ---
    x = frames.astype(np.float32) / 255.0
    if rng.random() < BRIGHTNESS_P:
        # BRIGHTNESS: multiply every pixel by 0.85 .. 1.15
        x = x * rng.uniform(1 - BRIGHTNESS, 1 + BRIGHTNESS)
    if rng.random() < CONTRAST_P:
        # CONTRAST: push pixels away from (or towards) the window's average brightness, by 0.85 .. 1.15
        mean = x.mean()
        x = (x - mean) * rng.uniform(1 - CONTRAST, 1 + CONTRAST) + mean
    if rng.random() < SATURATION_P:
        # SATURATION: move colours away from (or towards) grey, by 0.85 .. 1.15
        grey = x @ np.array([0.299, 0.587, 0.114], np.float32)     # each pixel's grey value (standard weights)
        grey = grey[..., None]                                      # same shape as x, to subtract per colour
        x = grey + (x - grey) * rng.uniform(1 - SATURATION, 1 + SATURATION)
    x = np.clip(x, 0.0, 1.0)                                        # back into the valid range
    if rng.random() < GAMMA_P:
        # GAMMA: x ** g with g in 0.85 .. 1.15 brightens or darkens the mid-tones, keeps black and white
        x = x ** rng.uniform(1 - GAMMA, 1 + GAMMA)

    # --- 3) sharpness: light blur (20%) OR light sharpen (20%), never both ---
    u = rng.random()                                                # one draw decides: blur, sharpen or nothing
    if u < BLUR_P:
        sigma = rng.uniform(*BLUR_SIGMA)                            # blur strength in pixels
        x = np.stack([cv2.GaussianBlur(f, (0, 0), sigma) for f in x])
    elif u < BLUR_P + SHARPEN_P:
        # sharpen = add back a share of (picture - blurred picture), which boosts the edges
        amount = rng.uniform(*SHARPEN_AMOUNT)                       # how much the edges are boosted
        x = np.stack([f + amount * (f - cv2.GaussianBlur(f, (0, 0), 1.0)) for f in x])
        x = np.clip(x, 0.0, 1.0)

    # --- 4) faint noise (15%): random grain of 2-5 brightness steps (out of 255) ---
    if rng.random() < NOISE_P:
        strength = rng.uniform(*NOISE_SIGMA) / 255.0                # one strength for the whole window
        x = np.clip(x + rng.normal(0.0, strength, x.shape).astype(np.float32), 0.0, 1.0)

    out = (x * 255.0 + 0.5).astype(np.uint8)                        # back to 0-255 whole numbers (rounded)

    # --- 5) mild JPEG compression (15%): save each frame as a JPEG of quality 70-90 and read it back ---
    if rng.random() < JPEG_P:
        quality = int(rng.integers(JPEG_QUALITY[0], JPEG_QUALITY[1] + 1))   # one quality for the whole window
        compressed = []
        for f in out:
            bgr = cv2.cvtColor(f, cv2.COLOR_RGB2BGR)                # OpenCV's JPEG expects BGR colour order
            ok, jpg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])   # compress in memory
            compressed.append(cv2.cvtColor(cv2.imdecode(jpg, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB))   # read back
        out = np.stack(compressed)
    return out


class TrainWindows(Dataset):
    """The training windows. Item i = this epoch's window of source i, returned as (16 frames, label, id)."""

    def __init__(self, sources: list[Source], seed: int):
        """Keep the sources and draw the plan for epoch 1.

        Arguments:
            sources: every source of the epoch, from training_sources() (4,738): one Source per normal clip, and per
                     crash clip one danger Source + one safe Source. Each says its kind, clip, frames file, the frames
                     its window may end on, and (crash clips) the alert and crash times.
            seed:    the number that fixes every random choice (window end points, augmentations), so a run can be
                     repeated exactly.
        """
        self.sources = sources
        self.seed = seed
        self.ids = [f"{s.kind}|{s.clip}" for s in sources]          # names used in logs, e.g. "bdd_normal|b1c..."
        self.set_epoch(1)                                            # so a plan exists before epoch 1 starts

    # ===== CORE 1: the epoch plan ====================================================================================
    def set_epoch(self, epoch: int) -> None:
        """Choose this epoch's window for EVERY source: one end frame, picked at random from its allowed ends.

        The random generator is seeded with (seed, epoch): the same epoch always picks the same windows, also when
        a stopped run is resumed. Each new epoch picks new windows. ml_utils calls this before every epoch, and the
        worker processes that load the windows start after it, so they use this plan.

        Arguments:
            epoch: the epoch about to start (1, 2, ...); with the seed it decides this epoch's windows.
        """
        self.epoch = epoch
        rng = np.random.default_rng([self.seed, epoch])            # this epoch's own random generator
        self.plan = np.array([int(rng.choice(s.ends)) for s in self.sources])    # end frame per source
        self.labels = np.array([window_label(s, e) for s, e in zip(self.sources, self.plan)], np.float32)
        self.targets = self.labels[:, None]                         # ml_utils prints the label balance from this

    def plan_counts(self) -> dict:
        """How many windows of each kind this epoch has (printed at each epoch start, logged at each validation)."""
        kinds = np.array([s.kind for s in self.sources])            # the kind of every source
        danger = kinds == "crash_danger"                            # True for danger sources
        return {"windows_total": len(self.sources),
                "windows_danger": int(danger.sum()),
                "windows_danger_label_1": int((danger & (self.labels == 1.0)).sum()),
                "windows_danger_ramp_0.7_to_1": int((danger & (self.labels < 1.0)).sum()),
                "windows_safe_crash_clip_part": int((kinds == "crash_safe").sum()),
                "windows_safe_nexar_normal": int((kinds == "nexar_normal").sum()),
                "windows_safe_bdd100k": int((kinds == "bdd_normal").sum()),
                "danger_share_pct": round(100.0 * float(danger.mean()), 1)}

    def __len__(self) -> int:
        return len(self.sources)                                    # one window per source

    def __getitem__(self, i: int):
        """Load window i of this epoch (runs in a worker process): read its 16 frames, augment, return.

        Arguments:
            i: which item (0 ... number of items - 1), chosen by ml_utils's shuffled order.
        """
        s = self.sources[i]
        end = int(self.plan[i])                                     # this epoch's end frame for source i
        # mmap_mode="r" opens the clip without reading it; slicing then reads only these 16 frames from disk;
        # np.array makes them a normal, writable copy (PyTorch warns about read-only arrays)
        frames = np.array(np.load(s.path, mmap_mode="r")[end - WINDOW_FRAMES:end])
        rng = np.random.default_rng([self.seed, self.epoch, i])    # this window's own augmentation draw
        frames = augment(frames, rng)
        label = torch.tensor([self.labels[i]])                      # shape (1,): one target per window
        return torch.from_numpy(frames), label, f"{self.ids[i]}|{end}"


class ValWindows(Dataset):
    """The 2,202 FIXED validation windows (from val_windows.json): never augmented, the same every epoch."""

    def __init__(self, windows: list[dict]):
        """Find each window's clip file and end frame, and the facts the scores need.

        Arguments:
            windows: the list read from val_windows.json, one dict per window (group, folder, clip, end / end_back,
                     rank, label, nexar_group: see make_val_windows.py).
        """
        # where each clip's frames are
        for w in windows:
            w["path"] = f"{CACHE}/{w['folder']}/{w['clip']}.npy"
        # Nexar windows are given as "frames before the clip's last frame" (end_back), so we need each clip's
        # length to know the end frame. BDD windows already have their end frame.
        lengths = [n_frames(w["path"]) for w in windows]              # from FRAME_COUNTS (no volume reads)
        for w, n in zip(windows, lengths):
            if w["end"] is None:
                w["end"] = n - w["end_back"]                        # e.g. last frame (back 0) or 0.5 s before (4)
        self.windows = windows
        self.ids = [f"{w['group']}|{w['clip']}|{w['end']}" for w in windows]   # names in the prediction files
        self.targets = np.array([[w["label"]] for w in windows], np.float32)    # the right answers
        # Per-window facts the scores need. They line up with the model's outputs because the validation loader
        # never shuffles: output k belongs to window k.
        self.group = np.array([w["group"] for w in windows])                  # nexar_crash / nexar_normal / bdd_hard
        self.rank = np.array([w["rank"] for w in windows])                    # 1st or 2nd window of its clip
        self.nexar_group = np.array([-1 if w["nexar_group"] is None else w["nexar_group"] for w in windows])  # -1: BDD

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, i: int):
        w = self.windows[i]
        frames = np.array(np.load(w["path"], mmap_mode="r")[w["end"] - WINDOW_FRAMES:w["end"]])   # writable copy
        return torch.from_numpy(frames), torch.tensor([w["label"]], dtype=torch.float32), self.ids[i]


TRAIN: TrainWindows | None = None        # set in build_data; the hooks below read them
VAL: ValWindows | None = None
STEPS_PER_EPOCH = [1]                    # weight updates per epoch (set in build_data; a list so it can be changed)


def build_data(cfg: dict) -> dict:
    """Build the train and validation datasets (on Modal), and set the rolling checkpoint to once per epoch.

    Arguments:
        cfg: the run's settings (ml_utils config); its rolling-checkpoint setting is filled in here.
    """
    global TRAIN, VAL
    ml._banner("STAGE 1 DATA", "📦")
    TRAIN = TrainWindows(training_sources(), SEED)
    VAL = ValWindows(json.loads(VAL_WINDOWS.read_text()))
    ml._table("validation windows (fixed, 2 per clip)", ["group", "windows", "label"],
              [[g, int((VAL.group == g).sum()), lab] for g, lab in
               (("nexar_crash", 1), ("nexar_normal", 0), ("bdd_hard", 0))], "🔎")

    # Weight updates per epoch: windows / 8 per GPU pass (a last, incomplete pass is dropped), then 4 passes per
    # update (rounded up: a last, shorter group of passes still makes an update).
    passes = len(TRAIN) // BATCH_SIZE
    steps = -(-passes // ACCUM_STEPS)                             # -(-a // b) = a / b rounded UP
    STEPS_PER_EPOCH[0] = steps
    cfg["output"]["checkpoint_every_steps"] = CHECKPOINT_EVERY    # a rolling checkpoint every N updates
    # (a resume loads the NEWEST checkpoint, rolling or last.pt, and continues mid-epoch if needed)
    if VALS_PER_EPOCH > 1:                                        # also validate inside the epoch, e.g. halfway
        # ml_utils: from that epoch on, validate every N updates (148 / 2 = 74). The step that ends an epoch is
        # validated once (ml_utils skips a second validation at the same step).
        cfg["evaluation"]["eval_steps_schedule"] = [[MORE_OFTEN_FROM_EPOCH, steps // VALS_PER_EPOCH]]
    print(f"  one epoch = {len(TRAIN):,} windows = {passes} GPU passes of {BATCH_SIZE} = {steps} weight updates; "
          f"rolling checkpoint every {steps} updates (the last {KEEP_LAST_N} kept)")
    return {"train": TRAIN, "val": VAL}                           # ml_utils trains on "train", scores "val"


# =====================================================================================================================
# MODEL
# =====================================================================================================================
# ===== CORE 4: the batched predictor =================================================================================
def batched_predict_future(self, encoder_features: torch.Tensor) -> torch.Tensor:
    """BADAS's "future" prediction for the WHOLE batch in one call (BADAS's own code does one clip at a time).

    What the predictor does: the encoder turns a window into 3,584 tokens (the "present"). The predictor gets those
    plus 896 empty slots for the "future", fills the slots in, and returns them (each token = 1,024 numbers).
    It is told which positions are present (context) and which to fill (target) by two lists of positions.
    BADAS's loop builds those lists for one clip; here the same lists are repeated for every clip of the batch, so
    one call does them all. check_batched_predictor() proves it gives the same numbers before training starts.
    `self` is BADAS's classifier object (this function replaces its own _predict_future_features).

    Arguments:
        self:             BADAS's classifier object (this function replaces its own method).
        encoder_features: the encoder's tokens, batch x 3,584 x 1,024 (the 'present').
    """
    batch, n_present, width = encoder_features.shape                 # e.g. 8, 3584, 1024

    # How many future slots: BADAS's checkpoint config says 1 s of future and "original_fps" 4, so 1 s / (16 frames /
    # 4 per s) = a quarter of the present tokens = 896. (Same formula as BADAS's own code.)
    # Note: we really feed 8 fps (16 frames = 2 s), so these 896 slots are 2 of 8 time steps = 0.5 s ahead, not 1 s.
    # Kept as is: BADAS-Open was trained this way, so its weights expect exactly 896 future slots.
    future_s = getattr(self.config, "future_prediction_seconds", 1.0)
    present_s = self.config.frame_count / getattr(self.config, "original_fps", 4)
    n_future = max(int(n_present * (future_s / present_s)), 1)

    # Build one long row of tokens per clip: the 3,584 real tokens from the encoder, then 896 placeholder tokens
    # for the future (all zeros). BADAS's code passes the predictor this full-length row, so we do the same.
    # The zeros are never used: the predictor throws them away and puts its own learned "fill me in" token there.
    empty = encoder_features.new_zeros(batch, n_future, width)        # the 896 placeholders: batch x 896 x 1,024
    tokens = torch.cat([encoder_features, empty], dim=1)              # real + placeholders: batch x 4,480 x 1,024

    # Tell the predictor which token positions are which, as two lists of position numbers per clip:
    #   context = positions 0 ... 3,583     -> "these are known (the 2 s we saw)"
    #   target  = positions 3,584 ... 4,479 -> "predict these (the future)"
    # Every clip uses the same numbers, so one list is copied once per clip in the batch (.expand).
    device = encoder_features.device
    context = torch.arange(n_present, device=device).unsqueeze(0).expand(batch, -1)                       # batch x 3,584
    target = torch.arange(n_present, n_present + n_future, device=device).unsqueeze(0).expand(batch, -1)  # batch x 896

    # Run the predictor; it returns only its guesses for the future positions: batch x 896 tokens x 1,024 numbers
    return self.predictor(tokens, context_mask=[context], target_mask=[target]).last_hidden_state


def check_batched_predictor(net: nn.Module, device) -> float:
    """Stop the run unless the batched predictor gives the same numbers as BADAS's own one-clip-at-a-time loop.

    4 random clips, full precision. "Same" = the largest difference is under PREDICTOR_CHECK_TOL (tiny differences
    come from the order of additions inside the GPU, not from a different computation).

    Arguments:
        net:    BADAS's classifier (before LoRA).
        device: where to run the check (the GPU).
    """
    net.eval()                                                        # no randomness (dropout off)
    x = torch.randn(4, WINDOW_FRAMES, 3, CHECK_H, CHECK_W, device=device)   # 4 random clips
    with torch.no_grad():                                             # no gradients needed for a check
        present = net._extract_video_features(x)                      # the encoder's 3,584 tokens per clip
        loop = type(net)._predict_future_features(net, present)      # BADAS's own code (one clip at a time)
        batched = batched_predict_future(net, present)               # ours (all clips at once)
    diff = float((loop - batched).abs().max())                        # the largest difference anywhere
    print(f"  ✅ batched predictor vs BADAS's per-clip loop: largest difference {diff:.2e} "
          f"(allowed {PREDICTOR_CHECK_TOL:g})")
    if not diff <= PREDICTOR_CHECK_TOL:
        raise SystemExit("batched predictor differs from BADAS's loop: stopping")
    return diff


# ===== CORE 3: LoRA on every layer ===================================================================================
def add_lora(net: nn.Module) -> nn.Module:
    """Wrap BADAS-Open with LoRA, switch on the small parts that train fully, then CHECK that nothing is left out.

    LoRA in one sentence: each chosen weight matrix W stays frozen, and next to it the model learns a small update
    B x A (A: 16 x input size, B: output size x 16, "rank 16"), added as W + (alpha / rank) x B x A = W + 2 x B x A.
    B starts at zero, so at step 0 the model is exactly BADAS-Open.

    The run stops when:
      - the number of LoRA layers is not the 219 expected (a renamed layer would silently lose its LoRA),
      - any frozen weight is neither the base of a LoRA layer nor a backup copy (= it would be left out of training),
      - the predictor is no longer one shared object (BADAS lists it twice: predictor and backbone.predictor).

    Arguments:
        net: BADAS's classifier (the network to wrap).
    """
    from peft import LoraConfig, get_peft_model                      # peft: the library that adds LoRA

    config = LoraConfig(r=LORA_RANK, lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
                        bias="none",                          # biases are not trained (standard for LoRA)
                        target_modules=LORA_TARGETS,          # which layers get LoRA (the 219, by name)
                        modules_to_save=FULLY_TRAINED)        # trained fully: time-attention + head
    model = get_peft_model(net, config)                       # BADAS wrapped: every target layer now has LoRA

    # peft leaves LayerNorms and the predictor's mask tokens frozen: switch them on (tiny, and they matter).
    # "lora_" = the new LoRA weights (already on); "original_module" = peft's frozen backup of the fully-trained parts.
    for name, p in model.named_parameters():
        is_norm_or_mask = "norm" in name or name.endswith("mask_tokens")
        if is_norm_or_mask and "lora_" not in name and "original_module" not in name:
            p.requires_grad_(True)                            # requires_grad = this weight gets trained

    # --- the checks ---
    # every layer that got LoRA (it now has a frozen "base_layer" and the new "lora_A" / "lora_B")
    lora_layers = {n: m for n, m in model.named_modules() if hasattr(m, "base_layer") and hasattr(m, "lora_A")}
    # the frozen weights that LoRA adapts (these are fine to be frozen)
    lora_bases = set()
    for n, m in lora_layers.items():
        for pn, _ in m.base_layer.named_parameters():
            lora_bases.add(f"{n}.base_layer.{pn}")
    # a frozen weight that is NOT a LoRA base and NOT peft's backup copy would never change: left out
    left_out = []
    for name, p in model.named_parameters():
        if not p.requires_grad and name not in lora_bases and "original_module" not in name:
            left_out.append(name)
    inner = model.base_model.model                                    # BADAS's classifier inside peft's wrapper
    shared = inner.predictor is inner.backbone.predictor              # still ONE predictor object?
    by_type = {}                                                      # LoRA layers counted by layer type
    for m in lora_layers.values():
        kind = type(m.base_layer).__name__                            # Linear or Conv3d
        by_type[kind] = by_type.get(kind, 0) + 1
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)   # values that will change
    total = sum(p.numel() for p in model.parameters())                          # all values
    ml._table("LoRA coverage check", ["check", "re sult"], [
        ("LoRA layers", f"{len(lora_layers)} (expected {EXPECTED_LORA_LAYERS})  {by_type}"),
        ("weights left out of training", len(left_out)),
        ("predictor still one shared object", shared),
        ("trainable values", f"{trainable / 1e6:.2f} M of {total / 1e6:.1f} M"),
    ], "🧩")
    if len(lora_layers) != EXPECTED_LORA_LAYERS or left_out or not shared:
        raise SystemExit(f"LoRA coverage check failed: {len(lora_layers)} layers, left out {left_out[:10]}, "
                         f"shared predictor {shared}")
    return model


def check_gradients_reach_everything(model: nn.Module, device) -> None:
    """One forward + backward pass on 2 random clips: every trainable weight must receive a gradient.

    A weight with no gradient is cut off from the loss and would never learn (a "dead path"). Two details:
      - drop_path (training randomly skips whole blocks) is paused, else a skipped block would look dead;
      - LoRA's A matrices get a gradient of exactly zero on this first pass (B is still zero): zero is fine, MISSING
        (None) is not.

    Arguments:
        model:  the full RiskModel (BADAS + LoRA).
        device: where to run the check (the GPU).
    """
    model.train()                                                     # training mode (as in real training)
    drop_path = [m for m in model.modules() if type(m).__name__ == "VJEPA2DropPath"]
    for m in drop_path:
        m.eval()                                                      # eval mode = never skip
    with torch.autocast("cuda", dtype=torch.bfloat16):                # same 16-bit maths as training
        out = model(torch.randn(2, WINDOW_FRAMES, 3, CHECK_H, CHECK_W, device=device))
    target = torch.tensor([[0.0], [1.0]], device=device)              # any labels will do
    nn.functional.binary_cross_entropy_with_logits(out.float(), target).backward()   # computes every gradient
    dead = [n for n, p in model.named_parameters() if p.requires_grad and p.grad is None]
    model.zero_grad(set_to_none=True)                                 # throw the gradients away: only a check
    for m in drop_path:
        m.train()                                                     # drop_path back on
    print(f"  ✅ gradient check: {len(dead)} trainable weights without a gradient (must be 0)")
    if dead:
        raise SystemExit(f"trainable weights with no gradient: {dead[:10]}")


class RiskModel(nn.Module):
    """BADAS-Open + LoRA, giving ONE number per window: the crash-risk logit (its sigmoid = BADAS's risk, 0..1)."""

    def __init__(self, device):
        """Load BADAS-Open, patch it for 16:9, add LoRA, and run the start-up checks.

        Arguments:
            device: where the model lives (the GPU).
        """
        super().__init__()
        from huggingface_hub import snapshot_download               # downloads from Hugging Face (or uses the cache)

        # --- load BADAS-Open exactly as its released code does (code + weights from Hugging Face) ---
        repo = Path(snapshot_download(BADAS_REPO, allow_patterns=["src/*", "src/**/*", "weights/*"]))
        sys.path.insert(0, str(repo / "src"))                       # so BADAS's own code can be imported
        from models.vjepa import VJEPAModel                         # BADAS's loader class
        badas = VJEPAModel(model_name=BASE_MODEL, checkpoint_path=str(repo / "weights" / "badas_open.pth"),
                           device=str(device), frame_count=WINDOW_FRAMES, img_size=FRAME_H, target_fps=float(FPS),
                           use_sliding_window=False)
        badas.load()                                                # builds the network and loads its weights
        net = badas.model                                           # the network: encoder, predictor, time-attention, head
        # 16:9: tell every attention layer the real token grid (16 rows x 28 columns), see wide_input.py
        n_patched = W.patch_positions(net, FRAME_H, FRAME_W)
        print(f"  ✅ 16:9 input: {n_patched} attention layers use the {FRAME_H // 16} x {FRAME_W // 16} patch grid "
              f"(expected 36)")
        if n_patched != 36:
            raise SystemExit("position patch: not every attention layer found: stopping")
        if GRAD_CHECKPOINTING and hasattr(net.backbone, "gradient_checkpointing_enable"):
            net.backbone.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            print("  🧮 gradient checkpointing ON (less memory, slower)")

        # --- CORE 4: prove the batched predictor equals BADAS's loop, then switch to it ---
        check_batched_predictor(net, device)
        x = torch.randn(2, WINDOW_FRAMES, 3, CHECK_H, CHECK_W, device=device)   # 2 random clips
        with torch.no_grad():
            before = net(x)                                         # plain BADAS-Open's 2 scores on them
        net._predict_future_features = types.MethodType(batched_predict_future, net)   # use ours from now on

        # --- CORE 3: LoRA on every layer (the coverage check runs inside) ---
        self.net = add_lora(net)

        # --- start check: LoRA starts at zero, so the outputs must still be plain BADAS-Open's ---
        self.net.eval()
        with torch.no_grad():
            diff = float((self.net(x) - before).abs().max())        # same 2 clips, now through LoRA + batched predictor
        print(f"  ✅ start check: after adding LoRA + the batched predictor, outputs differ from plain BADAS-Open by "
              f"{diff:.2e} (must be about 0)")
        if not diff <= PREDICTOR_CHECK_TOL:
            raise SystemExit("the model at step 0 is not BADAS-Open: stopping")
        check_gradients_reach_everything(self, device)
        # the names of the weights training changes (what the checkpoints store)
        self._trainable = {n for n, p in self.named_parameters() if p.requires_grad}

    # ===== CORE 5: the risk number and the loss =====================================================================
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: a batch of windows, B x 16 x 3 x 256 x 448 (already normalised by prepare). Returns B x 1.

        BADAS's head gives 2 scores per window: s_safe and s_crash. Its risk is softmax([s_safe, s_crash] / 2) for
        the crash class. With only two classes, that softmax is exactly sigmoid((s_crash - s_safe) / 2). So we pass
        on ONE number per window, z = (s_crash - s_safe) / 2, and sigmoid(z) is BADAS's risk.

        The loss (ml_utils, "bce") is binary cross-entropy between sigmoid(z) and the window's label (1, a ramp value
        from 0.7 to 1, or 0). That is the same loss as BADAS's own 2-class cross-entropy, with a soft target.

        Arguments:
            x: the batch from prepare(): B x 16 x 3 x 256 x 448, normalised.
        """
        scores = self.net(x)                                     # B x 2: column 0 = safe, column 1 = crash
        z = (scores[:, 1] - scores[:, 0]) / TEMPERATURE          # one number per window
        return z.unsqueeze(1)                                    # B x 1 (one target: crash_risk)

    # --- checkpoints store only what training changes ---
    # The frozen 330 M BADAS weights never change, so a checkpoint holds just the 14 M trainable ones (about
    # 57 MB, plus the optimizer state); the frozen part is reloaded from BADAS-Open at every start. ml_utils calls
    # these two methods when it saves and loads.
    def state_dict(self, *args, **kwargs):
        """The weights to save: only the trainable ones.

        Arguments:
            *args, **kwargs: passed on to PyTorch's own state_dict (prefix, keep_vars, ...).
        """
        full = super().state_dict(*args, **kwargs)               # every weight, frozen and trainable
        prefix = kwargs.get("prefix", "")                        # (empty unless called from a parent module)
        return type(full)((k, v) for k, v in full.items() if k[len(prefix):] in self._trainable)   # trainable only

    def load_state_dict(self, state_dict, strict: bool = True, assign: bool = False):
        """Load saved trainable weights; the frozen ones stay as loaded from BADAS-Open.

        Arguments:
            state_dict: the saved weights (from a checkpoint).
            strict:     True = stop if any trainable weight is missing from it.
            assign:     passed on to PyTorch (False = copy the values into the existing weights).
        """
        missing = sorted(self._trainable - set(state_dict))        # a trainable weight the checkpoint lacks
        if strict and missing:
            raise RuntimeError(f"checkpoint is missing {len(missing)} trainable weights, e.g. {missing[:5]}")
        res = super().load_state_dict(state_dict, strict=False, assign=assign)   # frozen ones stay as loaded
        if res.unexpected_keys:                                   # a weight this model does not have
            raise RuntimeError(f"checkpoint has unknown weights: {res.unexpected_keys[:5]}")
        return res


def build_model(cfg: dict) -> nn.Module:
    """Called by ml_utils on Modal: the model to train.

    Arguments:
        cfg: the run's settings (ml_utils config; used to pick the device).
    """
    os.environ.setdefault("HF_HOME", HF_CACHE)                   # Hugging Face uses the volume's download cache
    ml._banner("STAGE 1 MODEL: BADAS-Open + LoRA", "🧠")
    return RiskModel(ml.pick_device(cfg))                         # pick_device: the GPU


# =====================================================================================================================
# HOOKS: GPU preprocessing, scores, prints (ml_utils calls these at the right moments)
# =====================================================================================================================
def prepare(x: torch.Tensor, device, cfg) -> torch.Tensor:
    """Turn a batch of raw windows into model input, on the GPU (ml_utils calls this for every batch).

    In:  B x 16 x 256 x 448 x 3, values 0-255 (as stored in the 16:9 cache: already the right size and shape).
    Out: B x 16 x 3 x 256 x 448: scaled to 0..1, then normalised with the ImageNet mean / spread (what V-JEPA 2 was
         pretrained on), colour channel moved before height and width. Same as eval_risk.py --wide.

    Arguments:
        x:      the batch as loaded, B x 16 x 256 x 448 x 3 uint8.
        device: the GPU.
        cfg:    the run's settings (not needed here; ml_utils passes it to every prepare hook).
    """
    return W.normalise(x.to(device, non_blocking=True))               # done on the GPU (fast)


def _ap(crash_risks: np.ndarray, normal_risks: np.ndarray) -> float:
    """Average precision (AP): how well crash windows rank ABOVE normal ones. 1.0 = every crash window scores higher
    than every normal window; lower = some normal windows score as high as crashes (false alarms).

    Arguments:
        crash_risks:  the model's risk on the crash windows.
        normal_risks: the model's risk on the normal windows.
    """
    from sklearn.metrics import average_precision_score
    if not len(crash_risks) or not len(normal_risks):              # needs both kinds
        return float("nan")
    is_crash = np.r_[np.ones(len(crash_risks)), np.zeros(len(normal_risks))]   # the right answers: 1 crash, 0 normal
    return float(average_precision_score(is_crash, np.r_[crash_risks, normal_risks]))


LAST_RISK = None                           # the last validation's risks, kept for detailed_scores


# ===== CORE 6: the validation scores ================================================================================
def validation_scores(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    """The main validation numbers. ml_utils calls this after scoring the 2,202 windows, adds the numbers to
    val_log.csv (as val_<name>) and prints them; MONITOR (ap_crash_vs_all_normal) picks best.pt.

    y_prob: the model's risk for each validation window, in the same order as val_windows.json.

      ap_crash_vs_all_normal    AP: Nexar crash windows vs ALL normal ones (Nexar normal + BDD100K hard moments)
      ap_crash_vs_nexar_normal  AP: Nexar crash vs Nexar normal (same camera, same test moments)
      ap_crash_vs_bdd_hard      AP: Nexar crash vs the BDD100K moments plain BADAS found riskiest (false-beep cases)
      nexar_official_map        Nexar's own score: AP within each test group (clip ends 0.5 / 1.0 / 1.5 s before
                                the crash), on each clip's LAST-frame window only, averaged. Baseline: 0.903
      mean_risk_*               the average risk on each kind of window

    Arguments:
        y_true: the right answers per window (not needed: the window groups say which are crashes).
        y_prob: the model's risk per window, N x 1, in val_windows.json order.
    """
    global LAST_RISK
    risk = y_prob[:, 0]                                 # one risk per window
    LAST_RISK = risk                                    # kept for on_validation's detailed numbers

    # which windows are which (True / False per window)
    is_crash = VAL.group == "nexar_crash"
    is_nexar_normal = VAL.group == "nexar_normal"
    is_bdd = VAL.group == "bdd_hard"
    is_last_frame = VAL.rank == 1                       # the official test moment of a Nexar clip

    out = {"ap_crash_vs_all_normal": _ap(risk[is_crash], risk[is_nexar_normal | is_bdd]),
           "ap_crash_vs_nexar_normal": _ap(risk[is_crash], risk[is_nexar_normal]),
           "ap_crash_vs_bdd_hard": _ap(risk[is_crash], risk[is_bdd])}

    # Nexar's official score: one AP per test group, then their average
    per_group = []
    for k in GROUP_SECONDS:                             # groups 0, 1, 2
        in_group = VAL.nexar_group == k
        per_group.append(_ap(risk[is_crash & is_last_frame & in_group], risk[is_nexar_normal & is_last_frame & in_group]))
    out["nexar_official_map"] = float(np.mean(per_group))

    out["mean_risk_nexar_crash"] = float(risk[is_crash].mean())
    out["mean_risk_nexar_normal"] = float(risk[is_nexar_normal].mean())
    out["mean_risk_bdd_hard"] = float(risk[is_bdd].mean())
    return out


def detailed_scores(risk: np.ndarray) -> dict:
    """The rest of the validation numbers (on_validation adds them to the same val_log.csv row):

      group_<s>s_...                 per Nexar test group (s = 0.5 / 1.0 / 1.5 s before the crash): the official AP,
                                     AP vs the BDD100K hard moments, mean crash risk, crashes caught above 0.9 / 0.99
      crash_caught_pct_at_<t>        % of Nexar crash windows with risk above threshold t
      nexar_normal_alarm_pct_at_<t>  % of Nexar normal windows above t (false alarms)
      bdd_hard_alarm_pct_at_<t>      % of BDD100K hard moments above t (false alarms)
      calibration_error              0 = honest risk values (of windows given about 0.8, about 80% are crashes)

    Arguments:
        risk: the model's risk per validation window, in val_windows.json order.
    """
    is_crash = VAL.group == "nexar_crash"
    is_nexar_normal = VAL.group == "nexar_normal"
    is_bdd = VAL.group == "bdd_hard"
    is_last_frame = VAL.rank == 1
    out = {}

    # --- per Nexar test group ---
    for k, sec in GROUP_SECONDS.items():
        in_group = VAL.nexar_group == k
        crash_here = risk[is_crash & in_group]                        # this group's crash windows (both ranks)
        out[f"group_{sec}s_official_ap_crash_vs_nexar_normal"] = _ap(risk[is_crash & is_last_frame & in_group],
                                                                      risk[is_nexar_normal & is_last_frame & in_group])
        out[f"group_{sec}s_ap_crash_vs_bdd_hard"] = _ap(crash_here, risk[is_bdd])
        out[f"group_{sec}s_mean_risk_crash"] = float(crash_here.mean())
        for t in (0.9, 0.99):
            out[f"group_{sec}s_crash_caught_pct_at_{t}"] = round(100.0 * float((crash_here > t).mean()), 2)

    # --- at every threshold: share of windows above it ---
    for t in THRESHOLDS:
        out[f"crash_caught_pct_at_{t}"] = round(100.0 * float((risk[is_crash] > t).mean()), 2)
        out[f"nexar_normal_alarm_pct_at_{t}"] = round(100.0 * float((risk[is_nexar_normal] > t).mean()), 2)
        out[f"bdd_hard_alarm_pct_at_{t}"] = round(100.0 * float((risk[is_bdd] > t).mean()), 2)

    # --- calibration error: split windows into 10 bins by risk (0-0.1, ..., 0.9-1). In each bin compare the average
    #     risk with the share that really are crashes; add up the gaps, weighted by how many windows each bin holds ---
    truth = is_crash.astype(float)                                    # 1 for crash windows, 0 otherwise
    bin_of = np.clip((risk * 10).astype(int), 0, 9)                   # which of the 10 bins each window falls in
    gap = 0.0
    for b in range(10):
        in_bin = bin_of == b
        if in_bin.any():
            gap += abs(risk[in_bin].mean() - truth[in_bin].mean()) * in_bin.mean()
    out["calibration_error"] = float(gap)
    return out


VAL_SECS = [0.0]                           # seconds spent validating so far (taken out of the per-epoch estimate)


def hours_minutes(seconds: float) -> str:
    """Seconds as "12 h 05 min".

    Arguments:
        seconds: a duration in seconds.
    """
    minutes = int(round(seconds / 60))
    return f"{minutes // 60} h {minutes % 60:02d} min"


def video_watched(step: int) -> dict:
    """How much VIDEO the model has trained on after `step` weight updates, and how much is left in the whole run.

    Each weight update uses BATCH_SIZE x ACCUM_STEPS = 32 windows, and each window is 2 s of video. So after `step`
    updates the model has watched step x 32 x 2 s. The whole run is STEPS_PER_EPOCH x EPOCHS updates. (Counted in
    windows seen: the same clip comes back each epoch, at a new random moment.)

    Arguments:
        step: weight updates done so far.
    """
    window_s = WINDOW_FRAMES / FPS                                   # 2 s of video per window
    per_step_s = BATCH_SIZE * ACCUM_STEPS * window_s                 # 32 windows x 2 s = 64 s per update
    total_steps = STEPS_PER_EPOCH[0] * EPOCHS                        # every update of the whole run
    seen_s = step * per_step_s
    total_s = total_steps * per_step_s
    return {"seen_s": seen_s, "left_s": max(total_s - seen_s, 0.0), "total_s": total_s}


def on_epoch_start(epoch: int, model, loaders) -> None:
    """Print what this epoch trains on (TrainWindows.set_epoch has just drawn the plan).

    Arguments:
        epoch:   the epoch about to start.
        model:   the model (not needed here; ml_utils passes it to this hook).
        loaders: the data loaders (not needed here).
    """
    counts = TRAIN.plan_counts()
    rows = [[k.replace("windows_", "").replace("_", " "), v] for k, v in counts.items()]   # readable names
    ml._table(f"epoch {epoch}: training windows (one per source, new random end points)", ["windows", "count"],
              rows, "🎲")
    # video watched before this epoch starts (all earlier epochs are complete)
    vw = video_watched((epoch - 1) * STEPS_PER_EPOCH[0])
    print(f"  🎞️  video watched so far: {hours_minutes(vw['seen_s'])}   left: {hours_minutes(vw['left_s'])}   "
          f"whole run: {hours_minutes(vw['total_s'])}  ({EPOCHS} epochs; each window = 2 s)")


def on_validation(row: dict, epoch: int, step: int) -> None:
    """After each validation: add the detailed numbers and the cost to the val_log.csv row, then print ONE clear
    summary block (ml_utils's own lines above it list the same main numbers, plus its standard ones).

    Arguments:
        row:   this validation's val_log.csv row (val_<name> numbers so far); more columns are added to it.
        epoch: the current epoch.
        step:  weight updates done so far (0 = before any training).
    """
    # --- more columns for val_log.csv ---
    row.update({f"val_{k}": v for k, v in detailed_scores(LAST_RISK).items()})
    row.update({f"train_{k}": v for k, v in TRAIN.plan_counts().items()})

    # --- cost: time so far x price; per epoch = training seconds per update x updates per epoch + one validation ---
    if step:                                                          # step 0 runs before the clock starts
        VAL_SECS[0] += row.get("val_secs", 0.0)                      # this validation's time
    train_s = max(row.get("elapsed_s", 0.0) - VAL_SECS[0], 0.0)      # time spent training (not validating)
    row["cost_usd_so_far"] = round(row.get("elapsed_s", 0.0) / 3600 * PRICE_H, 3)
    vw = video_watched(step)                                          # hours of video trained on so far / left
    row["video_hours_watched"] = round(vw["seen_s"] / 3600, 3)
    row["video_hours_left"] = round(vw["left_s"] / 3600, 3)
    if step:                                                          # step 0 = before training: nothing to measure
        vals = VALS_PER_EPOCH if epoch >= MORE_OFTEN_FROM_EPOCH else 1   # validations in one epoch now
        per_epoch_s = train_s / step * STEPS_PER_EPOCH[0] + vals * row.get("val_secs", 0.0)
        row["est_minutes_per_epoch"] = round(per_epoch_s / 60, 1)
        row["est_cost_usd_per_epoch"] = round(per_epoch_s / 3600 * PRICE_H, 2)

    # --- the summary block ---
    def v(name):                                          # a number from this row
        return row.get(f"val_{name}", float("nan"))

    before = "  (plain BADAS-Open, before any training)" if step == 0 else ""
    ml._banner(f"STAGE 1 VALIDATION SUMMARY  epoch {epoch}  step {step}{before}", "📋")
    ml._table("ranking quality: average precision (1.0 = every crash window above every normal one)",
              ["measure", "value"], [
                  ("Nexar crash vs ALL normal  (picks best.pt)", f"{v('ap_crash_vs_all_normal'):.4f}"),
                  ("Nexar crash vs Nexar normal", f"{v('ap_crash_vs_nexar_normal'):.4f}"),
                  ("Nexar crash vs BDD100K val hard moments", f"{v('ap_crash_vs_bdd_hard'):.4f}"),
                  ("Nexar official mAP (last frame, 3 groups)", f"{v('nexar_official_map'):.4f}   (baseline 0.903)"),
                  ("calibration error (0 = honest risk values)", f"{v('calibration_error'):.4f}"),
              ], "🏁")
    ml._table("mean risk per window group", ["Nexar crash", "Nexar normal", "BDD100K val hard moments"],
              [[f"{v('mean_risk_nexar_crash'):.4f}", f"{v('mean_risk_nexar_normal'):.4f}",
                f"{v('mean_risk_bdd_hard'):.4f}"]], "📊")
    group_rows = []                                       # one row per Nexar test group
    for sec in GROUP_SECONDS.values():
        group_rows.append([f"{sec} s before the crash",
                           f"{v(f'group_{sec}s_official_ap_crash_vs_nexar_normal'):.4f}",
                           f"{v(f'group_{sec}s_ap_crash_vs_bdd_hard'):.4f}",
                           f"{v(f'group_{sec}s_mean_risk_crash'):.4f}",
                           f"{v(f'group_{sec}s_crash_caught_pct_at_0.9'):.1f}%",
                           f"{v(f'group_{sec}s_crash_caught_pct_at_0.99'):.1f}%"])
    ml._table("by Nexar test group (when the clip ends)",
              ["group", "official AP vs Nexar normal", "AP vs BDD hard", "mean crash risk",
               "crashes caught > 0.9", "crashes caught > 0.99"], group_rows, "⏱️")
    threshold_rows = []                                   # one row per threshold
    for t in THRESHOLDS:
        threshold_rows.append([t, f"{v(f'crash_caught_pct_at_{t}'):.1f}%",
                               f"{v(f'nexar_normal_alarm_pct_at_{t}'):.1f}%",
                               f"{v(f'bdd_hard_alarm_pct_at_{t}'):.1f}%"])
    ml._table("at each threshold: share of windows with risk above it",
              ["threshold", "crashes caught (Nexar crash)", "false alarms (Nexar normal)",
               "false alarms (BDD100K hard moments)"], threshold_rows, "🎚️")
    ml._table("video the model has trained on (each window = 2 s of video)", ["", "hours"], [
        ("watched so far", hours_minutes(vw["seen_s"])),
        ("left in this run", hours_minutes(vw["left_s"])),
        (f"whole run ({EPOCHS} epochs)", hours_minutes(vw["total_s"])),
    ], "🎞️")
    cost = [("cost so far (GPU + CPU + memory)", f"${row['cost_usd_so_far']:.2f}  at ${PRICE_H:.2f} per hour")]
    if step:
        cost += [("estimated time per epoch", f"{row['est_minutes_per_epoch']} min"),
                 ("estimated cost per epoch", f"${row['est_cost_usd_per_epoch']:.2f}"),
                 (f"estimated cost for {EPOCHS} epochs", f"${row['est_cost_usd_per_epoch'] * EPOCHS:.2f}")]
    ml._table("cost", ["item", "value"], cost, "💰")
    print("═" * 78 + "\n", flush=True)                   # a clear line: the summary block ends here


# the functions ml_utils should call: prepare every batch, score every validation, and the two print hooks
HOOKS = ml.Hooks(prepare=prepare, score=validation_scores, on_epoch_start=on_epoch_start,
                 on_validation=on_validation)


# =====================================================================================================================
# MODAL: what runs where
# =====================================================================================================================
import modal  # noqa: E402                               # the Modal library (cloud GPUs)

app = modal.App(EXP_NAME)                                 # the Modal app, named after this run
VOLUMES = ml.modal_volumes(CFG)                           # /runs (results) and /data (videos, cache, models)
try:                                                      # this PC's Hugging Face login, passed for this run only
    from huggingface_hub import get_token
    _HF = modal.Secret.from_dict({"HF_TOKEN": get_token() or ""})
except Exception:
    _HF = modal.Secret.from_dict({})


# The container: the PIP packages + the src/risk code (ml_utils.modal_image), the two volumes, the A100.
@app.function(image=ml.modal_image(CFG, PKG_ROOT), volumes=VOLUMES, secrets=[_HF], **ml.modal_resources(CFG))
def train_remote(run_id: str = "", smoke: bool = False):
    """Runs inside the Modal container on the A100: builds the model and data, then ml_utils trains.

    Arguments:
        run_id: run001, run002, ... (allocated on this PC by main).
        smoke:  True = the short smoke test.
    """
    os.environ["HF_HOME"] = HF_CACHE                       # must be set before transformers is imported
    cfg = cfg_for(smoke)                                   # the smoke test or the real run's settings
    ml.modal_train(cfg, EXP_DIR, build_model, build_data, hooks=HOOKS, run_id=run_id, volumes=VOLUMES)


@app.local_entrypoint()
def main(smoke: bool = False):
    """Runs on THIS PC when you type `python -m modal run stage1_train.py [--smoke]`: starts the GPU job, waits,
    then copies the results home. Ctrl+C stops the GPU first, then copies what is there.

    Arguments:
        smoke: --smoke on the command line = the short smoke test.
    """
    if not VAL_WINDOWS.exists():                           # the validation list must be built first (locally)
        raise SystemExit(f"{VAL_WINDOWS} missing: run make_val_windows.py first")
    cfg = cfg_for(smoke)
    ml.sync_on_interrupt(cfg, EXP_DIR)                     # Ctrl+C: stop the GPU, then copy the results home
    run_id = ml.launch_run_id(cfg, EXP_DIR)                # run001, run002, ... (tags every log row and file)
    status = "crashed"                                     # changed to "finished" if the job returns normally
    try:
        train_remote.remote(run_id, smoke)                 # start the GPU job and wait for it
        status = "finished"
    finally:
        ml.sync_back(cfg, EXP_DIR, status)                 # copy logs / checkpoints from the volume to this PC
