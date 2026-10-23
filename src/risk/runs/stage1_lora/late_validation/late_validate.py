"""Late validation: score stage 1 checkpoints on the NEW validation windows (windows.json), on one Modal GPU.

WHAT IT DOES
    For every step in config.yaml (0 = plain BADAS-Open, the rest = saved checkpoints of the finished run):
    load the weights, score all 2,559 windows, compute every score, and save them at once (a re-run skips the
    steps already done). The model, its 16:9 input and the window reader are stage1_train.py's own, so scoring is
    exactly what training's validation did, only on the new windows.

    The four cases (see make_windows.py):
        nexar_crash   label 1   Nexar Public crash clips: last frame + 0.5 s earlier (group 2: last frame only)
        nexar_normal  label 0   Nexar Public normal clips: last frame + 4 s earlier
        bdd_hard      label 0   the 2 moments per clean BDD100K val clip plain BADAS-Open found riskiest
        bdd_normal    label 0   1 random moment per clip

    The batch size is fixed (config.yaml scoring.batch_size). If the GPU runs out of memory, the job stops; lower
    the number in config.yaml by hand and run again.

OUTPUTS (copied home to late_validation/results/ at the end)
    scores.csv                 one row per step, every score
    late_validation.json       the same rows + settings, hardware, batch size, peak memory, time and cost per step
    log_<time>.txt             everything printed on the GPU
    predictions/step<N>.npz    the risk logit per window (NOT in git: the ids reveal Nexar test labels)

RUN IT (from the repo root; build windows.json first with make_windows.py):
    python -m modal run src\\risk\\runs\\stage1_lora\\late_validation\\late_validate.py
"""

import copy
import csv
import io
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import yaml


def _stage1_dir() -> Path:
    """Find the stage1_lora folder: on Modal the src/risk code is copied to /root/runs; on this PC it is one folder up."""
    here = Path(__file__).resolve()
    for candidate in (Path("/root/runs/runs/stage1_lora"), here.parent.parent):
        if (candidate / "stage1_train.py").exists():
            return candidate
    raise FileNotFoundError("stage1_train.py not found")


STAGE1_DIR = _stage1_dir()
sys.path.insert(0, str(STAGE1_DIR))
import stage1_train as S  # noqa: E402            # stage 1's model, input, window reader and settings
import ml_utils as ml  # noqa: E402                # (on the path through stage1_train) prints, Modal image / volumes

LV_DIR = STAGE1_DIR / "late_validation"
_C = yaml.safe_load((LV_DIR / "config.yaml").read_text(encoding="utf-8"))
_SC, _MO = _C["scoring"], _C["modal"]

# ---- settings (config.yaml) ----
WINDOWS = LV_DIR / _C["windows"]["out"]
STEPS = sorted(int(s) for s in _SC["steps"])          # step 0 first: the fresh model IS plain BADAS-Open
CKPT_DIR = Path(_SC["checkpoint_dir"])
BATCH_SIZE, NUM_WORKERS = _SC["batch_size"], _SC["num_workers"]
REMOTE_DIR = Path(_SC["results_dir"])                 # on the runs volume
LOCAL_DIR = LV_DIR / "results"                        # on this PC
PRICE_H = _MO["gpu_price_s"] * 3600 + _MO["cpu_cores"] * 0.0473 + _MO["memory_gb"] * 0.008   # $ per hour, all in
CASES = ["nexar_crash", "nexar_normal", "bdd_hard", "bdd_normal"]
NORMAL_CASES = CASES[1:]
CAUGHT_AT = (0.5, 0.9)                                # thresholds for the per-timing crash rows


# =====================================================================================================================
# SCORES
# =====================================================================================================================
def scores(risk: np.ndarray, W: dict) -> dict:
    """Every score for one checkpoint.

    Arguments:
        risk: the model's risk (0..1) per window, in windows.json order.
        W:    per-window facts: group (case), rank (1st / 2nd window of its clip), nexar_group (0/1/2, -1 for BDD),
              before_s (Nexar crash windows: seconds between the window's end and the crash).
    """
    is_ = {c: W["group"] == c for c in CASES}
    crash = risk[is_["nexar_crash"]]
    all_normal = risk[np.isin(W["group"], NORMAL_CASES)]
    out = {"ap_crash_vs_all_normal": S._ap(crash, all_normal)}              # crash vs every normal window
    for c in NORMAL_CASES:
        out[f"ap_crash_vs_{c}"] = S._ap(crash, risk[is_[c]])

    # Nexar's official score: per test group, last-frame windows only, crash vs Nexar normal; then the average.
    # It uses exactly the same windows as training's validation, so it is directly comparable with val_log.csv.
    last = W["rank"] == 1
    per_group = []
    for g, sec in S.GROUP_SECONDS.items():
        in_g = W["nexar_group"] == g
        ap = S._ap(risk[is_["nexar_crash"] & last & in_g], risk[is_["nexar_normal"] & last & in_g])
        out[f"group_{sec}s_official_ap"] = ap
        per_group.append(ap)
    out["nexar_official_map"] = float(np.mean(per_group))

    for c in CASES:
        out[f"mean_risk_{c}"] = float(risk[is_[c]].mean())

    # crash windows by how long before the crash they end (0.5 / 1.0 / 1.5 s)
    for sec in sorted(set(W["before_s"][is_["nexar_crash"]].tolist())):
        here = risk[is_["nexar_crash"] & (W["before_s"] == sec)]
        out[f"crash_{sec}s_windows"] = int(len(here))
        out[f"crash_{sec}s_mean_risk"] = float(here.mean())
        for t in CAUGHT_AT:
            out[f"crash_{sec}s_caught_pct_at_{t}"] = round(100.0 * float((here > t).mean()), 2)

    # at every threshold: crashes caught and false alarms per normal case
    for t in S.THRESHOLDS:
        out[f"crash_caught_pct_at_{t}"] = round(100.0 * float((crash > t).mean()), 2)
        for c in NORMAL_CASES:
            out[f"{c}_alarm_pct_at_{t}"] = round(100.0 * float((risk[is_[c]] > t).mean()), 2)

    # calibration error (same as training's): 10 risk bins, |mean risk - share of crashes|, weighted by bin size
    truth = is_["nexar_crash"].astype(float)
    bin_of = np.clip((risk * 10).astype(int), 0, 9)
    out["calibration_error"] = float(sum(abs(risk[bin_of == b].mean() - truth[bin_of == b].mean()) * (bin_of == b).mean()
                                         for b in range(10) if (bin_of == b).any()))
    return out


# =====================================================================================================================
# MODAL
# =====================================================================================================================
import modal  # noqa: E402

app = modal.App("stage1_late_validation")
_CFG = copy.deepcopy(S.CFG)                            # stage 1's settings (image, volumes) ...
_CFG["modal"].update(gpu=_MO["gpu"], timeout_hours=_MO["timeout_hours"], cpu=_MO["cpu_cores"],
                     memory_gb=_MO["memory_gb"])        # ... with this job's GPU and resources


class Tee(io.TextIOBase):
    """Print to the console AND keep a copy (saved as log_<time>.txt)."""

    def __init__(self, stream):
        self.stream, self.parts = stream, []

    def write(self, s):
        self.parts.append(s)
        return self.stream.write(s)

    def flush(self):
        self.stream.flush()


@app.function(image=ml.modal_image(_CFG, S.PKG_ROOT), volumes=S.VOLUMES, secrets=[S._HF], **ml.modal_resources(_CFG))
def score_remote() -> dict:
    """Runs on the GPU: build the model once, then score every step. Returns every row + the predictions."""
    import torch
    from torch.utils.data import DataLoader

    tee = Tee(sys.stdout)
    sys.stdout = tee
    os.environ["HF_HOME"] = S.HF_CACHE
    vol = S.VOLUMES["/runs"]
    (REMOTE_DIR / "predictions").mkdir(parents=True, exist_ok=True)
    (REMOTE_DIR / "rows").mkdir(parents=True, exist_ok=True)

    # --- the windows (stage 1's own reader: same cache, same frames, no augmentation) ---
    windows = json.loads(WINDOWS.read_text())
    val = S.ValWindows(windows)                         # fills each window's end frame
    W = {"group": val.group, "rank": val.rank, "nexar_group": val.nexar_group,
         "before_s": np.array([S.GROUP_SECONDS[w["nexar_group"]] + w["end_back"] / S.FPS
                               if w["group"] == "nexar_crash" else -1.0 for w in val.windows])}
    ml._table("late validation windows", ["case", "windows"], [[c, int((val.group == c).sum())] for c in CASES], "📦")
    loader = DataLoader(val, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)

    # --- the model: plain BADAS-Open + LoRA at zero (stage 1's start-up checks run here) ---
    device = torch.device("cuda")
    model = S.RiskModel(device).to(device).eval()
    gpu = torch.cuda.get_device_name(0)

    rows, preds = [], {}
    for step in STEPS:
        row_file, pred_file = REMOTE_DIR / "rows" / f"step{step}.json", REMOTE_DIR / "predictions" / f"step{step}.npz"
        if row_file.exists() and pred_file.exists():   # done in an earlier run: reuse
            rows.append(json.loads(row_file.read_text()))
            p = np.load(pred_file, allow_pickle=True)
            preds[step] = {"logits": p["logits"], "ids": p["ids"]}
            print(f"  ⏭️  step {step}: already scored, reused")
            continue

        # load the weights (step 0: none, the fresh model is plain BADAS-Open)
        source = "plain BADAS-Open"
        if step:
            path = next((p for p in (CKPT_DIR / f"top_step{step}.pt", CKPT_DIR / f"step{step}.pt") if p.exists()), None)
            if path is None:
                raise SystemExit(f"no checkpoint for step {step} in {CKPT_DIR}")
            ck = torch.load(path, map_location="cpu", weights_only=False)
            if int(ck.get("step", -1)) != step:
                raise SystemExit(f"{path.name} holds step {ck.get('step')}, not {step}")
            model.load_state_dict(ck["model"])          # strict: every trainable weight must be there
            source = path.name

        # score every window (no gradients, bf16 like training's validation)
        print(f"\n  ▶️  step {step}: scoring {len(val)} windows with {source} (batch {BATCH_SIZE})", flush=True)
        torch.cuda.reset_peak_memory_stats()
        t0, logits, done = time.time(), [], 0
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            for b, (x, _, _) in enumerate(loader, 1):
                logits.append(model(S.prepare(x, device, None)).float().cpu())
                done += len(x)
                if b % 5 == 0 or b == len(loader):            # a progress line every 5 batches
                    el = time.time() - t0
                    print(f"     batch {b}/{len(loader)} | {done}/{len(val)} windows | {done / el:.1f}/s | "
                          f"elapsed {el:.0f} s | left about {(len(val) - done) / max(done / el, 1e-9):.0f} s | "
                          f"GPU memory peak {torch.cuda.max_memory_allocated() / 1e9:.1f} GB", flush=True)
        secs = time.time() - t0
        z = torch.cat(logits).numpy()[:, 0]
        risk = 1.0 / (1.0 + np.exp(-z))                # sigmoid: the risk 0..1

        row = {"step": step, "checkpoint": source, **scores(risk, W),
               "windows": int(len(z)), "batch_size": BATCH_SIZE, "gpu": gpu,
               "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
               "score_secs": round(secs, 1), "windows_per_s": round(len(z) / secs, 1),
               "cost_usd": round(secs / 3600 * PRICE_H, 3)}
        np.savez(pred_file, logits=z.astype(np.float32), ids=np.array(val.ids))
        row_file.write_text(json.dumps(row, indent=1))
        vol.commit()                                    # saved on the volume now: a crash later loses nothing
        rows.append(row)
        preds[step] = {"logits": z.astype(np.float32), "ids": np.array(val.ids)}
        ml._table(f"step {step} ({source})", ["score", "value"], [
            ["AP crash vs all normal", f"{row['ap_crash_vs_all_normal']:.4f}"],
            ["Nexar official mAP (same as training's)", f"{row['nexar_official_map']:.4f}"],
            *[[f"AP crash vs {c}", f"{row[f'ap_crash_vs_{c}']:.4f}"] for c in NORMAL_CASES],
            ["crashes caught at 0.9", f"{row['crash_caught_pct_at_0.9']:.1f}%"],
            *[[f"{c} alarms at 0.9", f"{row[f'{c}_alarm_pct_at_0.9']:.1f}%"] for c in NORMAL_CASES],
            ["time / peak GPU memory", f"{secs:.0f} s / {row['peak_gpu_gb']} GB (batch {BATCH_SIZE})"]], "📋")

    sys.stdout = tee.stream
    return {"rows": rows, "preds": preds, "log": "".join(tee.parts)}


@app.local_entrypoint()
def main():
    """Runs on THIS PC: start the GPU job, wait, then save everything into late_validation/results/."""
    if not WINDOWS.exists():
        raise SystemExit(f"{WINDOWS} missing: run make_windows.py first")
    t0 = time.time()
    out = score_remote.remote()
    stamp = time.strftime("%Y%m%d_%H%M%S")
    (LOCAL_DIR / "predictions").mkdir(parents=True, exist_ok=True)

    rows = out["rows"]
    for step, p in out["preds"].items():
        np.savez(LOCAL_DIR / "predictions" / f"step{step}.npz", logits=p["logits"], ids=p["ids"])
    keys = list(dict.fromkeys(k for r in rows for k in r))   # every column, first-seen order
    with open(LOCAL_DIR / "scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    report = {"what": "stage 1 checkpoints re-scored on the new validation windows (late_validation/windows.json)",
              "windows_summary": json.loads((LOCAL_DIR / "windows_summary.json").read_text())
              if (LOCAL_DIR / "windows_summary.json").exists() else None,
              "settings": _C, "finished": stamp, "wall_secs": round(time.time() - t0, 1),
              "cost_usd_scoring": round(sum(r["cost_usd"] for r in rows), 3), "rows": rows}
    (LOCAL_DIR / "late_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (LOCAL_DIR / f"log_{stamp}.txt").write_text(out["log"], encoding="utf-8")

    best = max(rows, key=lambda r: r["ap_crash_vs_all_normal"])
    print(f"\nsaved {len(rows)} steps to {LOCAL_DIR}")
    print(f"best by AP crash vs all normal: step {best['step']} ({best['ap_crash_vs_all_normal']:.4f}); "
          f"scoring cost about ${report['cost_usd_scoring']}")
