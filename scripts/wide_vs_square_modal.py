"""Plain BADAS-Open on 100 Nexar Public clips with the 16:9 input (256 x 448), compared with the current squashed
input (256 x 256) on the SAME clips (Modal, one A100 40GB, about $1).

The squashed readings already exist (the baseline run: runs/baseline_badas_open/results/eval/series_nexar_public.json),
so only the 16:9 side runs here: each clip is decoded from its original video (8 frames per second, as the cache
does), every frame made 256 x 448 with its shape kept (src/risk/wide_input.py), and V-JEPA 2's position code
patched for the 16 x 28 patch grid. A reading every 0.5 s plus one at the clip's end, exactly like eval_risk.py.

Compared on the same 100 clips (50 crash, 50 normal, fixed random pick):
    Nexar official mAP (end-of-clip reading, AP per test group, averaged), AP over all 100,
    mean end-of-clip risk on crash and on normal clips, and how closely the two inputs' readings agree.

Output: src/risk/runs/stage1_lora/results/wide_vs_square_100.json (+ the printed table)

RUN IT (from the repo root):
    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session18.toml"
    .venv\\Scripts\\python.exe -m modal run scripts\\wide_vs_square_modal.py
"""

import csv
import json
import random
import time
from pathlib import Path

import modal

LOCAL = modal.is_local()
ROOT = Path(__file__).resolve().parents[1] if LOCAL else Path("/root")

# ---- CONFIG ----
VOLUME = "safe-distance-data"
GPU, GPU_PRICE_H = "A100-40GB", 2.10
N_EACH, SEED = 50, 20261017                       # 50 crash + 50 normal Nexar Public clips
SOLUTION = Path(r"C:\safe-distance-data\nexar\meta\solution.csv")
SQUARE_SERIES = ROOT / "src/risk/runs/baseline_badas_open/results/eval/series_nexar_public.json"
OUT = ROOT / "src/risk/runs/stage1_lora/results/wide_vs_square_100.json"
BADAS_REPO, BASE_MODEL, HF_CACHE = "nexar-ai/BADAS-Open", "facebook/vjepa2-vitl-fpc16-256-ssv2", "/data/models/hf"
STEP, BATCH, TEMPERATURE = 4, 16, 2.0             # a reading every 4 frames (0.5 s); 16 windows per GPU pass
# ----------------

app = modal.App("safe-distance-wide-check")
volume = modal.Volume.from_name(VOLUME)
from huggingface_hub import get_token  # noqa: E402

secret = modal.Secret.from_dict({"HF_TOKEN": (get_token() or "") if LOCAL else ""})
image = (modal.Image.debian_slim(python_version="3.12").apt_install("libgl1", "libglib2.0-0")
         .pip_install("torch==2.6.0", "torchvision==0.21.0", index_url="https://download.pytorch.org/whl/cu124")
         .pip_install("transformers==4.53.0", "huggingface_hub", "opencv-python-headless", "numpy", "pillow", "psutil",
                      "albumentations")
         .env({"HF_HOME": HF_CACHE})
         .add_local_file(str(ROOT / "src/risk/wide_input.py"), "/root/wide_input.py"))


def decode_wide(path: str):
    """The frames the cache would keep (frame round(i x fps / 8), 8 per second), each made 256 x 448, shape kept."""
    import cv2
    import numpy as np
    import wide_input as W
    cap = cv2.VideoCapture(path)
    fps, total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    wanted = [w for w in (int(round(i * fps / 8.0)) for i in range(int(round(total / fps * 8.0)))) if w < total]
    frames, k, j = [], 0, 0
    while j < len(wanted):
        ok, img = cap.read()
        if not ok:
            break
        while j < len(wanted) and wanted[j] == k:          # this video frame is one the cache keeps
            frames.append(W.wide_frame(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
            j += 1
        k += 1
    cap.release()
    return np.stack(frames)


@app.function(image=image, gpu=GPU, cpu=8, memory=32768, volumes={"/data": volume}, secrets=[secret], timeout=3600)
def score_wide(clips: list[tuple[str, str]]) -> dict:
    """16:9 readings for each (clip id, video path in the volume): [(window end time s, risk), ...]."""
    import sys
    import numpy as np
    import torch
    from huggingface_hub import snapshot_download
    import wide_input as W

    t0 = time.time()
    repo = Path(snapshot_download(BADAS_REPO, allow_patterns=["src/*", "src/**/*", "weights/*"]))
    sys.path.insert(0, str(repo / "src"))
    from models.vjepa import VJEPAModel
    badas = VJEPAModel(model_name=BASE_MODEL, checkpoint_path=str(repo / "weights" / "badas_open.pth"),
                       frame_count=16, img_size=224, target_fps=8.0, use_sliding_window=False)
    badas.load()
    net = badas.model.eval()
    n_layers = W.patch_positions(net, W.WIDE_H, W.WIDE_W)        # V-JEPA 2 now uses the 16 x 28 grid
    print(f"patched {n_layers} attention layers for {W.WIDE_H} x {W.WIDE_W}", flush=True)

    out = {}
    for n, (clip, path) in enumerate(clips, 1):
        frames = decode_wide(f"/data/{path}")                     # n x 256 x 448 x 3
        ends = list(range(16, len(frames) + 1, STEP))             # windows end every 0.5 s ...
        if ends and ends[-1] != len(frames):
            ends.append(len(frames))                              # ... plus one at the very end
        x = torch.from_numpy(frames).cuda()
        readings = []
        for i in range(0, len(ends), BATCH):
            batch = torch.stack([x[e - 16:e] for e in ends[i:i + BATCH]])          # B x 16 x 256 x 448 x 3
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
                logits = net(W.normalise(batch)).float()
            probs = torch.softmax(logits / TEMPERATURE, dim=1)[:, 1].cpu()
            readings += [(round(e / 8.0, 3), round(float(p), 5)) for e, p in zip(ends[i:i + BATCH], probs)]
        out[clip] = readings
        if n % 10 == 0:
            print(f"  {n}/{len(clips)} clips  {time.time() - t0:.0f} s", flush=True)
    return {"series": out, "seconds": round(time.time() - t0, 1), "layers_patched": n_layers}


def average_precision(labels: list[int], scores: list[float]) -> float:
    """Same as eval_risk.py / sklearn: precision-recall area, tied scores form one step."""
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


@app.local_entrypoint()
def main():
    rows = [r for r in csv.DictReader(SOLUTION.open()) if r["Usage"] == "Public"]
    rng = random.Random(SEED)
    pos = rng.sample([r for r in rows if r["target"] == "1"], N_EACH)
    neg = rng.sample([r for r in rows if r["target"] == "0"], N_EACH)
    picks = pos + neg
    jobs = [(r["id"], f"nexar/test-public/{'positive' if r['target'] == '1' else 'negative'}/{r['id']}.mp4")
            for r in picks]
    print(f"{len(jobs)} Nexar Public clips ({N_EACH} crash + {N_EACH} normal), 16:9 on 1 x {GPU}")
    res = score_wide.remote(jobs)
    wide = res["series"]
    square = json.loads(SQUARE_SERIES.read_text())

    # compare on the same clips: end-of-clip reading (Nexar's official moment) and all readings
    out = {"clips": len(picks), "seconds_on_gpu": res["seconds"], "layers_patched": res["layers_patched"],
           "cost_usd_estimate": round(res["seconds"] / 3600 * GPU_PRICE_H, 2)}
    for name, series in (("square_now", square), ("wide_16x9", wide)):
        y = [int(r["target"]) for r in picks]
        end = [series[r["id"]][-1][1] for r in picks]
        groups = sorted({r["group"] for r in picks})
        per_group = {g: average_precision([y[i] for i, r in enumerate(picks) if r["group"] == g],
                                          [end[i] for i, r in enumerate(picks) if r["group"] == g]) for g in groups}
        out[name] = {"nexar_official_map": round(sum(per_group.values()) / len(per_group), 4),
                     "ap_per_group": {f"{[0.5, 1.0, 1.5][int(g)]} s": round(v, 4) for g, v in per_group.items()},
                     "ap_all_100": round(average_precision(y, end), 4),
                     "mean_end_risk_crash": round(sum(e for e, t in zip(end, y) if t) / N_EACH, 4),
                     "mean_end_risk_normal": round(sum(e for e, t in zip(end, y) if not t) / N_EACH, 4)}
    # how closely the two inputs agree, reading by reading (same window end times)
    diffs = []
    for r in picks:
        sq = dict((t, p) for t, p in square[r["id"]])
        diffs += [abs(p - sq[t]) for t, p in wide[r["id"]] if t in sq]
    diffs.sort()
    out["readings_compared"] = len(diffs)
    out["risk_difference_median"] = round(diffs[len(diffs) // 2], 4)
    out["risk_difference_p90"] = round(diffs[int(len(diffs) * 0.9)], 4)
    out["wide_series"] = wide
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1))

    print(f"\n{'':30s} {'NOW (256 x 256 squashed)':>26s} {'16:9 (256 x 448)':>18s}")
    for k in ("nexar_official_map", "ap_all_100", "mean_end_risk_crash", "mean_end_risk_normal"):
        print(f"{k:30s} {out['square_now'][k]:>26} {out['wide_16x9'][k]:>18}")
    for g in out["square_now"]["ap_per_group"]:
        print(f"{'AP, clips ending ' + g + ' before':30s} {out['square_now']['ap_per_group'][g]:>26} "
              f"{out['wide_16x9']['ap_per_group'][g]:>18}")
    print(f"\nreading-by-reading risk difference: median {out['risk_difference_median']}, "
          f"90% under {out['risk_difference_p90']} ({out['readings_compared']} readings)")
    print(f"GPU time {res['seconds']} s, about ${out['cost_usd_estimate']}; saved {OUT}")
