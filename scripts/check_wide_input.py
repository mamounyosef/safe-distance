"""CPU check of the 16:9 input patch (src/risk/wide_input.py) with BADAS-Open, before any GPU money is spent.

1. With the grid set to the ORIGINAL 16 x 16, the patched position code must give exactly BADAS's outputs
   (proves the replacement does the same thing as V-JEPA 2's own code).
2. For a 16 x 28 grid, every token must get the right (time slot, row, column): compared with a reference grid.
3. A 256 x 448 window must run through the whole model (encoder 3,584 tokens, predictor 896 future tokens).
4. Real frames (4 Nexar crash windows 0.5 s before the crash, 4 BDD100K normal windows): plain BADAS-Open's risk
   with the CURRENT squashed input vs the 16:9 input. Not a score (8 windows), only a sanity look: if the patch were
   broken, the 16:9 risks would be nonsense.
Uses transformers 4.53.0 (the version on Modal) from a scratch folder, so this PC's own install is not touched.

Output: src/risk/runs/stage1_lora/results/wide_input_check.json

RUN IT (from the repo root):
    .venv\\Scripts\\python.exe scripts\\check_wide_input.py <folder holding transformers 4.53.0>
"""

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])                                          # transformers 4.53.0 first
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/risk"))
sys.path.insert(0, r"C:\safe-distance-data\models\badas-open\src")

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import transformers  # noqa: E402

import wide_input as W  # noqa: E402
from models.vjepa import VJEPAModel  # noqa: E402

# ---- CONFIG ----
BADAS = Path(r"C:\safe-distance-data\models\badas-open")
NEXAR = Path(r"C:\safe-distance-data\nexar\samples")
BDD = Path(r"C:\safe-distance-data\bdd100k\samples")
OUT = ROOT / "src/risk/runs/stage1_lora/results/wide_input_check.json"
N_EACH, SEED = 4, 5
# ----------------


def window_frames(path: Path, t_end: float) -> np.ndarray:
    """The 16 frames (8 per second, frame round(i x fps / 8), as the cache does) ending at t_end, RGB 1280 x 720."""
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    want = [int(round(i * fps / 8.0)) for i in range(int(round(t_end * 8)) - 16, int(round(t_end * 8)))]
    frames, k, j = [], 0, 0
    while j < len(want):
        ok, img = cap.read()
        if not ok:
            break
        while j < len(want) and want[j] == k:
            frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            j += 1
        k += 1
    cap.release()
    return np.stack(frames)


def main() -> None:
    torch.manual_seed(0)
    res = {"transformers": transformers.__version__}
    badas = VJEPAModel(model_name="facebook/vjepa2-vitl-fpc16-256-ssv2",
                       checkpoint_path=str(BADAS / "weights" / "badas_open.pth"), device="cpu",
                       frame_count=16, img_size=224, target_fps=8.0, use_sliding_window=False)
    badas.load()
    net = badas.model.eval()

    # 1) original grid through the patched code = BADAS's own outputs
    x = torch.randn(2, 16, 3, 256, 256)
    with torch.no_grad():
        before = net(x)
        res["layers_patched"] = W.patch_positions(net, 256, 256)
        after = net(x)
    res["square_grid_max_difference"] = float((after - before).abs().max())

    # 2) 16 x 28 grid: positions against a reference (time slot, row, column) grid
    att = next(m for m in net.modules() if type(m).__name__ == "VJEPA2RopeAttention")
    W.patch_positions(net, W.WIDE_H, W.WIDE_W)
    slot, row, col = att.get_position_ids(torch.zeros(1, 8 * 16 * 28, 1))
    ref = np.stack(np.meshgrid(np.arange(8), np.arange(16), np.arange(28), indexing="ij"), -1).reshape(-1, 3)
    got = np.stack([slot.numpy(), row.numpy(), col.numpy()], -1)
    res["wide_positions_all_correct"] = bool((got == ref).all())
    # and the predictor's future tokens (numbers 3584.. continue the same grid: time slots 8 and 9)
    s2, r2, c2 = att.get_position_ids(torch.zeros(1, 1, 1), masks=torch.arange(3584, 3584 + 896).unsqueeze(0))
    res["future_tokens_time_slots"] = sorted(set(s2[0, 0].tolist()))

    # 3) a 256 x 448 window through the whole model
    with torch.no_grad():
        feats = net._extract_video_features(torch.randn(1, 16, 3, W.WIDE_H, W.WIDE_W))
        future = type(net)._predict_future_features(net, feats)
        out = net(torch.randn(1, 16, 3, W.WIDE_H, W.WIDE_W))
    res["wide_encoder_tokens"] = int(feats.shape[1])
    res["wide_future_tokens"] = int(future.shape[1])
    res["wide_output_shape"] = list(out.shape)

    # 4) real windows: squashed (current) vs 16:9, plain BADAS-Open's risk
    rng = random.Random(SEED)
    meta = [r for r in csv.DictReader((NEXAR / "metadata.csv").open()) if (NEXAR / r["file_name"]).exists()]
    picks = [("nexar_crash", NEXAR / r["file_name"], float(r["time_of_event"]) - 0.5) for r in rng.sample(meta, N_EACH)]
    picks += [("bdd_normal", p, 20.0) for p in rng.sample(sorted(BDD.glob("*.mov")), N_EACH)]
    rows = []
    for kind, path, t in picks:
        fr = window_frames(path, t)
        # current: squash to 224 (cache) -> BADAS's processor (292, centre 256), original square grid
        W.patch_positions(net, 256, 256)
        sq = np.stack([cv2.resize(f, (224, 224)) for f in fr])
        px = badas.processor(videos=sq, return_tensors="pt")["pixel_values_videos"]
        with torch.no_grad():
            r_sq = float(torch.softmax(net(px) / 2.0, 1)[0, 1])
        # 16:9: shape kept, 256 x 448, wide grid
        W.patch_positions(net, W.WIDE_H, W.WIDE_W)
        wd = torch.from_numpy(np.stack([W.wide_frame(f) for f in fr]))[None]
        with torch.no_grad():
            r_wd = float(torch.softmax(net(W.normalise(wd)) / 2.0, 1)[0, 1])
        rows.append({"kind": kind, "clip": path.name, "t_end_s": round(t, 2), "risk_now_squashed": round(r_sq, 4),
                     "risk_16x9": round(r_wd, 4)})
        print(rows[-1], flush=True)
    res["real_windows"] = rows
    res["passed_checks_1_to_3"] = (res["square_grid_max_difference"] == 0.0 and res["wide_positions_all_correct"]
                                   and res["wide_encoder_tokens"] == 3584 and res["wide_future_tokens"] == 896)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "real_windows"}, indent=1))
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
