"""Run BADAS-Open once on a dummy 2 s clip (CPU) and record the tensor shape at every step, in call order.

Output: src/risk/badas_shapes.json (used for the architecture diagram). Numbers come from a real forward pass.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\trace_badas_shapes.py
"""

import json
import sys
from pathlib import Path

import torch

# ---- CONFIG ----
BADAS = Path(r"C:\safe-distance-data\models\badas-open")
OUT = Path(__file__).resolve().parents[1] / "src" / "risk" / "badas_shapes.json"
INPUT = (1, 16, 3, 256, 256)          # batch, frames, colour channels, height, width (after BADAS's processor)
# Repeated blocks: only these ones are traced in detail (all blocks have the same shapes).
DETAIL = ("encoder.layer.0.", "predictor.layer.0.")
# ----------------

sys.path.insert(0, str(BADAS / "src"))
from models.vjepa import VJEPAModel  # noqa: E402


def shape(x):
    """Shape(s) of a tensor, a tuple of tensors or a model output object."""
    if isinstance(x, torch.Tensor):
        return list(x.shape)
    if hasattr(x, "last_hidden_state"):
        return shape(x.last_hidden_state)
    if isinstance(x, (tuple, list)):
        return [shape(v) for v in x if v is not None]
    return None


badas = VJEPAModel(model_name="facebook/vjepa2-vitl-fpc16-256-ssv2",
                   checkpoint_path=str(BADAS / "weights" / "badas_open.pth"),
                   device="cpu", frame_count=16, img_size=224, target_fps=8.0, use_sliding_window=False)
badas.load()
net = badas.model.eval()

calls = []
seen = set()
for name, m in net.named_modules():
    if not name or id(m) in seen:          # the top-level 'predictor' is the same object as backbone.predictor
        continue
    seen.add(id(m))

    def hook(mod, inp, out, name=name):
        calls.append({"module": name, "type": type(mod).__name__,
                      "in": shape(inp), "out": shape(out),
                      "params": sum(p.numel() for p in mod.parameters(recurse=True))})
    m.register_forward_hook(hook)

with torch.no_grad():
    logits = net(torch.zeros(INPUT))
calls.append({"module": "OUTPUT logits", "type": "", "in": None, "out": list(logits.shape), "params": 0})

cfg = {k: getattr(net.config, k, None) for k in ("future_prediction_seconds", "original_fps", "frame_count",
                                                  "predictor_combination_method", "temporal_method")}
OUT.write_text(json.dumps({"input": list(INPUT), "config": cfg, "calls": calls}, indent=1))
print(f"{len(calls)} calls traced -> {OUT}")
print("config:", cfg)
for c in calls:
    if ".layer." in c["module"] and not any(d in c["module"] for d in DETAIL):
        continue
    print(f"{c['module']:60s} {c['type']:28s} in={c['in']} out={c['out']}")
