"""Health check of a stage-1 training run: validation trajectory, a recompute of the logged AP from the saved
predictions, and the training-loss / gradient trend between validations. Writes results/val_health.json.

RUN IT (from the repo root):
    python scripts\\stage1_val_health.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd


def average_precision_score(y: np.ndarray, p: np.ndarray) -> float:
    """Same as sklearn's: mean of the precision at each crash window, ranking by risk (ties counted together)."""
    order = np.argsort(-p, kind="mergesort")
    y, p = y[order].astype(float), p[order]
    last = np.r_[np.flatnonzero(np.diff(p)), len(p) - 1]      # end index of each group of tied risks
    tp = np.cumsum(y)[last]
    precision, recall = tp / (last + 1), tp / y.sum()
    return float(np.sum(np.diff(np.r_[0.0, recall]) * precision))

RES = Path(__file__).resolve().parents[1] / "src/risk/runs/stage1_lora/results"
KEYS = ["val_ap_crash_vs_all_normal", "val_nexar_official_map", "val_ap_crash_vs_bdd_hard", "val_macro_auroc",
        "val_logloss", "val_calibration_error", "val_mean_risk_nexar_crash", "val_mean_risk_nexar_normal",
        "val_mean_risk_bdd_hard"]


def recompute(npz: Path) -> dict:
    """AP of crash windows vs every normal window, recomputed from the saved risks (needs the labels inside)."""
    d = np.load(npz, allow_pickle=True)
    out = {"keys": list(d.keys())}
    y = next((d[k] for k in ("labels", "y", "targets") if k in d), None)
    p = next((d[k] for k in ("risks", "probs", "preds", "scores", "logits") if k in d), None)   # AP only needs order
    if y is not None and p is not None:
        y, p = np.asarray(y).ravel(), np.asarray(p).ravel()
        out.update(n=int(len(y)), n_pos=int((y >= 0.5).sum()), ap=float(average_precision_score(y >= 0.5, p)))
    return out


def main() -> None:
    val = pd.read_csv(RES / "val_log.csv").drop_duplicates("step", keep="last").sort_values("step")
    train = pd.read_csv(RES / "train_log.csv").drop_duplicates("global_step", keep="last").sort_values("global_step")
    rows, prev = [], 0
    for _, v in val.iterrows():
        s = int(v.step)
        seg = train[(train.global_step > prev) & (train.global_step <= s)]
        row = {"run": v.run_id, "epoch": int(v.epoch), "step": s, **{k[4:]: round(float(v[k]), 4) for k in KEYS}}
        if len(seg):
            row.update(train_loss=round(float(seg.loss.mean()), 4), gnorm=round(float(seg.gnorm.median()), 2),
                       clip_pct=round(float(seg.clip_pct.mean()), 1), lr=float(seg.lr.iloc[-1]))
        npz = next(iter(sorted(RES.glob(f"predictions/*_val_s{s}.npz"))), None)
        if npz:
            rc = recompute(npz)
            row["npz_keys"] = rc["keys"]
            if "ap" in rc:
                row["ap_recomputed"] = round(rc["ap"], 4)
                row["n_windows"], row["n_crash"] = rc["n"], rc["n_pos"]
        rows.append(row)
        prev = s
    after = train[train.global_step > prev]
    tail = {"steps": [int(after.global_step.min()), int(after.global_step.max())],
            "train_loss": round(float(after.loss.mean()), 4)} if len(after) else None
    report = {"validations": rows, "training_after_last_val": tail,
              "train_steps_logged": int(len(train)), "last_train_step": int(train.global_step.max())}
    (RES / "val_health.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    cols = ["run", "epoch", "step", "ap_crash_vs_all_normal", "ap_recomputed", "nexar_official_map",
            "ap_crash_vs_bdd_hard", "logloss", "calibration_error", "mean_risk_nexar_crash",
            "mean_risk_nexar_normal", "mean_risk_bdd_hard", "train_loss", "gnorm", "clip_pct", "lr"]
    print(pd.DataFrame(rows).reindex(columns=cols).to_string(index=False))
    print("npz keys:", rows[-1].get("npz_keys"))
    print("after last val:", tail, "| last train step:", report["last_train_step"])


if __name__ == "__main__":
    main()
