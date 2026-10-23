"""
shared_code.py - the safe-distance project's shared code: the training engine (general: loop, logs,
checkpoints, Modal) and, at the end, the crash-risk parts every stage uses (scores, model, fixed windows).
(Was ml_utils.py.)

Extracted from a production Kaggle engine (knee-MRI, RSNA 2026) and made task-agnostic. Copy this ONE file into a project's runs/ folder; each run folder then holds only
a config.yaml delta and a thin train.py that builds the model and the datasets.

What it covers
  config        defaults < runs/shared_config.yaml < runs/<run>/config.yaml, deep-merged
  printing      boxed banners / key-value boxes / tables, a full console capture per run
  run identity  run001, run002 ... per experiment, tagging every CSV row and file
  training      AMP (fp16/bf16), grad accumulation, clipping, EMA, SAM, LP-FT, LLRD, warmup+cosine,
                early stopping, tiered validation cadence, exact mid-epoch resume, `extend` a
                finished run on a fresh lr curve, warm start from another run, top-K checkpoints
  diagnostics   compute / real / end-to-end throughput, data-wait %, MFU, GPU busy %, peak memory,
                grad norm + clip %, update-to-weight ratio, feature/logit scale probe
  tasks         binary | multilabel | multiclass | regression (metrics, losses, activations)
  outputs       train_log.csv, val_log.csv, training_summary.json, per-validation prediction .npz,
                plots, ud_ratio.csv
  inference     load_weights, predict (with TTA), thresholds
  cv/ensemble   make_folds, load_predictions, blend, hill_climb
  modal         image, resources, run-id allocation, sync results home, stop app on Ctrl+C
  kaggle        CLI wrapper, dataset push + wait, kernel push + wait, submit, metadata writers

Every print block is switchable under logging.print in the config. Nothing here imports a
project; the project hands in a model, datasets and (optionally) Hooks.
"""

from __future__ import annotations

import os

# Cap OpenMP/MKL threads before torch is imported (Kaggle gives 4 vCPUs; oversubscription hurts).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, str(min(8, os.cpu_count() or 4)))

import copy
import csv

import json
import math
import random
import re

import sys
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml
from torch.utils.data import DataLoader, Dataset, Sampler

import logging as _logging


class _ExitWhenAppStopped(_logging.Filter):
    """Swallow modal's heartbeat tracebacks once the app is stopped, and exit the client.

    Stopping a run from the Modal dashboard leaves the local `modal run` process heartbeating
    a dead app every 10 s, and each reply - ConflictError "App state is APP_STATE_STOPPED" -
    is logged as a full traceback until Ctrl+C. That reply means the app is already gone, so
    the right end state is simply this process exiting. Anything else passes through.
    """

    _done = False

    def filter(self, record):
        exc = record.exc_info[1] if record.exc_info else None
        text = "%s %s" % (record.getMessage(), exc or "")
        if "APP_STATE_STOPPED" not in text:
            return True
        if not _ExitWhenAppStopped._done:
            _ExitWhenAppStopped._done = True
            print("\n  app stopped on Modal - closing the local client", flush=True)
            os._exit(0)                  # the remote app is already stopped; nothing to clean up
        return False


for _name in ("modal-utils", "modal-client"):
    _logging.getLogger(_name).addFilter(_ExitWhenAppStopped())

try:
    import cv2
    cv2.setNumThreads(0)          # workers do their own parallelism
except ImportError:
    cv2 = None

# box-drawing glyphs need utf-8; Windows consoles default to cp1252
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# =============================================================================
# pretty printing
# =============================================================================
W = 78


def _rule(ch: str = "\u2500"):
    print(ch * W)


def _banner(title: str, emoji: str = ""):
    """Big section header."""
    print()
    print("\u2554" + "\u2550" * (W - 2) + "\u2557")
    label = f" {emoji} {title} ".ljust(W - 2)
    print("\u2551" + label + "\u2551")
    print("\u255A" + "\u2550" * (W - 2) + "\u255D")


def _kv(title: str, pairs, emoji: str = ""):
    """Boxed key/value block. `pairs` may contain (k, v) or None for a separator."""
    head = f" {emoji} {title} ".rstrip()
    print("\u250C\u2500" + head + "\u2500" * max(0, W - len(head) - 3) + "\u2510")
    for row in pairs:
        if row is None:
            print("\u251C" + "\u2500" * (W - 2) + "\u2524")
            continue
        k, v = row
        text = f" {k:<22}\u2502 {v}"
        if _w(text) > W - 2:
            text = text[:W - 5] + "..."
        print("\u2502" + _pad(text, W - 2) + "\u2502")
    print("\u2514" + "\u2500" * (W - 2) + "\u2518")


def _table(title: str, headers, rows, emoji: str = ""):
    """Boxed table. Title sits above the box so it never overflows the border."""
    if not rows:
        return
    cols = [[str(h)] + [str(r[i]) for r in rows] for i, h in enumerate(headers)]
    wid = [max(_w(c) for c in col) for col in cols]
    print(f"  {emoji} {title}".rstrip())
    print("┌" + "┬".join("─" * (w + 2) for w in wid) + "┐")
    print("│ " + " │ ".join(_pad(h, w) for h, w in zip(headers, wid)) + " │")
    print("├" + "┼".join("─" * (w + 2) for w in wid) + "┤")
    for r in rows:
        print("│ " + " │ ".join(_pad(c, w) for c, w in zip(r, wid)) + " │")
    print("└" + "┴".join("─" * (w + 2) for w in wid) + "┘")

def _w(s: str) -> int:
    # emoji take two terminal cells, so plain len() skews every border to their right
    return sum(0 if ord(c) == 0xFE0F else 2 if ord(c) >= 0x1F000 else 1 for c in str(s))


def _pad(s: str, w: int) -> str:
    return str(s) + " " * max(0, w - _w(s))


# public names for the printing helpers, so project scripts can reuse the same look
rule, banner, kv, table = _rule, _banner, _kv, _table


# =============================================================================
# timing
# =============================================================================
class Timer:
    """`with Timer("decode"):` prints how long the block took; `.sec` holds the number.

    verbose=False keeps it silent. cuda_sync=True waits for queued GPU work at both ends,
    because CUDA calls return before the kernels finish and would otherwise time nothing.
    """

    def __init__(self, label: str = "", verbose: bool = True, cuda_sync: bool = False):
        self.label, self.verbose, self.cuda_sync, self.sec = label, verbose, cuda_sync, 0.0

    def __enter__(self):
        if self.cuda_sync and torch.cuda.is_available():
            torch.cuda.synchronize()
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        if self.cuda_sync and torch.cuda.is_available():
            torch.cuda.synchronize()
        self.sec = time.perf_counter() - self.t0
        if self.verbose:
            print(f"  ⏱️  {self.label or 'block'}: {fmt_precise(self.sec)}", flush=True)
        return False


def timed(fn=None, *, label: str | None = None):
    """Decorator printing a function's wall time on every call: `@timed` or `@timed(label=..)`."""
    import functools

    def wrap(f):
        @functools.wraps(f)
        def inner(*a, **k):
            with Timer(label or f.__name__):
                return f(*a, **k)
        return inner
    return wrap(fn) if fn is not None else wrap


def fmt_precise(sec: float) -> str:
    """Seconds -> "812 ms" / "4.21 s" / "4m09s" / "1h04m09s"."""
    if sec < 1.0:
        return f"{sec * 1000:.0f} ms"
    if sec < 60.0:
        return f"{sec:.2f} s"
    return fmt(sec)


# =============================================================================
# config
# =============================================================================
def _deep_merge(base: dict, over: dict) -> dict:
    # recursive dict merge; `over` wins on scalars, dicts get merged key by key.
    # copy.deepcopy so an untouched nested dict isn't shared with `base` - otherwise
    # two configs off one load alias each other and swap run_ids.
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = _deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def _coerce_sci(node):
    """Turn YAML's accidental strings back into floats.

    YAML only reads scientific notation as a number when the mantissa has a decimal point:
    `8.0e-6` is a float, `8e-6` is the STRING "8e-6". Every learning rate in this repo is
    written in that notation, so one missing dot silently hands a string to the optimizer.
    float() happens to rescue most call sites, which is worse - it means the typo survives
    into a run and only shows up as a config print that looks subtly wrong.

    Only strings carrying an exponent marker are touched, so genuine strings ("last",
    "auto_clamped", "cosine") and plain digits (a resume step) are left alone.
    """
    items = node.items() if isinstance(node, dict) else enumerate(node)
    for k, v in list(items):
        if isinstance(v, (dict, list)):
            _coerce_sci(v)
        elif isinstance(v, str) and ("e" in v or "E" in v):
            try:
                node[k] = float(v)
            except ValueError:
                pass


# Every key the engine reads, with its default. Merge order: DEFAULTS < shared_config.yaml <
# the run's config.yaml, so a project config only states what differs. Also the reference
# for what each knob means.
DEFAULTS_YAML = r"""
experiment:
  name: null                 # default: the run folder's name
  run_id: null               # allocated at launch (run001, run002, ...)
  notes: ""

task:
  type: multilabel           # binary | multilabel | multiclass | regression
  targets: []                # label columns (binary/multilabel/regression) or class names (multiclass)
  num_classes: null          # multiclass only; default len(targets)

metrics:
  monitor: auto              # the val metric that picks best.pt; auto = macro_auroc (binary/multilabel),
                             # accuracy (multiclass), rmse (regression). Any key of the val metrics works.
  mode: auto                 # max | min | auto (min for loss/rmse/mae/logloss/mse, else max)
  threshold: 0.5             # binarizes soft targets and cuts predictions for F1/precision/recall
  top_k: [3]                 # multiclass top-k accuracies
  qwk: false                 # multiclass: also quadratic weighted kappa (ordinal classes)

paths:
  data_dir: "data"           # free-form; resolve(name, cfg) joins bare names onto data_dir

reproducibility:
  seed: 42
  deterministic: false       # true = bit-identical reruns, slower

dataloader:
  batch_size: 32
  accum_steps: 1             # micro-batches per optimizer step
  num_workers: 4
  val_batch_size: null       # null = batch_size (eval has no backward, can usually go wider)
  val_num_workers: null      # null = num_workers
  pin_memory: true
  persistent_workers: true
  prefetch_factor: 2
  drop_last: true            # train only

training:
  device: auto               # auto | cuda | cpu | cuda:1
  epochs: 10
  amp: true                  # mixed precision on CUDA
  amp_dtype: float16         # float16 (with GradScaler) | bfloat16
  channels_last: false       # NHWC layout for 4-D image inputs (faster convs on tensor cores)
  grad_clip: 3.0             # 0 = off. Low caps silently throttle the real lr: watch clip_pct
  grad_clip_floor: 0.0       # warn when grad_clip is set below this (0 = no check)
  grad_checkpointing: false  # calls model(.backbone).set_grad_checkpointing(True) when it exists
  backbone_chunk: 0          # run model.backbone N images at a time (checkpointed in training)
  tf32: true
  compile: false             # torch.compile
  compile_mode: default
  lp_ft_epochs: 0            # freeze model.backbone for the first N epochs (linear probe, then fine-tune)
  stop_after_steps: 0        # stop early at this global step; the lr schedule stays the full run's
  loss:
    name: auto               # auto | bce | focal | aucm | ce | mse | l1 | huber | smooth_l1
    pos_weight: null         # bce/focal/aucm: null | auto | auto_clamped | number | list
    class_weight: null       # ce: null | auto | list
    label_smoothing: 0.0     # ce
    focal_gamma: 2.0
    aucm_margin: 1.0
    aucm_bce_mix: 0.1
    huber_delta: 1.0
  optimizer:
    name: adamw              # adamw | adam | sgd
    lr: 1.0e-4               # BACKBONE lr (or the only lr when the model has no .backbone)
    head_lr: null            # null = lr / backbone_lr_mult
    backbone_lr_mult: 1.0    # head_lr = lr / mult (0.1 -> the head trains 10x faster)
    fresh_lr: null           # lr for modules flagged `is_fresh = True` inside the backbone
    layer_decay: null        # LLRD: lr shrinks by this factor per depth from head to stem
    weight_decay: 0.05
    no_decay_bias_norm: true # 1-D params (biases, norms) get weight_decay 0
    betas: [0.9, 0.999]
    momentum: 0.9            # sgd
    nesterov: true           # sgd
    eight_bit: false         # bitsandbytes AdamW8bit
  scheduler:
    name: cosine             # cosine | linear | constant | step
    warmup_frac: 0.05        # linear warm-up from 0 over this share of the steps
    min_lr_mult: 0.01        # cosine/linear floor as a fraction of the peak
    schedule_epochs: null    # stretch the curve over this many epochs (null = training.epochs)
    milestones: []           # step: epochs at which lr *= gamma
    gamma: 0.1
  early_stopping:
    enable: true
    patience: 5              # counted in VALIDATIONS, not epochs
    reset_tag: null          # change it to reset best/patience ONCE (the monitored metric changed meaning)
  ema:
    enable: false            # exponential moving average of the weights
    decay: 0.999
    warmup: true             # decay ramps (1+n)/(10+n) early so the average is not stuck at init
    eval: true               # validate (and pick best.pt) with the EMA weights
  sam:
    enable: false            # sharpness-aware minimization: 2 forward/backward per step
    rho: 0.05
    adaptive: false          # ASAM (rho usually ~10x larger)
  extend:                    # continue a FINISHED run on a fresh lr curve (keeps weights + moments)
    enable: false
    epochs: 5
    lr: null
    warmup_frac: 0.02
    min_lr_mult: null
    reset_optimizer: false
    reset_patience: true

evaluation:
  enable: true               # false = no held-out set: checkpoints still written, "best" = latest
  eval_every_epochs: 1       # validate at each Nth epoch end (0/null = off)
  eval_every_steps: 0        # validate every N optimizer steps (0 = off) ...
  eval_steps_schedule: []    # ... or tiered: [[from_epoch, every_steps], ...], e.g. [[1, 400], [5, 200], [7, 100]]
  validate_before_training: false   # score at step 0; "only" = score and stop
  validate_on_resume: false  # score once on the first step after a resume

logging:
  unit: sample               # what ONE dataset item is called (sample, img, study, row, text)
  sub_unit: null             # optional finer unit inside a sample (img in a 96-image study)
  sub_units_per_sample: 1
  console_log_every: 20      # optimizer steps between console lines
  diagnostics_every: 200     # steps between ud-ratio / scale-probe readings (0 = off)
  flops_probe: true          # count FLOPs once (needed for MFU)
  print:
    config: true             # boxed config sections
    raw_config: true         # the merged YAML verbatim
    environment: true        # host, versions, CPU/RAM, GPUs
    data: true               # split sizes and label balance
    model: true              # parameter counts
    lr_groups: true          # learning rate per param group / LLRD depth
    step_line: true          # loss / lr / gnorm / elapsed / ETA line
    throughput: true         # compute / real / end-to-end rate and data-wait %
    compute: true            # MFU, SM busy %, memory controller busy %
    ud_ratio: true           # update-to-weight ratio summary
    scale_probe: true        # feature / logit scale at the head
    warmup: true             # warmup start / complete lines
    per_target_eval: true    # every target's metrics at each validation
    final_summary: true      # end-of-run table
    clip_warning: true       # warn when > 50% of steps are clipped
  wandb:
    enabled: false
    project: null

output:
  run_dir: results
  checkpoints_dir: checkpoints
  best_name: best.pt
  train_log_csv: train_log.csv
  val_log_csv: val_log.csv
  summary_json: training_summary.json
  console_capture_dir: train_config   # full terminal capture per run
  debug_dir: debug
  predictions_dir: predictions
  save_predictions: true     # raw outputs per validation as .npz (free checkpoint ensembling later)
  checkpoint_every_steps: 0  # periodic step checkpoints (0 = only at validations)
  keep_last_n: 3             # rolling window over step checkpoints
  keep_top_k: 3              # best K validations kept as top_step*.pt
  top_k_weights_only: true
  async_checkpoints: true    # write checkpoints on a worker thread from a CPU snapshot
  commit_every_steps: 25     # Modal: flush the runs volume this often
  make_plots: true
  plots_dir: plots
  upload_checkpoints: null   # {modal_config, volume, patterns}: copy local checkpoints to a Modal volume

modal:
  gpu: "L40S"
  timeout_hours: 8
  cpu: null
  memory_gb: null
  scaledown_window: 2
  python_version: "3.11"
  pip: [torch, torchvision, timm, numpy, pandas, scikit-learn, pyyaml, matplotlib, psutil, nvidia-ml-py]
  extra_pip: []
  apt: []
  runs_volume: "runs"
  runs_mount: "/runs"
  data_volume: null          # e.g. "my-data"; mounted at data_mount
  data_mount: "/data"
  ship_data_dir: true        # add the local data/ folder (small files) to the image
  data_ignore: ["**/*.pt", "**/*.npz", "**/*.parquet", "raw", "shards", "images"]
  path_remap: {}             # {"paths.data_dir": "/root/data", "paths.images": "/data/images"}
  secrets: []
  sync_checkpoints: false    # also bring checkpoints home when syncing results

resume: last                 # null | best | last | <step> | <path>
resume_force: false          # resume even though guarded config keys changed
resume_guard: [model.name, training.epochs, training.optimizer.lr, training.optimizer.backbone_lr_mult,
               training.optimizer.layer_decay, training.optimizer.weight_decay, training.scheduler.name,
               training.grad_clip, task.type, task.targets]
"""
DEFAULTS = yaml.safe_load(DEFAULTS_YAML)


def with_defaults(cfg: dict) -> dict:
    """cfg on top of DEFAULTS (cfg wins). Safe to call twice."""
    out = _deep_merge(DEFAULTS, cfg or {})
    _coerce_sci(out)
    return out


def cfg_get(cfg: dict, dotted: str, default=None):
    """cfg_get(cfg, "training.optimizer.lr") with a default for any missing level."""
    d = cfg
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def cfg_set(cfg: dict, dotted: str, value) -> None:
    """cfg_set(cfg, "paths.data_dir", "/root/data"), creating missing levels."""
    d = cfg
    ks = dotted.split(".")
    for k in ks[:-1]:
        d = d.setdefault(k, {})
    d[ks[-1]] = value


def load_config(experiment_dir, config_name: str = "config.yaml",
                shared_name: str = "shared_config.yaml", verbose: bool = False,
                overrides: dict | None = None) -> dict:
    """DEFAULTS < <runs>/shared_config.yaml (if present) < <run>/config.yaml < overrides.

    experiment_dir is the run folder; the shared file lives in its parent. The run name
    defaults to the folder name, which is also what the Modal app is called.
    """
    exp_dir = Path(experiment_dir)
    shared_p = exp_dir.parent / shared_name
    shared = yaml.safe_load(shared_p.read_text(encoding="utf-8")) if shared_p.exists() else {}
    own_p = exp_dir / config_name
    own = yaml.safe_load(own_p.read_text(encoding="utf-8")) if own_p.exists() else {}
    cfg = _deep_merge(_deep_merge(DEFAULTS, shared or {}), own or {})
    if overrides:
        cfg = _deep_merge(cfg, overrides)
    _coerce_sci(cfg)
    if not cfg["experiment"].get("name"):
        cfg["experiment"]["name"] = exp_dir.name
    if verbose:
        print_config(cfg)
    return cfg


def save_config(cfg: dict, path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def _flatten(d: dict, prefix: str = "") -> list:
    rows = []
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and v:
            rows += _flatten(v, key + ".")
        else:
            rows.append((key, v))
    return rows


_SECTION_EMOJI = {"experiment": "🎯", "task": "🧩", "metrics": "📏", "paths": "📁",
                  "reproducibility": "🎲", "dataloader": "🚚", "training": "🏋️", "evaluation": "🔎",
                  "logging": "📝", "output": "📋", "modal": "☁️", "model": "🧠", "input": "🖼️",
                  "augmentation": "🎨", "inference": "🚀"}


def print_config(cfg: dict):
    """Every config section as a boxed key/value block, then the raw merged YAML.

    Generic: walks whatever sections the config has, so project-specific sections
    (model, input, augmentation, ...) print exactly like the engine's own.
    """
    pr = cfg_get(cfg, "logging.print", {}) or {}
    _banner("CONFIGURATION", "⚙️")
    loose = []
    for sec, val in cfg.items():
        if isinstance(val, dict):
            if sec == "logging":                     # the print switches are noise here
                val = {k: v for k, v in val.items() if k != "print"}
            rows = _flatten(val)
            if rows:
                _kv(sec, rows, _SECTION_EMOJI.get(sec, "•"))
        else:
            loose.append((sec, val))
    if loose:
        _kv("top level", loose, "🔧")
    if pr.get("raw_config", True):
        print()
        print("── raw merged config (verbatim) " + "─" * (W - 31))
        print(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True).rstrip())
        _rule()


def task_type(cfg: dict) -> str:
    t = str(cfg_get(cfg, "task.type", "multilabel")).lower()
    if t not in ("binary", "multilabel", "multiclass", "regression"):
        raise ValueError(f"task.type must be binary | multilabel | multiclass | regression, got {t!r}")
    return t


def target_names(cfg: dict) -> list:
    """Label columns, class names, or generated names when the config lists none."""
    names = list(cfg_get(cfg, "task.targets", []) or [])
    if names:
        return names
    if task_type(cfg) == "multiclass" and cfg_get(cfg, "task.num_classes"):
        return [f"class{i}" for i in range(int(cfg["task"]["num_classes"]))]
    return ["target"]


def num_outputs(cfg: dict) -> int:
    """Logits the model's head must produce for this task."""
    t = task_type(cfg)
    if t == "multiclass":
        return int(cfg_get(cfg, "task.num_classes") or len(target_names(cfg)))
    if t == "binary":
        return 1
    return len(target_names(cfg))


def resolve(name: str, cfg: dict) -> Path:
    """Bare filename -> paths.data_dir/<name>; absolute paths pass through."""
    p = Path(name)
    return p if p.is_absolute() else Path(cfg["paths"]["data_dir"]) / name


def amp_dtype(cfg: dict) -> torch.dtype:
    """training.amp_dtype: "float16" (default, with a GradScaler) | "bfloat16" (no scaler needed;
    for language-model trunks whose fp16 activations can overflow)."""
    return torch.bfloat16 if str(cfg["training"].get("amp_dtype", "float16")) == "bfloat16" else torch.float16


def train_batch_size(cfg: dict) -> int:
    """Samples per training micro-batch (dataloader.batch_size; training.batch_size also read)."""
    dl = cfg.get("dataloader", {})
    bs = dl.get("batch_size")
    if bs is None:
        bs = cfg["training"].get("batch_size")
    if bs is None:
        raise KeyError("batch_size missing: set dataloader.batch_size in the run config")
    return int(bs)


def accum_steps(cfg: dict) -> int:
    """Micro-batches per weight update. Lives under dataloader, next to batch_size;
    training.accum_steps still works for older run configs."""
    dl = cfg.get("dataloader", {})
    return int(dl.get("accum_steps", cfg["training"].get("accum_steps", 1)))

# =============================================================================
# run identity
# =============================================================================
# Every run of an experiment gets a sequential id: run001, run002, ... It tags
# every CSV row and prefixes every file the run writes, so artifacts from two
# runs can be merged across machines without ever blending into each other.
RUN_ID_RE = re.compile(r"run\d+")


def run_id_of(name: str) -> str | None:
    """Leading runNNN of a filename, e.g. run007_e1_s800.png -> run007."""
    m = re.match(r"(run\d+)", str(name))
    return m.group(1) if m else None


def scan_run_ids(results_dir) -> set[str]:
    """Every runNNN this results/ folder already shows evidence of."""
    results_dir = Path(results_dir)
    ids = set()
    for sub in (".run_ids", "train_config", "debug", "predictions"):
        d = results_dir / sub
        if d.is_dir():
            ids |= {r for q in d.glob("run*") if (r := run_id_of(q.name))}
    for name in ("train_log.csv", "val_log.csv"):
        f = results_dir / name
        if f.exists():
            try:                                   # a truncated log must not block a launch
                ids |= set(pd.read_csv(f, usecols=["run_id"], engine="python",
                                       on_bad_lines="skip")["run_id"]
                           .dropna().astype(str))
            except Exception:
                pass
    return {i for i in ids if RUN_ID_RE.fullmatch(str(i))}


def next_run_no(ids) -> int:
    return max((int(str(i)[3:]) for i in ids if RUN_ID_RE.fullmatch(str(i))), default=0) + 1


def allocate_run_id(results_dir, known=()) -> str:
    """Reserve the next free runNNN for this experiment.

    Called on THIS PC at launch, never inside the container: the number is then
    passed into the run. `known` carries ids already seen on the Modal volume, so a
    relaunch can't reuse one. The reservation itself is an exclusive-create, so two
    concurrent launches here can't collide either.
    """
    results_dir = Path(results_dir)
    lock_dir = results_dir / ".run_ids"            # markers only, never synced
    lock_dir.mkdir(parents=True, exist_ok=True)
    n = next_run_no(scan_run_ids(results_dir) | {str(k) for k in known})
    import platform
    while True:
        cand = f"run{n:03d}"
        try:
            with open(lock_dir / cand, "x", encoding="utf-8") as fh:
                fh.write(f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC  "
                         f"{platform.node()}  {workspace_name()}\n")
            return cand
        except FileExistsError:                    # someone else took it a moment ago
            n += 1


def hardware_info(cfg: dict) -> dict:
    """What this run actually trained on. Asked of the driver, not the config.

    The config records what we REQUESTED; a run that silently landed on a different
    card, or fell back to CPU, would otherwise look identical in the summary. That
    matters here because runs get resumed on fresh hardware mid-flight.
    """
    m = cfg.get("modal", {}) or {}
    dl = cfg.get("dataloader", {}) or {}
    # runtime_side(), not workspace_name(): this dict is written into the COMMITTED
    # training_summary.json, and which account a job landed on is nobody's business
    hw = {"gpu_requested": m.get("gpu"), "workspace": runtime_side(),
          "cpu_requested": m.get("cpu"), "memory_gb_requested": m.get("memory_gb"),
          "num_workers": dl.get("num_workers"),
          "batch_size": dl.get("batch_size"), "accum_steps": dl.get("accum_steps")}
    try:
        hw["torch"] = torch.__version__
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            hw["gpu"] = torch.cuda.get_device_name(0)
            hw["gpu_count"] = torch.cuda.device_count()
            hw["gpu_memory_gb"] = round(props.total_memory / 1024**3, 1)
            hw["gpu_capability"] = f"sm_{props.major}{props.minor}"
            hw["cuda"] = torch.version.cuda
            hw["gpu_peak_gb"] = round(torch.cuda.max_memory_allocated() / 1024**3, 2)
        else:
            hw["gpu"] = "cpu"
    except Exception as e:                        # never let bookkeeping kill a run
        hw["gpu"] = f"unknown ({type(e).__name__})"
    return hw


def workspace_name() -> str:
    """A console label for the active Modal workspace (a local, git-ignored helper decides).

    For the CONSOLE and for results/.run_ids/*, both of which stay on this PC - the
    launch log lands in results/train_config/, and that plus .run_ids are git-ignored.
    Never put this in a committed artifact: use runtime_side() for those.
    """
    ws = os.environ.get("MODAL_WORKSPACE") or os.environ.get("MODAL_PROFILE")
    if ws:
        return ws
    try:                                       # optional, git-ignored local lookup
        from _local_workspace import label
        return label() or runtime_side()
    except Exception:
        return runtime_side()


def runtime_side() -> str:
    """Which side of the wire this is, with no account name in it.

    training_summary.json is committed, so it gets this rather than workspace_name().
    MODAL_TASK_ID exists only inside a container, so "local" would be exactly backwards
    there - say which side we are on instead.
    """
    return "modal-container" if os.environ.get("MODAL_TASK_ID") else "local"


def set_seed(seed: int, deterministic: bool = False):
    # deterministic=False keeps cudnn benchmark on, which is much faster
    random.seed(seed); np.random.seed(seed)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = deterministic
    torch.backends.cudnn.benchmark = not deterministic
    os.environ["PYTHONHASHSEED"] = str(seed)


seed_everything = set_seed


def seed_worker(worker_id: int):
    """Give every dataloader worker its own reproducible stream."""
    seed = torch.initial_seed() % 2**32
    np.random.seed(seed); random.seed(seed)


def pick_device(cfg: dict | None = None) -> torch.device:
    """training.device: auto (cuda when available) | cuda | cuda:N | cpu."""
    want = str(cfg_get(cfg or {}, "training.device", "auto"))
    if want == "auto":
        ok = torch.cuda.is_available() and torch.cuda.device_count() > 0
        return torch.device("cuda" if ok else "cpu")
    return torch.device(want)


class ResumableSampler(Sampler):
    """Shuffling sampler whose permutation is a pure function of (seed, epoch).

    torch's default RandomSampler draws from the global RNG, so the order an epoch
    sees depends on everything consumed before it - a resumed run gets a different
    permutation and there is no way to say "continue where you stopped".

    Here each epoch's order is torch.randperm under a generator seeded seed+epoch,
    identical whether or not the run was interrupted. set_epoch(epoch, skip=k) then
    drops the first k indices, so the workers never even load the studies already
    trained on this epoch, and the epoch finishes on exactly the tail it would have.
    The skip clears after that one epoch.

    __len__ stays the full epoch size so steps_per_epoch and the lr schedule are
    unaffected; only the resumed epoch yields fewer batches.
    """

    def __init__(self, n: int, seed: int):
        self.n, self.seed, self.epoch, self.skip = int(n), int(seed), 0, 0

    def set_epoch(self, epoch: int, skip: int = 0):
        self.epoch, self.skip = int(epoch), max(0, int(skip))

    def __iter__(self):
        g = torch.Generator()
        g.manual_seed(self.seed + self.epoch)
        perm = torch.randperm(self.n, generator=g).tolist()
        if self.skip:
            perm = perm[self.skip:]
            self.skip = 0
        return iter(perm)

    def __len__(self):
        return self.n


def val_loader_settings(cfg: dict) -> tuple[int, int]:
    """(batch_size, num_workers) for eval loaders - val_* keys, else the train values."""
    dl = cfg.get("dataloader", {})
    nw = dl.get("val_num_workers")
    return (int(dl.get("val_batch_size") or train_batch_size(cfg)),
            int(dl.get("num_workers", 4) if nw is None else nw))


# =============================================================================
# data: loaders and the batch contract
# =============================================================================
# A dataset item is (inputs, targets) or (inputs, targets, id). `inputs` may be a tensor,
# a tuple/list of tensors, or a dict of tensors (passed to the model as **kwargs by the
# default forward). A test set without labels returns any placeholder target (e.g. 0).
# Optional dataset attributes the engine uses when present:
#   ids        list of row ids, in dataset order (prediction files carry them)
#   targets    array (N,) or (N, T) of labels (label-balance print, pos_weight=auto)
#   df         a DataFrame holding task.targets columns (same use as `targets`)
#   set_epoch  called with the epoch number before each training epoch (main process
#              only; set dataloader.persistent_workers false if workers must see it)

def split_batch(batch):
    """-> (inputs, targets, ids-or-None) from a 2- or 3-element batch or a dict batch."""
    if isinstance(batch, dict):
        b = dict(batch)
        y = b.pop("targets", b.pop("target", b.pop("y", b.pop("labels", None))))
        ids = b.pop("ids", b.pop("id", None))
        x = b.pop("inputs", b.pop("x", None))
        return (b if x is None else x), y, ids
    if isinstance(batch, (list, tuple)):
        if len(batch) == 2:
            return batch[0], batch[1], None
        if len(batch) >= 3:
            return batch[0], batch[1], batch[2]
    raise TypeError("a batch must be (inputs, targets[, ids]) or a dict with inputs/targets")


def to_device(obj, device, channels_last: bool = False):
    """Move tensors (nested in dicts/lists/tuples) to device; 4-D float tensors optionally NHWC."""
    if torch.is_tensor(obj):
        obj = obj.to(device, non_blocking=True)
        if channels_last and obj.ndim == 4 and obj.is_floating_point():
            obj = obj.contiguous(memory_format=torch.channels_last)
        return obj
    if isinstance(obj, dict):
        return {k: to_device(v, device, channels_last) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(to_device(v, device, channels_last) for v in obj)
    return obj


def batch_size_of(obj) -> int:
    """Samples in a batch: the leading dim of the first tensor found."""
    if torch.is_tensor(obj):
        return int(obj.shape[0]) if obj.ndim else 1
    if isinstance(obj, dict):
        for v in obj.values():
            n = batch_size_of(v)
            if n:
                return n
    if isinstance(obj, (list, tuple)):
        for v in obj:
            n = batch_size_of(v)
            if n:
                return n
    return 0


def slice_batch(obj, n: int):
    """First n samples of every tensor in a (nested) batch."""
    if torch.is_tensor(obj):
        return obj[:n] if obj.ndim else obj
    if isinstance(obj, dict):
        return {k: slice_batch(v, n) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(slice_batch(v, n) for v in obj)
    return obj


def dataset_targets(ds, cfg: dict):
    """(N, T) float array of the dataset's labels when it exposes them, else None."""
    ds = getattr(ds, "dataset", ds)                  # a DataLoader or a Subset wrapper
    try:
        if hasattr(ds, "targets") and ds.targets is not None:
            a = np.asarray(ds.targets, dtype=float)
        elif hasattr(ds, "df") and all(t in ds.df.columns for t in target_names(cfg)):
            a = ds.df[target_names(cfg)].to_numpy(dtype=float)
        else:
            return None
        return a.reshape(len(a), -1)
    except Exception:
        return None


def dataset_ids(ds) -> list:
    """Row ids in dataset order: ds.ids, else ds.df's first id-like column, else 0..N-1."""
    ds = getattr(ds, "dataset", ds)
    ids = getattr(ds, "ids", None)
    if ids is not None:
        return list(ids)
    return list(range(len(ds)))


def build_loaders(cfg: dict, data: dict) -> dict:
    """{split: Dataset | DataLoader} -> {split: DataLoader}.

    "train" shuffles through ResumableSampler (exact mid-epoch resume); every other split
    keeps its order. DataLoaders passed in are used as they are.
    """
    dl = cfg["dataloader"]
    vbs, vnw = val_loader_settings(cfg)
    out = {}
    for split, ds in data.items():
        if ds is None:
            continue
        if isinstance(ds, DataLoader):
            out[split] = ds
            continue
        train = split == "train"
        nw = int(dl.get("num_workers", 4)) if train else vnw
        smp = ResumableSampler(len(ds), cfg["reproducibility"]["seed"]) if train else None
        out[split] = DataLoader(
            ds, batch_size=train_batch_size(cfg) if train else vbs,
            sampler=smp, shuffle=False, num_workers=nw,
            pin_memory=bool(dl.get("pin_memory", True)) and torch.cuda.is_available(),
            persistent_workers=bool(dl.get("persistent_workers", True)) and nw > 0,
            worker_init_fn=seed_worker,
            prefetch_factor=dl.get("prefetch_factor", 2) if nw > 0 else None,
            drop_last=bool(dl.get("drop_last", True)) and train,
            collate_fn=getattr(ds, "collate_fn", None))
    if "train" not in out:
        raise ValueError("data needs a 'train' split")
    return out


def print_data_summary(loaders: dict, cfg: dict):
    """Split sizes, batches, units, and the label balance per split."""
    _banner("DATA", "📦")
    lg = cfg["logging"]
    unit, sub = lg.get("unit", "sample"), lg.get("sub_unit")
    per = int(lg.get("sub_units_per_sample") or 1)
    rows = []
    for name, ld in loaders.items():
        n = len(ld.dataset)
        r = [name, f"{n:,}", f"{len(ld):,}", ld.batch_size]
        if sub:
            r.append(f"{n * per:,}")
        rows.append(r)
    heads = ["split", f"{unit}s", "batches", "batch size"] + ([f"{sub}s"] if sub else [])
    _table("splits", heads, rows, "📊")

    t = task_type(cfg)
    names = target_names(cfg)
    ys = {k: dataset_targets(ld.dataset, cfg) for k, ld in loaders.items()}
    ys = {k: v for k, v in ys.items() if v is not None and len(v)}
    if not ys:
        print("  (label balance: the datasets expose no `targets` / `df`, skipped)")
        return
    thr = float(cfg["metrics"]["threshold"])
    rows = []
    if t in ("binary", "multilabel"):
        for i, nm in enumerate(names):
            cells = [nm]
            for k, y in ys.items():
                if y.shape[1] > i:
                    cells += [f"{y[:, i].mean():.3f}", f"{(y[:, i] > thr).mean():.1%}"]
            rows.append(cells)
        heads = ["target"] + sum([[f"{k} mean", f"{k} >{thr:g}"] for k in ys], [])
        _table("label balance", heads, rows, "⚖️")
    elif t == "multiclass":
        C = num_outputs(cfg)
        cls = names if len(names) == C else [f"class{i}" for i in range(C)]
        lab = {k: (y.argmax(1) if y.shape[1] > 1 else y[:, 0].astype(int)) for k, y in ys.items()}
        for c in range(C):
            rows.append([cls[c]] + [f"{int((v == c).sum()):,} ({(v == c).mean():.1%})" for v in lab.values()])
        _table("class balance", ["class"] + list(lab), rows, "⚖️")
    else:
        for i, nm in enumerate(names):
            cells = [nm]
            for k, y in ys.items():
                if y.shape[1] > i:
                    c = y[:, i]
                    cells.append(f"{c.mean():.4g} ± {c.std():.3g}  [{c.min():.3g}, {c.max():.3g}]")
            rows.append(cells)
        _table("target distribution (mean ± std [min, max])", ["target"] + list(ys), rows, "⚖️")


# =============================================================================
# logging
# =============================================================================
class _Tee:
    """Write to the console and the capture file at once, flushing every time."""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for st in self._streams:
            try:
                st.write(data); st.flush()
            except Exception:
                pass                      # a broken capture file must never kill a run

    def flush(self):
        for st in self._streams:
            try:
                st.flush()
            except Exception:
                pass

    def isatty(self):
        return False


class CSVLogger:
    """Append-only CSV, header on first row, flushed per row so a crash keeps the log."""

    def __init__(self, path: Path, run_id: str = ""):
        self.path = Path(path); self.run_id = run_id; self._f = None; self._w = None

    def log(self, row: dict):
        row = {"run_id": self.run_id, **row}       # first column: which run wrote this line
        try:
            if self._f is None:
                new = (not self.path.exists()) or self.path.stat().st_size == 0
                fields = list(row.keys())
                if not new:                        # reuse the file's own header, never mix two
                    try:
                        with open(self.path, newline="", encoding="utf-8") as fh:
                            old = next(csv.reader(fh), [])
                        if old and old != fields:
                            extra = [c for c in fields if c not in old]
                            if extra:
                                # The run now logs columns this file predates - a new loss
                                # reporting its internals, say. Keeping the old header would
                                # silently DROP them (extrasaction="ignore"), so widen the
                                # file instead: rewrite it once with the union header and
                                # blanks for the rows that never had these values.
                                self._migrate(old, old + extra)
                                fields = old + extra
                                print(f"  📝 {self.path.name}: added {len(extra)} new "
                                      f"column(s), existing rows back-filled blank")
                            else:
                                print(f"  [warn] {self.path.name} has a different header, "
                                      f"appending in its column order")
                                fields = old
                    except Exception as e:
                        print(f"  [warn] header check on {self.path.name} failed: "
                              f"{type(e).__name__}: {e}")
                self._f = open(self.path, "a", newline="", encoding="utf-8")
                self._w = csv.DictWriter(self._f, fieldnames=fields, restval="",
                                         extrasaction="ignore")
                if new:
                    self._w.writeheader()
            else:
                # Columns can appear MID-RUN: gate_* rows are only built on the diagnostic
                # cadence, so row 1 does not have them and the header locked without them.
                # DictWriter(extrasaction="ignore") would drop them silently for the whole
                # run - which is exactly how mricore_vitb_cross_attention_ft lost every
                # gamma value it printed. Widen the file instead, same as on resume.
                late = [k for k in row if k not in self._w.fieldnames]
                if late:
                    fields = list(self._w.fieldnames) + late
                    self._f.close()
                    self._migrate(list(self._w.fieldnames), fields)
                    self._f = open(self.path, "a", newline="", encoding="utf-8")
                    self._w = csv.DictWriter(self._f, fieldnames=fields, restval="",
                                             extrasaction="ignore")
                    print(f"  📝 {self.path.name}: added {len(late)} new "
                          f"column(s) mid-run, earlier rows back-filled blank")
            self._w.writerow(row); self._f.flush()
        except Exception as e:                # logging must never crash training
            print(f"  [warn] CSV log failed: {type(e).__name__}: {e}")
            self._f, self._w = None, None

    def _migrate(self, old: list, new: list):
        """Rewrite the CSV under a wider header, via a temp file so a kill cannot eat it."""
        tmp = self.path.with_suffix(".migrating")
        with open(self.path, newline="", encoding="utf-8") as fh, \
                open(tmp, "w", newline="", encoding="utf-8") as out:
            r = csv.DictReader(fh)
            w = csv.DictWriter(out, fieldnames=new, restval="", extrasaction="ignore")
            w.writeheader()
            for row in r:
                w.writerow(row)
        tmp.replace(self.path)

    def close(self):
        try:
            if self._f:
                self._f.close()
        except Exception:
            pass


# =============================================================================
# metrics / loss / optim
# =============================================================================
def binary_metrics(y_true: np.ndarray, y_prob: np.ndarray, tasks: list,
                   thr: float = 0.5, pred_thr=None) -> dict:
    """Binary / multilabel: per-task AUROC + AUPRC and the operating-point stats at `thr`.

    Soft targets are fine: they binarize at `thr` for scoring.

    pred_thr: scalar or one value per task for cutting the PREDICTIONS; defaults to thr.
    """
    from sklearn.metrics import average_precision_score, roc_auc_score

    # targets always binarize at thr; predictions may use calibrated per-task cuts
    pt = np.asarray(thr if pred_thr is None else pred_thr, dtype=float)
    pt = np.broadcast_to(pt, (len(tasks),)).astype(float)

    per = {}
    for i, t in enumerate(tasks):
        yt = (y_true[:, i] > thr).astype(int)          # soft targets need a threshold to score
        yp = y_prob[:, i]
        one_class = yt.min() == yt.max()
        pbi = (yp > pt[i]).astype(int)
        tp_ = int(((yt == 1) & (pbi == 1)).sum()); fp_ = int(((yt == 0) & (pbi == 1)).sum())
        fn_ = int(((yt == 1) & (pbi == 0)).sum()); tn_ = int(((yt == 0) & (pbi == 0)).sum())
        p_ = tp_ / max(tp_ + fp_, 1); r_ = tp_ / max(tp_ + fn_, 1)
        per[t] = {
            "auroc": float("nan") if one_class else roc_auc_score(yt, yp),
            "auprc": float("nan") if one_class else average_precision_score(yt, yp),
            "pos": int(yt.sum()),
            "threshold": float(pt[i]),
            "precision": float(p_), "recall": float(r_),
            "f1": float(2 * p_ * r_ / max(p_ + r_, 1e-9)),
            "specificity": float(tn_ / max(tn_ + fp_, 1)),
        }
    au = [v["auroc"] for v in per.values() if not math.isnan(v["auroc"])]
    ap = [v["auprc"] for v in per.values() if not math.isnan(v["auprc"])]

    yb, pb = (y_true > thr).astype(int), (y_prob > pt[None, :]).astype(int)
    tp = ((yb == 1) & (pb == 1)).sum(); fp = ((yb == 0) & (pb == 1)).sum()
    fn = ((yb == 1) & (pb == 0)).sum(); tn = ((yb == 0) & (pb == 0)).sum()
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    return {
        "macro_auroc": float(np.mean(au)) if au else float("nan"),
        "macro_auprc": float(np.mean(ap)) if ap else float("nan"),
        "precision": float(prec), "recall": float(rec),
        "f1": float(2 * prec * rec / max(prec + rec, 1e-9)),
        "specificity": float(tn / max(tn + fp, 1)),
        "per_task": per,
    }


class FocalBCE(nn.Module):
    """Binary cross-entropy that down-weights easy examples (gamma) to focus on hard ones."""

    def __init__(self, gamma=2.0, pos_weight=None):
        super().__init__(); self.gamma = gamma; self.register_buffer("pw", pos_weight)

    def forward(self, logits, target):
        bce = F.binary_cross_entropy_with_logits(
            logits, target, pos_weight=self.pw, reduction="none")
        p = torch.sigmoid(logits)
        mod = (target * (1 - p) + (1 - target) * p) ** self.gamma   # small when the guess is right
        return (mod * bce).mean()


class AUCMarginLoss(nn.Module):
    """Pairwise squared-hinge surrogate for AUROC - the competition metric itself.

    Every positive/negative pair in the batch is pushed `margin` apart; the pair
    weight is y_i*(1-y_j), so soft LLM targets work without rounding. Self-contained
    (no libauc), so it needs no extra dependency and plain AdamW drives it. A small
    BCE mix keeps the probabilities calibrated and covers batches with no pairs.
    """

    def __init__(self, margin: float = 1.0, bce_mix: float = 0.1, pos_weight=None):
        super().__init__()
        self.margin = float(margin); self.bce_mix = float(bce_mix)
        self.register_buffer("pw", pos_weight)

    def forward(self, logits, target):
        p = torch.sigmoid(logits)                       # (B, T) in 0-1, the AUC is over these
        d = p.unsqueeze(1) - p.unsqueeze(0)             # (B, B, T) pairwise score gaps
        w = target.unsqueeze(1) * (1 - target).unsqueeze(0)     # i positive, j negative
        hinge = torch.clamp(self.margin - d, min=0) ** 2
        loss = (w * hinge).sum() / w.sum().clamp(min=1e-6)
        if self.bce_mix > 0 or w.sum() <= 0:
            bce = F.binary_cross_entropy_with_logits(logits, target, pos_weight=self.pw)
            loss = loss + max(self.bce_mix, 1e-3) * bce
        return loss

def _best_f1_threshold(y_true_col, y_prob_col) -> tuple:
    """Exact max-F1 cut for one task, read off the precision-recall curve."""
    from sklearn.metrics import precision_recall_curve

    yt, yp = np.asarray(y_true_col), np.asarray(y_prob_col)
    n_pos = int(yt.sum())
    if n_pos == 0 or n_pos == len(yt):            # degenerate task: nothing to optimize
        return 0.5, float("nan")
    prec, rec, thr = precision_recall_curve(yt, yp)
    f1 = (2 * prec * rec / (prec + rec + 1e-12))[:-1]    # last point has no threshold
    if len(f1) == 0 or np.all(np.isnan(f1)):
        return 0.5, float("nan")
    i = int(np.nanargmax(f1))
    # sklearn cuts at p >= thr, compute_metrics at p > thr; nudge down so they agree
    return float(np.nextafter(thr[i], -np.inf)), float(f1[i])


def activate(outputs: torch.Tensor | np.ndarray, cfg_or_type) -> np.ndarray:
    """Raw model outputs -> predictions: sigmoid (binary/multilabel), softmax (multiclass),
    identity (regression). Accepts a cfg or a task-type string."""
    t = cfg_or_type if isinstance(cfg_or_type, str) else task_type(cfg_or_type)
    x = torch.as_tensor(np.asarray(outputs) if not torch.is_tensor(outputs) else outputs).float()
    if t in ("binary", "multilabel"):
        x = torch.sigmoid(x)
    elif t == "multiclass":
        x = torch.softmax(x, dim=-1)
    return x.cpu().numpy()


def _as2d(a) -> np.ndarray:
    a = np.asarray(a)
    return a.reshape(len(a), -1) if a.ndim != 2 else a


def _logloss_bin(y, p, eps=1e-7) -> float:
    p = np.clip(p, eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def multiclass_metrics(y_true, y_prob, classes: list, top_k=(3,), qwk: bool = False) -> dict:
    """Accuracy, balanced accuracy, macro/weighted F1, log loss, top-k, macro OvR AUROC,
    optional quadratic weighted kappa, and per-class precision/recall/F1/AUROC/support.
    y_true: (N,) class indices or (N, C) one-hot/soft (argmax taken)."""
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score, cohen_kappa_score,
                                 f1_score, log_loss, precision_recall_fscore_support,
                                 roc_auc_score)
    y_prob = _as2d(y_prob)
    C = y_prob.shape[1]
    yt = np.asarray(y_true)
    yt = yt.argmax(1) if (yt.ndim == 2 and yt.shape[1] > 1) else yt.reshape(-1).astype(int)
    pred = y_prob.argmax(1)
    labels = list(range(C))
    m = {"accuracy": float(accuracy_score(yt, pred)),
         "balanced_accuracy": float(balanced_accuracy_score(yt, pred)),
         "macro_f1": float(f1_score(yt, pred, average="macro", labels=labels, zero_division=0)),
         "weighted_f1": float(f1_score(yt, pred, average="weighted", labels=labels, zero_division=0))}
    try:
        pn = np.clip(y_prob, 1e-7, 1.0)
        m["logloss"] = float(log_loss(yt, pn / pn.sum(1, keepdims=True), labels=labels))
    except Exception:
        m["logloss"] = float("nan")
    order = np.argsort(-y_prob, axis=1)
    for k in top_k or ():
        if 1 < int(k) < C:
            m[f"top{int(k)}_acc"] = float(np.mean([yt[i] in order[i, :int(k)] for i in range(len(yt))]))
    if qwk:
        m["qwk"] = float(cohen_kappa_score(yt, pred, weights="quadratic"))
    p_, r_, f_, s_ = precision_recall_fscore_support(yt, pred, labels=labels, zero_division=0)
    per, aus = {}, []
    for c in labels:
        yb = (yt == c).astype(int)
        au = float("nan") if yb.min() == yb.max() else float(roc_auc_score(yb, y_prob[:, c]))
        if au == au:
            aus.append(au)
        per[classes[c] if c < len(classes) else f"class{c}"] = {
            "auroc": au, "precision": float(p_[c]), "recall": float(r_[c]), "f1": float(f_[c]),
            "pos": int(s_[c])}
    m["macro_auroc"] = float(np.mean(aus)) if aus else float("nan")
    m["per_task"] = per
    return m


def regression_metrics(y_true, y_pred, names: list) -> dict:
    """RMSE, MAE, R2, Pearson and Spearman per target, macro-averaged across targets."""
    yt, yp = _as2d(y_true).astype(float), _as2d(y_pred).astype(float)
    try:
        from scipy.stats import spearmanr
    except Exception:
        spearmanr = None
    per = {}
    for i in range(yp.shape[1]):
        a, b = yt[:, i], yp[:, i]
        err = b - a
        ss = float(((a - a.mean()) ** 2).sum())
        pear = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
        spr = float(spearmanr(a, b)[0]) if spearmanr and a.std() > 0 and b.std() > 0 else float("nan")
        per[names[i] if i < len(names) else f"t{i}"] = {
            "rmse": float(np.sqrt(np.mean(err ** 2))), "mae": float(np.mean(np.abs(err))),
            "mse": float(np.mean(err ** 2)),
            "r2": float(1 - (err ** 2).sum() / ss) if ss > 0 else float("nan"),
            "pearson": pear, "spearman": spr}
    m = {}
    for k in ("rmse", "mae", "mse", "r2", "pearson", "spearman"):
        v = [d[k] for d in per.values() if d[k] == d[k]]
        m[k] = float(np.mean(v)) if v else float("nan")
    m["per_task"] = per
    return m


def compute_metrics(y_true, y_prob, cfg: dict, pred_thr=None, score_fn=None) -> dict:
    """Every metric for this task type, as {name: float, ..., "per_task": {target: {...}}}.

    y_prob is ACTIVATED output (see activate). score_fn(y_true, y_prob) -> dict adds any
    custom (competition) metric, which can then be the monitor.
    """
    t, names = task_type(cfg), target_names(cfg)
    if t in ("binary", "multilabel"):
        yt, yp = _as2d(y_true).astype(float), _as2d(y_prob).astype(float)
        thr = float(cfg["metrics"]["threshold"])
        m = binary_metrics(yt, yp, names[:yp.shape[1]] if len(names) >= yp.shape[1]
                           else [f"t{i}" for i in range(yp.shape[1])], thr, pred_thr)
        # log loss against the binarized target, macro over targets
        m["logloss"] = float(np.mean([_logloss_bin((yt[:, i] > thr).astype(float), yp[:, i])
                                      for i in range(yp.shape[1])]))
        m["accuracy"] = float(((yp > (thr if pred_thr is None else np.asarray(pred_thr)))
                               == (yt > thr)).mean())
    elif t == "multiclass":
        m = multiclass_metrics(y_true, y_prob, names, cfg["metrics"].get("top_k") or (),
                               bool(cfg["metrics"].get("qwk")))
    else:
        m = regression_metrics(y_true, y_prob, names)
    if score_fn is not None:
        try:
            extra = score_fn(y_true, y_prob) or {}
            m.update({k: float(v) for k, v in extra.items()})
        except Exception as e:
            print(f"  ⚠️  custom score_fn failed: {type(e).__name__}: {e}")
    return m


_MIN_METRICS = ("loss", "logloss", "rmse", "mae", "mse", "error", "wer", "cer")


def monitor_spec(cfg: dict) -> tuple[str, str]:
    """(metric name without the val_ prefix, "max" | "min") that picks best.pt."""
    name = str(cfg["metrics"].get("monitor") or "auto")
    if name == "auto":
        name = {"binary": "macro_auroc", "multilabel": "macro_auroc",
                "multiclass": "accuracy", "regression": "rmse"}[task_type(cfg)]
    if name.startswith("val_"):
        name = name[4:]
    mode = str(cfg["metrics"].get("mode") or "auto")
    if mode == "auto":
        mode = "min" if any(name.endswith(k) or name == k for k in _MIN_METRICS) else "max"
    return name, mode


def make_score_fn(cfg: dict, score_fn=None) -> Callable:
    """f(y_true, y_prob) -> the monitored metric, for ensembling / hill climbing."""
    name, _ = monitor_spec(cfg)

    def f(y_true, y_prob):
        return compute_metrics(y_true, y_prob, cfg, score_fn=score_fn).get(name, float("nan"))
    return f


def best_thresholds(y_true, y_prob, thr: float = 0.5) -> tuple[list, list]:
    """Per-target max-F1 cut-offs (binary/multilabel). -> (thresholds, best F1s)."""
    yt, yp = _as2d(y_true), _as2d(y_prob)
    out = [_best_f1_threshold((yt[:, i] > thr).astype(int), yp[:, i]) for i in range(yp.shape[1])]
    return [o[0] for o in out], [o[1] for o in out]


class TaskLoss(nn.Module):
    """Wraps a base loss and reshapes / casts the targets for the task type, so a model can
    emit (B,) or (B, 1) for binary and the dataset can hand class indices or soft one-hots."""

    def __init__(self, base: nn.Module, ttype: str):
        super().__init__()
        self.base, self.ttype = base, ttype

    def forward(self, out, y):
        out = out.float()
        if self.ttype == "multiclass":
            if y.ndim == 1 or (y.ndim == 2 and y.shape[1] == 1 and out.shape[-1] != 1):
                y = y.reshape(-1).long()
            else:
                y = y.float()                       # soft / one-hot targets
            return self.base(out, y)
        y = y.float()
        if out.ndim == 2 and y.ndim == 1 and out.shape[1] == 1:
            y = y[:, None]
        elif out.ndim == 1 and y.ndim == 2 and y.shape[1] == 1:
            y = y[:, 0]
        return self.base(out, y)

    # AUC-M-style losses expose internals for the CSV; pass them through
    def state(self):
        return self.base.state() if hasattr(self.base, "state") else {}

    def load_state(self, d):
        if hasattr(self.base, "load_state"):
            self.base.load_state(d)


def build_loss(cfg: dict, train_targets: np.ndarray | None, device) -> nn.Module:
    """training.loss.name: auto | bce | focal | aucm | ce | mse | l1 | huber | smooth_l1."""
    t = task_type(cfg)
    lc = cfg["training"]["loss"]
    name = lc.get("name", "auto")
    if name == "auto":
        name = {"binary": "bce", "multilabel": "bce", "multiclass": "ce", "regression": "mse"}[t]
    pw = None
    pwv = lc.get("pos_weight")
    if name in ("bce", "focal", "aucm") and pwv not in (None, False):
        if pwv in ("auto", "auto_clamped"):
            if train_targets is None:
                print("  ⚠️  pos_weight=auto needs dataset.targets or dataset.df - ignored")
            else:
                # rare labels get a bigger weight so they are not drowned out by common ones
                prev = np.clip(train_targets.mean(0), 1e-3, 1.0)
                w = (1 - prev) / prev
                if pwv == "auto_clamped":
                    w = np.maximum(w, 1.0)          # boost rare targets, never damp common ones
                pw = torch.tensor(w, dtype=torch.float32, device=device)
        else:
            pw = torch.tensor(np.atleast_1d(np.asarray(pwv, dtype=np.float32)), device=device)
    if pw is not None:
        print(f"  ⚖️  pos_weight: {np.round(pw.cpu().numpy(), 3).tolist()}")
    if name == "bce":
        base = nn.BCEWithLogitsLoss(pos_weight=pw)
    elif name == "focal":
        base = FocalBCE(lc.get("focal_gamma", 2.0), pw)
    elif name == "aucm":
        base = AUCMarginLoss(lc.get("aucm_margin", 1.0), lc.get("aucm_bce_mix", 0.1), pw)
    elif name == "ce":
        cw = lc.get("class_weight")
        w = None
        if cw == "auto":
            if train_targets is None:
                print("  ⚠️  class_weight=auto needs dataset.targets or dataset.df - ignored")
            else:
                C = num_outputs(cfg)
                lab = (train_targets.argmax(1) if train_targets.shape[1] > 1
                       else train_targets[:, 0].astype(int))
                cnt = np.bincount(lab, minlength=C).astype(float)
                w = torch.tensor(len(lab) / (C * np.maximum(cnt, 1)), dtype=torch.float32, device=device)
        elif cw is not None:
            w = torch.tensor(cw, dtype=torch.float32, device=device)
        if w is not None:
            print(f"  ⚖️  class_weight: {np.round(w.cpu().numpy(), 3).tolist()}")
        base = nn.CrossEntropyLoss(weight=w, label_smoothing=float(lc.get("label_smoothing", 0.0)))
    elif name == "mse":
        base = nn.MSELoss()
    elif name == "l1":
        base = nn.L1Loss()
    elif name == "huber":
        base = nn.HuberLoss(delta=float(lc.get("huber_delta", 1.0)))
    elif name == "smooth_l1":
        base = nn.SmoothL1Loss()
    else:
        raise ValueError(f"unknown training.loss.name {name!r}")
    return TaskLoss(base, t).to(device)


def _llrd_depths(backbone: nn.Module) -> tuple[dict, int]:
    """Map backbone param name -> depth (0 = nearest the pixels), plus the head depth.

    Handles the two timm layouts we use: ViT-style `blocks.<i>` and ConvNeXt-style
    `stages.<i>.blocks.<j>`. Anything unrecognized sits at the deepest backbone level.
    """
    names = [n for n, _ in backbone.named_parameters()]
    blocks = getattr(backbone, "blocks", None)
    stages = getattr(backbone, "stages", None)
    depth = {}
    if blocks is not None and hasattr(blocks, "__len__"):          # ViT / Swin-ish
        n_layers = len(blocks) + 1                                 # + the head
        for n in names:
            m = re.match(r"blocks\.(\d+)\.", n)
            if m:
                depth[n] = int(m.group(1)) + 1
            elif any(n.startswith(k) for k in ("patch_embed", "cls_token", "pos_embed", "stem")):
                depth[n] = 0
            else:
                depth[n] = n_layers - 1                            # final norm rides with the last block
        return depth, n_layers
    if stages is not None and hasattr(stages, "__len__"):          # ConvNeXt / ResNet-ish
        counts = [len(getattr(s, "blocks", [])) for s in stages]
        offset = np.cumsum([0] + counts).tolist()                  # blocks before each stage
        n_layers = int(offset[-1]) + 1
        for n in names:
            m = re.match(r"stages\.(\d+)\.blocks\.(\d+)\.", n)
            if m:
                depth[n] = offset[int(m.group(1))] + int(m.group(2)) + 1
            elif (m2 := re.match(r"stages\.(\d+)\.", n)):          # that stage's downsample
                depth[n] = offset[int(m2.group(1))]
            elif n.startswith("stem"):
                depth[n] = 0
            else:
                depth[n] = n_layers - 1
        return depth, n_layers
    return {n: 0 for n in names}, 1                                # unknown layout: one backbone level


def _param_groups_llrd(model: nn.Module, base_lr: float, weight_decay: float,
                       layer_decay: float) -> list:
    """One param group per (depth, decay flag): lr = base_lr * layer_decay**(top - depth).

    Early layers barely move, the head trains at full lr. 1-D params (norms, biases)
    get no weight decay, the usual fine-tuning convention.
    """
    backbone = getattr(model, "backbone", None)
    bdepth, n_layers = _llrd_depths(backbone) if backbone is not None else ({}, 1)
    top = n_layers                                    # head sits one level above the backbone
    scales = [layer_decay ** (top - d) for d in range(top + 1)]
    groups = {}
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        d = bdepth.get(n[len("backbone."):], top) if n.startswith("backbone.") else top
        nd = p.ndim == 1
        key = (d, nd)
        g = groups.setdefault(key, {"params": [], "lr": base_lr * scales[d],
                                    "weight_decay": 0.0 if nd else weight_decay,
                                    "lr_scale": scales[d], "layer_id": d})
        g["params"].append(p)
    return [groups[k] for k in sorted(groups)]


def _print_llrd(groups: list, base_lr: float, layer_decay: float, top: int):
    """Boxed per-depth learning rates, so the decay can be eyeballed before it runs."""
    per = {}
    for g in groups:
        per.setdefault(g["layer_id"], g["lr"])
        per[g["layer_id"]] = g["lr"]
    depths = sorted(per)
    show = depths if len(depths) <= 8 else depths[:3] + [None] + depths[-3:]
    rows = []
    for d in show:
        if d is None:
            rows.append(["...", "...", "..."])
            continue
        label = "stem / embed" if d == 0 else ("head + pool" if d == top else f"block {d - 1}")
        rows.append([d, label, f"{per[d]:.3e}"])
    _table(f"LLRD layer_decay={layer_decay}  base_lr={base_lr:.2e}  "
           f"({len(depths)} depths, {len(groups)} groups)",
           ["depth", "what", "lr"], rows, "\U0001FA9C")


UPLOAD_POINTER = Path.home() / ".ml_utils_upload_modal_config"   # one line: a Modal config path


def resolve_upload_modal_config(value: str) -> str:
    """`modal_config: "local"` reads the real path from ~/.ml_utils_upload_modal_config, a file
    outside the repo, so no workspace-specific path is ever committed. Any other value is
    used as given."""
    if value != "local":
        return value
    if not UPLOAD_POINTER.exists():
        raise SystemExit(f"upload_checkpoints.modal_config is 'local' but {UPLOAD_POINTER} "
                         f"does not exist: write the Modal config path into it")
    return UPLOAD_POINTER.read_text(encoding="utf-8").strip()


def _adamw(o: dict):
    """torch AdamW, or bitsandbytes' 8-bit AdamW when optimizer.eight_bit is set: the two
    moment buffers stored in 8 bits (block-wise quantised) instead of 32, 4x less optimizer
    memory, same update rule. Tensors under 4,096 elements stay 32-bit."""
    if o.get("eight_bit"):
        import bitsandbytes as bnb
        print("  🗜️  8-bit AdamW (bitsandbytes): moment buffers in 8 bits")
        return bnb.optim.AdamW8bit
    return torch.optim.AdamW


def chunk_backbone(model: nn.Module, n: int) -> None:
    """Run model.backbone over `n` images at a time instead of the whole (B*windows) stack.

    Training: each chunk sits under its own activation checkpoint, so only ONE chunk's
    activations are alive at once (the rest is recomputed chunk by chunk in the backward).
    Eval: plain chunks, no checkpoint. Exact for backbones that treat every image on its own
    (LayerNorm, no BatchNorm, no cross-image attention); refused otherwise. The forward is
    patched on the instance, so parameter names and checkpoints are unchanged."""
    from torch.utils.checkpoint import checkpoint
    bb = getattr(model, "backbone")
    bn = [m_ for m_ in bb.modules() if isinstance(m_, nn.modules.batchnorm._BatchNorm)]
    if bn:
        raise SystemExit(f"backbone_chunk: {len(bn)} BatchNorm layers mix images across a "
                         f"chunk boundary, so chunking would change the result")
    orig = bb.forward

    def fwd(x):
        grad = bb.training and torch.is_grad_enabled()
        if x.shape[0] <= n and not grad:
            return orig(x)
        return torch.cat([checkpoint(orig, c, use_reentrant=False) if grad else orig(c)
                          for c in x.split(n)], dim=0)
    bb.forward = fwd
    print(f"  🧩 backbone runs {n} images at a time (training: one checkpointed chunk alive)")


def _split_decay(params_named, wd: float, no_decay_1d: bool):
    """[(name, p)] -> one or two groups: weight-decayed and (1-D params) undecayed."""
    dec = [p for n, p in params_named if not (no_decay_1d and p.ndim <= 1)]
    nod = [p for n, p in params_named if no_decay_1d and p.ndim <= 1]
    out = []
    if dec:
        out.append({"params": dec, "weight_decay": wd})
    if nod:
        out.append({"params": nod, "weight_decay": 0.0})
    return out


def _opt_class(o: dict, device_type: str = "cuda"):
    name = str(o.get("name", "adamw")).lower()
    if name == "adamw":
        return _adamw(o), {"betas": tuple(o.get("betas", (0.9, 0.999)))}
    if name == "adam":
        return torch.optim.Adam, {"betas": tuple(o.get("betas", (0.9, 0.999)))}
    if name == "sgd":
        return torch.optim.SGD, {"momentum": float(o.get("momentum", 0.9)),
                                 "nesterov": bool(o.get("nesterov", True))}
    raise ValueError(f"unknown optimizer {name!r} (adamw | adam | sgd)")


def build_optimizer(model: nn.Module, cfg: dict, verbose: bool = True):
    """Optimizer with up to three learning rates.

    `optimizer.lr` is the BACKBONE rate (model.backbone is usually ~all the parameters, so
    that is the number worth setting directly). The rest of the model is the head, at
    head_lr (explicit) or lr / backbone_lr_mult. With layer_decay, LLRD replaces the split:
    depths decay downward from the head. Modules flagged `is_fresh = True` inside the
    backbone get optimizer.fresh_lr. A model with no .backbone trains at one lr.
    """
    o = cfg["training"]["optimizer"]
    lr = float(o["lr"])
    mult = float(o.get("backbone_lr_mult", 1.0) or 1.0)    # 0 would divide by zero
    head_lr = float(o["head_lr"]) if o.get("head_lr") else lr / mult
    wd = float(o.get("weight_decay", 0.05))
    nd = bool(o.get("no_decay_bias_norm", True))
    cls, extra = _opt_class(o)
    ld = o.get("layer_decay")
    if ld:
        groups = _param_groups_llrd(model, head_lr, wd, float(ld))
        if not nd:
            for g in groups:
                g["weight_decay"] = wd
        if verbose:
            _print_llrd(groups, head_lr, float(ld), max(g["layer_id"] for g in groups))
        return cls(groups, lr=head_lr, weight_decay=wd, **extra)

    # split structurally, not by name: everything under .backbone is the pretrained trunk
    has_bb = hasattr(model, "backbone") or hasattr(getattr(model, "_orig_mod", None), "backbone")
    fresh_ids = set()
    for _, mod_ in model.named_modules():
        if getattr(mod_, "is_fresh", False):
            fresh_ids.update(id(q) for q in mod_.parameters())
    fresh_lr = o.get("fresh_lr")
    bb, hd, fr = [], [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        n0 = n[len("_orig_mod."):] if n.startswith("_orig_mod.") else n
        if fresh_lr and id(p) in fresh_ids:
            fr.append((n, p))
        elif has_bb and n0.startswith("backbone."):
            bb.append((n, p))
        else:
            hd.append((n, p))
    groups, rows = [], []
    for label, plist, glr in (("backbone", bb, lr), ("head" if has_bb else "all", hd,
                                                     head_lr if has_bb else lr),
                              ("fresh", fr, float(fresh_lr or 0))):
        for g in _split_decay(plist, wd, nd):
            g.update(lr=glr, name=label, is_backbone=(label == "backbone"))
            groups.append(g)
            rows.append([label, f"{sum(p.numel() for p in g['params']) / 1e6:.3f}M",
                         f"{glr:.2e}", g["weight_decay"]])
    if verbose:
        _table(f"optimizer {o.get('name', 'adamw')}  ({len(groups)} param groups)",
               ["group", "params", "lr", "weight_decay"], rows, "🧮")
        if fresh_ids and not fresh_lr:
            print(f"  ⚠️  {len(fresh_ids)} tensors declare is_fresh but optimizer.fresh_lr is "
                  f"unset - they train at the backbone/head rate")
    return cls(groups, lr=head_lr if has_bb else lr, weight_decay=wd, **extra)


def schedule_steps(cfg: dict, total_steps: int) -> int:
    """Steps the lr CURVE spans, which is not always the steps we train for.

    scheduler.schedule_epochs stretches the cosine over a different number of epochs than
    training.epochs, so a shortened run replays a longer run's lr trajectory instead of
    annealing fully into its own end.
    """
    se = cfg["training"]["scheduler"].get("schedule_epochs")
    ep = cfg["training"].get("epochs") or 0
    if not se or not ep or int(se) == int(ep):
        return total_steps
    return max(1, int(round(total_steps * float(se) / float(ep))))


def warmup_steps(cfg: dict, total_steps: int) -> int:
    """How many steps the lr ramp lasts - same formula build_scheduler uses."""
    n = schedule_steps(cfg, total_steps)
    return max(1, int(n * cfg["training"]["scheduler"].get("warmup_frac", 0.05)))


def build_scheduler(opt, cfg: dict, total_steps: int, steps_per_epoch: int = 0):
    """Learning-rate schedule as a multiplier on each group's base lr: linear warm-up from 0
    over warmup_frac, then cosine | linear decay to min_lr_mult, constant, or step
    (lr *= gamma at each epoch in `milestones`)."""
    s = cfg["training"]["scheduler"]
    kind = str(s.get("name", "cosine")).lower()
    warm = warmup_steps(cfg, total_steps)
    lo = float(s.get("min_lr_mult", 0.01))
    n = schedule_steps(cfg, total_steps)
    if n != total_steps:
        print(f"  \U0001F4C9 lr curve spans {n} steps ({s['schedule_epochs']} epochs) but "
              f"training stops at {total_steps} ({cfg['training']['epochs']} epochs) - "
              f"ends at {100 * total_steps / n:.0f}% of the curve, not at its floor")
    total_steps = n
    miles = sorted(int(m) * max(steps_per_epoch, 1) for m in (s.get("milestones") or []))
    gamma = float(s.get("gamma", 0.1))
    if kind not in ("cosine", "linear", "constant", "step"):
        raise ValueError(f"unknown scheduler {kind!r} (cosine | linear | constant | step)")

    def fn(step):                                    # returns a multiplier on the base lr
        if step < warm:
            return step / warm                       # linear warm-up from 0
        prog = min((step - warm) / max(1, total_steps - warm), 1.0)
        if kind == "cosine":
            return lo + (1 - lo) * 0.5 * (1 + math.cos(math.pi * prog))
        if kind == "linear":
            return lo + (1 - lo) * (1 - prog)
        if kind == "step":
            return gamma ** sum(step >= m for m in miles)
        return 1.0
    return torch.optim.lr_scheduler.LambdaLR(opt, fn)


# =============================================================================
# checkpoints & resume
# =============================================================================
def _rng_state(device) -> dict:
    st = {"python": random.getstate(), "numpy": np.random.get_state(),
          "torch": torch.get_rng_state()}
    if device.type == "cuda":
        st["cuda"] = torch.cuda.get_rng_state_all()
    return st


def _restore_rng(st: dict, device):
    try:
        random.setstate(st["python"]); np.random.set_state(st["numpy"])
        torch.set_rng_state(st["torch"].cpu() if hasattr(st["torch"], "cpu") else st["torch"])
        if device.type == "cuda" and "cuda" in st:
            torch.cuda.set_rng_state_all([t.cpu() for t in st["cuda"]])
    except Exception as e:                     # a resumed run must not die over RNG
        print(f"  [warn] could not restore RNG: {type(e).__name__}: {e}")


class ScaleProbe:
    """Feature and logit scale at the head, every N steps.

    The diagnostic that was missing when dinov3_convnext_base underfitted by 0.11 AUROC.
    Its trunk was fine; its FEATURES were 4.8x larger than the ImageNet trunk's, because
    a backbone's final LayerNorm carries a learned gain that ships inside the downloaded
    weights and nothing in self-supervised pretraining ever pressured that gain toward a
    scale a linear head wants. Bigger features mean bigger logits (a head confident before
    it has learned anything, where the sigmoid slope is shallow) AND proportionally bigger
    head gradients, since dL/dW = delta @ f.T carries f. Neither is visible in the loss.

    Healthy: feature std near 1, logit |max| under ~2 early on. A feature std far from 1
    means the head's learning rate does not mean what the config says it means.
    """

    def __init__(self, model, every: int = 200):
        self.every = int(every)
        self.buf, self.handle, self.head_name = None, None, None
        head = None
        for n, m in model.named_modules():          # the last Linear IS the head
            if isinstance(m, nn.Linear):
                head, self.head_name = m, n
        if head is not None:
            self.handle = head.register_forward_hook(self._hook)

    def _hook(self, _mod, inp, out):
        if self.buf is not False:                   # False = not an active step
            f, o = inp[0].detach().float(), out.detach().float()
            # head weight norm too: logits = head_w . features, so features and logits alone
            # cannot say WHICH side moved. dinov2_vits14_25d showed feat_l2 FALLING
            # 24.5 -> 17.9 while logit_std ROSE 0.78 -> 1.30, which can only mean the head
            # grew to compensate - and a bigger head sends bigger gradients back into the
            # trunk, eroding the features further. That loop is invisible without this.
            w = getattr(_mod, "weight", None)
            self.buf = (float(f.std()), float(f.norm(dim=-1).mean()),
                        float(o.std()), float(o.abs().max()),
                        float(w.detach().float().norm()) if w is not None else float("nan"))

    def active(self, step: int) -> bool:
        return self.handle is not None and self.every > 0 and step % self.every == 0

    def arm(self, on: bool):
        self.buf = None if on else False            # None = armed, waiting for a forward

    def read(self):
        b = self.buf if isinstance(self.buf, tuple) else None
        self.buf = False
        return b

    @staticmethod
    def row(b):
        if not b:
            return {}
        r = {"feat_std": round(b[0], 4), "feat_l2": round(b[1], 3),
             "logit_std": round(b[2], 4), "logit_absmax": round(b[3], 3)}
        if len(b) > 4:
            r["head_w_norm"] = round(b[4], 4)
        return r

    @staticmethod
    def summarize(b):
        if not b:
            return ""
        fs, fl, ls, lm = b[:4]
        hw = b[4] if len(b) > 4 else None
        flag = ""
        if fs > 2.5 or fs < 0.15:
            flag = ("   <-- feature scale is far from 1: the head's effective lr is not "
                    "what the config says. Consider model.feat_norm")
        head = f"   |   head |W| {hw:.2f}" if hw is not None and hw == hw else ""
        return (f"  \U0001F4CF scale  features std {fs:.3f}  L2 {fl:.1f}   |   "
                f"logits std {ls:.3f}  |max| {lm:.2f}{head}{flag}")


class UDRatio:
    """log10 of the update-to-data ratio per weight matrix, the Karpathy diagnostic.

    The usual form is log10(lr * grad.std() / param.std()), which assumes the step IS
    lr*grad. Under PESG that is false - there is momentum, a proximal term and a
    weight-decay term - and under AMP the grads are still loss-scaled at that point.
    So this snapshots the parameter BEFORE the step and diffs it AFTER, which is the
    real update whatever the optimizer did to produce it.

    Roughly -3 is healthy. Much below and the layer is effectively frozen; much above
    and the step is large against the weights it is moving, which is how a trunk gets
    wrecked. Only 2D+ weights are tracked - biases and norms have their own scales and
    read as noise.
    """

    def __init__(self, model, every: int = 200, top_n: int = 8):
        self.every, self.top_n = int(every), int(top_n)
        self.params = [(n, q) for n, q in model.named_parameters()
                       if q.requires_grad and q.ndim >= 2]
        # HEAD and TRUNK are reported apart, because the healthy band differs. A
        # reinitialized head starts random and SHOULD sit at or above -3; a converged
        # pretrained trunk should only drift, so -5 or -6 is right for it, not a
        # problem. Pooling them hides both facts behind one median.
        self.head = {n for n, _ in self.params
                     if any(k in n.lower() for k in ("head", "classifier", ".fc."))
                     and "backbone" not in n.lower()}
        self.snap, self.rows = None, []

    def active(self, gstep: int) -> bool:
        return self.every > 0 and gstep % self.every == 0

    def before(self):
        self.snap = [q.detach().clone() for _, q in self.params]

    def after(self, epoch: int, gstep: int):
        if self.snap is None:
            return None
        out = []
        for (n, q), old in zip(self.params, self.snap):
            d = (q.detach() - old).std().item()
            w = q.detach().std().item()
            if w > 0 and d > 0:
                out.append((n, math.log10(d / w)))
        self.snap = None
        for n, r in out:
            self.rows.append({"epoch": epoch, "step": gstep, "param": n, "log10_ud": r})
        return out

    @staticmethod
    def _fmt(label, vals, want):
        v = sorted(vals)
        return ("     %-7s n=%-3d min %6.2f  mean %6.2f  median %6.2f  max %6.2f   %s"
                % (label, len(v), v[0], sum(v) / len(v), v[len(v) // 2], v[-1], want))

    def summarize(self, out):
        if not out:
            return ""
        hv = [r for n, r in out if n in self.head]
        bv = [r for n, r in out if n not in self.head]
        lines = ["  📏 ud log10 (update / weight)"]
        if hv:
            lines.append(self._fmt("head", hv, "(random head: want ~-3 or above)"))
        if bv:
            lines.append(self._fmt("trunk", bv, "(pretrained: -5..-6 is drift, not frozen)"))
        # Only flag what is genuinely wrong for its own role.
        dead = [n for n, r in out if n not in self.head and r < -7.0]
        hot = [n for n, r in out if n not in self.head and r > -3.0]
        cold_head = [n for n, r in out if n in self.head and r < -4.5]
        if dead:
            lines.append("     ⚠️  trunk frozen (< -7): %d tensors, e.g. %s"
                         % (len(dead), dead[0]))
        if hot:
            lines.append("     ⚠️  trunk hot (> -3, may damage the pretrained "
                         "features): %d tensors, e.g. %s" % (len(hot), hot[0]))
        if cold_head:
            lines.append("     ⚠️  head barely moving (< -4.5): %s" % cold_head[0])
        return chr(10).join(lines)

    def dump(self, path):
        """MERGE with what is already there, never truncate.

        self.rows only holds this process's samples, so a plain to_csv would wipe every
        earlier epoch on the first save after a workspace hand-off. Dedupes on
        (step, param) so a replayed mid-epoch resume cannot double-count.
        """
        if not self.rows:
            return
        try:
            df = pd.DataFrame(self.rows)
            if path.exists():
                try:
                    df = pd.concat([pd.read_csv(path), df], ignore_index=True)
                except Exception as e:
                    print(f"  [warn] {path.name} unreadable, starting fresh: "
                          f"{type(e).__name__}: {e}")
            df = (df.drop_duplicates(subset=["step", "param"], keep="last")
                    .sort_values(["step", "param"]))
            df.to_csv(path, index=False)
        except Exception as e:
            print(f"  [warn] could not write {path.name}: {type(e).__name__}: {e}")


def _uncompiled(model):
    """The real module behind a torch.compile wrapper, or the model itself.

    torch.compile returns an OptimizedModule that holds the original under
    `_orig_mod`, and its state_dict keys all gain an "_orig_mod." prefix. Saving that
    prefix would make every checkpoint depend on whether compile happened to be on,
    so checkpoints are always written from the ORIGINAL module.
    """
    return getattr(model, "_orig_mod", model)


def _load_model_state(model, sd, allow_head_mismatch: bool = False):
    """Load weights whichever side of torch.compile they were saved from.

    Strips a leading "_orig_mod." (a checkpoint written by an older compiled run) and
    loads into the unwrapped module, so compiled and non-compiled runs can resume from
    each other's checkpoints in either direction.

    `allow_head_mismatch` is for SPECIALIST transfer: seed a 1-task model from a 12-task
    checkpoint by taking the backbone and dropping the head, whose shape cannot match
    ((12, 1024) into (1, 1024)). It is deliberately NOT the default - a silent partial load
    is how a half-random model trains for an hour and looks completely normal doing it.
    Every skipped and every missing tensor is printed, and anything missing OUTSIDE the head
    is a hard error.
    """
    if any(k.startswith("_orig_mod.") for k in sd):
        sd = {k[len("_orig_mod."):] if k.startswith("_orig_mod.") else k: v
              for k, v in sd.items()}
    m = _uncompiled(model)
    if not allow_head_mismatch:
        return m.load_state_dict(sd)

    own = m.state_dict()
    keep, skipped = {}, []
    for k, v in sd.items():
        if k in own and own[k].shape == v.shape:
            keep[k] = v
        else:
            skipped.append("%s %s -> %s" % (k, tuple(v.shape),
                                            tuple(own[k].shape) if k in own else "absent"))
    missing = [k for k in own if k not in keep]
    # a skipped tensor is only acceptable if it is the task head
    bad = [k for k in missing if "head" not in k.lower() and "classifier" not in k.lower()
           and "fc." not in k.lower()]
    if bad:
        raise SystemExit("transfer would leave %d NON-HEAD tensor(s) untrained: %s\n"
                         "   the checkpoint does not match this architecture"
                         % (len(bad), bad[:6]))
    print("  transfer: loaded %d tensors, fresh head (%d tensor(s))" % (len(keep), len(missing)))
    for x in skipped:
        print("      skipped %s" % x)
    for k in missing:
        print("      fresh   %s %s" % (k, tuple(own[k].shape)))
    m.load_state_dict(keep, strict=False)
    return None


def save_checkpoint(path: Path, cfg, model, opt=None, sched=None, scaler=None,
                    epoch=0, step=0, score=None, track=None, device=None,
                    weights_only=False, elapsed_sec=0.0, epoch_complete=True,
                    saver=None, note=None, loss_fn=None, ema=None):
    """Full state by default, so a run can resume exactly where it stopped.

    epoch_complete=False marks a checkpoint written part-way through an epoch, so
    resume replays that epoch instead of silently skipping the rest of its data.
    ema: a ModelEMA; its weights ride along as "ema" (load_weights prefers them).
    """
    payload = {"model": _uncompiled(model).state_dict(), "cfg": cfg, "epoch": epoch,
               "step": step, "score": score, "track": track,
               "elapsed_sec": elapsed_sec, "epoch_complete": epoch_complete}
    if ema is not None:
        payload["ema"] = ema.state_dict()
    if not weights_only:
        if loss_fn is not None and hasattr(loss_fn, "state"):
            payload["loss"] = loss_fn.state()      # AUC-M's learned a / b / alpha
        if opt is not None:
            payload["optimizer"] = opt.state_dict()
        if sched is not None:
            payload["scheduler"] = sched.state_dict()
        if scaler is not None:
            payload["scaler"] = scaler.state_dict()
        if device is not None:
            payload["rng"] = _rng_state(device)
    if saver is not None:
        # freeze it here, on the training thread, THEN hand it off. Serialising live
        # tensors on a worker while the next step mutates them is the way this goes
        # wrong; a host-RAM copy costs ~0.2s against ~10s of torch.save.
        return saver.write(_cpu_snapshot(payload), path, note)
    _write_checkpoint(payload, path)
    if note:
        print(note)
    return path


def _write_checkpoint(payload: dict, path: Path) -> Path:
    """torch.save via a temp file, so a kill mid-write cannot leave a half checkpoint."""
    tmp = path.with_suffix(".tmp")
    torch.save(payload, tmp)
    tmp.replace(path)                          # atomic: never leave a half-written ckpt
    _after_checkpoint_write(path)              # optional off-site copy (CheckpointUploader)
    return path


def _cpu_snapshot(x):
    """Deep-copy every tensor to host RAM, leaving plain python objects alone."""
    if torch.is_tensor(x):
        return x.detach().to("cpu", copy=True)
    if isinstance(x, dict):
        return {k: _cpu_snapshot(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return type(x)(_cpu_snapshot(v) for v in x)
    return x


class CheckpointUploader:
    """Copy freshly written checkpoints to a Modal volume, so a LOCAL run can keep only a few on
    disk (output.upload_checkpoints: {modal_config, volume, patterns}).

    Each file is hard-linked into results/_upload_staging first (no extra disk, and it survives
    the rolling prune deleting the original mid-upload), then `modal volume put --force` runs in a
    subprocess whose ONLY Modal config is the one given, on a single background thread, newest
    version first if the same name is queued twice. Success and failure are printed in the
    training console; a failed upload never stops training.
    """

    def __init__(self, spec: dict, run_name: str, res_dir: Path, rel_ckpt_dir: str, default_volume: str):
        import fnmatch
        import queue
        import threading
        self.spec, self.run = spec, run_name
        # the same volume and path a Modal run writes to: <runs_volume>:/<run>/results/checkpoints
        self.volume = spec.get("volume") or default_volume
        self.rel = rel_ckpt_dir
        self.patterns = spec.get("patterns", ["step*.pt", "top_step*.pt", "best.pt"])
        self.cfg_path = str(Path(os.path.expanduser(resolve_upload_modal_config(spec["modal_config"]))))
        self.stage = Path(res_dir) / "_upload_staging"
        self.stage.mkdir(parents=True, exist_ok=True)
        self._match = lambda n: any(fnmatch.fnmatch(n, p) for p in self.patterns)
        self.q, self.pending, self.lock = queue.Queue(), {}, threading.Lock()
        self.done = self.failed = 0
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"  ☁️  checkpoint upload ON: {', '.join(self.patterns)} -> Modal volume "
              f"'{self.volume}':/{self.run}/{self.rel}/ ({self.cfg_path})", flush=True)

    def offer(self, path: Path) -> None:
        path = Path(path)
        if not self._match(path.name):
            return
        staged = self.stage / path.name
        try:
            if staged.exists():
                staged.unlink()
            os.link(path, staged)                  # same volume: instant, no extra space
        except OSError as e:
            print(f"  ⚠️  upload staging failed for {path.name}: {e}", flush=True)
            return
        with self.lock:
            fresh = path.name not in self.pending
            self.pending[path.name] = staged
        if fresh:
            self.q.put(path.name)

    def _loop(self):
        import subprocess
        import time as _t
        while True:
            name = self.q.get()
            if name is None:
                return
            with self.lock:
                staged = self.pending.pop(name, None)
            if staged is None or not staged.exists():
                continue
            size = staged.stat().st_size
            remote = f"/{self.run}/{self.rel}/{name}"
            env = dict(os.environ, MODAL_CONFIG_PATH=self.cfg_path, PYTHONUTF8="1")
            ca = Path.home() / ".certs" / "ca-bundle.pem"
            if ca.exists():
                env["REQUESTS_CA_BUNDLE"] = env["SSL_CERT_FILE"] = str(ca)
            t0 = _t.time()
            r = subprocess.run([sys.executable, "-m", "modal", "volume", "put", "--force",
                                self.volume, str(staged), remote],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", env=env)
            dt = _t.time() - t0
            if r.returncode == 0:
                self.done += 1
                print(f"  ☁️  uploaded {name} ({size / 1e9:.2f} GB) -> {self.volume}:{remote} "
                      f"in {dt:.0f}s ({size / 1e6 / max(dt, 1e-9):.0f} MB/s)", flush=True)
            else:
                self.failed += 1
                tail = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["?"]
                print(f"  ⚠️  upload FAILED for {name} after {dt:.0f}s: {tail[0][:200]}", flush=True)
            with self.lock:
                if name not in self.pending:
                    try:
                        staged.unlink()
                    except OSError:
                        pass

    def join(self) -> None:
        """Wait for every queued upload, then stop the thread."""
        self.q.put(None)
        self.thread.join()
        print(f"  ☁️  checkpoint uploads finished: {self.done} uploaded, {self.failed} failed", flush=True)


_UPLOADER = None                                   # set by run_experiment when configured


def _after_checkpoint_write(path: Path) -> None:
    if _UPLOADER is not None:
        _UPLOADER.offer(path)


class AsyncSaver:
    """Write checkpoints on a worker thread, from a frozen CPU copy.

    Base writes last.pt + best.pt + a top-k file at every validation (~2.4 GB) and a
    1 GB periodic checkpoint every 100 steps. Inline, the GPU idles through all of it.

    Only ONE write runs at a time, and starting a new one first joins the previous:
    that keeps file operations ordered, so pruning and top-k eviction can never race
    a write. In practice it never blocks - saves are minutes apart and take seconds.
    """

    def __init__(self, enabled: bool = True):
        self.enabled, self.thread = bool(enabled), None
        self.count, self.error = 0, None

    def write(self, payload: dict, path: Path, note: str | None = None) -> Path:
        if not self.enabled:
            _write_checkpoint(payload, path)
            if note:
                print(note)
            return path
        self.join()
        import threading
        self.thread = threading.Thread(target=self._run, args=(payload, path, note),
                                       daemon=True)
        self.thread.start()
        return path

    def _run(self, payload, path, note=None):
        try:
            _write_checkpoint(payload, path)
            self.count += 1
            if note:
                # printed HERE, not at the call site: the point of the line is that the
                # file is on the volume, and with an async write the call site reaches
                # it seconds early. A claim of "saved" has to mean saved.
                print(note, flush=True)
        except Exception as e:                 # a failed write must not kill training
            self.error = f"{path.name}: {type(e).__name__}: {e}"
            print(f"  ⚠️  checkpoint write failed, {self.error}", flush=True)

    def join(self, timeout: float = 900.0) -> None:
        """Block until nothing is in flight. Call before touching checkpoint files."""
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout)


def _resolve_resume(resume, ckpt_dir: Path) -> Path | None:
    """null | 'best' | 'last' | <step int> | <path> -> a file to load."""
    if resume in (None, False, ""):
        return None
    if isinstance(resume, str) and resume not in ("best", "last"):
        pth = Path(resume)
        if pth.exists():
            return pth
    if resume == "best":
        pth = ckpt_dir / "best.pt"
        return pth if pth.exists() else None
    if resume == "last":
        # newest of ALL of them, not last.pt by preference: last.pt is only written at
        # a validation, so it can trail the newest step*.pt by a whole eval interval.
        # This is the preemption-safe setting - Modal restarts a preempted container on
        # the same input, and a hardcoded step number makes it replay from there forever.
        cands = list(ckpt_dir.glob("step*.pt"))
        pth = ckpt_dir / "last.pt"
        if pth.exists():
            cands.append(pth)
        return max(cands, key=lambda q: q.stat().st_mtime) if cands else None
    if isinstance(resume, int) or str(resume).isdigit():
        pth = ckpt_dir / f"step{int(resume)}.pt"
        return pth if pth.exists() else None
    return None


def resolve_init_from(spec: str, out_dir, cfg: dict) -> Path:
    """Where another run's checkpoint lives, given "<run>/<checkpoint>" or a path.

    out_dir is THIS run's folder, so its parent is the runs root on either side: the Modal
    volume mount or the local repo. A bare run name means that run's best.pt.
    """
    p = Path(str(spec))
    if p.is_absolute() and p.exists():
        return p
    runs_root = Path(out_dir).parent
    parts = str(spec).replace("\\", "/").split("/")
    run = parts[0]
    name = parts[1] if len(parts) > 1 else cfg["output"]["best_name"]
    if not name.endswith(".pt"):
        name += ".pt"
    cand = [runs_root / run / cfg["output"]["run_dir"] / cfg["output"]["checkpoints_dir"] / name,
            runs_root / str(spec),
            Path(str(spec))]
    for c in cand:
        if c.exists():
            return c
    raise FileNotFoundError(
        "model.init_from=%r matched nothing. Looked in:\n  %s"
        % (spec, "\n  ".join(str(c) for c in cand)))


def load_checkpoint(resume, model, ckpt_dir: Path, opt=None, sched=None,
                    scaler=None, device=None, cfg_now: dict | None = None, ema=None) -> dict:
    """Restore whatever the checkpoint holds. Returns {} when there is nothing to do."""
    path = _resolve_resume(resume, ckpt_dir)
    if path is None:
        if resume not in (None, False, ""):
            print(f"  \u26A0\uFE0F  resume={resume!r} requested but no checkpoint found "
                  f"in {ckpt_dir}")
        return {}
    print(f"  \u21A9\uFE0F  resuming from {path}")
    ck = torch.load(path, map_location="cpu", weights_only=False)
    _load_model_state(model, ck["model"])
    for obj, key in ((opt, "optimizer"), (sched, "scheduler"), (scaler, "scaler")):
        if obj is not None and key in ck and ck[key] is not None:
            try:
                obj.load_state_dict(ck[key])
            except Exception as e:
                print(f"  [warn] could not restore {key}: {type(e).__name__}: {e}")
    if ema is not None:
        if ck.get("ema"):
            ema.load_state_dict(ck["ema"])
        else:
            ema.reset(model)                     # no EMA in the file: start it from the weights
    if device is not None and "rng" in ck:
        _restore_rng(ck["rng"], device)
    print(f"  \u21A9\uFE0F  resumed at epoch {ck.get('epoch')}, step {ck.get('step')}, "
          f"score={ck.get('score')}")
    # the cosine schedule spans epochs x steps_per_epoch, so resuming under a
    # different `epochs` silently trains on a different lr curve
    was = ((ck.get("cfg") or {}).get("training") or {}).get("epochs")
    now = ((cfg_now or {}).get("training") or {}).get("epochs")
    if was is not None and now is not None and was != now:
        print(f"  ⚠️  epochs changed {was} -> {now}: the lr curve is NOT the "
              f"one this checkpoint was trained under")
    return ck


def save_predictions(pred_dir: Path, split: str, run_id: str, epoch: int, step: int,
                     score, logits, targets, ids, tasks) -> Path | None:
    """One .npz of raw per-sample outputs (logits), so ensembling later needs no GPU.

    Kept for every validation: a few KB to MB each, and it makes checkpoint and cross-run
    ensembling a local CPU job. ids are stored so rows stay alignable across checkpoints
    and runs without trusting loader order.
    """
    try:
        pred_dir.mkdir(parents=True, exist_ok=True)
        f = pred_dir / f"{run_id}_{split}_s{step}.npz"
        np.savez_compressed(
            f, logits=np.asarray(logits, np.float32),
            targets=np.asarray(targets, np.float32),
            ids=np.asarray(ids, dtype=object),
            tasks=np.asarray(list(tasks), dtype=object),
            meta=np.asarray([run_id, split, str(epoch), str(step),
                             "" if score is None else f"{score:.6f}"], dtype=object))
        return f
    except Exception as e:                    # bookkeeping must never kill a run
        print(f"  ⚠️  could not save {split} predictions: {type(e).__name__}: {e}")
        return None


def prune_checkpoints(ckpt_dir: Path, keep_last_n: int, keep_names=(), saver=None):
    """Rolling window over the periodic step checkpoints."""
    if keep_last_n <= 0:
        return
    # deliberately does NOT wait on an in-flight write. It only ever unlinks files
    # OLDER than the newest, writes are serialised so anything older is complete, and
    # an unfinished write is a .tmp that this glob cannot see. Joining here would undo
    # the async saving entirely, since prune runs right after the periodic checkpoint.
    files = sorted(ckpt_dir.glob("step*.pt"), key=lambda q: q.stat().st_mtime)
    for f in files[:-keep_last_n]:
        if f.name not in keep_names:
            mb = f.stat().st_size / 1024**2
            try:
                f.unlink()
                print(f"  🗑️  pruned {f.name} ({mb:.0f} MB) - "
                      f"outside the keep_last_n={keep_last_n} window")
            except OSError as e:
                print(f"  [warn] could not prune {f.name}: {e}")


def update_top_k(ckpt_dir: Path, cfg, model, epoch: int, step: int, score: float,
                 track: list, k: int, weights_only: bool = True, saver=None,
                 mode: str = "max", ema=None) -> list:
    """Keep the K best validations of the whole run, not just the single best.

    best.pt is overwritten every improvement, so every runner-up is otherwise
    lost -- and those are exactly what ensembling wants.
    """
    if k <= 0 or score != score:                # k=0 disables; NaN never ranks
        return track
    track = [r for r in (track or []) if r["step"] != step]
    track.append({"step": step, "epoch": epoch, "score": float(score),
                  "file": f"top_step{step}.pt"})
    track.sort(key=lambda r: -r["score"] if mode == "max" else r["score"])
    keep, drop = track[:k], track[k:]
    if any(r["step"] == step for r in keep):
        save_checkpoint(ckpt_dir / f"top_step{step}.pt", cfg, model, epoch=epoch,
                        step=step, score=score, weights_only=weights_only, saver=saver,
                        ema=ema)
    # same reasoning as prune_checkpoints: everything in `drop` is from an earlier
    # step than the one just written, and writes are serialised, so none of it is
    # still open. The current step is only saved when it survives into `keep`.
    for r in drop:
        f = ckpt_dir / r["file"]
        if f.exists():
            try:
                f.unlink()
                print(f"  🗑️  evicted {f.name} (score {r['score']:.4f}, "
                      f"epoch {r['epoch']}) - pushed out of the top-{k}")
            except OSError as e:
                print(f"  [warn] could not evict {f.name}: {e}")
    (ckpt_dir / "top_k.json").write_text(json.dumps(keep, indent=2))
    return keep



class ModelEMA:
    """Exponential moving average of a model's weights (a frozen copy, updated each step).

    shadow = decay * shadow + (1 - decay) * weights, floats only; integer buffers (BatchNorm
    counters) are copied. With warmup the decay ramps as (1+n)/(10+n), so early averages
    are not dominated by the random init. Validate with .module when training.ema.eval.
    """

    def __init__(self, model: nn.Module, decay: float = 0.999, warmup: bool = True):
        self.module = copy.deepcopy(_uncompiled(model)).eval()
        for p in self.module.parameters():
            p.requires_grad_(False)
        self.decay, self.warmup, self.updates = float(decay), bool(warmup), 0

    def _d(self) -> float:
        return min(self.decay, (1 + self.updates) / (10 + self.updates)) if self.warmup else self.decay

    @torch.no_grad()
    def update(self, model: nn.Module):
        self.updates += 1
        d = self._d()
        src = _uncompiled(model).state_dict()
        for k, v in self.module.state_dict().items():
            s = src[k].detach()
            if v.dtype.is_floating_point:
                v.lerp_(s.to(v.dtype), 1.0 - d)
            else:
                v.copy_(s)

    @torch.no_grad()
    def reset(self, model: nn.Module):
        self.module.load_state_dict(_uncompiled(model).state_dict())

    def state_dict(self) -> dict:
        return {"module": self.module.state_dict(), "updates": self.updates}

    def load_state_dict(self, sd: dict):
        self.module.load_state_dict(sd["module"])
        self.updates = int(sd.get("updates", 0))


# =============================================================================
# eval / train
# =============================================================================
def _eval_cadence_str(cfg: dict) -> str:
    """One line describing the validation cadence."""
    e = cfg["evaluation"]
    parts = []
    sched = e.get("eval_steps_schedule") or []
    if sched:
        parts.append(", ".join(f"every {int(s)} steps from epoch {int(ep)}" for ep, s in sched))
    elif e.get("eval_every_steps"):
        parts.append(f"every {int(e['eval_every_steps'])} steps")
    if e.get("eval_every_epochs"):
        parts.append(f"every {int(e['eval_every_epochs'])} epoch(s) at epoch end")
    return " + ".join(parts) or "only at the end"


def eval_interval(cfg: dict, epoch: int) -> int:
    """Steps between validations for this epoch - 0 disables step-triggered eval.

    Cadence is driven by the GLOBAL STEP, not the epoch. The epoch only selects which
    interval applies: early epochs move fast and are not worth scoring often, later ones
    are where the best checkpoint usually shows up. evaluation.eval_steps_schedule is a
    list of [from_epoch, every_steps] tiers (the last tier whose from_epoch <= epoch
    wins); without it, evaluation.eval_every_steps applies everywhere.
    """
    e = cfg["evaluation"]
    sched = sorted((int(a), int(b)) for a, b in (e.get("eval_steps_schedule") or []))
    if sched:
        every = 0
        for ep, s in sched:
            if epoch >= ep:
                every = s
        return every
    return int(e.get("eval_every_steps") or 0)


def eval_due(cfg: dict, epoch: int, gstep: int, resume_eval: list) -> str | None:
    """Should this step be validated, and what should the log call the trigger?

    Returns the trigger label, or None to skip. `resume_eval` is a one-element list used
    as a mutable flag: the one-off `evaluation.validate_on_resume` validation DISARMS the
    moment it is consumed, whichever branch consumes it, so it can never fire twice and a
    resume landing exactly on a cadence step scores once, not twice.

    Split out of the training loop so it can be tested without a GPU. The loop must not
    re-implement this - a copy is a copy that drifts.
    """
    ev = eval_interval(cfg, epoch)
    if ev and gstep % ev == 0:
        resume_eval[0] = False
        return "every %d steps" % ev
    if resume_eval[0]:
        resume_eval[0] = False
        return "first step after resume"
    return None


@dataclass
class Hooks:
    """Optional overrides; every field left None uses the engine default.

    forward(model, inputs) -> outputs          default: model(**inputs) for a dict, model(*inputs)
                                               for a tuple/list, model(inputs) otherwise. A model
                                               may return (outputs, aux) in training; aux is ignored
                                               unless `loss` uses it.
    loss(raw_outputs, targets, inputs) -> t    default: build_loss(cfg) on the outputs
    prepare(inputs, device, cfg) -> inputs     default: to_device (+ channels_last for 4-D floats)
    score(y_true, y_prob) -> {name: float}     extra (competition) metrics, usable as the monitor
    on_epoch_start(epoch, model, loaders)      anything per epoch (curriculum, unfreezing, ...)
    on_validation(row, epoch, step)            after every validation row is built
    """
    forward: Callable | None = None
    loss: Callable | None = None
    prepare: Callable | None = None
    score: Callable | None = None
    on_epoch_start: Callable | None = None
    on_validation: Callable | None = None


def default_forward(model, inputs):
    if isinstance(inputs, dict):
        return model(**inputs)
    if isinstance(inputs, (list, tuple)):
        return model(*inputs)
    return model(inputs)


def _fwd(hooks: Hooks, model, inputs):
    """-> (main output tensor, raw output). Handles (out, aux) tuples and HF ModelOutputs."""
    out = (hooks.forward or default_forward)(model, inputs)
    if isinstance(out, (tuple, list)):
        return out[0], out
    if hasattr(out, "logits"):
        return out.logits, out
    return out, out


def _prep(hooks: Hooks, inputs, device, cfg):
    if hooks.prepare is not None:
        return hooks.prepare(inputs, device, cfg)
    return to_device(inputs, device, bool(cfg["training"].get("channels_last")))


def _loss(hooks: Hooks, loss_fn, outputs, raw, targets, inputs):
    if hooks.loss is not None:
        return hooks.loss(raw, targets, inputs)
    return loss_fn(outputs, targets)


@torch.no_grad()                                   # no gradients: eval only, saves memory
def evaluate(model, loader, loss_fn, cfg, device, hooks: Hooks | None = None,
             collect: dict | None = None) -> dict:
    """Run the whole loader -> compute_metrics(...) + mean loss + sample_count.

    Pass `collect` to also keep the raw outputs, targets and ids: they are what makes
    checkpoint ensembling free later (averaging saved logits needs no GPU).
    Batches whose targets are None (a test split) only produce outputs.
    """
    hooks = hooks or Hooks()
    model.eval()
    outs, ys, ids_all, losses, n_loss = [], [], [], 0.0, 0
    use_amp = cfg["training"]["amp"] and device.type == "cuda"
    for batch in loader:
        x, y, ids = split_batch(batch)
        x = _prep(hooks, x, device, cfg)
        with torch.autocast("cuda", enabled=use_amp, dtype=amp_dtype(cfg)):
            o, raw = _fwd(hooks, model, x)
            if y is not None and loss_fn is not None:
                y = y.to(device, non_blocking=True)
                b = batch_size_of(y)
                losses += float(_loss(hooks, loss_fn, o, raw, y, x)) * b
                n_loss += b
        outs.append(o.float().cpu())
        if y is not None:
            ys.append(y.float().cpu() if torch.is_tensor(y) else torch.as_tensor(np.asarray(y)))
        if ids is not None:
            ids_all += list(ids.tolist() if torch.is_tensor(ids) else ids)
    logits = torch.cat(outs).numpy()
    probs = activate(logits, cfg)
    if ys:
        y_true = torch.cat(ys).numpy()
        m = compute_metrics(y_true, probs, cfg, score_fn=hooks.score)
    else:
        y_true, m = None, {}
    m["loss"] = losses / max(n_loss, 1) if n_loss else float("nan")
    m["sample_count"] = int(len(logits))
    if collect is not None:
        collect["logits"] = logits.astype(np.float32)
        collect["targets"] = None if y_true is None else y_true.astype(np.float32)
        collect["ids"] = ids_all if len(ids_all) == len(logits) else dataset_ids(loader.dataset)
    return m


def metrics_row(prefix: str, m: dict, round_to: int = 6) -> dict:
    """Flatten metrics for a CSV row: <prefix>_<metric> and <prefix>_<metric>_<target>."""
    row = {}
    for k, v in m.items():
        if k == "per_task":
            continue
        if isinstance(v, (int, float, np.floating, np.integer)):
            row[f"{prefix}_{k}"] = (round(float(v), round_to)
                                    if isinstance(v, (float, np.floating)) else int(v))
    for t, d in (m.get("per_task") or {}).items():
        for k in ("auroc", "auprc", "f1", "rmse", "mae", "r2", "pearson"):
            if k in d:
                row[f"{prefix}_{k}_{t}"] = round(float(d[k]), round_to)
    return row


def print_environment(cfg: dict):
    """Hardware and software this run is actually executing on."""
    import platform

    _banner("ENVIRONMENT", "\U0001F5A5\uFE0F")

    rows = [("host", platform.node()),
            ("platform", f"{platform.system()} {platform.release()}"),
            ("python", platform.python_version()),
            ("torch", torch.__version__),
            ("cuda (torch)", torch.version.cuda or "cpu build")]
    try:
        import timm
        rows.append(("timm", timm.__version__))
    except Exception:
        pass
    rows.append(("numpy / pandas", f"{np.__version__} / {pd.__version__}"))
    if cv2 is not None:
        rows.append(("opencv", cv2.__version__))
    _kv("software", rows, "\U0001F4E6")

    # ---- CPU / RAM ---------------------------------------------------------
    cpu_rows = [("logical cores", os.cpu_count())]
    try:
        import psutil
        vm = psutil.virtual_memory()
        cpu_rows += [("physical cores", psutil.cpu_count(logical=False)),
                     ("RAM total", f"{vm.total / 1024**3:.1f} GiB"),
                     ("RAM available", f"{vm.available / 1024**3:.1f} GiB")]
    except ImportError:
        cpu_rows.append(("RAM", "install psutil for memory details"))
    try:                                   # cpu.max = "quota period"; quota/period = real cores
        with open("/sys/fs/cgroup/cpu.max") as fh:
            q, per = fh.read().split()
            if q != "max":
                cpu_rows.append(("container CPU limit", f"{int(q) / int(per):.2f} cores"))
    except Exception:
        pass
    try:                                   # the cgroup limit is what Modal actually gives us
        with open("/sys/fs/cgroup/memory.max") as fh:
            v = fh.read().strip()
            if v.isdigit():
                cpu_rows.append(("container RAM limit", f"{int(v) / 1024**3:.1f} GiB"))
    except Exception:
        pass
    _kv("cpu / memory", cpu_rows, "\U0001F9EE")

    # ---- GPU ---------------------------------------------------------------
    if torch.cuda.is_available():
        rows = []
        for i in range(torch.cuda.device_count()):
            d = torch.cuda.get_device_properties(i)
            rows.append([i, d.name, f"{d.total_memory / 1024**3:.1f} GiB",
                         f"{d.major}.{d.minor}", d.multi_processor_count])
        _table("gpu", ["#", "device", "memory", "capability", "SMs"], rows,
               "\U0001F3AE")
        print(f"  cudnn benchmark={torch.backends.cudnn.benchmark}  "
              f"tf32_matmul={torch.backends.cuda.matmul.allow_tf32}  "
              f"tf32_cudnn={torch.backends.cudnn.allow_tf32}")
    else:
        _kv("gpu", [("available", "NO - running on CPU")], "\U0001F3AE")


def set_lp_ft_phase(cfg: dict, model: nn.Module, epoch: int) -> None:
    """LP-FT: freeze the backbone for the first N epochs, then unfreeze it.

    LP-FT is Linear Probing then Fine-Tuning. Phase 1 trains ONLY the head on frozen
    features; phase 2 unfreezes everything and fine-tunes normally.

    WHY IT EXISTS HERE. Kumar et al., ICLR 2022 (arXiv 2202.10054) show that when the
    pretrained features are good and the domain shift is large, fine-tuning from a
    RANDOMLY INITIALISED head is worse than a frozen linear probe: the head is still noise
    while it back-propagates into the trunk, so the first updates destroy the very features
    that made the backbone worth choosing. Their fix is to let the head converge first.

    Typical sign: a backbone whose FROZEN features probe well fine-tunes worse end-to-end
    (large domain shift, e.g. web photos to medical scans). Off by default.

        training:
          lp_ft_epochs: 1      # epochs 1..N train the head alone, N+1 onward everything

    The optimizer keeps both param groups throughout; freezing is done with requires_grad,
    so the backbone's AdamW moments stay intact across the switch and the lr schedule is
    untouched. Frozen parameters also skip their backward pass, so phase 1 is cheaper.
    """
    n = int(cfg.get("training", {}).get("lp_ft_epochs") or 0)
    if n <= 0:
        return
    bb = getattr(_uncompiled(model), "backbone", None)
    if bb is None:
        print("  ⚠️  lp_ft_epochs set but the model has no .backbone - ignored")
        return
    freeze = epoch <= n
    already = not next(bb.parameters()).requires_grad
    if freeze == already and epoch != 1:
        return                                   # nothing to change this epoch
    for p in bb.parameters():
        p.requires_grad_(not freeze)
    n_bb = sum(p.numel() for p in bb.parameters()) / 1e6
    if freeze:
        print(f"  \U0001F9CA LP-FT phase 1: backbone FROZEN ({n_bb:.1f}M params), head only "
              f"- epochs 1..{n}")
    else:
        print(f"  \U0001F525 LP-FT phase 2: backbone UNFROZEN ({n_bb:.1f}M params) from "
              f"epoch {epoch}")

def check_normalization(cfg: dict, model: nn.Module) -> None:
    """Fail fast when the config's pixel normalisation contradicts the backbone's own.

    Every pretrained backbone was trained on pixels scaled a particular way, and it expects
    the same scaling at fine-tune time. Getting this wrong is SILENT: the run trains, the
    loss falls, and the model is simply worse than it should be.

    timm records the right values on each model's `pretrained_cfg`, so this compares
    input.norm_mean / input.norm_std against the backbone and refuses to start on a
    mismatch. No input.norm_* keys in the config = no check.

    To deviate DELIBERATELY (weights loaded from elsewhere, say) set:

        input:
          norm_mismatch_ok: true   # and say WHY in a comment

    Only the backbone is inspected. A model with no timm backbone is skipped silently.
    """
    inp = cfg.get("input", {})
    want_m, want_s = inp.get("norm_mean"), inp.get("norm_std")
    if want_m is None or want_s is None:
        return
    # A run that loads its OWN weights (model.weights) uses the timm entry only as an
    # empty skeleton, so its pretrained_cfg describes weights that are not in the model.
    if cfg.get("model", {}).get("weights"):
        print(f"[norm] skipped: model.weights={cfg['model']['weights']!r} replaces the timm "
              f"weights, so its pretrained_cfg does not describe this trunk. "
              f"Using config mean {list(want_m)}, std {list(want_s)}.")
        return
    # the backbone may be nested (model.backbone) or be the model itself
    for m in (getattr(_uncompiled(model), "backbone", None), _uncompiled(model)):
        pcfg = getattr(m, "pretrained_cfg", None)
        if isinstance(pcfg, dict) and pcfg.get("mean") and pcfg.get("std"):
            break
    else:
        return
    got_m, got_s = list(pcfg["mean"]), list(pcfg["std"])
    close = (len(got_m) == len(want_m[:len(got_m)])
             and all(abs(a - b) < 1e-3 for a, b in zip(got_m, want_m))
             and all(abs(a - b) < 1e-3 for a, b in zip(got_s, want_s)))
    name = cfg.get("model", {}).get("name", "?")
    if close:
        print(f"[norm] OK: config matches {name}'s pretrained_cfg "
              f"(mean {got_m}, std {got_s})")
        return
    msg = (f"normalisation mismatch for backbone {name!r}:\n"
           f"    config    mean {list(want_m)}  std {list(want_s)}\n"
           f"    backbone  mean {got_m}  std {got_s}\n"
           f"  The backbone was pretrained on the second pair. Training on the first is a "
           f"SILENT error:\n"
           f"  the run will converge and simply score worse.\n"
           f"  Fix input.norm_mean / input.norm_std, or set input.norm_mismatch_ok: true "
           f"if the deviation\n"
           f"  is deliberate (say why in a comment).")
    if inp.get("norm_mismatch_ok"):
        print(f"[norm] DELIBERATE MISMATCH, allowed by input.norm_mismatch_ok\n  {msg}")
        return
    raise SystemExit("[norm] " + msg)


def check_grad_clip(cfg: dict):
    """Warn when grad_clip sits below training.grad_clip_floor (0 = no check).

    Clipping rescales every update whose gradient norm exceeds the cap, so a low cap
    silently throttles the effective learning rate below the one the config advertises.
    Watch the clip_pct column of train_log.csv; the run also warns live when > 50% clip.
    """
    g = cfg["training"].get("grad_clip")
    floor = float(cfg["training"].get("grad_clip_floor") or 0)
    if g and floor and float(g) < floor:
        print(f"  ⚠️  grad_clip {g} is below the configured floor {floor}: a low cap throttles "
              f"the effective lr. Check clip_pct in train_log.csv.")


def run_experiment(cfg: dict, model: nn.Module, out_dir, data: dict, hooks: Hooks | None = None,
                   persist_fn=None, log_fn=None):
    """Public entry: tee the whole console into results/train_config/<run_id>_<stamp>.txt,
    then train. Streams are restored even if the run crashes, traceback included.

    cfg      config (load_config output; defaults are filled in if missing)
    model    nn.Module producing num_outputs(cfg) logits per sample
    out_dir  the run folder; results land in out_dir/<output.run_dir>
    data     {"train": Dataset|DataLoader, "val": ..., any other split: report-only eval}
    hooks    Hooks overrides (forward / loss / prepare / score / callbacks)
    persist_fn  called to flush outputs (Modal: runs_volume.commit)
    log_fn   log_fn(dict, step), e.g. wandb
    Returns the best monitored score.
    """
    cfg = with_defaults(cfg)
    out_dir = Path(out_dir)
    res_dir = out_dir / cfg["output"]["run_dir"]
    exp = cfg.setdefault("experiment", {})
    exp["name"] = exp.get("name") or out_dir.name
    # normally allocated on the launching PC and passed in; only a bare local run gets here
    exp["run_id"] = exp.get("run_id") or allocate_run_id(res_dir)
    cap_dir = res_dir / cfg["output"].get("console_capture_dir", "train_config")
    cap_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    cap_path = cap_dir / f"{exp['run_id']}_{stamp}.txt"
    try:
        sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    orig_out, orig_err = sys.stdout, sys.stderr
    log_f = open(cap_path, "a", encoding="utf-8")
    sys.stdout, sys.stderr = _Tee(orig_out, log_f), _Tee(orig_err, log_f)
    print(f"[capture] full console of this run -> {cap_path}")
    print(f"[capture] run_id: {exp['run_id']}  side: {runtime_side()}")
    print(f"[capture] command: {' '.join(sys.argv)}")
    print(f"[capture] started {datetime.now():%Y-%m-%d %H:%M:%S}")
    try:
        return _run_experiment(cfg, model, out_dir, data, hooks or Hooks(), persist_fn, log_fn)
    finally:
        sys.stdout, sys.stderr = orig_out, orig_err
        log_f.close()
        print(f"[capture] saved -> {cap_path}")


def _print_eval(tag: str, epoch: int, epochs: int, gstep: int, m: dict,
                elapsed: float, eta: float, emoji: str = "\U0001F50E",
                prev: dict | None = None, took: float | None = None,
                per_target: bool = True):
    """One validation block: loss, every scalar metric (with its delta), then every target.

    `prev` is this split's metrics from the last time IT was scored, so the deltas
    compare like with like. `took` is how long this pass alone ran.
    """
    def d(key):
        if not prev or key not in prev or not isinstance(prev[key], (int, float)):
            return ""
        return f" ({m[key] - prev[key]:+.4f})"

    t_str = "" if took is None else f"  ⏱️ took={fmt(took)}"
    print("-" * 70)
    print(f"  {emoji} [{tag}] epoch={epoch}/{epochs} step={gstep}  n={m['sample_count']}  "
          f"loss={m['loss']:.4f}{d('loss')}{t_str}  elapsed={fmt(elapsed)}  ETA={fmt(eta)}")
    keys = [k for k, v in m.items() if k not in ("loss", "sample_count", "per_task")
            and isinstance(v, (int, float))]
    for i in range(0, len(keys), 4):           # four metrics per line
        print("     📊 " + "  ".join(f"{k}={m[k]:.4f}{d(k)}" for k in keys[i:i + 4]))
    if per_target and m.get("per_task"):
        for t, v in m["per_task"].items():
            # a target with no positives in the split has no defined AUROC/AUPRC (n/a)
            bits = [f"{k.upper() if k in ('auroc', 'auprc', 'rmse', 'mae') else k}="
                    + ("   n/a" if x != x else f"{x:.4f}")
                    for k, x in v.items() if k not in ("pos", "threshold") and isinstance(x, float)]
            pos = f"  (n={v['pos']})" if "pos" in v else ""
            print(f"        {str(t)[:22]:22s} " + "  ".join(bits[:6]) + pos)


class AsyncPersist:
    """Flush the Modal volume off the training thread.

    volume.commit() is a blocking network flush. Called inline every N steps it stalls
    the GPU for its whole duration - visible on the Modal dashboard as utilisation
    dropping to zero on exactly the commit period. The data is already written to the
    container filesystem by then; commit only publishes it, so nothing is lost by
    doing it slightly later.

    One worker at a time: if a commit is still running when the next is due, skip it
    rather than queue - the next one publishes the same files plus more. Overlapping
    commits are also what the volume API is least happy about.
    """

    def __init__(self, fn):
        self.fn, self.thread, self.skipped, self.done = fn, None, 0, 0
        self.last_error = None

    def __call__(self, blocking: bool = False):
        if self.fn is None:
            return
        if blocking:
            self.join()
            self._run()
            return
        if self.thread is not None and self.thread.is_alive():
            self.skipped += 1                  # a flush is already in flight
            return
        import threading
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        try:
            self.fn()
            self.done += 1
        except Exception as e:                 # a failed flush must not kill training
            self.last_error = f"{type(e).__name__}: {e}"

    def join(self, timeout: float = 300.0):
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout)


def _run_experiment(cfg: dict, model: nn.Module, out_dir: Path, data: dict, hooks: Hooks,
                    persist_fn=None, log_fn=None):
    """Full training run: loaders, loss, optimizer, epoch loop, eval, checkpoints, logs."""
    P = cfg["logging"]["print"]
    LG = cfg["logging"]
    persist = AsyncPersist(persist_fn)         # volume flushes, off the training thread
    saver = AsyncSaver(cfg["output"].get("async_checkpoints", True))
    global _UPLOADER
    _UPLOADER = None
    if cfg["output"].get("upload_checkpoints"):
        _o = cfg["output"]
        _UPLOADER = CheckpointUploader(
            _o["upload_checkpoints"], cfg["experiment"]["name"], Path(out_dir) / _o["run_dir"],
            f"{_o['run_dir']}/{_o['checkpoints_dir']}", cfg["modal"]["runs_volume"])
    device = pick_device(cfg)
    epochs = int(cfg["training"]["epochs"])
    run_id = cfg["experiment"].get("run_id") or ""
    print("#" * 70)
    print(f"# 🚀 run_experiment: {cfg['experiment']['name']}")
    print(f"# 🆔 run_id={run_id}  side={runtime_side()}  task={task_type(cfg)}")
    print(f"# \U0001F5A5️  device={device}  epochs={epochs}")
    print("#" * 70)
    set_seed(cfg["reproducibility"]["seed"], cfg["reproducibility"]["deterministic"])
    print(f"[set_seed] seed={cfg['reproducibility']['seed']}  "
          f"deterministic={cfg['reproducibility']['deterministic']}")
    if P.get("environment", True):
        print_environment(cfg)
    if P.get("config", True):
        print_config(cfg)
    check_normalization(cfg, model)
    check_grad_clip(cfg)

    out = Path(out_dir) / cfg["output"]["run_dir"]
    ckpt_dir = out / cfg["output"]["checkpoints_dir"]
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    print(f"[paths] results -> {out}")
    # every file this run writes carries its run_id as a prefix, so nothing collides
    cap_dir = out / cfg["output"].get("console_capture_dir", "train_config")
    cap_dir.mkdir(parents=True, exist_ok=True)
    save_config(cfg, cap_dir / f"{run_id}_config.yaml")

    loaders = build_loaders(cfg, data)
    if "val" not in loaders and cfg["evaluation"].get("enable", True):
        print("  ⚠️  no 'val' split: evaluation.enable forced off (best = latest)")
        cfg["evaluation"]["enable"] = False
    extra_splits = [k for k in loaders if k not in ("train", "val")]
    if P.get("data", True):
        print_data_summary(loaders, cfg)
    train_targets = dataset_targets(loaders["train"].dataset, cfg)

    model = model.to(device)
    if cfg["training"]["channels_last"]:
        # channels_last is a RANK-4 layout (N, C, H, W). Conv3d weights are rank 5, and torch
        # raises on them rather than skipping, so a 3-D model gets the rank-5 layout instead.
        _has5d = any(p_.ndim == 5 for p_ in model.parameters())
        _fmt = torch.channels_last_3d if _has5d else torch.channels_last
        model = model.to(memory_format=_fmt)
        if _has5d:
            print("  🧊 channels_last_3d (the model has rank-5 conv weights)")
    # Trade compute for VRAM: don't keep intermediate activations, recompute them in the
    # backward pass. Roughly 30-40% slower per step, far less activation memory. timm
    # exposes this on the backbone; a plain nn.Module may not have it at all.
    if cfg["training"].get("grad_checkpointing"):
        _bb = getattr(model, "backbone", model)
        if hasattr(_bb, "set_grad_checkpointing"):
            _bb.set_grad_checkpointing(True)
            print("  🧮 gradient checkpointing ON (slower steps, far less VRAM)")
        elif hasattr(_bb, "gradient_checkpointing_enable"):      # HuggingFace
            _bb.gradient_checkpointing_enable()
            print("  🧮 gradient checkpointing ON (HF)")
        else:
            print(f"  ⚠️  grad_checkpointing requested but {type(_bb).__name__} "
                  f"has no set_grad_checkpointing - ignored")
    if cfg["training"].get("backbone_chunk"):
        chunk_backbone(model, int(cfg["training"]["backbone_chunk"]))
    tot_p = sum(q.numel() for q in model.parameters())
    tr_p = sum(q.numel() for q in model.parameters() if q.requires_grad)
    if P.get("model", True):
        _banner("MODEL", "\U0001F9E0")
        mc = cfg.get("model", {}) or {}
        _kv("architecture", [
            ("class", type(model).__name__),
            ("name", mc.get("name", "-")),
            ("pretrained", mc.get("pretrained", "-")),
            ("has .backbone", hasattr(model, "backbone")),
            ("output logits", f"{num_outputs(cfg)}  ({task_type(cfg)})"),
            None,
            ("total params", f"{tot_p:,}  ({tot_p/1e6:.2f} M)"),
            ("trainable", f"{tr_p:,}  ({tr_p/1e6:.2f} M, {100*tr_p/max(tot_p,1):.1f}%)"),
            ("frozen", f"{tot_p-tr_p:,}  ({(tot_p-tr_p)/1e6:.2f} M)"),
            ("param memory", f"{sum(q.numel() * q.element_size() for q in model.parameters()) / 1024**2:.1f} MB"),
        ], "\U0001F9F1")

    loss_fn = build_loss(cfg, train_targets, device) if hooks.loss is None else None
    opt = build_optimizer(model, cfg, verbose=P.get("lr_groups", True))
    # Which groups are the pretrained trunk? Structural, not by name: everything under
    # .backbone is the trunk, the rest is the freshly initialised head. Computed once,
    # because param_groups never change shape after this.
    _bb_pids = {id(p) for n, p in model.named_parameters() if n.startswith("backbone.")}
    _grp_is_bb = [any(id(p) in _bb_pids for p in g["params"]) for g in opt.param_groups]
    accum = accum_steps(cfg)
    # CEIL, not floor: the epoch's last, partial accumulation window is stepped (rescaled to
    # its real size in the loop), exactly like the partial last batch of an accum-1 run.
    n_micro = len(loaders["train"])
    steps_per_epoch = max(1, -(-n_micro // accum))
    total = steps_per_epoch * epochs
    sched = build_scheduler(opt, cfg, total, steps_per_epoch)
    warm = warmup_steps(cfg, total)
    if device.type == "cuda" and cfg["training"].get("tf32", True):
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    ema = None
    _emc = cfg["training"].get("ema") or {}
    if _emc.get("enable"):
        ema = ModelEMA(model, _emc.get("decay", 0.999), _emc.get("warmup", True))
        print(f"  🌗 EMA on: decay={ema.decay}  warmup={ema.warmup}  "
              f"validate with EMA={bool(_emc.get('eval', True))}")
    if cfg["training"].get("compile", False):
        try:
            model = torch.compile(model, mode=cfg["training"].get("compile_mode", "default"))
            print(f"  ⚡ torch.compile enabled (mode={cfg['training'].get('compile_mode', 'default')})")
        except Exception as e:
            print(f"  [warn] torch.compile failed: {type(e).__name__}: {e}")
    use_amp_train = cfg["training"]["amp"] and device.type == "cuda"
    # bf16 has fp32's exponent range: no loss scaling needed; fp16 keeps its scaler
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp_train and amp_dtype(cfg) == torch.float16)
    unit = LG.get("sub_unit") or LG.get("unit") or "sample"
    per_sample = int(LG.get("sub_units_per_sample") or 1) if LG.get("sub_unit") else 1
    diag_every = int(LG.get("diagnostics_every") or 0)
    # "is every layer actually moving?" separates a frozen or throttled trunk from a merely
    # unlucky one - the loss curve shows them as the same thing
    ud = UDRatio(model, diag_every)
    if diag_every:
        print(f"  📏 update/weight ratio logging: {len(ud.params)} weight tensors, "
              f"every {ud.every} steps -> ud_ratio.csv")
    probe = ScaleProbe(model, diag_every)
    if probe.handle is not None and diag_every:
        print(f"  \U0001F4CF feature/logit scale probe on {probe.head_name!r}, "
              f"every {probe.every} steps")

    print(f"[setup] optimizer={cfg['training']['optimizer']['name']}  "
          f"scheduler={cfg['training']['scheduler']['name']}  amp={use_amp_train} "
          f"({str(amp_dtype(cfg)).replace('torch.', '') if use_amp_train else 'fp32'})  "
          f"grad scaler={scaler.is_enabled()}")
    print(f"[setup] steps/epoch={steps_per_epoch}  total_steps={total}  accum={accum}  "
          f"{unit}s/optimizer-step={train_batch_size(cfg) * accum * per_sample}")
    _vbs, _vnw = val_loader_settings(cfg)
    print(f"[setup] loss={cfg['training']['loss']['name'] if hooks.loss is None else 'hooks.loss'}  "
          f"train bs={train_batch_size(cfg)}/{cfg['dataloader'].get('num_workers', 4)}w  "
          f"val bs={_vbs}/{_vnw}w  monitor={'val_' + monitor_spec(cfg)[0]} ({monitor_spec(cfg)[1]})  "
          f"eval={_eval_cadence_str(cfg)}")

    _mon, _mode = monitor_spec(cfg)
    es = cfg["training"].get("early_stopping", {}) or {}
    es = {"enable": es.get("enable", True), "monitor": "val_" + _mon, "mode": _mode,
          "patience": int(es.get("patience", 5)),
          "reset_tag": es.get("reset_tag")}       # one-time reset when the monitored metric changed meaning
    _worst = -math.inf if _mode == "max" else math.inf

    def _better(a, b):
        return a > b if _mode == "max" else a < b

    best, best_epoch, bad, gstep = _worst, 0, 0, 0
    start_epoch, top_k_track = 1, []
    # declared up here because the resume block below restores into them
    extra_best = {}               # {split: [score, epoch, bad]} - report-only splits, never drive best.pt
    prev_eval = {}                # each split's last metrics, for the printed deltas
    ext_state = {}                # the extension in progress, so a CRASH mid-extension
                                  # resumes the SAME one instead of starting another
    units_done = [0]              # samples (or sub-units) trained on, across resumes
    ck = load_checkpoint(cfg.get("resume"), model, ckpt_dir, opt, sched, scaler, device,
                         cfg_now=cfg, ema=ema)
    # WARM START. Only when this run has nothing of its own: a preempted container must
    # resume ITS progress, not jump back to the donor and lose the epochs in between.
    _init = (cfg.get("model") or {}).get("init_from")
    if _init and not ck:
        _src = resolve_init_from(_init, out_dir, cfg)
        _dck = torch.load(_src, map_location="cpu", weights_only=False)
        _sd = _dck.get("model", _dck)
        _res = _load_model_state(
            model, _sd,
            allow_head_mismatch=bool((cfg.get("model") or {}).get("init_from_allow_head")))
        _miss = list(getattr(_res, "missing_keys", []) or [])
        _unex = list(getattr(_res, "unexpected_keys", []) or [])
        print("\n  \U0001F331 WARM START from %s" % _src)
        print("       donor: step %s  epoch %s  score %s"
              % (_dck.get("global_step") or _dck.get("step"), _dck.get("epoch"),
                 _dck.get("score")))
        print("       %d tensor(s) loaded, %d missing, %d unexpected"
              % (len(_sd) - len(_unex), len(_miss), len(_unex)))
        print("       WEIGHTS ONLY: optimizer, scheduler and the step counter stay fresh, "
              "so warmup and the whole lr schedule run again")
        if _miss or _unex:
            # A silent partial load is how a half-random model trains for an hour and looks
            # completely normal doing it.
            raise RuntimeError(
                "warm start is incomplete: %d missing %s, %d unexpected %s. Set "
                "model.init_from_allow_head if only the head should differ."
                % (len(_miss), _miss[:6], len(_unex), _unex[:6]))
        if ema is not None:
            ema.reset(model)

    # A checkpoint outlives the config that produced it. `resume: "last"` is the right
    # default (preemption must not restart the run), but it means editing a setting and
    # relaunching SILENTLY continues the old run under the new label - the two halves
    # trained under different settings and the result describes neither. Preemption
    # replays the SAME config, so it never trips this; `extend` is exempt by design.
    if ck and not (cfg["training"].get("extend") or {}).get("enable"):
        _ocfg = ck.get("cfg") or {}
        _diff = []
        for key in cfg.get("resume_guard") or []:
            o_, n_ = cfg_get(_ocfg, key, "<absent>"), cfg_get(cfg, key, "<absent>")
            if o_ != n_ and o_ != "<absent>":
                _diff.append((key, o_, n_))
        if _diff:
            _w = max(len(l) for l, _, _ in _diff)
            _lines = "\n".join(f"      {l:<{_w}}  checkpoint={o!r}  ->  config={n!r}"
                                 for l, o, n in _diff)
            if cfg.get("resume_force"):
                print(f"\n  ⚠️  RESUMING ACROSS A CONFIG CHANGE (resume_force is set):"
                      f"\n{_lines}\n"
                      f"      The run trains part of itself under each. The result is not "
                      f"attributable to either config.\n")
            else:
                raise RuntimeError(
                    f"refusing to resume: this checkpoint (step {ck.get('step')}) was "
                    f"written under a different config.\n{_lines}\n\n"
                    f"    Continuing would train one half of the run under each setting, "
                    f"so the result would describe neither.\n"
                    f"    Pick one:\n"
                    f"      * start clean - delete {ckpt_dir} (on Modal: the run's results/ "
                    f"on the '{cfg['modal']['runs_volume']}' volume) or set resume: null\n"
                    f"      * continue the OLD run on a new lr curve - set "
                    f"training.extend.enable\n"
                    f"      * you really do mean it - set resume_force: true in the config")

    resumed_elapsed, history, resume_skip = 0.0, [], 0
    if ck:
        gstep = int(ck.get("step") or 0)
        ck_epoch = int(ck.get("epoch") or 0)
        tr = ck.get("track") or {}
        best = tr.get("best", _worst)
        best_epoch = tr.get("best_epoch", 0)
        bad = int(tr.get("bad", 0))               # keep counting toward patience
        top_k_track = tr.get("top_k", [])
        history = list(tr.get("history", []))     # so the final summary sees the whole run
        extra_best.update(tr.get("extra_best", {}) or {})
        prev_eval.update(tr.get("prev_eval", {}))  # deltas survive a resume
        ext_state.update(tr.get("extend", {}) or {})
        units_done[0] = int(tr.get("units_done", 0))
        resumed_elapsed = float(ck.get("elapsed_sec") or 0.0)
        if ck.get("epoch_complete", True):
            start_epoch = ck_epoch + 1
        else:
            # mid-epoch: skip the samples this epoch already trained on. Derived from
            # gstep, not a stored counter, so the skip always lands on an accumulation
            # boundary. ResumableSampler makes the epoch's order reproducible.
            start_epoch = ck_epoch
            done = gstep - (ck_epoch - 1) * steps_per_epoch
            resume_skip = max(0, done) * accum          # in micro-batches
            print(f"  ↩️  mid-epoch resume: epoch {ck_epoch} continues at "
                  f"optimizer step {done}/{steps_per_epoch} "
                  f"({resume_skip} micro-batches skipped)")
        print(f"  ↩️  restored: best={best:.4f} @ epoch {best_epoch}  "
              f"patience={bad}/{es['patience']}  top_k={len(top_k_track)}  "
              f"elapsed={fmt(resumed_elapsed)}")

        # early_stopping.reset_tag: the MONITORED METRIC changed meaning (val re-labelled,
        # a different metric). The stored best could never be beaten, so patience would
        # run out on a different metric. A new tag resets best/patience/top-k ONCE; the tag
        # is saved, so later resumes of the same tag keep counting normally.
        _rt = es.get("reset_tag")
        if _rt and tr.get("es_tag") != _rt:
            print(f"  🔄 early stopping reset for metric tag {_rt!r} (was {tr.get('es_tag')!r}): best {best:.4f} and "
                  f"patience {bad} dropped, top-k list cleared")
            best, best_epoch, bad, top_k_track = _worst, 0, 0, []

    # ---- extend: carry a FINISHED run on under a fresh lr curve ---------------
    # A plain resume restores the cosine schedule the checkpoint stopped under. Once
    # that schedule has run to its end the lr sits at min_lr_mult (1% of base), so
    # "resume" would technically continue and effectively train on nothing. `extend`
    # keeps the weights and the AdamW moments but hands the optimizer a NEW cosine
    # over the extra epochs, at a new peak lr - the cheap way to give a run that was
    # still improving at its last step more room, without paying for it from scratch.
    ext = cfg["training"].get("extend") or {}
    if ext.get("enable"):
        if not ck:
            raise RuntimeError("training.extend.enable is set but no checkpoint was "
                               "loaded - there is nothing to extend. Check `resume`.")
        extra = int(ext.get("epochs") or 0)
        if extra < 1:
            raise ValueError("training.extend.enable is set but extend.epochs < 1")

        # An extension that is ALREADY under way must not start a second one. Without
        # this, a crash at epoch 13 of an 11->16 extension would resume, read epoch 13
        # as the new baseline, and extend to 19 - on a fresh lr curve back at its peak,
        # every time it crashed. The extension's identity is stored in the checkpoint,
        # so `continuing` means "carry the SAME curve on from where it stopped".
        continuing = bool(ext_state)
        if continuing:
            base_epoch = int(ext_state["base_epoch"])
            extra = int(ext_state["epochs"])          # the config cannot move the goalposts
        else:
            base_epoch = int(ck.get("epoch") or 0)
        epochs = base_epoch + extra           # keep epoch numbering continuous in the logs
        ext_start = base_epoch * steps_per_epoch      # first step OF the extension
        done_epochs = int(ck.get("epoch") or 0)
        start_epoch = done_epochs + 1
        resume_skip = 0                       # the last epoch finished; start a clean one
        if not ck.get("epoch_complete", True):
            # crashed mid-epoch: fall back on the same skip the normal resume path uses
            start_epoch = done_epochs
            resume_skip = max(0, gstep - (done_epochs - 1) * steps_per_epoch) * accum

        ecfg = json.loads(json.dumps(cfg))    # private copy - only the schedule differs
        if ext.get("warmup_frac") is not None:
            ecfg["training"]["scheduler"]["warmup_frac"] = float(ext["warmup_frac"])
        # An extension is short, so the run's usual 1% floor spends most of it at a lr that
        # cannot move anything. Raising the floor keeps the extra epochs actually training.
        if ext.get("min_lr_mult") is not None:
            ecfg["training"]["scheduler"]["min_lr_mult"] = float(ext["min_lr_mult"])
        ext_total = steps_per_epoch * extra

        base_lr = float(cfg["training"]["optimizer"]["lr"])
        new_lr = ext_state.get("lr") if continuing else ext.get("lr")
        # `not continuing` matters. The ratio rescales initial_lr IN PLACE, and on a
        # resume the optimizer state already comes back holding the extension's lr - so
        # re-applying it multiplies the cut in a second time. A 5e-5 -> 2.5e-6 extension
        # returned at 1.25e-7 after one hand-off, 20x under its own floor, and the run
        # went flat while looking like it was training. Silent, and this repo hands off
        # constantly. On a resume the restored optimizer is already correct.
        if new_lr and not continuing:
            # scale every group by the same ratio, so whatever split build_optimizer
            # made (backbone_lr_mult, layer_decay) survives untouched
            ratio = float(new_lr) / base_lr
            for g in opt.param_groups:
                g["initial_lr"] = g.get("initial_lr", g["lr"]) * ratio
                g["lr"] = g["initial_lr"]
        if ext.get("reset_optimizer"):
            opt.state.clear()                 # throw away the AdamW moments too
        # fresh LambdaLR: last_epoch back to -1, so the new cosine starts at its peak
        sched = build_scheduler(opt, ecfg, ext_total, steps_per_epoch)
        warm = warmup_steps(ecfg, ext_total)
        into = max(0, gstep - ext_start)      # steps already spent inside the extension
        for _ in range(into):
            sched.step()                      # fast-forward onto the SAME point of the curve
        total = ext_start + ext_total         # keeps ETA and the "x of total" prints honest
        if ext.get("reset_patience", True) and not continuing:
            bad = 0                           # only once, at the start of the extension
            for _eb in extra_best.values():
                _eb[2] = 0
        ext_state.update({"base_epoch": base_epoch, "epochs": extra, "lr": new_lr})

        # initial_lr, not lr: the fresh schedule sits at warmup step 0, where lr is 0
        _lrs = ", ".join(f"{g.get('initial_lr', g['lr']):.2e}" for g in opt.param_groups)
        _pat = ("reset to 0" if (ext.get("reset_patience", True) and not continuing)
                else f"kept at {bad}")   # reset only fires on a NEW extension
        _opt = "RESET" if ext.get("reset_optimizer") else "moments kept"
        _wf = ecfg["training"]["scheduler"].get("warmup_frac", 0.05)
        _banner("CONTINUING AN EXTENSION" if continuing else "EXTENDING A FINISHED RUN",
                "🔁")
        print(f"  from       : epoch {done_epochs}, step {gstep}, best {best:.4f}")
        if continuing:
            print(f"  ↩️  already {into}/{ext_total} steps into the extension that "
                  f"started at epoch {base_epoch} - same curve, NOT a new one")
        print(f"  adding     : {extra} epochs = {ext_total} steps "
              f"(epochs {start_epoch}-{epochs}, steps {gstep + 1}-{total})")
        print(f"  peak lr    : {_lrs}   (base was {base_lr:.2e}"
              + (f", now {float(new_lr):.2e})" if new_lr else ", unchanged)"))
        print(f"  warmup     : {warm} steps ({_wf:.0%} of the extension)")
        print(f"  optimizer  : {_opt}")
        print(f"  patience   : {_pat}")
    train_log = CSVLogger(out / cfg["output"]["train_log_csv"], run_id)
    val_log = CSVLogger(out / cfg["output"]["val_log_csv"], run_id)
    t0 = time.time() - resumed_elapsed            # ETA/elapsed span the whole run
    prev_loss = None

    last_val_step = -1
    score, improved = _worst, False
    # Chronic gradient clipping is silent and it costs real learning rate: a model whose
    # gnorm sits above grad_clip gets every update rescaled, so the lr in the config stops
    # being the lr the model actually sees. Counted here and warned about below.
    clip_seen, clip_hit, clip_warned = [0], [0], [False]
    clip_vals = deque(maxlen=4000)     # finite gnorms, for the distribution below
    # training.sam: {enable, rho, adaptive}. SAM = 2 forward/backward per step (~2x step cost).
    _sam = (cfg.get("training", {}).get("sam") or {})
    _sam_on = bool(_sam.get("enable"))
    _sam_rho = float(_sam.get("rho", 0.05))
    _sam_ad = bool(_sam.get("adaptive", False))      # ASAM (Kwon 2021): rho usually ~10x larger, e.g. 0.5
    sam_gn, sam_loss2 = deque(maxlen=200), deque(maxlen=200)
    if _sam_on:
        assert accum == 1, "training.sam needs accum_steps 1 (the second pass reuses the one batch)"
        print(f"  ⛰️  SAM {'(adaptive) ' if _sam_ad else ''}rho={_sam_rho}: 2 passes per step")

    stop_now = [False]            # raised the moment patience runs out, so the step
                                  # loop stops AT patience, not at the next epoch boundary
    eval_model = (lambda: ema.module if (ema is not None and _emc.get("eval", True)) else model)

    def _track():
        """Everything a resume needs that is not weights. ONE definition, shared by every
        checkpoint kind, so nothing is lost when a run resumes from a step*.pt."""
        return {"best": best, "best_epoch": best_epoch, "bad": bad,
                "top_k": top_k_track, "history": history,
                "extra_best": dict(extra_best), "units_done": units_done[0],
                "prev_eval": dict(prev_eval), "extend": dict(ext_state),
                "es_tag": es.get("reset_tag")}

    def _write_summary(epoch, row):
        summary_path = out / cfg["output"]["summary_json"]
        summary = json.dumps(_json_safe({
            "experiment": cfg["experiment"]["name"], "run_id": run_id,
            "task": task_type(cfg), "epoch": epoch, "epochs": epochs, "global_step": gstep,
            "best_score": best, "best_epoch": best_epoch, "monitor": es["monitor"],
            "mode": es["mode"], "hardware": hardware_info(cfg),
            "last": row, "elapsed": fmt(time.time() - t0),
            # always last, always null until a human fills it in after submitting.
            # carried over on every rewrite so a filled-in record survives a resume.
            "submission": carried_submission(summary_path)}), indent=2)
        summary_path.write_text(summary)
        # a per-run copy too, so a sync can carry it without clobbering the other side
        (cap_dir / f"{run_id}_summary.json").write_text(summary)

    def _validate_and_checkpoint(epoch: int, gstep: int, tag: str = "epoch"):
        """Score val (and any report-only split), log, checkpoint, update early stopping."""
        nonlocal best, best_epoch, bad, top_k_track, last_val_step
        nonlocal score, improved
        if gstep == last_val_step:            # a step-trigger already covered this step
            return None
        last_val_step = gstep
        el = time.time() - t0
        eta = el * (total / max(gstep, 1) - 1)
        done = (tag == "epoch")          # mid-epoch checkpoints must replay their epoch

        # NO HELD-OUT SET: evaluation.enable false (or no "val" split). A score on training
        # data climbs whatever the model does, so skip evaluation and keep the
        # checkpointing. "Best" can only mean LATEST: the score is the step counter.
        if not cfg["evaluation"].get("enable", True):
            score, improved = float(gstep), True
            best, best_epoch, bad = score, epoch, 0
            top_k_track = update_top_k(ckpt_dir, cfg, model, epoch, gstep, score,
                                       top_k_track, cfg["output"].get("keep_top_k", 0),
                                       cfg["output"].get("top_k_weights_only", True),
                                       saver=saver, mode="max", ema=ema)
            save_checkpoint(ckpt_dir / cfg["output"]["best_name"], cfg, model, opt, sched,
                            scaler, epoch, gstep, score, track=_track(), device=device,
                            elapsed_sec=el, epoch_complete=done, saver=saver,
                            loss_fn=loss_fn, ema=ema, note="")
            ud.dump(out / "ud_ratio.csv")
            save_checkpoint(ckpt_dir / "last.pt", cfg, model, opt, sched, scaler, epoch,
                            gstep, score, track=_track(), device=device, loss_fn=loss_fn,
                            elapsed_sec=el, epoch_complete=done, saver=saver, ema=ema, note="")
            print("  \U0001F4BE checkpoint at epoch %d step %d (%s) - no validation, best = latest"
                  % (epoch, gstep, tag))
            _write_summary(epoch, {"epoch": epoch, "step": gstep, "trigger": tag})
            persist()
            model.train()
            return None

        em = eval_model()
        print("=" * 70)
        print(f"\U0001F50E VALIDATION ({tag}) - epoch {epoch}/{epochs}  step {gstep}  "
              f"({len(loaders['val'])} batches, {len(loaders['val'].dataset)} {LG.get('unit', 'sample')}s)"
              + ("  [EMA weights]" if em is not model else "") + " ...")
        _t = time.time()
        packs = {"val": {}}
        vm = evaluate(em, loaders["val"], loss_fn, cfg, device, hooks, collect=packs["val"])
        val_secs = time.time() - _t
        _print_eval("VAL", epoch, epochs, gstep, vm, el, eta,
                    prev=prev_eval.get("val"), took=val_secs,
                    per_target=P.get("per_target_eval", True))
        prev_eval["val"] = {k: v for k, v in vm.items() if k != "per_task"}

        row = {"epoch": epoch, "step": gstep, "trigger": tag}
        row.update(metrics_row("val", vm))
        row["val_secs"] = round(val_secs, 1)

        # verdict printed with its own split, not after the others - decided here, the
        # checkpoint itself is written further down
        score = row.get(es["monitor"])
        if score is None:
            raise KeyError(f"monitor {es['monitor']!r} is not among the val metrics: "
                           f"{sorted(k for k in row if k.startswith('val_'))[:30]}")
        score = float(score)
        improved = score == score and _better(score, best)
        prev_best = best
        if improved:
            best, best_epoch, bad = score, epoch, 0
            was = "" if not math.isfinite(prev_best) else f"  (was {prev_best:.4f}, {score - prev_best:+.4f})"
            print(f"     ⭐ new best {es['monitor']} = {score:.4f}{was} -> best.pt")
        else:
            bad += 1
            if es["enable"] and bad >= es["patience"]:
                stop_now[0] = True     # stop right here, not at the next epoch end
            print(f"     ⚠️  no improvement ({bad}/{es['patience']})  "
                  f"{es['monitor']} = {score:.4f}, best {best:.4f} @ epoch {best_epoch}")

        # every other split: scored and logged, tracked against its own best, but it never
        # touches best.pt or the early-stopping counter
        for sp in extra_splits:
            _t = time.time()
            packs[sp] = {}
            sm = evaluate(em, loaders[sp], loss_fn, cfg, device, hooks, collect=packs[sp])
            secs = time.time() - _t
            if "sample_count" in sm and len(sm) <= 3:          # an unlabelled split
                print(f"  🧪 [{sp}] predicted {sm['sample_count']} rows (no labels) in {fmt(secs)}")
            else:
                _print_eval(sp.upper(), epoch, epochs, gstep, sm, el, eta, "🧪",
                            prev=prev_eval.get(sp), took=secs,
                            per_target=P.get("per_target_eval", True))
                prev_eval[sp] = {k: v for k, v in sm.items() if k != "per_task"}
                s_score = sm.get(_mon, float("nan"))
                eb = extra_best.setdefault(sp, [_worst, 0, 0])
                if s_score == s_score and _better(s_score, eb[0]):
                    was = "" if not math.isfinite(eb[0]) else f"  (was {eb[0]:.4f}, {s_score - eb[0]:+.4f})"
                    eb[:] = [s_score, epoch, 0]
                    print(f"     ⭐ new best {sp}_{_mon} = {s_score:.4f}{was}")
                else:
                    eb[2] += 1
                    print(f"     ⚠️  no improvement ({eb[2]}/{es['patience']})  {sp}_{_mon} = "
                          f"{s_score:.4f}, best {eb[0]:.4f} @ epoch {eb[1]}")
                print("     ℹ️  report only - never drives best.pt")
                row.update(metrics_row(sp, sm))
            row[f"{sp}_secs"] = round(secs, 1)

        row["elapsed_s"] = round(el, 1)
        if hooks.on_validation is not None:
            hooks.on_validation(row, epoch, gstep)
        val_log.log(row)
        history.append(row)
        if log_fn:
            log_fn({f"val/{k}": v for k, v in row.items() if isinstance(v, (int, float))},
                   gstep)

        # update the top-K board FIRST, so best.pt/last.pt carry the current board.
        top_k_track = update_top_k(ckpt_dir, cfg, model, epoch, gstep, score, top_k_track,
                                   cfg["output"].get("keep_top_k", 0),
                                   cfg["output"].get("top_k_weights_only", True),
                                   saver=saver, mode=es["mode"], ema=ema)

        if improved:
            save_checkpoint(ckpt_dir / cfg["output"]["best_name"], cfg, model, opt, sched,
                            scaler, epoch, gstep, score, track=_track(), device=device,
                            elapsed_sec=el, epoch_complete=done, saver=saver, loss_fn=loss_fn,
                            ema=ema, note=f"  \U0001F4BE best.pt written (score {score:.4f})")

        ud.dump(out / "ud_ratio.csv")         # flushed with last.pt, survives preemption
        save_checkpoint(ckpt_dir / "last.pt", cfg, model, opt, sched, scaler, epoch, gstep,
                        score, track=_track(), device=device, loss_fn=loss_fn,
                        elapsed_sec=el, epoch_complete=done, saver=saver, ema=ema,
                        note=("  \U0001F4BE saved last.pt (epoch %d)%s" % (
                            epoch, f"  \U0001F3C6 top-{len(top_k_track)} kept"
                            if top_k_track else "")))
        # raw logits for every split, every validation. Ensembling top-K checkpoints
        # later then costs nothing: load, average, score - no model, no GPU.
        if cfg["output"].get("save_predictions", True):
            pred_dir = out / cfg["output"].get("predictions_dir", "predictions")
            _saved = []
            for _split, _pack in packs.items():
                if not _pack:
                    continue
                _f = save_predictions(pred_dir, _split, run_id, epoch, gstep, score,
                                      _pack["logits"],
                                      _pack["targets"] if _pack["targets"] is not None
                                      else np.zeros((len(_pack["logits"]), 0), np.float32),
                                      _pack["ids"], target_names(cfg))
                if _f:
                    _saved.append(f"{_split}:{_pack['logits'].shape[0]}")
            if _saved:
                print("  📦 predictions saved (" + ", ".join(_saved)
                      + f") -> {pred_dir.name}/")

        _write_summary(epoch, row)
        persist()
        model.train()
        return score


    # counted once on a real batch, then reused - the count itself is not free
    flops_per_sample = [None]
    last_print = [None, None]       # (elapsed, gstep) of the previous console line
    _peak = _peak_tflops(torch.cuda.get_device_name(device)) if device.type == "cuda" else 0.0
    # evaluation.validate_on_resume: score ONCE on the first step back, then behave normally.
    # The cadence is a modulo on the global step, so a checkpoint that lands between two
    # validations leaves a gap on resume. This closes that gap.
    resume_eval = [bool(ck) and bool(cfg["evaluation"].get("validate_on_resume"))]
    if resume_eval[0]:
        print("  \U0001F501 validate_on_resume: scoring once on the first step back")

    # evaluation.validate_before_training: score at step 0, before ANY gradient has been
    # applied - what the starting (pretrained / warm-started) weights are worth on THIS
    # run's inputs. "only" stops right there: one validation pass, no training.
    _vbt = cfg["evaluation"].get("validate_before_training")
    if _vbt and not ck:
        print("\n  \U0001F9EA validate_before_training: scoring the starting weights at step 0, "
              "before any gradient step")
        _validate_and_checkpoint(0, 0, "step 0, before training")
        if str(_vbt).lower() == "only":
            print("  \U0001F9EA validate_before_training: 'only' - stopping without training")
            saver.join()
            if persist_fn:
                persist_fn()
            return best
    epoch = start_epoch
    for epoch in range(start_epoch, epochs + 1):
        print("\n" + "=" * 70)
        print(f"\U0001F4DA EPOCH {epoch}/{epochs}")
        print("=" * 70)
        set_lp_ft_phase(cfg, model, epoch)
        _tds = getattr(loaders["train"], "dataset", None)
        if hasattr(_tds, "set_epoch"):
            _tds.set_epoch(epoch)                  # augmentation schedules, curricula
        if hooks.on_epoch_start is not None:
            hooks.on_epoch_start(epoch, model, loaders)
        skip = resume_skip if epoch == start_epoch else 0
        smp = getattr(loaders["train"], "sampler", None)
        it = skip
        if isinstance(smp, ResumableSampler):
            smp.set_epoch(epoch, skip * train_batch_size(cfg))   # sampler counts samples
            _train_it = iter(loaders["train"])
        else:
            if hasattr(smp, "set_epoch"):
                smp.set_epoch(epoch)
            _train_it = iter(loaders["train"])
            for _ in range(skip):                  # a custom loader: consume what was done
                next(_train_it, None)
        model.train()
        # two throughput numbers so slow data can't hide behind a fast GPU:
        #   compute = units / GPU time only, real = units / wall incl. the data wait.
        # next() is timed by hand (not via `for`) so eval/checkpoint time between
        # steps never gets miscounted as waiting on data.
        roll = deque(maxlen=20)          # (units, wall, data_wait) for the last 20 steps
        win_units, win_t0, win_data, win_first = 0, time.time(), 0.0, 0.0
        while True:
            _tf = time.time()
            try:
                _batch = next(_train_it)
            except StopIteration:
                break
            x, y, _ = split_batch(_batch)
            data_dt = time.time() - _tf              # blocked purely on this batch
            it += 1
            if (it - 1) % accum == 0:                # fresh accumulation window
                win_units, win_t0 = 0, time.time()
                win_data, win_first = 0.0, data_dt
            win_data += data_dt
            x = _prep(hooks, x, device, cfg)
            y = y.to(device, non_blocking=True)
            # `it % accum == 0` is the micro-batch that also triggers the optimizer step
            # below. Arming one earlier means the NEXT iteration's arm(False) wipes the
            # reading before read() sees it.
            probe.arm(probe.active(gstep + 1) and (it % accum == 0 or it == n_micro))
            with torch.autocast("cuda", enabled=use_amp_train, dtype=amp_dtype(cfg)):
                logits, raw = _fwd(hooks, model, x)
                loss = _loss(hooks, loss_fn, logits, raw, y, x)
                loss = loss / accum
            scaler.scale(loss).backward()
            n_units = batch_size_of(y) * per_sample
            units_done[0] += n_units
            win_units += n_units
            if it % accum == 0 or it == n_micro:
                _r = it % accum
                if _r:
                    # partial last window: each of its _r micro-losses was divided by accum,
                    # so the summed gradient is _r/accum of the window's MEAN gradient. Scale
                    # it back: identical to one batch of those samples at accum 1.
                    for _p in model.parameters():
                        if _p.grad is not None:
                            _p.grad.mul_(accum / _r)
                gnorm = float("nan")
                _clip = float(cfg["training"]["grad_clip"] or 0.0)
                if _sam_on:
                    # SAM (Foret 2021): step from the WORST nearby point. Grads at w -> move to
                    # w + rho*g/||g|| (ASAM: scaled by |w|), recompute grads there, move back,
                    # then the normal clip + step uses those second grads. The first grads are
                    # read through 1/scale by hand: unscale_ may run only once per step, and it
                    # must run on the SECOND grads so the GradScaler's inf check sees them.
                    _inv = (1.0 / scaler.get_scale()) if scaler.is_enabled() else 1.0
                    _sp = [p for p in model.parameters() if p.grad is not None]
                    with torch.no_grad():
                        _sc = [(p.abs() if _sam_ad else None) for p in _sp]
                        _gn = torch.norm(torch.stack([((p.grad * s) if _sam_ad else p.grad).float().norm()
                                                      for s, p in zip(_sc, _sp)])) * _inv
                    if torch.isfinite(_gn):          # inf/nan first grads: plain step, GradScaler skips it
                        with torch.no_grad():
                            _f = _sam_rho * _inv / (_gn + 1e-12)
                            _eps = [((p.grad * s * s) if _sam_ad else p.grad) * _f for s, p in zip(_sc, _sp)]
                            _old = [p.detach().clone() for p in _sp]     # restore exactly, not w + e - e
                            for p, e in zip(_sp, _eps):
                                p.add_(e.to(p.dtype))
                            del _eps
                        sam_gn.append(float(_gn))
                        opt.zero_grad(set_to_none=True)
                        with torch.autocast("cuda", enabled=use_amp_train, dtype=amp_dtype(cfg)):
                            _o2, _raw2 = _fwd(hooks, model, x)
                            _l2 = _loss(hooks, loss_fn, _o2, _raw2, y, x)
                        scaler.scale(_l2).backward()
                        with torch.no_grad():
                            for p, o in zip(_sp, _old):
                                p.copy_(o)
                        del _old
                        sam_loss2.append(float(_l2.detach()))
                if _clip:
                    scaler.unscale_(opt)
                    gnorm = float(nn.utils.clip_grad_norm_(model.parameters(), _clip))
                    if math.isfinite(gnorm):        # AMP skips a step on inf/nan
                        clip_seen[0] += 1
                        clip_hit[0] += int(gnorm > _clip)
                        clip_vals.append(gnorm)
                _ud_on = ud.active(gstep + 1)
                if _ud_on:
                    ud.before()
                scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True); sched.step()
                if ema is not None:
                    ema.update(model)
                gstep += 1
                _extra = {}                # SAM internals and loss internals, merged into the log
                _pb = probe.read()
                if _ud_on:
                    _uo = ud.after(epoch, gstep)
                    _um = ud.summarize(_uo)
                    if _um and P.get("ud_ratio", True):
                        print(_um)
                if _pb and P.get("scale_probe", True):
                    print(ScaleProbe.summarize(_pb))
                lrs = sched.get_last_lr()
                lr, lr_lo, lr_hi = lrs[-1], min(lrs), max(lrs)
                # Named, not just min and max. With layer_decay the minimum is the EARLIEST
                # trunk layer, which is not "the backbone rate" in any useful sense - the
                # trunk's TOP layer is what is really training. Report both ends and the head.
                _bb = [v for v, isb in zip(lrs, _grp_is_bb) if isb]
                _hd = [v for v, isb in zip(lrs, _grp_is_bb) if not isb]
                lr_bb_hi = max(_bb) if _bb else None
                lr_bb_lo = min(_bb) if _bb else None
                lr_head = max(_hd) if _hd else lr_hi
                l = loss.item() * accum
                # dt spans the whole window; the waits inside it aren't compute
                dt = time.time() - win_t0
                wall = win_first + dt
                comp_t = max(dt - (win_data - win_first), 1e-9)
                roll.append((win_units, wall, win_data))
                r_i = sum(a for a, _, _ in roll)
                r_w = max(sum(b for _, b, _ in roll), 1e-9)
                r_d = sum(c for _, _, c in roll)
                ips = win_units / comp_t                     # compute-only
                real_ips = r_i / r_w                         # incl. data wait, 20-step
                wait_pct = 100.0 * r_d / r_w
                # the number that actually decides what the run costs: every unit since
                # step 0 over every second since step 0. Unlike the two above it carries
                # validation, checkpoint writes, volume commits and epoch boundaries - all
                # the things the in-loop figures step around. Both survive a resume.
                overall_ips = units_done[0] / max(time.time() - t0, 1e-9)
                mem = (torch.cuda.max_memory_allocated(device) / 1024**3
                       if device.type == "cuda" else 0.0)
                el = time.time() - t0
                eta = el * (total / gstep - 1)
                if hasattr(loss_fn, "stats"):
                    _extra.update(loss_fn.stats(target_names(cfg)))
                if sam_gn:
                    # sam_gnorm: ||g|| at w (unscaled, ASAM-weighted if adaptive); sam_loss2: loss at the
                    # perturbed point. sam_loss2 minus the row's train loss = the sharpness SAM is fighting.
                    _extra["sam_gnorm"] = round(sum(sam_gn) / len(sam_gn), 5)
                    _extra["sam_loss2"] = round(sum(sam_loss2) / len(sam_loss2), 5)
                    _extra["sam_n"] = len(sam_gn)
                    sam_gn.clear(); sam_loss2.clear()
                # GPU use, logged every step (not only printed): MFU = share of the card's peak
                # FLOP/s this step really used; SM / memory-controller busy = share of time busy.
                # FLOPs are counted once, on the first step (one extra forward of one sample).
                _mfu_pct = _sm_pct = _mc_pct = None
                if device.type == "cuda":
                    if flops_per_sample[0] is None:
                        flops_per_sample[0] = (_measure_flops_per_sample(model, x, cfg, device, hooks)
                                               if LG.get("flops_probe", True) else 0.0)
                    _sm_pct, _mc_pct = _gpu_busy()
                    if flops_per_sample[0] and _peak:
                        _mfu_pct = round(100.0 * 3.0 * flops_per_sample[0] * (ips / per_sample) / 1e12 / _peak, 1)
                train_log.log({**_extra, **ScaleProbe.row(_pb),
                               "mfu_pct": _mfu_pct, "sm_busy_pct": _sm_pct, "mem_ctrl_busy_pct": _mc_pct,
                               "epoch": epoch, "epoch_step": -(-it // accum),
                               "global_step": gstep, "loss": round(l, 6), "lr": lr,
                               "lr_min": lr_lo, "lr_max": lr_hi,
                               "lr_head": lr_head,
                               "lr_backbone_max": lr_bb_hi, "lr_backbone_min": lr_bb_lo,
                               "gnorm": round(gnorm, 4),
                               "clip_pct": (round(100.0 * clip_hit[0] / clip_seen[0], 1)
                                            if clip_seen[0] else None),
                               "units_s": round(ips, 1),
                               "real_units_s": round(real_ips, 1),
                               "data_wait_pct": round(wait_pct, 1),
                               "overall_units_s": round(overall_ips, 1),
                               "units_done": units_done[0],
                               "gpu_mem_gb": round(mem, 2), "elapsed_s": round(el, 1)})
                # 200 steps is enough to tell a chronic rate from a warmup spike
                if (P.get("clip_warning", True) and not clip_warned[0] and clip_seen[0] >= 200
                        and clip_hit[0] / clip_seen[0] > 0.5):
                    clip_warned[0] = True
                    _v = sorted(clip_vals)
                    _md, _mn = _v[len(_v) // 2], sum(_v) / len(_v)
                    print(
                        f"\n  ⚠️  CLIPPING {100.0 * clip_hit[0] / clip_seen[0]:.0f}% of {clip_seen[0]} steps at grad_clip={_clip:g} "
                        f"-> real step below the live lr {lr_hi:.2e}.\n"
                        f"      gnorm  med {_md:.2f}  mean {_mn:.2f}  min {_v[0]:.2f}  max {_v[-1]:.2f}  ->  raise grad_clip or lower lr\n")

                # flushing the volume is its own concern - a crash between two
                # validations must not cost the log rows written in between
                ce = int(cfg["output"].get("commit_every_steps", 0) or 0)
                if ce and gstep % ce == 0:
                    persist()                  # async: never blocks the step loop
                trig = eval_due(cfg, epoch, gstep, resume_eval)
                if trig:
                    _validate_and_checkpoint(epoch, gstep, trig)
                    if stop_now[0]:
                        break             # stop AT patience, not at the next epoch end
                _sa = int(cfg["training"].get("stop_after_steps") or 0)
                if _sa and gstep >= _sa:
                    # a deliberately short run (e.g. checking a machine against a known curve):
                    # the lr schedule stays the FULL run's, so every step up to here matches it
                    print(f"\n🛑 stop_after_steps={_sa} reached at step {gstep}")
                    stop_now[0] = True
                    break
                every = cfg["output"].get("checkpoint_every_steps", 0)
                if every and gstep % every == 0:
                    save_checkpoint(ckpt_dir / f"step{gstep}.pt", cfg, model, opt, sched,
                                    scaler, epoch, gstep,
                                    track=_track(), loss_fn=loss_fn,
                                    device=device, elapsed_sec=el,
                                    epoch_complete=False, saver=saver, ema=ema,
                                    note=(f"  \U0001F4BE periodic checkpoint @ step "
                                          f"{gstep} (rolling, keep_last_n="
                                          f"{cfg['output'].get('keep_last_n', 3)})"))
                    prune_checkpoints(ckpt_dir, cfg["output"].get("keep_last_n", 3),
                                      saver=saver)
                    persist()             # flush logs to the volume too
                if P.get("warmup", True):
                    if gstep == 1 and warm:
                        print(f"  🔥 warmup STARTED - lr ramps from 0 to base over "
                              f"{warm} step(s) ({cfg['training']['scheduler']['warmup_frac']:.0%} "
                              f"of {total})")
                    if warm and gstep == warm:   # not elif: warm can be 1 on tiny runs
                        _bbs = ("backbone %.3e" % lr_bb_hi if lr_bb_hi == lr_bb_lo
                                else "backbone top %.3e, bottom %.3e" % (lr_bb_hi, lr_bb_lo)) \
                            if lr_bb_hi is not None else "no backbone group"
                        print(f"  ✅ warmup COMPLETE at step {warm} - base lr reached "
                              f"(head {lr_head:.3e}, {_bbs}); "
                              f"{cfg['training']['scheduler']['name']} schedule begins")
                _cle = int(LG.get("console_log_every") or 0)
                if _cle and (gstep % _cle == 0 or gstep == 1):
                    if P.get("step_line", True):
                        d = "" if prev_loss is None else f" ({l - prev_loss:+.4f})"
                        # one lr when every group shares it, both ends when LLRD or
                        # backbone_lr_mult splits them
                        if lr_lo == lr_hi:
                            lr_s = f"lr={lr_hi:.3e}"
                        elif lr_bb_hi is None:
                            lr_s = f"lr[head={lr_head:.3e}]"
                        elif lr_bb_hi == lr_bb_lo:
                            lr_s = f"lr[head={lr_head:.3e} backbone={lr_bb_hi:.3e}]"
                        else:
                            lr_s = (f"lr[head={lr_head:.3e}  backbone top={lr_bb_hi:.3e} "
                                    f"bottom={lr_bb_lo:.3e}]")
                        print("─" * 70)
                        print(f"  Epoch {epoch}/{epochs}  epoch_step: {-(-it // accum)}/{steps_per_epoch}"
                              f"  global_step: {gstep}/{total}")
                        # one step's gnorm is noisy, so the rolling mean is what actually says
                        # whether the model runs hot, and clip% says how much survives the cap
                        _gw = list(clip_vals)[-50:]
                        _gs = ""
                        if _gw:
                            _gs = (f" (avg{len(_gw)} {sum(_gw) / len(_gw):.2f}"
                                   f", clip {100.0 * clip_hit[0] / max(clip_seen[0], 1):.0f}%)")
                        # wall time since the previous console line. Nothing to difference
                        # against on this process's FIRST line (elapsed survives a resume
                        # while last_print does not)
                        _since = ""
                        if last_print[0] is not None and gstep > last_print[1]:
                            _since = (f"  +{fmt(el - last_print[0])}"
                                      f"/{gstep - last_print[1]}st")
                        last_print[0], last_print[1] = el, gstep
                        print(f"     loss={l:.4f}{d}  {lr_s}  gnorm={gnorm:.2f}{_gs}  "
                              f"elapsed={fmt(el)}  ETA={fmt(eta)}"
                              + (f"  gpu_mem(peak)={mem:.2f}GB" if device.type == "cuda" else "")
                              + _since)
                    if P.get("throughput", True):
                        print()                      # split what the model is doing from how fast
                        print(f"     throughput: {ips:.0f} {unit}/s compute | {real_ips:.0f} {unit}/s real "
                              f"({len(roll)}-step) | data-wait {wait_pct:.0f}%")
                        _eff = 100.0 * overall_ips / max(real_ips, 1e-9)
                        print(f"     ➤ END-TO-END: {overall_ips:.0f} {unit}/s over the whole "
                              f"run ({_eff:.0f}% of in-loop) - {units_done[0]:,} {unit}s "
                              f"in {fmt(time.time() - t0)}")
                    # Is the GPU actually WORKING, or just occupied? units/s says how fast
                    # this model runs; MFU says how much of the card that speed uses, so a
                    # number that looks fine can still be leaving 80% on the table.
                    if device.type == "cuda" and P.get("compute", True):
                        if flops_per_sample[0] is None:
                            flops_per_sample[0] = (_measure_flops_per_sample(model, x, cfg, device, hooks)
                                                   if LG.get("flops_probe", True) else 0.0)
                        _sm, _mc = _gpu_busy()
                        _bits = []
                        # x3: backward costs roughly twice forward, so fwd+bwd ~ 3x fwd.
                        # ips is units/s, so samples/s = ips / per_sample
                        _ach = 3.0 * flops_per_sample[0] * (ips / per_sample) / 1e12
                        if flops_per_sample[0] and _peak:
                            _bits.append(f"MFU {100.0 * _ach / _peak:.0f}% "
                                         f"({_ach:.1f} of {_peak:.0f} TFLOP/s fp16/bf16)")
                        elif flops_per_sample[0]:
                            _bits.append(f"{_ach:.1f} TFLOP/s (no peak figure for this card)")
                        if flops_per_sample[0]:
                            _bits.append(f"{flops_per_sample[0] / 1e9:.2f} GFLOP/{LG.get('unit', 'sample')} fwd")
                        if _sm is not None:
                            _bits.append(f"SM busy {_sm:.0f}%")
                        if _mc is not None:
                            _bits.append(f"mem ctrl busy {_mc:.0f}%")
                        if _bits:
                            print("     compute:    " + " | ".join(_bits), flush=True)
                    prev_loss = l
                    if log_fn:
                        log_fn({"train/loss": l, "train/lr": lr, "train/gnorm": gnorm,
                                f"train/{unit}_per_s": real_ips}, gstep)

        # drop_last=false leaves a ragged tail: those micro-batches ran backward() but
        # never reached opt.step(), so without this their gradients leak into the first
        # step of the next epoch (and a resumed run, being a fresh process, would not
        # have them - the two trajectories then diverge).
        if it % accum and it != n_micro:           # the full epoch's tail is now stepped
            opt.zero_grad(set_to_none=True)
            print(f"  \U0001F9F9 discarded {it % accum} trailing micro-batch(es) "
                  f"(not a full accumulation window)")

        if stop_now[0] and not (es["enable"] and bad >= es["patience"]):
            break                                      # stop_after_steps
        ee = int(cfg["evaluation"].get("eval_every_epochs") or 0)
        if ee and epoch % ee == 0:
            _validate_and_checkpoint(epoch, gstep, "epoch")

        if stop_now[0] or (es["enable"] and bad >= es["patience"]):
            print(f"\n🛑 early stop: {bad} validations without improvement "
                  f"(patience={es['patience']})")
            break

    if last_val_step != gstep:
        print("\n  📌 final validation (these last steps hit no trigger)")
        _validate_and_checkpoint(epoch, gstep, "final")

    train_log.close(); val_log.close()
    total_time = time.time() - t0
    best_row = next((r for r in history if r.get(es["monitor"]) == best),
                    history[-1] if history else {})
    print("\n" + "=" * 70)
    print(f"\U0001F3C1 FINISHED - {cfg['experiment']['name']}  ({run_id})")
    print("=" * 70)
    # history holds one row per VALIDATION, which is not one per epoch once
    # step-triggered validation fires more than once inside an epoch
    print(f"  ⏱️  total time       : {fmt(total_time)}  "
          f"({epoch} epochs, {gstep} steps, {len(history)} validations, "
          f"{units_done[0]:,} {unit}s)")
    if cfg["evaluation"].get("enable", True):
        print(f"  ⭐ best {es['monitor']:<15s}: {best:.4f}  @ epoch {best_epoch}")
    else:
        print("  ⭐ no validation: best.pt = the latest weights")
    if best_row and P.get("final_summary", True) and cfg["evaluation"].get("enable", True):
        print(f"  \U0001F4C9 val loss at best  : {best_row.get('val_loss')}")
        for sp in extra_splits:
            if f"{sp}_{_mon}" in best_row:
                print(f"  \U0001F9EA {sp} {_mon:<12s}: {best_row[f'{sp}_{_mon}']}  (report only)")
        # per-target table at the best validation: the first per-target metric that exists
        names = target_names(cfg)
        key = next((k for k in ("auroc", "rmse", "f1", "mae")
                    if any(f"val_{k}_{t}" in best_row for t in names)), None)
        if key:
            hib = key in ("auroc", "f1")
            vals = [(t, best_row.get(f"val_{key}_{t}", float("nan"))) for t in names]
            vals = [(t, v) for t, v in vals if t is not None]
            ranked = sorted(vals, key=lambda kv: (-(kv[1]) if hib else kv[1]) if kv[1] == kv[1] else 1e9)
            rows = []
            for t, v in ranked:
                cells = [t, "  n/a" if v != v else f"{v:.4f}"]
                if key == "auroc":
                    a = best_row.get(f"val_auprc_{t}", float("nan"))
                    cells.append("  n/a" if a != a else f"{a:.4f}")
                for sp in extra_splits:
                    a = best_row.get(f"{sp}_{key}_{t}", float("nan"))
                    cells.append("  n/a" if a != a else f"{a:.4f}")
                if key == "auroc":
                    cells.append("█" * int(max(0.0, v - 0.5) * 40) if v == v else "")
                rows.append(cells)
            heads = (["target", f"val {key.upper()}"] + (["val AUPRC"] if key == "auroc" else [])
                     + [f"{sp} {key.upper()}" for sp in extra_splits]
                     + (["above chance"] if key == "auroc" else []))
            _table(f"per-target at the best validation (epoch {best_epoch})", heads, rows, "\U0001F50D")
    print(f"  \U0001F4BE checkpoints       : {ckpt_dir}")
    print(f"  \U0001F4DD logs              : {out / cfg['output']['train_log_csv']}")
    print(f"                        {out / cfg['output']['val_log_csv']}")
    print("=" * 70)

    # curves for every run, and a plotting bug must never sink a finished run. make_plots
    # is usually off on Modal (a container only holds its own CSV rows); a LOCAL run has the
    # whole log on disk, so it always plots
    if cfg["output"].get("make_plots", True) or runtime_side() == "local":
        _safe("make_plots", make_plots, cfg, out,
              cfg["output"].get("plots_dir", "plots"))
    saver.join()                           # every checkpoint on disk before we flush
    if saver.error:
        print(f"  ⚠️  a checkpoint write failed: {saver.error}")
    persist(blocking=True)                 # the run is over: this one has to land
    if persist.skipped:
        print(f"  ℹ️  {persist.done} volume flushes, {persist.skipped} "
              f"skipped as redundant (one was already in flight)")
    if persist.last_error:
        print(f"  ⚠️  last volume flush error: {persist.last_error}")
    saver.join()                           # the last checkpoint is on disk (and offered)
    if _UPLOADER is not None:
        _UPLOADER.join()                   # ... and every upload has landed
        _UPLOADER = None
    return best

SUBMISSION_TEMPLATE = {
    "submitted": None,            # UTC, "2026-08-20 16:09" - kaggle reports UTC
    "public_score": None,         # the leaderboard number
    "private_score": None,        # only after the deadline
    "runtime_seconds": None,      # what the Efficiency Prize is ranked on
    "runtime": None,              # the same thing readable: "44:32" or "1:35:34"
    "kernel": None,               # "<user>/<slug>"
    "kernel_version": None,       # which version was submitted
    "submission_ref": None,       # kaggle's id, so the entry can be found again
    "checkpoint": None,           # which checkpoint went into the dataset
    "notes": None,
}


def carried_submission(summary_path) -> dict:
    """Keep a hand-filled submission record across summary rewrites.

    The summary is rewritten at every validation, so a record typed in by hand would
    otherwise be erased by the next one - or by a resume.
    """
    try:
        old = json.loads(Path(summary_path).read_text()).get("submission")
    except Exception:
        old = None
    if not isinstance(old, dict):
        return dict(SUBMISSION_TEMPLATE)
    rec = {k: old.get(k, v) for k, v in SUBMISSION_TEMPLATE.items()}
    # fill runtime from the seconds, so only one of the two has to be typed in
    if rec.get("runtime") is None:
        rec["runtime"] = clock(rec.get("runtime_seconds"))
    return rec


def clock(sec: float | None) -> str | None:
    """Seconds -> "44:32", or "1:35:34" once it runs past an hour."""
    if sec is None:
        return None
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt(sec: float) -> str:
    """Seconds -> "1h04m09s" / "4m09s"."""
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s"

# =============================================================================
# compute diagnostics: FLOPs, peak throughput, GPU busy
# =============================================================================
def _measure_flops_per_sample(model, x, cfg, device, hooks: Hooks | None = None) -> float:
    """FLOPs for ONE sample's forward pass, counted once on a real (already prepared) batch.

    Counted, not looked up: models wrap a trunk in their own heads and run at their own
    resolution, so published GFLOP figures rarely describe what actually runs.
    """
    try:
        from torch.utils.flop_counter import FlopCounterMode
    except ImportError:
        return 0.0
    was_training = model.training
    try:
        # ONE sample, not the whole batch: the answer is per-sample either way, and a
        # second full-batch forward could OOM the run just to print a diagnostic.
        x1 = slice_batch(x, 1)
        model.eval()
        with torch.no_grad():
            fc = FlopCounterMode(display=False)
            with fc:
                _fwd(hooks or Hooks(), model, x1)
            total = fc.get_total_flops()
        return float(total) / max(batch_size_of(x1), 1)
    except Exception as e:
        # never let a diagnostic kill a training run
        print(f"  [warn] could not count FLOPs: {type(e).__name__}: {e}")
        return 0.0
    finally:
        if was_training:
            model.train()
        if device.type == "cuda":
            torch.cuda.empty_cache()
            # the probe's own allocation must not masquerade as a training peak
            torch.cuda.reset_peak_memory_stats(device)


# Dense (non-sparse) tensor-core throughput at the precision amp actually uses, bf16/fp16
# with fp32 accumulate. Vendor headline numbers usually quote 2x these via sparsity.
# Order matters: the first key contained in the device name wins (L40S before L40 before L4).
_PEAK_TFLOPS = {
    "B200": 2250.0, "B100": 1800.0, "H200": 989.0, "H100": 989.0,
    "A100": 312.0, "L40S": 362.0, "L40": 181.0, "L4": 121.0, "A10G": 125.0, "A10": 125.0,
    "A6000": 155.0, "6000 Ada": 364.0, "V100": 125.0, "P100": 18.7, "T4": 65.0,
    "5090": 209.5, "4090": 165.2, "4080": 97.5, "4070": 58.0, "4060": 60.5,
    "3090": 71.0, "3080": 59.5,
}


def _peak_tflops(name: str) -> float:
    """Peak dense bf16 TFLOP/s for this device, 0.0 when we have no figure for it."""
    for k, v in _PEAK_TFLOPS.items():
        if k.lower() in (name or "").lower():
            return v
    return 0.0


def _gpu_busy() -> tuple:
    """(sm_busy_pct, mem_ctrl_busy_pct) from NVML, (None, None) when unavailable.

    Both are TIME-based: the fraction of the sample window in which any kernel was
    resident, and in which the memory controller was reading or writing. Neither is an
    achieved-bandwidth or a FLOP figure - a kernel using 3% of the tensor cores still
    reports ~100% SM busy, which is exactly why MFU is printed beside them.
    """
    try:
        return torch.cuda.utilization(), torch.cuda.memory_usage()
    except Exception:
        return None, None


# =============================================================================
# modal glue
# =============================================================================
def modal_image(cfg: dict, runs_dir, data_dir=None, extra_pip=()):
    """Container image for remote runs: deps + the runs/ folder (code only) + small data files.

    modal.pip / modal.extra_pip / modal.apt / modal.python_version come from the config.
    Pip and apt steps go BEFORE the local files: Modal refuses any build step after
    add_local_* (it would rebuild on every code change). runs/ lands at /root/runs and
    data_dir (when given and modal.ship_data_dir) at /root/data, minus modal.data_ignore.
    """
    import modal
    m = cfg["modal"]
    img = modal.Image.debian_slim(python_version=str(m.get("python_version", "3.11")))
    apt = list(m.get("apt") or [])
    if apt:
        img = img.apt_install(*apt)
    img = img.pip_install(*(list(m.get("pip") or []) + list(m.get("extra_pip") or []) + list(extra_pip)))
    # CODE ONLY: results/ holds checkpoints, predictions and plots that the container never
    # reads (checkpoints reach it through the runs VOLUME). Indexing them on every launch is
    # pure wait before the GPU starts.
    img = img.add_local_dir(str(Path(runs_dir)), "/root/runs",
                            ignore=["**/results", "**/__pycache__", "**/*.pt", "**/*.pth",
                                    "**/*.npz", "**/*.png", "**/*.ckpt", "**/*.safetensors"])
    if data_dir is not None and m.get("ship_data_dir", True) and Path(data_dir).is_dir():
        img = img.add_local_dir(str(Path(data_dir)), "/root/data",
                                ignore=list(m.get("data_ignore") or []))
    return img


def modal_volumes(cfg: dict) -> dict:
    """{mount: Volume} for the runs volume and the optional data volume."""
    import modal
    m = cfg["modal"]
    vols = {m["runs_mount"]: modal.Volume.from_name(m["runs_volume"], create_if_missing=True)}
    if m.get("data_volume"):
        vols[m["data_mount"]] = modal.Volume.from_name(m["data_volume"], create_if_missing=True)
    return vols


def modal_secrets(cfg: dict) -> list:
    import modal
    names = list(cfg["modal"].get("secrets") or [])
    if cfg["logging"].get("wandb", {}).get("enabled") and "wandb-secret" not in names:
        names.append("wandb-secret")
    return [modal.Secret.from_name(n) for n in names]


def modal_resources(cfg: dict) -> dict:
    """gpu/timeout always; cpu and memory only when the run config asks for them."""
    m = cfg["modal"]
    kw = {"gpu": m["gpu"], "timeout": int(float(m.get("timeout_hours", 8)) * 3600),
          # release the GPU the moment training returns. Modal's default is 60s of
          # idle-but-billed reservation, paid while this PC is still syncing artifacts.
          "scaledown_window": int(m.get("scaledown_window", 2))}
    if m.get("cpu"):
        kw["cpu"] = float(m["cpu"])              # cores, a reservation not a cap
    if m.get("memory_gb"):
        kw["memory"] = int(float(m["memory_gb"]) * 1024)   # config is GB, modal wants MiB
    return kw


def remote_run_ids(cfg: dict) -> set:
    """runNNN ids already on the runs volume for this experiment (no container needed)."""
    rd = cfg["output"]["run_dir"]
    files = volume_files(cfg["modal"]["runs_volume"],
                         f"{cfg['experiment']['name']}/{rd}/{cfg['output']['console_capture_dir']}") or {}
    return {r for f in files if (r := run_id_of(f.split("/")[-1]))}


def launch_run_id(cfg: dict, exp_dir) -> str:
    """Allocate this launch's runNNN, here on the launching PC.

    The volume is consulted too, so a number already used remotely is never handed out
    again (a run resumed on Modal keeps its ids even when this PC has no local copy).
    """
    known = set()
    try:
        known = remote_run_ids(cfg)
    except Exception as e:                     # offline / no credit: local state still works
        print(f"  ⚠️  couldn't read run ids off the volume "
              f"({type(e).__name__}: {e}) - numbering from local state only")
    rid = allocate_run_id(Path(exp_dir) / cfg["output"]["run_dir"], known)
    print(f"  🆔 allocated {rid} for {cfg['experiment']['name']}"
          + (f"  (volume already had {len(known)})" if known else ""))
    return rid


_SYNCED = False


def sync_back(cfg: dict, exp_dir, status: str = "", once: bool = True) -> None:
    """Pull this run's artifacts home. Fires on success, on crash, and on Ctrl+C.

    `once` guards against syncing twice when both the signal handler and the
    entrypoint's finally fire for the same interrupt.
    """
    global _SYNCED
    if once and _SYNCED:
        return
    _SYNCED = True
    try:
        print(f"\n  \U0001F504 syncing artifacts back ({status}) ...")
        sync_results(cfg, exp_dir, direction="down")
    except Exception as e:                     # a failed sync must never mask a training error
        print(f"  ⚠️  artifact sync failed: {type(e).__name__}: {e}")
    plot_after_run(cfg, exp_dir, status)       # after the sync: it needs the merged CSVs


def plot_after_run(cfg: dict, exp_dir, status: str = "") -> None:
    """Draw the training curves on this PC once the run has finished, from the merged CSVs
    (a container that resumed several times only holds part of the history)."""
    if status != "finished":
        return
    try:
        results = Path(exp_dir) / cfg["output"].get("run_dir", "results")
        if not (results / cfg["output"]["train_log_csv"]).exists():
            print(f"  ⚠️  no local CSVs in {results} - skipping the plots")
            return
        make_plots(cfg, results, cfg["output"].get("plots_dir", "plots"))
    except Exception as e:                     # a bad plot must never mask a finished run
        print(f"  ⚠️  plotting failed: {type(e).__name__}: {e}")


def modal_train(cfg: dict, exp_dir, build_model: Callable, build_data: Callable,
                hooks: Hooks | None = None, run_id: str = "", volumes: dict | None = None):
    """The body of a Modal GPU function: remap paths, build, train, always commit.

    Call it from inside the @app.function in a run's train.py (see the template).
    """
    rcfg = remote_cfg(cfg)
    if run_id:
        rcfg["experiment"]["run_id"] = run_id      # allocated on the launching PC
    runs_vol = (volumes or {}).get(rcfg["modal"]["runs_mount"])
    out_dir = Path(rcfg["modal"]["runs_mount"]) / rcfg["experiment"]["name"]
    wb = rcfg["logging"].get("wandb", {}) or {}
    run, log_fn = None, None
    if wb.get("enabled"):
        import wandb
        run = wandb.init(project=wb.get("project") or rcfg["experiment"]["name"],
                         name=f"{rcfg['experiment']['name']}_{run_id}", config=rcfg)
        log_fn = lambda d, s: run.log(d, step=s)
    try:
        return run_experiment(rcfg, build_model(rcfg), out_dir, build_data(rcfg), hooks,
                              persist_fn=(runs_vol.commit if runs_vol is not None else None),
                              log_fn=log_fn)
    finally:
        if run:
            run.finish()
        if runs_vol is not None:
            runs_vol.commit()                      # always save results, even after a crash


def modal_launch(cfg: dict, exp_dir, remote_fn) -> None:
    """The body of a run's @app.local_entrypoint: Ctrl+C-safe launch, then sync home."""
    sync_on_interrupt(cfg, exp_dir)               # ctrl+c stops the app, then pulls artifacts
    run_id = launch_run_id(cfg, exp_dir)          # sequential, reserved here
    status = "crashed"
    try:
        remote_fn.remote(run_id)
        status = "finished"
    finally:
        # the container can't reach this PC, so the pull happens here - and it has to
        # happen whether training finished or blew up
        sync_back(cfg, exp_dir, status)

def stop_running_app(cfg: dict, timeout: int = 90) -> str | None:
    """Stop this run's Modal app, so the GPU stops billing BEFORE we spend time syncing.

    THE PROBLEM THIS FIXES. sync_on_interrupt used to pull the artifacts first and only then
    hand over to Modal's own handler, which is what actually stops the app. So from Ctrl+C
    until the last file landed - tens of seconds, sometimes a minute - the container was
    still alive and still training. That is paid A100 time spent on ~60 steps that get
    thrown away, on every single interrupt.

    Order is now: stop the container, then sync. The artifacts are safe either way because
    they live on the VOLUME, not in the container, and the container commits them every
    `output.commit_every_steps` (25) regardless.

    WHAT THIS COSTS. Stopping first can lose whatever was written since the last commit: up
    to 24 rows of train_log, and up to 99 steps of checkpoint progress
    (`checkpoint_every_steps` is 100). That is a bounded, cheap loss against paying for a
    minute of idle GPU every time.

    Found by NAME - `modal.App` is created as App(cfg["experiment"]["name"]) in every run's
    train.py - so no run folder needs to change. `--json` is used because the plain table
    truncates the description to "convnext_ba...".
    """
    import subprocess                       # not a module-level import in this file

    name = cfg.get("experiment", {}).get("name")
    if not name:
        return None
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run([sys.executable, "-m", "modal", "app", "list", "--json"],
                           capture_output=True, timeout=timeout, env=env)
        out = (r.stdout or b"").decode("utf-8", "replace")
        rows = json.loads(out[out.index("["):out.rindex("]") + 1])
    except Exception as e:
        print(f"     (could not list apps: {type(e).__name__}: {e})", flush=True)
        return None
    for row in rows:
        if row.get("Description") != name or row.get("Stopped at"):
            continue
        state = (row.get("State") or "").lower()
        if "ephemeral" not in state and "running" not in state:
            continue
        app_id = row.get("App ID")
        try:
            subprocess.run([sys.executable, "-m", "modal", "app", "stop", app_id, "-y"],
                           capture_output=True, timeout=timeout, env=env)
            return app_id
        except Exception as e:
            print(f"     (stop failed: {type(e).__name__}: {e})", flush=True)
            return None
    return None


def sync_on_interrupt(cfg: dict, exp_dir) -> None:
    """Sync on Ctrl+C too, by hooking the signal rather than trusting `finally`.

    `modal run` installs its own SIGINT handler and tears the local process down
    before the entrypoint's finally block gets there, so stopping a run by hand used
    to leave the CSVs and debug images sitting on the volume. The container itself
    keeps committing (`output.commit_every_steps`), so they were never lost - but
    they had to be fetched by hand afterwards.

    Modal's handler still runs after ours, so Ctrl+C keeps stopping the app as before.
    """
    import signal

    def _mute_heartbeat_noise():
        """Stop modal's heartbeat loop from spamming tracebacks at a deliberately dead app.

        We stop the app ourselves to release the GPU before syncing. The client does not know
        that, so its background heartbeat keeps calling AppHeartbeat, gets
        `ConflictError: App state is APP_STATE_STOPPED`, and logs a FULL TRACEBACK every few
        seconds for the whole sync - tens of seconds of scrollback burying the one line that
        matters. Dropping only the heartbeat-failure records leaves every other modal error
        visible.

        The filter goes on the root HANDLERS as well as the named loggers: a filter on a
        logger only sees records logged directly to it, not ones propagating up from
        children, and the record's origin has moved between modal versions.
        """
        import logging

        class _DropHeartbeat(logging.Filter):
            def filter(self, record):
                try:
                    msg = record.getMessage()
                except Exception:
                    return True
                noisy = "Loop attempt" in msg and "heartbeat" in msg
                if not noisy and record.exc_info:
                    noisy = "APP_STATE_STOPPED" in str(record.exc_info[1])
                return not noisy

        filt = _DropHeartbeat()
        for nm in ("modal-client", "modal", "modal.runner", "modal._utils.async_utils"):
            logging.getLogger(nm).addFilter(filt)
        for h in logging.getLogger().handlers:
            h.addFilter(filt)

    def make(previous):
        def handler(signum, frame):
            print("\n  \u23F9\uFE0F  interrupted - stopping the container, then pulling artifacts "
                  "(Ctrl+C again to skip)", flush=True)
            # STOP THE CONTAINER FIRST. Syncing takes tens of seconds and the GPU bills
            # for every one of them; Modal's own handler only stops the app AFTER ours
            # returns, so doing it here is the difference between paying for the sync and
            # not. See stop_running_app for what this can cost (up to 24 unlogged steps).
            _mute_heartbeat_noise()   # before the stop, or the first failures still print
            _app = stop_running_app(cfg)
            print(f"     container {'stopped: ' + _app if _app else 'not found (already down?)'}"
                  f" - GPU released, now pulling artifacts", flush=True)
            sync_back(cfg, exp_dir, "interrupted")
            if callable(previous):
                return previous(signum, frame)      # let modal stop the app as usual
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)
        return handler

    for sig in (signal.SIGINT, getattr(signal, "SIGTERM", None)):
        if sig is None:
            continue
        try:
            signal.signal(sig, make(signal.getsignal(sig)))
        except Exception:                           # not the main thread, or no such signal
            pass


def remote_cfg(cfg: dict) -> dict:
    """Copy of the config with local paths swapped for the container's, from modal.path_remap
    ({"paths.data_dir": "/root/data", ...}). paths.data_dir defaults to /root/data when the
    local data folder ships in the image (modal.ship_data_dir)."""
    r = json.loads(json.dumps(cfg))               # cheap deep copy, leaves the local cfg alone
    remap = dict(cfg["modal"].get("path_remap") or {})
    if cfg["modal"].get("ship_data_dir", True):
        remap.setdefault("paths.data_dir", "/root/data")
    for k, v in remap.items():
        cfg_set(r, k, v)
    return r


# =============================================================================
# modal: bring a run's results home (Python SDK, no CLI subprocesses)
# =============================================================================
# merged row-wise on these keys; every other file is copied when one side lacks it
MERGE_CSVS = {"train_log.csv": ("run_id", "global_step"),
              "val_log.csv": ("run_id", "step", "trigger"),
              "ud_ratio.csv": ("step", "param")}
# per-side "latest" files: the remote copy wins (the local hand-filled submission block is kept)
LATEST_ONLY = {"training_summary.json", "top_k.json"}


def _vol(name: str):
    import modal
    return modal.Volume.from_name(name)


def volume_files(volume: str, base: str) -> dict | None:
    """{path relative to base: size} for every file under base on a Modal volume.
    {} when base does not exist, None when the volume cannot be listed."""
    from modal.volume import FileEntryType
    base = base.strip("/")
    try:
        entries = _vol(volume).listdir(base, recursive=True)
    except Exception as e:
        msg = str(e).lower()
        if "not found" in msg or "no such" in msg or "does not exist" in msg:
            return {}
        print(f"  ⚠️  could not list {volume}:/{base} ({type(e).__name__}: {e})")
        return None
    out = {}
    for e in entries:
        if e.type != FileEntryType.FILE:
            continue
        p = e.path.strip("/")
        rel = p[len(base):].strip("/") if p.startswith(base) else p
        out[rel] = int(e.size)
    return out


def pull_file(volume: str, remote: str, dest) -> Path:
    """Download one file from a Modal volume, atomically (temp file + replace)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with open(tmp, "wb") as fh:
        for chunk in _vol(volume).read_file(remote.strip("/")):
            fh.write(chunk)
    os.replace(tmp, dest)
    return dest


def push_files(volume: str, pairs: list, force: bool = True) -> None:
    """Upload [(local path, remote path)] to a Modal volume in one batch."""
    if not pairs:
        return
    with _vol(volume).batch_upload(force=force) as b:
        for local, remote in pairs:
            b.put_file(str(local), "/" + str(remote).strip("/"))


def sync_results(cfg: dict, exp_dir, direction: str = "down", dry: bool = False,
                 include_checkpoints: bool | None = None) -> dict:
    """Make <exp_dir>/results match <runs_volume>:/<experiment>/results.

    CSV logs are MERGED row-wise (union, keyed on run_id + step), so a run resumed across
    several containers ends up with one complete history on both sides. Other files are
    copied to whichever side lacks them; summary files take the remote copy (keeping a
    hand-filled local submission block). Checkpoints are skipped unless asked for.
    direction: down | up | both.
    """
    exp = cfg["experiment"]["name"]
    vol = cfg["modal"]["runs_volume"]
    rd = cfg["output"]["run_dir"]
    lbase, rbase = Path(exp_dir) / rd, f"{exp}/{rd}"
    ckd = cfg["output"]["checkpoints_dir"]
    inc_ck = cfg["modal"].get("sync_checkpoints") if include_checkpoints is None else include_checkpoints
    skip_top = {".run_ids", "plots", "__pycache__"} | (set() if inc_ck else {ckd})
    print(f"\n  🔄 sync {vol}:/{rbase}  <->  {lbase}   ({direction}{', dry run' if dry else ''})")
    remote = volume_files(vol, rbase)
    if remote is None:
        return {"ok": False}
    remote = {k: v for k, v in remote.items() if k.split("/")[0] not in skip_top
              and not k.endswith((".tmp", ".part", ".migrating"))}
    local = {}
    if lbase.is_dir():
        for p in lbase.rglob("*"):
            if p.is_file():
                rel = p.relative_to(lbase).as_posix()
                if rel.split("/")[0] not in skip_top and not rel.endswith((".tmp", ".part")):
                    local[rel] = p.stat().st_size
    rows, gets, puts = [], [], []
    import tempfile
    for name, keys in MERGE_CSVS.items():
        if name not in remote and name not in local:
            continue
        ldf, lnote = read_csv(lbase / name)
        rdf, rnote = pd.DataFrame(), "missing"
        if name in remote:
            tmp = Path(tempfile.mkdtemp()) / name
            try:
                pull_file(vol, f"{rbase}/{name}", tmp)
                rdf, rnote = read_csv(tmp)
            except Exception as e:
                rdf, rnote = None, f"download failed ({type(e).__name__})"
        if ldf is None or rdf is None:
            rows.append([name, "skip", f"local {lnote} / remote {rnote}"])
            continue
        cols = list(ldf.columns) + [c for c in rdf.columns if c not in ldf.columns]
        merged = canon(pd.concat([ldf, rdf], ignore_index=True, sort=False), keys, cols)
        if direction in ("down", "both") and not _same_rows(merged, canon(ldf, keys, cols), keys):
            rows.append([name, f"⬇ merge {len(ldf)}→{len(merged)}", rnote])
            if not dry:
                atomic_write(merged, lbase / name)
        if direction in ("up", "both") and not _same_rows(merged, canon(rdf, keys, cols), keys):
            rows.append([name, f"⬆ merge {len(rdf)}→{len(merged)}", lnote])
            if not dry:
                tmp = Path(tempfile.mkdtemp()) / name
                atomic_write(merged, tmp)
                puts.append((tmp, f"{rbase}/{name}"))
    keep_sub = {}
    for rel in sorted(set(local) | set(remote)):
        if rel in MERGE_CSVS:
            continue
        in_l, in_r = rel in local, rel in remote
        if in_r and (not in_l or (rel.split("/")[-1] in LATEST_ONLY and local[rel] != remote[rel])):
            if direction in ("down", "both"):
                rows.append([rel, "⬇ download", f"{remote[rel]:,} B"])
                gets.append(rel)
                if in_l and rel.endswith("training_summary.json"):
                    keep_sub[rel] = _read_submission(lbase / rel)
        elif in_l and not in_r and direction in ("up", "both"):
            rows.append([rel, "⬆ upload", f"{local[rel]:,} B"])
            puts.append((lbase / rel, f"{rbase}/{rel}"))
    if not dry:
        t0 = time.time()
        failed = []
        for rel in gets:
            try:
                pull_file(vol, f"{rbase}/{rel}", lbase / rel)
            except Exception as e:
                failed.append((rel, f"{type(e).__name__}: {e}"))
        for rel, sub in keep_sub.items():
            _restore_submission(lbase / rel, sub)
        try:
            push_files(vol, puts)
        except Exception as e:
            failed.append(("upload batch", f"{type(e).__name__}: {e}"))
        if gets or puts:
            print(f"    ⚡ {len(gets)} down, {len(puts)} up in {time.time() - t0:.1f}s")
        for rel, err in failed:
            print(f"    ⚠️  {rel}: {err[:160]}")
    _table(f"{exp} - {'DRY RUN, nothing written' if dry else 'synced'}",
           ["file", "action", "detail"], rows, "🔄")
    if not rows:
        print("    ✔ already in sync")
    return {"ok": True, "down": len(gets), "up": len(puts)}


def _same_rows(a: pd.DataFrame, b: pd.DataFrame, keys) -> bool:
    """Same rows regardless of order (canon only orders by run and step, not by every key)."""
    if len(a) != len(b) or list(a.columns) != list(b.columns):
        return False
    k = [c for c in keys if c in a.columns] or list(a.columns)

    def _norm(df):
        # two pandas versions print the same float differently (-1.90618092449042 vs
        # -1.9061809244904202); compare numbers at 10 significant digits, text as text
        def f(x):
            try:
                return f"{float(x):.10g}"
            except (TypeError, ValueError):
                return x
        return df.map(f).sort_values(k, kind="stable").reset_index(drop=True)
    return _norm(a).equals(_norm(b))


def _read_submission(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")).get("submission")
    except Exception:
        return None


def _restore_submission(path: Path, keep) -> None:
    """Put a hand-filled submission block back after the remote summary overwrote it."""
    if not keep or not any(v is not None for v in keep.values()):
        return
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        if any(v is not None for v in (d.get("submission") or {}).values()):
            return
        d["submission"] = keep
        Path(path).write_text(json.dumps(d, indent=2), encoding="utf-8")
        print(f"    📌 kept the submission record in {Path(path).name}")
    except Exception as e:
        print(f"    ⚠️  could not restore the submission block: {e}")


def pull_checkpoint(cfg: dict, exp_dir, name: str = "best.pt") -> Path:
    """Download one checkpoint of this run from the runs volume into results/checkpoints/."""
    rd, ckd = cfg["output"]["run_dir"], cfg["output"]["checkpoints_dir"]
    dest = Path(exp_dir) / rd / ckd / name
    t0 = time.time()
    pull_file(cfg["modal"]["runs_volume"], f"{cfg['experiment']['name']}/{rd}/{ckd}/{name}", dest)
    print(f"  ⬇ {name} ({dest.stat().st_size / 1e6:.0f} MB) in {fmt(time.time() - t0)} -> {dest}")
    return dest

def atomic_write(df: pd.DataFrame, path: Path):
    """Temp file + replace, so a killed sync can never leave a half-written log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
    os.replace(tmp, path)


# =============================================================================
# CSV merging
# =============================================================================
def read_csv(path: Path):
    """(frame, note). frame=None means unreadable - that side must never be trusted.

    Everything is read as text: a merge should move rows around, never reformat
    the numbers inside them.
    """
    try:
        if not path.exists():
            return pd.DataFrame(), "missing"      # absent is fine; None means CORRUPT
        if path.stat().st_size == 0:
            return pd.DataFrame(), "empty"
        df = pd.read_csv(path, dtype=str, keep_default_na=False, engine="python",
                         on_bad_lines="skip")
        return df, f"{len(df)} rows"
    except pd.errors.EmptyDataError:
        return pd.DataFrame(), "header only"
    except Exception as e:                        # noqa: BLE001
        return None, f"CORRUPT ({type(e).__name__})"


def _keycols(df: pd.DataFrame, keys) -> list:
    k = [c for c in keys if c in df.columns]
    return k or list(df.columns)


def canon(df: pd.DataFrame, keys, cols=None) -> pd.DataFrame:
    """Align columns, drop duplicate keys (richest row wins), sort by run then step."""
    df = df.copy()
    if cols is not None:
        cols = ["run_id"] + [c for c in cols if c != "run_id"]   # run_id always leads
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df = df[list(cols)]
    df = df.fillna("")
    if "run_id" in df.columns:
        # pre-run_id logs still have to merge; they all land in one "legacy" bucket
        df["run_id"] = df["run_id"].replace("", "legacy")
    if df.empty:
        return df
    step0 = next((c for c in ("global_step", "step") if c in df.columns), None)
    if step0:
        # a killed process leaves half a line behind; a real row always has a step
        df = df[pd.to_numeric(df[step0], errors="coerce").notna()]
    rank = (df != "").sum(axis=1)
    df = (df.assign(_rank=rank).sort_values("_rank", ascending=False, kind="stable")
            .drop_duplicates(subset=_keycols(df, keys), keep="first")
            .drop(columns="_rank"))
    step = next((c for c in ("global_step", "step") if c in df.columns), None)
    by = [c for c in ("run_id",) if c in df.columns]
    if step:
        df = df.assign(_n=pd.to_numeric(df[step], errors="coerce").fillna(-1))
        by.append("_n")
    if by:
        df = df.sort_values(by, kind="stable")
    return df.drop(columns=[c for c in ("_n",) if c in df.columns]).reset_index(drop=True)
# =============================================================================
# plots - post-hoc PNGs from the two CSVs. CPU only, no torch needed.
# =============================================================================
def _safe(label: str, fn, *args, **kwargs):
    """Run fn but never let it kill a run; warn and carry on."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        print(f"  ⚠️  {label} failed (continuing): {type(e).__name__}: {e}")
        return None


def _smooth(series, window: int):
    """Trailing rolling mean; min_periods=1 so the start of the curve survives."""
    if window and window > 1:
        return pd.Series(series).rolling(window, min_periods=1).mean()
    return pd.Series(series)


def _epoch_boundary_steps(df) -> list:
    """Steps where a new epoch starts - drawn as faint guides."""
    steps, prev = [], None
    if df is None or "epoch" not in df.columns:
        return steps
    for st, ep in zip(df["global_step"], df["epoch"]):
        if prev is not None and ep != prev:
            steps.append(st)
        prev = ep
    return steps


def _vlines(ax, steps):
    for s in steps:
        ax.axvline(s, color="0.85", lw=0.8, zorder=0)


def _mark_extreme(ax, x, y, mode: str = "max", color: str = "crimson"):
    """Star the best point of a curve and label it."""
    y = np.asarray(y, dtype=float)
    if len(y) == 0 or np.all(np.isnan(y)):
        return
    i = int(np.nanargmax(y)) if mode == "max" else int(np.nanargmin(y))
    xi = float(np.asarray(x)[i])
    ax.scatter([xi], [y[i]], marker="*", s=200, color=color, zorder=6)
    ax.annotate(f"{y[i]:.4f}\n@ step {int(xi)}", (xi, y[i]), textcoords="offset points",
                xytext=(8, -14), fontsize=8, color=color)


def _runs_in(df, col="run_id") -> list:
    """Run ids present, in first-seen order. Never blend two runs into one line."""
    if df is None or col not in df.columns:
        return [None]
    ids = [r for r in dict.fromkeys(df[col].astype(str).tolist()) if r and r != "nan"]
    return ids or [None]


def _run_slice(df, rid):
    if df is None:
        return None
    if rid is None or "run_id" not in df.columns:
        return df
    sub = df[df["run_id"].astype(str) == rid]
    return sub if len(sub) else None


def make_plots(cfg: dict, results_dir, out_subdir: str = "plots",
               smooth_window: int = 25, dpi: int = 130) -> list:
    """Training-curve PNGs from train_log.csv + val_log.csv -> results/plots/.

    Both CSVs can hold several runs (the run_id column), so every run is drawn as
    its own series and never averaged together.
    """
    import matplotlib
    matplotlib.use("Agg")                     # headless: write files, never open a window
    import matplotlib.pyplot as plt

    results_dir = Path(results_dir)
    cfg = with_defaults(cfg)
    o, tasks = cfg["output"], target_names(cfg)
    name = cfg.get("experiment", {}).get("name", "experiment")
    tr_path, va_path = results_dir / o["train_log_csv"], results_dir / o["val_log_csv"]
    plots_dir = results_dir / out_subdir
    plots_dir.mkdir(parents=True, exist_ok=True)

    _banner("PLOTS", "\U0001F4C8")
    print(f"  train log : {tr_path}")
    print(f"  val   log : {va_path}")
    print(f"  output    : {plots_dir}")
    tr = pd.read_csv(tr_path) if tr_path.exists() else None
    va = pd.read_csv(va_path) if va_path.exists() else None
    if tr is None:
        print("  ⚠️  no train_log.csv - skipping the train-based plots")
    if va is None:
        print("  ⚠️  no val_log.csv - skipping the validation-based plots")
    if tr is None and va is None:
        return []

    runs = _runs_in(tr if tr is not None else va)
    for df in (tr, va):                       # a run may appear in only one of the two
        if df is None:
            continue
        for r in _runs_in(df):
            if r not in runs:
                runs.append(r)
    colors = plt.get_cmap("tab10").colors
    cmap = {r: colors[i % len(colors)] for i, r in enumerate(runs)}
    single = len(runs) == 1
    bsteps = _epoch_boundary_steps(tr) if (single and tr is not None) else []
    print(f"  runs      : {', '.join(str(r) for r in runs)}")
    saved = []

    def _save(fig, fname):
        fig.tight_layout(); fig.savefig(plots_dir / fname, dpi=dpi); plt.close(fig)
        saved.append(fname); print(f"  ✅ {fname}")

    def _lbl(rid, extra=""):
        base = str(rid) if rid else "run"
        return f"{base}{extra}"

    # 1) loss: raw + smoothed train, val as markers, one colour per run
    def _plot_loss():
        fig, ax = plt.subplots(figsize=(9, 5))
        for r in runs:
            c = cmap[r]
            t = _run_slice(tr, r)
            if t is not None and "loss" in t.columns:
                ax.plot(t["global_step"], t["loss"], color=c, alpha=0.2, lw=0.8)
                ax.plot(t["global_step"], _smooth(t["loss"].values, smooth_window),
                        color=c, lw=1.8, label=_lbl(r, " train"))
            v = _run_slice(va, r)
            if v is not None and "val_loss" in v.columns:
                ax.plot(v["step"], v["val_loss"], color=c, ls="--", marker="o", ms=4,
                        lw=1.4, label=_lbl(r, " val"))
        _vlines(ax, bsteps)
        ax.set_xlabel("global step"); ax.set_ylabel("loss")
        ax.set_title(f"{name} - loss (train smoothed x{smooth_window})")
        ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        _save(fig, "loss_curves.png")

    # 2) one macro metric over steps, best point starred per run
    def _plot_macro(col, title, fname, mode="max", extra_col=None):
        if va is None or col not in va.columns:
            return
        fig, ax = plt.subplots(figsize=(9, 5))
        for r in runs:
            v = _run_slice(va, r)
            if v is None:
                continue
            ax.plot(v["step"], v[col], color=cmap[r], marker="o", ms=4, lw=1.8,
                    label=_lbl(r))
            _mark_extreme(ax, v["step"].values, v[col].values, mode, cmap[r])
            if extra_col and extra_col in v.columns and v[extra_col].notna().any():
                ax.plot(v["step"], v[extra_col], color=cmap[r], ls=":", marker="^",
                        ms=4, lw=1.2, alpha=0.7, label=_lbl(r, " " + extra_col.split("_")[0]))
        _vlines(ax, bsteps)
        ax.set_xlabel("global step"); ax.set_ylabel(col)
        ax.set_title(f"{name} - {title}"); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        _save(fig, fname)

    # 2b) the SAME macro metric, but read like a table: every validation point gets a
    #     tick carrying its exact global step and epoch, a dropline down to the axis so
    #     the eye can trace it, and its value printed on the marker.
    def _plot_macro_detailed(col, title, fname, mode="max"):
        if va is None or col not in va.columns:
            return
        # x is the POSITION of a validation, not its step: evaluations get denser late in
        # training, and on a linear step axis those points (and their labels) pile up
        # into an unreadable smear. Even spacing gives every point the same room.
        pts = []
        for r in runs:
            v = _run_slice(va, r)
            if v is None:
                continue
            eps = v["epoch"].values if "epoch" in v.columns else v["step"].values
            for st, ep in zip(v["step"].values, eps):
                pts.append((int(st), int(ep) if ep == ep else 0))
        pts = sorted(set(pts))
        if not pts:
            return
        pos = {st: i for i, (st, _) in enumerate(pts)}
        n = len(pts)
        fig, ax = plt.subplots(figsize=(max(11.0, 0.42 * n), 7.5))

        lo, hi = np.inf, -np.inf
        for r in runs:
            v = _run_slice(va, r)
            if v is not None and not np.all(np.isnan(v[col].values.astype(float))):
                y = v[col].values.astype(float)
                lo = min(lo, np.nanmin(y)); hi = max(hi, np.nanmax(y))
        if not np.isfinite(lo):
            return
        span = max(hi - lo, 0.004)
        floor = lo - span * 0.18                 # droplines stop below every marker
        ax.set_ylim(floor, hi + span * 0.30)     # headroom for the rotated value labels

        # a resumed run re-scores steps an earlier segment already scored, with slightly
        # different values; printing every one stacks the labels into an unreadable blot.
        # Each step's number is printed once, from the LAST segment that scored it.
        owner = {}
        for r in runs:
            v = _run_slice(va, r)
            if v is not None:
                for st, yv in zip(v["step"].values, v[col].values.astype(float)):
                    if yv == yv:
                        owner[int(st)] = r
        for r in runs:
            v = _run_slice(va, r)
            if v is None:
                continue
            c = cmap[r]
            x = np.array([pos[int(st)] for st in v["step"].values], dtype=float)
            y = v[col].values.astype(float)
            ax.vlines(x, floor, y, color=c, alpha=0.25, lw=1.0, zorder=1)
            ax.plot(x, y, color=c, marker="o", ms=5, lw=1.8, label=_lbl(r), zorder=3)
            best = int(np.nanargmax(y)) if mode == "max" else int(np.nanargmin(y))
            for i, (xi, yi) in enumerate(zip(x, y)):
                if yi != yi or owner.get(int(v["step"].values[i])) != r:
                    continue
                ax.annotate("%.4f" % yi, (xi, yi), textcoords="offset points",
                            xytext=(0, 8), ha="center", va="bottom",
                            fontsize=7.5, rotation=90,
                            color="crimson" if i == best else c,
                            fontweight="bold" if i == best else "normal", zorder=5)
            if not np.all(np.isnan(y)):
                ax.scatter([x[best]], [y[best]], marker="*", s=220, color="crimson",
                           zorder=6)

        ax.set_xlim(-0.7, n - 0.3)
        ax.set_xticks(range(n))
        ax.set_xticklabels(["%d\nep %d" % (st, ep) for st, ep in pts],
                           fontsize=7)
        ax.set_xlabel("global step (and epoch) at each validation")
        ax.set_ylabel(col)
        ax.set_title("%s - %s (every validation point, evenly spaced)" % (name, title))
        ax.legend(fontsize=8, loc="lower right")
        ax.grid(True, axis="y", alpha=0.3)
        _save(fig, fname)

    # 3) per-task small multiples, one panel per finding, one line per run
    def _plot_per_task(prefix, title, fname):
        if va is None:
            return
        cols = [(t, f"val_{prefix}_{t}") for t in tasks if f"val_{prefix}_{t}" in va.columns]
        if not cols:
            return
        ncol = 4
        nrow = int(math.ceil(len(cols) / ncol))
        fig, axes = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 2.4 * nrow),
                                 sharex=True, sharey=True)
        axes = np.atleast_1d(axes).ravel()
        for ax, (t, c) in zip(axes, cols):
            for r in runs:
                v = _run_slice(va, r)
                if v is not None:
                    ax.plot(v["step"], v[c], color=cmap[r], marker="o", ms=2.5, lw=1.3,
                            label=_lbl(r))
            if prefix == "auroc":
                ax.axhline(0.5, color="0.6", lw=0.7, ls=":")     # chance level
            ax.set_title(t, fontsize=9); ax.grid(True, alpha=0.3)
        for ax in axes[len(cols):]:
            ax.axis("off")
        if len(runs) > 1 or runs[0]:
            axes[0].legend(fontsize=7, loc="lower right", framealpha=0.7)
        fig.suptitle(f"{name} - {title}", fontsize=11)
        _save(fig, fname)

    # 4) macro F1 / precision / recall / specificity at 0.5
    def _plot_op_point():
        if va is None:
            return
        series = [("val_f1", "F1"), ("val_precision", "precision"),
                  ("val_recall", "recall"), ("val_specificity", "specificity")]
        series = [s for s in series if s[0] in va.columns]
        if not series:
            return
        fig, ax = plt.subplots(figsize=(9, 5))
        styles = ["-", "--", ":", "-."]
        for r in runs:
            v = _run_slice(va, r)
            if v is None:
                continue
            for (col, lbl), st in zip(series, styles):
                ax.plot(v["step"], v[col], color=cmap[r], ls=st, lw=1.5, marker="o",
                        ms=3, label=_lbl(r, f" {lbl}"))
        _vlines(ax, bsteps)
        ax.set_xlabel("global step"); ax.set_ylabel("score @ threshold 0.5")
        ax.set_title(f"{name} - operating point (threshold 0.5)")
        ax.legend(fontsize=7, ncol=2); ax.grid(True, alpha=0.3)
        _save(fig, "macro_f1_precision_recall.png")

    # 5) learning rate
    def _plot_lr():
        if tr is None or "lr" not in tr.columns:
            return
        fig, ax = plt.subplots(figsize=(9, 4))
        for r in runs:
            t = _run_slice(tr, r)
            if t is not None:
                ax.plot(t["global_step"], t["lr"], color=cmap[r], lw=1.6, label=_lbl(r))
        _vlines(ax, bsteps)
        ax.set_xlabel("global step"); ax.set_ylabel("learning rate")
        ax.set_title(f"{name} - learning rate (warmup + cosine)")
        ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        _save(fig, "learning_rate.png")

    # 6) throughput / GPU memory / gradient norm, stacked
    def _plot_diagnostics():
        if tr is None:
            return
        fig, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
        _u = cfg["logging"].get("sub_unit") or cfg["logging"].get("unit") or "sample"
        panels = [("units_s", f"{_u}s / s (compute)"), ("gpu_mem_gb", "GPU mem peak (GB)"),
                  ("gnorm", "grad norm")]
        for ax, (col, ylab) in zip(axes, panels):
            for r in runs:
                t = _run_slice(tr, r)
                if t is None or col not in t.columns:
                    continue
                ax.plot(t["global_step"], t[col], color=cmap[r], alpha=0.25, lw=0.8)
                ax.plot(t["global_step"], _smooth(t[col].values, smooth_window),
                        color=cmap[r], lw=1.6, label=_lbl(r))
            ax.set_ylabel(ylab); ax.grid(True, alpha=0.3); _vlines(ax, bsteps)
        axes[0].set_title(f"{name} - throughput / memory / gradients")
        axes[0].legend(fontsize=8); axes[-1].set_xlabel("global step")
        _save(fig, "training_diagnostics.png")

    # update-to-weight ratio, if the run logged it. Its own CSV, not train_log, because
    # it is one row PER TENSOR per step rather than one row per step.
    def _plot_ud():
        ud_csv = results_dir / "ud_ratio.csv"
        if not ud_csv.exists():
            return
        d = pd.read_csv(ud_csv)
        if d.empty:
            return

        def _ishead(n):
            # NOT a substring test on "fc": every ConvNeXt block has mlp.fc1/mlp.fc2,
            # so that matched 100+ trunk tensors and put them all in the legend.
            return "backbone" not in n and any(k in n for k in ("head", "classifier", "fc"))

        def _depth(n):
            # natural sort: plain string order puts blocks.10 before blocks.2, which
            # scrambled the depth axis into noise.
            return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", n)]

        head = sorted([n for n in d["param"].unique() if _ishead(n)], key=_depth)
        trunk = sorted([n for n in d["param"].unique() if not _ishead(n)], key=_depth)
        names = trunk + head                       # shallow trunk -> deep trunk -> head
        steps = sorted(d["step"].unique())
        vc = plt.get_cmap("viridis")
        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13, 9),
                                      gridspec_kw={"height_ratios": [2, 1]})

        # a single sample draws nothing as a line, so fall back to markers
        style = dict(marker="o", ms=3, ls="none") if len(steps) < 2 else dict(lw=0.7)
        for i, n in enumerate(trunk):
            t = d[d["param"] == n].sort_values("step")
            ax.plot(t["step"], t["log10_ud"], color=vc(i / max(len(trunk) - 1, 1)),
                    alpha=0.55, **style)
        for n in head:
            t = d[d["param"] == n].sort_values("step")
            ax.plot(t["step"], t["log10_ud"], color="crimson", zorder=5,
                    label=f"HEAD  {n}", **dict(style, **({} if len(steps) < 2 else {"lw": 2.2})))
        # one proxy entry for the 100+ trunk curves, instead of 100+ legend rows
        ax.plot([], [], color=vc(0.5), lw=2, label=f"trunk ({len(trunk)} tensors)")
        ax.axhline(-3, color="k", ls="--", lw=1.2, label="-3  (from-scratch target)")
        ax.axhspan(-6, -5, color="steelblue", alpha=0.10,
                   label="-5..-6  (pretrained drift)")
        ax.set_ylabel("log10(update / weight)")
        ax.set_title(f"{name} - update-to-weight ratio")
        ax.legend(fontsize=8, loc="best"); ax.grid(True, alpha=0.3)
        _vlines(ax, bsteps)

        last = d[d["step"] == d["step"].max()].set_index("param").reindex(names)
        xs = range(len(names))
        ax2.plot(xs, last["log10_ud"].values, "-", lw=0.8, color="0.6", zorder=1)
        ax2.scatter(list(xs)[:len(trunk)], last["log10_ud"].values[:len(trunk)],
                    s=12, color="steelblue", label="trunk", zorder=3)
        ax2.scatter(list(xs)[len(trunk):], last["log10_ud"].values[len(trunk):],
                    s=45, color="crimson", marker="*", label="head", zorder=4)
        ax2.axhline(-3, color="k", ls="--", lw=1.2)
        ax2.axhspan(-6, -5, color="steelblue", alpha=0.10)
        ax2.set_xlabel("tensor, shallow trunk -> deep trunk -> head")
        ax2.set_ylabel("log10(update / weight)")
        ax2.set_title(f"profile at step {int(d['step'].max())}")
        ax2.legend(fontsize=8, loc="best"); ax2.grid(True, alpha=0.3)
        _save(fig, "ud_ratio.png")

    _safe("plot:loss", _plot_loss)
    # every scalar val metric gets its own curve; the monitored one also the detailed view
    mon, mode = monitor_spec(cfg)
    extra = []
    if va is not None:
        names_ = set(tasks)
        extra = sorted({c.split("_", 1)[0] for c in va.columns
                        if c.endswith("_" + mon) and not c.startswith("val_")})
        for col in [c for c in va.columns if c.startswith("val_")
                    and c not in ("val_secs", "val_sample_count")
                    and not any(c.endswith("_" + t) for t in names_)
                    and pd.api.types.is_numeric_dtype(va[c])]:
            m_ = col[4:]
            mm = "min" if any(m_.endswith(k) or m_ == k for k in _MIN_METRICS) else "max"
            _safe(f"plot:{m_}", _plot_macro, col, f"validation {m_}", f"val_{m_}.png", mm,
                  next((f"{s}_{m_}" for s in extra if f"{s}_{m_}" in va.columns), None))
    _safe("plot:monitor_detailed", _plot_macro_detailed, f"val_{mon}",
          f"validation {mon} (monitored)", f"val_{mon}_detailed.png", mode)
    for s in extra:
        _safe(f"plot:{s}_detailed", _plot_macro_detailed, f"{s}_{mon}",
              f"{s} {mon} (report only)", f"{s}_{mon}_detailed.png", mode)
    for k in ("auroc", "auprc", "f1", "rmse", "mae", "r2", "pearson"):
        _safe(f"plot:per_target_{k}", _plot_per_task, k, f"per-target {k}", f"per_target_{k}.png")
    _safe("plot:op_point", _plot_op_point)
    _safe("plot:lr", _plot_lr)
    _safe("plot:diagnostics", _plot_diagnostics)
    _safe("plot:ud_ratio", _plot_ud)
    print(f"  \U0001F4C8 wrote {len(saved)} plot(s) -> {plots_dir}")
    return saved

def _json_safe(obj):
    """Make a dict JSON-valid: NaN/inf -> null, numpy scalars -> python."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        v = float(obj)
        return v if math.isfinite(v) else None
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    return obj


# =============================================================================
# inference
# =============================================================================
def resolve_checkpoint(exp_dir, cfg: dict, which="best") -> Path:
    """best | last | top1..topK | <step> | <path> -> a checkpoint file of this run."""
    ckd = Path(exp_dir) / cfg["output"]["run_dir"] / cfg["output"]["checkpoints_dir"]
    if isinstance(which, str) and re.fullmatch(r"top\d+", which):
        track = json.loads((ckd / "top_k.json").read_text())
        return ckd / track[int(which[3:]) - 1]["file"]
    p = _resolve_resume(which, ckd)
    if p is None:
        raise FileNotFoundError(f"no checkpoint {which!r} under {ckd}")
    return p


def load_weights(model: nn.Module, path, prefer_ema: bool = True, strict: bool = True,
                 device=None) -> dict:
    """Load a checkpoint's weights into model (EMA weights when present and preferred).
    Returns the checkpoint dict (cfg, epoch, step, score ...)."""
    ck = torch.load(Path(path), map_location="cpu", weights_only=False)
    sd = ck.get("model", ck) if isinstance(ck, dict) else ck
    used = "model"
    if prefer_ema and isinstance(ck, dict) and ck.get("ema"):
        sd, used = ck["ema"]["module"], "ema"
    if any(k.startswith("_orig_mod.") for k in sd):
        sd = {k[len("_orig_mod."):] if k.startswith("_orig_mod.") else k: v for k, v in sd.items()}
    _uncompiled(model).load_state_dict(sd, strict=strict)
    if device is not None:
        model.to(device)
    print(f"  ✅ loaded {used} weights from {Path(path).name}  (epoch {ck.get('epoch') if isinstance(ck, dict) else '?'}, "
          f"step {ck.get('step') if isinstance(ck, dict) else '?'}, score {ck.get('score') if isinstance(ck, dict) else '?'})")
    return ck if isinstance(ck, dict) else {}


def tta_hflip(x):
    """Horizontal flip of a 4-D image batch (last dim)."""
    return torch.flip(x, dims=[-1]) if torch.is_tensor(x) and x.ndim >= 3 else x


def tta_vflip(x):
    return torch.flip(x, dims=[-2]) if torch.is_tensor(x) and x.ndim >= 3 else x


@torch.no_grad()
def predict(model: nn.Module, data, cfg: dict, hooks: Hooks | None = None, device=None,
            tta: list | None = None, batch_size: int | None = None,
            num_workers: int | None = None, average: str = "logits",
            progress_every: float = 10.0) -> dict:
    """Run a Dataset or DataLoader -> {"logits", "probs", "ids", "targets"}.

    tta: list of input transforms (e.g. [tta_hflip]); the identity is always included and
    outputs are averaged in logit space ("logits") or after activation ("probs").
    Prints a throttled progress line with samples/s and ETA.
    """
    cfg = with_defaults(cfg)
    hooks = hooks or Hooks()
    device = device or pick_device(cfg)
    if isinstance(data, DataLoader):
        loader = data
    else:
        vbs, vnw = val_loader_settings(cfg)
        nw = vnw if num_workers is None else int(num_workers)
        loader = DataLoader(data, batch_size=int(batch_size or vbs), shuffle=False,
                            num_workers=nw, pin_memory=device.type == "cuda",
                            collate_fn=getattr(data, "collate_fn", None))
    model.eval().to(device)
    use_amp = cfg["training"]["amp"] and device.type == "cuda"
    views = [None] + list(tta or [])
    L, Y, ids_all, seen = [], [], [], 0
    n_total = len(loader.dataset)
    t0 = last = time.time()
    for bi, batch in enumerate(loader, 1):
        x, y, ids = split_batch(batch)
        x = _prep(hooks, x, device, cfg)
        acc = None
        for v in views:
            xv = x if v is None else v(x)
            with torch.autocast("cuda", enabled=use_amp, dtype=amp_dtype(cfg)):
                o, _ = _fwd(hooks, model, xv)
            o = o.float()
            o = o if average == "logits" else torch.as_tensor(activate(o, cfg))
            acc = o.cpu() if acc is None else acc + o.cpu()
        L.append(acc / len(views))
        if y is not None and torch.is_tensor(y):
            Y.append(y.float().cpu())
        if ids is not None:
            ids_all += list(ids.tolist() if torch.is_tensor(ids) else ids)
        seen += batch_size_of(x)
        now = time.time()
        if progress_every and (now - last >= progress_every or bi == len(loader)):
            sps = seen / max(now - t0, 1e-9)
            print(f"     [predict] batch {bi}/{len(loader)} | {seen}/{n_total} "
                  f"({100 * seen / max(n_total, 1):.0f}%) | {sps:.1f}/s | "
                  f"elapsed {fmt(now - t0)} | ETA {fmt((n_total - seen) / max(sps, 1e-9))}", flush=True)
            last = now
    out = torch.cat(L).numpy()
    logits = out if average == "logits" else None
    probs = activate(out, cfg) if average == "logits" else out
    return {"logits": logits, "probs": probs,
            "ids": ids_all if len(ids_all) == len(out) else dataset_ids(loader.dataset),
            "targets": torch.cat(Y).numpy() if Y and sum(len(t) for t in Y) == len(out) else None}


# =============================================================================
# cross-validation folds and ensembling
# =============================================================================
def make_folds(df: pd.DataFrame, n_splits: int = 5, kind: str = "stratified",
               target=None, group: str | None = None, seed: int = 42,
               col: str = "fold") -> pd.DataFrame:
    """Copy of df with a fold column (0..n_splits-1).

    kind: kfold | stratified (target = one column) | group (group column) |
          stratified_group | multilabel (target = list of 0/1 columns; uses iterstrat's
          MultilabelStratifiedKFold when installed, else stratifies on the label count).
    Regression targets are stratified on 10 quantile bins.
    """
    from sklearn.model_selection import GroupKFold, KFold, StratifiedGroupKFold, StratifiedKFold
    df = df.reset_index(drop=True).copy()
    df[col] = -1
    X = np.zeros(len(df))

    def _strat(y):
        y = pd.Series(np.asarray(y))
        if pd.api.types.is_float_dtype(y) and y.nunique() > 20:      # continuous: quantile bins
            return pd.qcut(y, 10, labels=False, duplicates="drop").to_numpy()
        return y.to_numpy()

    if kind == "kfold":
        it = KFold(n_splits, shuffle=True, random_state=seed).split(X)
    elif kind == "stratified":
        it = StratifiedKFold(n_splits, shuffle=True, random_state=seed).split(X, _strat(df[target]))
    elif kind == "group":
        it = GroupKFold(n_splits).split(X, groups=df[group])
    elif kind == "stratified_group":
        it = StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed).split(
            X, _strat(df[target]), groups=df[group])
    elif kind == "multilabel":
        Ym = df[list(target)].to_numpy()
        try:
            from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
            it = MultilabelStratifiedKFold(n_splits=n_splits, shuffle=True,
                                           random_state=seed).split(X, Ym)
        except ImportError:
            print("  ⚠️  iterative-stratification not installed: stratifying on the label count")
            it = StratifiedKFold(n_splits, shuffle=True, random_state=seed).split(
                X, np.minimum((Ym > 0.5).sum(1), 3))
    else:
        raise ValueError(f"unknown fold kind {kind!r}")
    for f, (_, va) in enumerate(it):
        df.loc[va, col] = f
    sizes = df[col].value_counts().sort_index()
    print(f"  🧩 {n_splits} {kind} folds: " + ", ".join(f"f{k}={v}" for k, v in sizes.items()))
    return df


def load_predictions(pred_dir, split: str = "val", run_id: str | None = None) -> list:
    """Every saved prediction .npz in a run's predictions/ folder, oldest step first.
    -> [{"file", "run_id", "split", "epoch", "step", "score", "logits", "targets", "ids", "tasks"}]"""
    out = []
    for f in sorted(Path(pred_dir).glob(f"*_{split}_s*.npz")):
        d = np.load(f, allow_pickle=True)
        meta = list(d["meta"])
        if run_id and meta[0] != run_id:
            continue
        out.append({"file": f, "run_id": meta[0], "split": meta[1], "epoch": int(meta[2]),
                    "step": int(meta[3]), "score": float(meta[4]) if meta[4] else None,
                    "logits": d["logits"], "targets": d["targets"],
                    "ids": list(d["ids"]) if "ids" in d else list(d.get("study_ids", [])),
                    "tasks": list(d["tasks"])})
    out.sort(key=lambda r: (r["run_id"], r["step"]))
    return out


def align(preds: list, ids_key: str = "ids") -> list:
    """Reorder every member's rows to the first member's id order (raises on id mismatch)."""
    ref = list(preds[0][ids_key])
    pos = {k: i for i, k in enumerate(ref)}
    out = []
    for p in preds:
        idx = [pos[k] for k in p[ids_key]]
        order = np.argsort(idx)
        if sorted(idx) != list(range(len(ref))):
            raise ValueError("members cover different ids - cannot align")
        q = dict(p)
        for k in ("logits", "targets"):
            if q.get(k) is not None and len(q[k]) == len(order):
                q[k] = np.asarray(q[k])[order]
        q[ids_key] = ref
        out.append(q)
    return out


def blend(arrays: list, weights=None, method: str = "mean", task: str = "multilabel") -> np.ndarray:
    """Combine member outputs (same shape). method:
    mean      weighted average of the arrays as given (logits or probabilities)
    prob      activate each member's LOGITS first, then average the probabilities
    rank      average per-column ranks scaled to 0..1 (AUROC-style metrics only care about order)
    geo       geometric mean of probabilities (pass probabilities)"""
    A = [np.asarray(a, dtype=np.float64) for a in arrays]
    w = np.ones(len(A)) if weights is None else np.asarray(weights, dtype=np.float64)
    w = w / w.sum()
    if method == "prob":
        A = [activate(a, task).astype(np.float64) for a in A]
    elif method == "rank":
        from scipy.stats import rankdata
        A = [np.column_stack([rankdata(c) / len(c) for c in _as2d(a).T]).reshape(a.shape) for a in A]
    elif method == "geo":
        return np.exp(sum(wi * np.log(np.clip(a, 1e-9, None)) for wi, a in zip(w, A)))
    return sum(wi * a for wi, a in zip(w, A))


def hill_climb(members: dict, y_true, score_fn: Callable, maximize: bool = True,
               iters: int = 50, transform: Callable | None = None, verbose: bool = True) -> tuple:
    """Greedy forward selection WITH replacement (Caruana et al. 2004) over out-of-fold outputs.

    members: {name: array}; score_fn(y_true, blended) -> float; transform maps the averaged
    array before scoring (e.g. lambda a: activate(a, cfg) when averaging logits).
    Returns ({name: weight}, best score).
    """
    names = list(members)
    tf = transform or (lambda a: a)
    sc = {n: score_fn(y_true, tf(members[n])) for n in names}
    first = (max if maximize else min)(names, key=lambda n: sc[n])
    chosen, cur = [first], np.asarray(members[first], dtype=np.float64)
    best = sc[first]
    if verbose:
        _table("members alone", ["member", "score"],
               [[n, f"{sc[n]:.5f}"] for n in sorted(names, key=lambda n: -sc[n] if maximize else sc[n])], "🧗")
        print(f"  start: {first} = {best:.5f}")
    for _ in range(iters):
        k = len(chosen)
        cand = {n: score_fn(y_true, tf((cur * k + np.asarray(members[n])) / (k + 1))) for n in names}
        n_best = (max if maximize else min)(names, key=lambda n: cand[n])
        gain = cand[n_best] - best if maximize else best - cand[n_best]
        if gain <= 0:
            break
        cur = (cur * k + np.asarray(members[n_best])) / (k + 1)
        chosen.append(n_best)
        best = cand[n_best]
        if verbose:
            print(f"  + {n_best:<40s} -> {best:.5f}  ({'+' if maximize else '-'}{gain:.5f})")
    from collections import Counter
    cnt = Counter(chosen)
    weights = {n: c / len(chosen) for n, c in cnt.items()}
    if verbose:
        _table(f"hill-climb ensemble: {best:.5f}", ["member", "weight"],
               [[n, f"{w:.3f}"] for n, w in sorted(weights.items(), key=lambda kv: -kv[1])], "🏆")
    return weights, best


def leaderboard(runs_dir, split: str = "val") -> pd.DataFrame:
    """Best monitored score of every run under runs_dir (from val_log.csv + summary), printed."""
    rows = []
    for exp in sorted(p for p in Path(runs_dir).iterdir() if p.is_dir()):
        res = exp / "results"
        vl, sj = res / "val_log.csv", res / "training_summary.json"
        if not vl.exists():
            continue
        try:
            s = json.loads(sj.read_text()) if sj.exists() else {}
            mon, mode = s.get("monitor"), s.get("mode", "max")
            log = pd.read_csv(vl)
            if not mon or mon not in log.columns:
                mon = next((c for c in log.columns if c.startswith(f"{split}_")
                            and c != f"{split}_secs"), None)
            if mon is None or log[mon].dropna().empty:
                continue
            i = log[mon].idxmax() if mode == "max" else log[mon].idxmin()
            rows.append({"run": exp.name, "metric": mon, "best": float(log.loc[i, mon]),
                         "epoch": log.loc[i, "epoch"], "step": log.loc[i, "step"],
                         "validations": len(log), "runs": log["run_id"].nunique()
                         if "run_id" in log.columns else 1, "mode": mode})
        except Exception as e:
            print(f"  ⚠️  {exp.name}: {type(e).__name__}: {e}")
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("best", ascending=(df["mode"].iloc[0] == "min")).reset_index(drop=True)
        _table(f"leaderboard ({runs_dir})", ["#", "run", "metric", "best", "epoch", "step", "vals"],
               [[i + 1, r.run, r.metric, f"{r.best:.5f}", r.epoch, r.step, r.validations]
                for i, r in df.iterrows()], "🏁")
    return df



def _kaggle(*args, check=True, quiet=False, cwd=None):
    """Run the kaggle CLI with this PC's CA bundle (Avast intercepts HTTPS)."""
    import subprocess

    env = dict(os.environ)
    ca = Path.home() / ".certs" / "ca-bundle.pem"
    if ca.exists():
        env["REQUESTS_CA_BUNDLE"] = env["SSL_CERT_FILE"] = str(ca)
    # the CLI writes kernel logs with the console codepage, and our prints have
    # emoji in them - without this the log download dies on a charmap error
    env["PYTHONUTF8"] = "1"                    # this one is a flag, not an encoding name
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, "-m", "kaggle", *args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env,
                       cwd=str(cwd) if cwd else None)
    out = (r.stdout or "") + (r.stderr or "")
    if not quiet:
        print("    " + out.strip().replace("\n", "\n    "))
    if check and r.returncode:
        raise SystemExit(f"❌ kaggle {' '.join(args)} failed ({r.returncode})")
    return out


def wait_for_dataset(user: str, slug: str, tries: int = 40, secs: int = 30, local_dir=None):
    """Block until kaggle finishes processing the upload, and check EVERY file landed.

    Push a notebook too early and the dataset is not mounted - the kernel dies with a
    missing file. Kaggle can also report "Upload successful" and silently drop a file during
    ingest, and an OLD version lists the same names, so with local_dir every local file must
    be listed at its local size before this returns.
    """
    missing = ["?"]
    for i in range(tries):
        time.sleep(secs)
        try:
            # follows every page: the listing paginates at 20 rows by default, and a file on
            # page 2 reads exactly like a dropped one
            have = kaggle_dataset_files(f"{user}/{slug}")
        except SystemExit:
            continue
        if local_dir is None:
            missing = [] if have else ["(nothing listed yet)"]
        else:
            loc = {f.name: f.stat().st_size for f in Path(local_dir).iterdir()
                   if f.is_file() and f.name != "dataset-metadata.json"}
            missing = sorted(k for k in loc if loc[k] != have.get(k))
        if not missing:
            print(f"      ✅ dataset ready after {(i + 1) * secs}s ({len(have)} file(s)"
                  f"{', every size matches the upload' if local_dir is not None else ''})")
            return
        print(f"      … {len(missing)} file(s) not ready yet ({(i + 1) * secs}s)", flush=True)
    raise SystemExit(
        "❌ kaggle never listed %d file(s) after %ds: %s\n"
        "   Re-push the dataset before running a notebook on it."
        % (len(missing), tries * secs, ", ".join(missing[:10])))


def submission_message(cfg: dict, exp_dir) -> str:
    """`<exp> | val_<monitor> 0.8940 | <extra split> 0.8901` - read off the finished run.

    Read from val_log.csv, not training_summary.json: the CSV is merged across every
    resumption, so it is the one source that is always complete.
    """
    cfg = with_defaults(cfg)
    exp_dir = Path(exp_dir)
    name = cfg["experiment"]["name"]
    mon, mode = monitor_spec(cfg)
    res = exp_dir / cfg["output"]["run_dir"]
    try:
        log = pd.read_csv(res / cfg["output"]["val_log_csv"])
        col = f"val_{mon}"
        row = log.loc[log[col].idxmax() if mode == "max" else log[col].idxmin()]
        bits = [name, f"{col} {float(row[col]):.4f}"]
        for c in log.columns:
            if c.endswith("_" + mon) and c != col and pd.notna(row[c]):
                bits.append(f"{c} {float(row[c]):.4f}")
        return " | ".join(bits)
    except Exception:
        pass
    try:                                    # no CSV: fall back to the summary
        summary = json.loads((res / cfg["output"]["summary_json"]).read_text())
        return f"{name} | {summary['monitor']} {float(summary['best_score']):.4f}"
    except Exception:
        return name


def _kaggle_slug(title: str) -> str:
    """The slug Kaggle will actually derive from a kernel title.

    It slugifies the TITLE and ignores the id you asked for. So compute the slug the same
    way it does and use that as the id, rather than discovering the mismatch afterwards.
    """
    out = "".join(c if c.isalnum() else "-" for c in title.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def kaggle_title(name: str, suffix: str = "") -> str:
    """Kaggle rejects a dataset or kernel title outside 6-50 characters. Keep the suffix
    even when the name has to be cut, so a dataset and a notebook built from the same run
    never get identical titles."""
    t = f"{name} {suffix}".strip()
    if 6 <= len(t) <= 50:
        return t
    if len(t) < 6:
        return (t + " " + "-" * 6)[:6]
    return (f"{name[:50 - len(suffix) - 1]} {suffix}" if suffix else name[:50]).strip()


def _push_and_wait(user, notebook_slug, nb_dir, wait, poll_secs):
    """Push the notebook and wait. Returns (version, ok); ok False = error or cancel."""
    print(f"\n  notebook {user}/{notebook_slug}")
    out = _kaggle("kernels", "push", "-p", str(nb_dir))
    m = re.search(r"version\s+(\d+)", out, re.I)
    version = m.group(1) if m else None
    print(f"      pushed version {version or '?'}")
    if not wait:
        return version, True
    print("\n  waiting for the kernel to finish")
    # wall clock from "pushed" to "complete". Not the same as the kernel's own runtime
    # (kaggle queues before it starts), but it is the only figure visible from here, and
    # it upper-bounds the competition's runtime cap.
    wait_t0 = time.time()
    while True:
        st = _kaggle("kernels", "status", f"{user}/{notebook_slug}", quiet=True, check=False)
        low = st.lower()
        if "kernelworkerstatus" not in low and "status" not in low:
            # a failed status CALL (network, API hiccup) is not a finished kernel: retry, never crash
            print(f"      … status call failed, retrying: {st.strip()[:90]}")
            time.sleep(poll_secs)
            continue
        if "complete" in low or "error" in low or "cancel" in low:
            break
        print(f"      … {st.strip()[:90]}  ({fmt(time.time() - wait_t0)})", flush=True)
        time.sleep(poll_secs)
    el = time.time() - wait_t0
    if "complete" in low:
        print(f"      ✅ complete in {el / 60:.1f} min ({el / 3600:.2f} h, queue included)")
        return version, True
    print(f"      ❌ {st.strip()}")
    print("      fetch the log with: kaggle kernels output "
          f"{user}/{notebook_slug} -p .")
    return version, False

def kaggle_dataset_files(user_slug: str) -> dict:
    """{file name: bytes} of a Kaggle dataset's CURRENT version (follows every page)."""
    import csv as _csv
    import io as _io
    out, token = {}, None
    for _ in range(50):
        args = ["datasets", "files", user_slug, "--csv", "--page-size", "200"]
        if token:
            args += ["--page-token", token]
        txt = _kaggle(*args, quiet=True)
        m = re.search(r"Next Page Token = (\S+)", txt)
        token = m.group(1) if m else None
        body = txt[txt.find("name,size"):] if "name,size" in txt else ""
        for row in _csv.DictReader(_io.StringIO(body)):
            try:
                out[row["name"]] = int(row["size"])
            except (KeyError, ValueError, TypeError):
                pass
        if not token:
            break
    return out


kaggle = _kaggle                   # public name: kaggle("competitions", "list")


def kaggle_dataset_metadata(folder, user: str, slug: str, title: str | None = None,
                            license: str = "CC0-1.0") -> Path:
    """Write dataset-metadata.json into folder (the file `kaggle datasets create` reads)."""
    p = Path(folder) / "dataset-metadata.json"
    p.write_text(json.dumps({"title": kaggle_title(title or slug), "id": f"{user}/{slug}",
                             "licenses": [{"name": license}]}, indent=2), encoding="utf-8")
    return p


def kaggle_kernel_metadata(folder, user: str, slug: str, code_file: str, title: str | None = None,
                           competition: str | None = None, datasets=(), kernels=(), models=(),
                           gpu: bool = True, internet: bool = False, private: bool = True,
                           kernel_type: str = "notebook", language: str = "python") -> Path:
    """Write kernel-metadata.json (the file `kaggle kernels push` reads).

    Code competitions need internet off; their weights travel as a dataset/model source.
    Kaggle derives the slug from the TITLE, so the title is slugified to match `slug`.
    """
    t = title or slug.replace("-", " ")
    if _kaggle_slug(t) != slug:
        print(f"  ⚠️  Kaggle will slugify title {t!r} to {_kaggle_slug(t)!r}, not {slug!r}")
    meta = {"id": f"{user}/{slug}", "title": t, "code_file": code_file,
            "language": language, "kernel_type": kernel_type, "is_private": bool(private),
            "enable_gpu": bool(gpu), "enable_tpu": False, "enable_internet": bool(internet),
            "dataset_sources": list(datasets), "competition_sources": [competition] if competition else [],
            "kernel_sources": list(kernels), "model_sources": list(models)}
    p = Path(folder) / "kernel-metadata.json"
    p.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return p


def kaggle_dataset_push(folder, message: str = "update", wait: bool = True,
                        dir_mode: str = "zip") -> None:
    """Create the dataset, or add a new version when it exists; then wait until Kaggle
    lists every local file at its local size (Kaggle can silently drop files on ingest)."""
    folder = Path(folder)
    meta = json.loads((folder / "dataset-metadata.json").read_text(encoding="utf-8"))
    user, slug = meta["id"].split("/", 1)
    _banner(f"KAGGLE DATASET {meta['id']}", "📦")
    # kaggle CLI on Windows mangles -p paths, so run it from inside the folder with "."
    # `datasets status` answers 403 for a dataset that does not exist yet, so asking is
    # useless - try to create, and fall back to a new version if it is already there
    out = _kaggle("datasets", "create", "-p", ".", "--dir-mode", dir_mode, cwd=folder, check=False)
    low = out.lower()
    if any(k in low for k in ("already exists", "already in use", "409", "403")):
        print("      exists -> new version")
        _kaggle("datasets", "version", "-p", ".", "-m", message, "--dir-mode", dir_mode, cwd=folder)
    elif not any(k in low for k in ("successfully", "being created", "is being created")):
        raise SystemExit("❌ dataset upload failed: %s" % out.strip()[-500:])   # the END holds the reason
    if wait:
        wait_for_dataset(user, slug, local_dir=folder)


def kaggle_kernel_push(folder, wait: bool = True, poll_secs: int = 60) -> tuple:
    """Push a notebook/script folder (with kernel-metadata.json) and optionally wait for the
    run to finish. -> (version, ok)."""
    meta = json.loads((Path(folder) / "kernel-metadata.json").read_text(encoding="utf-8"))
    user, slug = meta["id"].split("/", 1)
    _banner(f"KAGGLE KERNEL {meta['id']}", "🚀")
    return _push_and_wait(user, slug, Path(folder), wait, poll_secs)


def kaggle_kernel_output(user_slug: str, dest) -> Path:
    """Download a finished kernel's output files and log into dest."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    _kaggle("kernels", "output", user_slug, "-p", str(dest))
    return dest


def kaggle_submit(competition: str, message: str, file: str = "submission.csv",
                  kernel: str | None = None, version: str | None = None) -> str:
    """Submit. A file competition uploads `file`; a code competition (kernel="user/slug")
    submits that kernel's output file, optionally a specific version. Spends an attempt."""
    args = ["competitions", "submit", "-c", competition, "-f", file, "-m", message]
    if kernel:
        args += ["-k", kernel]
        if version:
            args += ["-v", str(version)]
    return _kaggle(*args)


def kaggle_submissions(competition: str) -> str:
    """The competition's submission list (status, public score) as the CLI prints it."""
    return _kaggle("competitions", "submissions", "-c", competition)


def kaggle_download(competition: str, dest, unzip: bool = True) -> Path:
    """Download (and unzip) a competition's data into dest."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    _kaggle("competitions", "download", "-c", competition, "-p", str(dest))
    if unzip:
        import zipfile
        for z in dest.glob("*.zip"):
            with zipfile.ZipFile(z) as zf:
                zf.extractall(dest)
            print(f"  📂 unzipped {z.name}")
    return dest


# =============================================================================
# CRASH-RISK PROJECT (safe-distance): parts shared by stage 1, the late validation, later stages and the final test
#   risk_settings          one flat dict of the model / data / LoRA settings (from a stage's config.yaml)
#   frame_count            frames in a cached clip (from wide_frame_counts.json, no volume reads)
#   FixedWindows           fixed 2 s windows from the 16:9 cache (validation and test sets; never augmented)
#   risk_ap, calibration_error, risk_scores   the crash-risk scores
#   RiskModel              BADAS-Open + 16:9 + batched predictor + LoRA, one crash-risk logit per window
#   load_risk_checkpoint   load a saved stage checkpoint into a RiskModel
# =============================================================================
def risk_settings(cfg_yaml: dict, pkg_root) -> dict:
    """The model / data / LoRA settings as one flat dict (what the shared crash-risk parts below read).

    Arguments:
        cfg_yaml: a stage's config.yaml, read (needs its data, model and lora sections).
        pkg_root: the src/risk folder (data paths in the config are relative to it).
    """
    import wide_input as W                                 # the 16:9 input (frame shape, normalising, position patch)
    d, m, lo = cfg_yaml["data"], cfg_yaml["model"], cfg_yaml["lora"]
    return {"cache": d["cache"], "frame_counts": Path(pkg_root) / d["frame_counts"],
            "fps": d["fps"], "window_frames": d["window_frames"], "frame_h": W.WIDE_H, "frame_w": W.WIDE_W,
            "badas_repo": m["badas_repo"], "base_model": m["base_model"], "hf_cache": m["hf_cache"],
            "temperature": m["temperature"], "predictor_check_tol": m["predictor_check_tol"],
            "grad_checkpointing": m["grad_checkpointing"],
            "lora_rank": lo["rank"], "lora_alpha": lo["alpha"], "lora_dropout": lo["dropout"],
            "lora_targets": lo["targets"], "lora_expected_layers": lo["expected_layers"],
            "lora_fully_trained": lo["fully_trained"]}


_FRAME_COUNTS: dict = {}                     # counts file -> {"folder/clip": frames}, read once per file


def frame_count(path: str, counts_file) -> int:
    """Number of frames in a cached clip, looked up in the counts file (counted once by wide_frame_counts.py).

    Why not read the file: opening about 5,000 cache files on the Modal volume at start-up choked the GPU
    container (no progress for 9 minutes). The counts file ships with the code, so this reads nothing from the volume.

    Arguments:
        path:        a cached clip's .npy file (.../<cache folder>/<clip>.npy).
        counts_file: wide_frame_counts.json.
    """
    key_file = str(counts_file)
    if key_file not in _FRAME_COUNTS:
        _FRAME_COUNTS[key_file] = json.loads(Path(counts_file).read_text())
    p = Path(path)
    key = f"{p.parent.name}/{p.stem}"                                 # e.g. nexar_train_positive/00266
    if key not in _FRAME_COUNTS[key_file]:
        raise SystemExit(f"{key} is not in {Path(counts_file).name}: re-run wide_frame_counts.py")
    return _FRAME_COUNTS[key_file][key]


class FixedWindows(Dataset):
    """FIXED windows (a validation or test set): never augmented, the same every time they are scored."""

    def __init__(self, windows: list[dict], s: dict):
        """Find each window's clip file and end frame, and the facts the scores need.

        Arguments:
            windows: one dict per window (group, folder, clip, end / end_back, rank, label, nexar_group), as written by
                     make_val_windows.py / late_validation/make_windows.py.
            s:       risk_settings().
        """
        self.window_frames = s["window_frames"]
        # where each clip's frames are
        for w in windows:
            w["path"] = f"{s['cache']}/{w['folder']}/{w['clip']}.npy"
        # Nexar windows are given as "frames before the clip's last frame" (end_back), so we need each clip's
        # length to know the end frame. BDD windows already have their end frame.
        for w in windows:
            if w["end"] is None:
                w["end"] = frame_count(w["path"], s["frame_counts"]) - w["end_back"]   # e.g. back 0 = last frame
        self.windows = windows
        self.ids = [f"{w['group']}|{w['clip']}|{w['end']}" for w in windows]   # names in the prediction files
        self.targets = np.array([[w["label"]] for w in windows], np.float32)    # the right answers
        # Per-window facts the scores need. They line up with the model's outputs because the loader never
        # shuffles: output k belongs to window k.
        self.group = np.array([w["group"] for w in windows])                  # nexar_crash / nexar_normal / bdd_...
        self.rank = np.array([w["rank"] for w in windows])                    # 1st or 2nd window of its clip
        self.nexar_group = np.array([-1 if w["nexar_group"] is None else w["nexar_group"] for w in windows])  # -1: BDD
        # Nexar crash windows: seconds between the window's end and the crash (group's seconds + frames back / fps)
        self.end_back_s = np.array([(w["end_back"] or 0) / s["fps"] for w in windows])

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, i: int):
        w = self.windows[i]
        frames = np.array(np.load(w["path"], mmap_mode="r")[w["end"] - self.window_frames:w["end"]])   # writable copy
        return torch.from_numpy(frames), torch.tensor([w["label"]], dtype=torch.float32), self.ids[i]


def risk_ap(crash_risks: np.ndarray, normal_risks: np.ndarray) -> float:
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


def calibration_error(risk: np.ndarray, is_crash: np.ndarray) -> float:
    """0 = honest risk values (of windows given about 0.8, about 80% are crashes). Windows split into 10 bins by
    risk (0-0.1, ..., 0.9-1); in each bin the average risk is compared with the share that really are crashes;
    the gaps are added up, weighted by how many windows each bin holds.

    Arguments:
        risk:     the model's risk per window (0..1).
        is_crash: True / 1 for crash windows.
    """
    truth = np.asarray(is_crash, dtype=float)
    bin_of = np.clip((risk * 10).astype(int), 0, 9)                   # which of the 10 bins each window falls in
    gap = 0.0
    for b in range(10):
        in_bin = bin_of == b
        if in_bin.any():
            gap += abs(risk[in_bin].mean() - truth[in_bin].mean()) * in_bin.mean()
    return float(gap)


def risk_scores(risk: np.ndarray, win: FixedWindows, group_seconds: dict, thresholds,
                caught_at=(0.5, 0.9)) -> dict:
    """Every crash-risk score for one set of predictions. Works for any mix of window cases: the crash case is
    "nexar_crash", every other case is normal (e.g. nexar_normal, bdd_hard, bdd_normal).

      ap_crash_vs_all_normal       AP: crash windows vs every normal window
      ap_crash_vs_<case>           AP: crash vs one normal case
      nexar_official_map           Nexar's own score: per test group, LAST-frame windows only, crash vs nexar_normal,
                                   then the average (group_<s>s_official_ap: each group's AP)
      mean_risk_<case>             the average risk per case
      crash_<s>s_...               crash windows by how long before the crash they end: count, mean risk, % caught
      crash_caught_pct_at_<t>      % of crash windows above threshold t
      <case>_alarm_pct_at_<t>      % of a normal case's windows above t (false alarms)
      calibration_error            see calibration_error()

    Arguments:
        risk:          the model's risk (0..1) per window, in the windows' order.
        win:           the FixedWindows they were scored on.
        group_seconds: Nexar test group -> seconds before the crash its clips end ({0: 0.5, 1: 1.0, 2: 1.5}).
        thresholds:    the risk thresholds for the caught / alarm percentages.
        caught_at:     the thresholds for the per-timing crash rows.
    """
    cases = list(dict.fromkeys(win.group.tolist()))                    # every case present, in first-seen order
    normal_cases = [c for c in cases if c != "nexar_crash"]
    is_ = {c: win.group == c for c in cases}
    is_crash = win.group == "nexar_crash"
    crash = risk[is_crash]
    out = {"ap_crash_vs_all_normal": risk_ap(crash, risk[~is_crash])}
    for c in normal_cases:
        out[f"ap_crash_vs_{c}"] = risk_ap(crash, risk[is_[c]])

    # Nexar's official score (needs nexar_normal windows)
    last = win.rank == 1
    is_nn = win.group == "nexar_normal"
    per_group = []
    for g, sec in group_seconds.items():
        in_g = win.nexar_group == g
        ap = risk_ap(risk[is_crash & last & in_g], risk[is_nn & last & in_g])
        out[f"group_{sec}s_official_ap"] = ap
        per_group.append(ap)
    out["nexar_official_map"] = float(np.mean(per_group))

    for c in cases:
        out[f"mean_risk_{c}"] = float(risk[is_[c]].mean())

    # crash windows by how long before the crash they end (the group's seconds + how far back the window ends)
    before_s = np.array([group_seconds.get(g, np.nan) for g in win.nexar_group]) + win.end_back_s
    for sec in sorted(set(before_s[is_crash].tolist())):
        here = risk[is_crash & (before_s == sec)]
        out[f"crash_{sec}s_windows"] = int(len(here))
        out[f"crash_{sec}s_mean_risk"] = float(here.mean())
        for t in caught_at:
            out[f"crash_{sec}s_caught_pct_at_{t}"] = round(100.0 * float((here > t).mean()), 2)

    # at every threshold: crashes caught and false alarms per normal case
    for t in thresholds:
        out[f"crash_caught_pct_at_{t}"] = round(100.0 * float((crash > t).mean()), 2)
        for c in normal_cases:
            out[f"{c}_alarm_pct_at_{t}"] = round(100.0 * float((risk[is_[c]] > t).mean()), 2)

    out["calibration_error"] = calibration_error(risk, is_crash)
    return out


# ----- the crash-risk model --------------------------------------------------
def batched_predict_future(self, encoder_features: torch.Tensor) -> torch.Tensor:
    """BADAS's "future" prediction for the WHOLE batch in one call (BADAS's own code does one clip at a time).

    What the predictor does: the encoder turns a window into 3,584 tokens (the "present"). The predictor gets those
    plus 896 empty slots for the "future", fills the slots in, and returns them (each token = 1,024 numbers).
    It is told which positions are present (context) and which to fill (target) by two lists of positions.
    BADAS's loop builds those lists for one clip; here the same lists are repeated for every clip of the batch, so
    one call does them all. check_batched_predictor() proves it gives the same numbers before the model is used.
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


def check_batched_predictor(net: nn.Module, device, s: dict) -> float:
    """Stop unless the batched predictor gives the same numbers as BADAS's own one-clip-at-a-time loop.

    4 random clips, full precision. "Same" = the largest difference is under predictor_check_tol (tiny differences
    come from the order of additions inside the GPU, not from a different computation).

    Arguments:
        net:    BADAS's classifier (before LoRA).
        device: where to run the check (the GPU).
        s:      risk_settings().
    """
    net.eval()                                                        # no randomness (dropout off)
    x = torch.randn(4, s["window_frames"], 3, s["frame_h"], s["frame_w"], device=device)   # 4 random clips
    with torch.no_grad():                                             # no gradients needed for a check
        present = net._extract_video_features(x)                      # the encoder's 3,584 tokens per clip
        loop = type(net)._predict_future_features(net, present)      # BADAS's own code (one clip at a time)
        batched = batched_predict_future(net, present)               # ours (all clips at once)
    diff = float((loop - batched).abs().max())                        # the largest difference anywhere
    print(f"  ✅ batched predictor vs BADAS's per-clip loop: largest difference {diff:.2e} "
          f"(allowed {s['predictor_check_tol']:g})")
    if not diff <= s["predictor_check_tol"]:
        raise SystemExit("batched predictor differs from BADAS's loop: stopping")
    return diff


def add_lora(net: nn.Module, s: dict) -> nn.Module:
    """Wrap BADAS-Open with LoRA, switch on the small parts that train fully, then CHECK that nothing is left out.

    LoRA in one sentence: each chosen weight matrix W stays frozen, and next to it the model learns a small update
    B x A (A: 16 x input size, B: output size x 16, "rank 16"), added as W + (alpha / rank) x B x A = W + 2 x B x A.
    B starts at zero, so at step 0 the model is exactly BADAS-Open.

    Stops when:
      - the number of LoRA layers is not the one expected (a renamed layer would silently lose its LoRA),
      - any frozen weight is neither the base of a LoRA layer nor a backup copy (= it would be left out of training),
      - the predictor is no longer one shared object (BADAS lists it twice: predictor and backbone.predictor).

    Arguments:
        net: BADAS's classifier (the network to wrap).
        s:   risk_settings().
    """
    from peft import LoraConfig, get_peft_model                      # peft: the library that adds LoRA

    config = LoraConfig(r=s["lora_rank"], lora_alpha=s["lora_alpha"], lora_dropout=s["lora_dropout"],
                        bias="none",                          # biases are not trained (standard for LoRA)
                        target_modules=s["lora_targets"],     # which layers get LoRA (the 219, by name)
                        modules_to_save=s["lora_fully_trained"])   # trained fully: time-attention + head
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
    _table("LoRA coverage check", ["check", "result"], [
        ("LoRA layers", f"{len(lora_layers)} (expected {s['lora_expected_layers']})  {by_type}"),
        ("weights left out of training", len(left_out)),
        ("predictor still one shared object", shared),
        ("trainable values", f"{trainable / 1e6:.2f} M of {total / 1e6:.1f} M"),
    ], "🧩")
    if len(lora_layers) != s["lora_expected_layers"] or left_out or not shared:
        raise SystemExit(f"LoRA coverage check failed: {len(lora_layers)} layers, left out {left_out[:10]}, "
                         f"shared predictor {shared}")
    return model


def check_gradients_reach_everything(model: nn.Module, device, s: dict) -> None:
    """One forward + backward pass on 2 random clips: every trainable weight must receive a gradient.

    A weight with no gradient is cut off from the loss and would never learn (a "dead path"). Two details:
      - drop_path (training randomly skips whole blocks) is paused, else a skipped block would look dead;
      - LoRA's A matrices get a gradient of exactly zero on this first pass (B is still zero): zero is fine, MISSING
        (None) is not.

    Arguments:
        model:  the full RiskModel (BADAS + LoRA).
        device: where to run the check (the GPU).
        s:      risk_settings().
    """
    model.train()                                                     # training mode (as in real training)
    drop_path = [m for m in model.modules() if type(m).__name__ == "VJEPA2DropPath"]
    for m in drop_path:
        m.eval()                                                      # eval mode = never skip
    with torch.autocast("cuda", dtype=torch.bfloat16):                # same 16-bit maths as training
        out = model(torch.randn(2, s["window_frames"], 3, s["frame_h"], s["frame_w"], device=device))
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

    def __init__(self, device, s: dict):
        """Load BADAS-Open, patch it for 16:9, add LoRA, and run the start-up checks.

        Arguments:
            device: where the model lives (the GPU).
            s:      risk_settings().
        """
        super().__init__()
        from huggingface_hub import snapshot_download               # downloads from Hugging Face (or uses the cache)
        import wide_input as W                                      # the 16:9 position patch

        self.temperature = s["temperature"]
        # --- load BADAS-Open exactly as its released code does (code + weights from Hugging Face) ---
        repo = Path(snapshot_download(s["badas_repo"], allow_patterns=["src/*", "src/**/*", "weights/*"]))
        sys.path.insert(0, str(repo / "src"))                       # so BADAS's own code can be imported
        from models.vjepa import VJEPAModel                         # BADAS's loader class
        badas = VJEPAModel(model_name=s["base_model"], checkpoint_path=str(repo / "weights" / "badas_open.pth"),
                           device=str(device), frame_count=s["window_frames"], img_size=s["frame_h"],
                           target_fps=float(s["fps"]), use_sliding_window=False)
        badas.load()                                                # builds the network and loads its weights
        net = badas.model                                           # the network: encoder, predictor, time-attention, head
        # 16:9: tell every attention layer the real token grid (16 rows x 28 columns), see wide_input.py
        n_patched = W.patch_positions(net, s["frame_h"], s["frame_w"])
        print(f"  ✅ 16:9 input: {n_patched} attention layers use the {s['frame_h'] // 16} x {s['frame_w'] // 16} "
              f"patch grid (expected 36)")
        if n_patched != 36:
            raise SystemExit("position patch: not every attention layer found: stopping")
        if s["grad_checkpointing"] and hasattr(net.backbone, "gradient_checkpointing_enable"):
            net.backbone.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
            print("  🧮 gradient checkpointing ON (less memory, slower)")

        # --- prove the batched predictor equals BADAS's loop, then switch to it ---
        check_batched_predictor(net, device, s)
        x = torch.randn(2, s["window_frames"], 3, s["frame_h"], s["frame_w"], device=device)   # 2 random clips
        with torch.no_grad():
            before = net(x)                                         # plain BADAS-Open's 2 scores on them
        import types
        net._predict_future_features = types.MethodType(batched_predict_future, net)   # use ours from now on

        # --- LoRA on every layer (the coverage check runs inside) ---
        self.net = add_lora(net, s)

        # --- start check: LoRA starts at zero, so the outputs must still be plain BADAS-Open's ---
        self.net.eval()
        with torch.no_grad():
            diff = float((self.net(x) - before).abs().max())        # same 2 clips, now through LoRA + batched predictor
        print(f"  ✅ start check: after adding LoRA + the batched predictor, outputs differ from plain BADAS-Open by "
              f"{diff:.2e} (must be about 0)")
        if not diff <= s["predictor_check_tol"]:
            raise SystemExit("the model at step 0 is not BADAS-Open: stopping")
        check_gradients_reach_everything(self, device, s)
        # the names of the weights training changes (what the checkpoints store)
        self._trainable = {n for n, p in self.named_parameters() if p.requires_grad}

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: a batch of windows, B x 16 x 3 x 256 x 448 (already normalised). Returns B x 1.

        BADAS's head gives 2 scores per window: s_safe and s_crash. Its risk is softmax([s_safe, s_crash] / 2) for
        the crash class. With only two classes, that softmax is exactly sigmoid((s_crash - s_safe) / 2). So we pass
        on ONE number per window, z = (s_crash - s_safe) / 2, and sigmoid(z) is BADAS's risk.

        The loss ("bce") is binary cross-entropy between sigmoid(z) and the window's label (1, a ramp value from 0.7
        to 1, or 0). That is the same loss as BADAS's own 2-class cross-entropy, with a soft target.

        Arguments:
            x: the batch, B x 16 x 3 x 256 x 448, normalised (wide_input.normalise).
        """
        scores = self.net(x)                                     # B x 2: column 0 = safe, column 1 = crash
        z = (scores[:, 1] - scores[:, 0]) / self.temperature     # one number per window
        return z.unsqueeze(1)                                    # B x 1 (one target: crash_risk)

    # --- checkpoints store only what training changes ---
    # The frozen 330 M BADAS weights never change, so a checkpoint holds just the 14 M trainable ones (about
    # 57 MB, plus the optimizer state); the frozen part is reloaded from BADAS-Open at every start. save_checkpoint
    # and load_checkpoint call these two methods.
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


def load_risk_checkpoint(model: RiskModel, path, step: int | None = None) -> dict:
    """Load a saved checkpoint's trainable weights into a RiskModel (strict: every trainable weight must be there).

    Arguments:
        model: the RiskModel (built fresh = plain BADAS-Open).
        path:  the checkpoint file (step<N>.pt, top_step<N>.pt, best.pt, last.pt).
        step:  if given, stop unless the checkpoint holds exactly this step.
    """
    ck = torch.load(path, map_location="cpu", weights_only=False)
    if step is not None and int(ck.get("step", -1)) != step:
        raise SystemExit(f"{Path(path).name} holds step {ck.get('step')}, not {step}")
    model.load_state_dict(ck["model"])
    return ck


# =============================================================================
# CLI:  python shared_code.py <command> ...
# =============================================================================
def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="shared_code: plots, sync, leaderboard, config")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plot", help="draw the curves of one run from its CSVs")
    p.add_argument("exp_dir")
    p = sub.add_parser("sync", help="bring a run's results home from its Modal runs volume")
    p.add_argument("exp_dir")
    p.add_argument("--direction", choices=["down", "up", "both"], default="down")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--checkpoints", action="store_true", help="also sync checkpoints")
    p = sub.add_parser("pull", help="download one checkpoint of a run from Modal")
    p.add_argument("exp_dir")
    p.add_argument("--name", default="best.pt")
    p = sub.add_parser("leaderboard", help="best score of every run under a runs/ folder")
    p.add_argument("runs_dir")
    p = sub.add_parser("config", help="print a run's merged config")
    p.add_argument("exp_dir")
    a = ap.parse_args()
    if a.cmd == "leaderboard":
        leaderboard(a.runs_dir)
        return
    cfg = load_config(a.exp_dir)
    if a.cmd == "plot":
        make_plots(cfg, Path(a.exp_dir) / cfg["output"]["run_dir"], cfg["output"]["plots_dir"])
    elif a.cmd == "sync":
        sync_results(cfg, a.exp_dir, a.direction, a.dry_run, a.checkpoints or None)
    elif a.cmd == "pull":
        pull_checkpoint(cfg, a.exp_dir, a.name)
    elif a.cmd == "config":
        print_config(cfg)


if __name__ == "__main__":
    _cli()
