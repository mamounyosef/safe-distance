"""Check, on the CPU, that LoRA can be attached to every part of BADAS-Open and that nothing is left out.

Before writing the stage 1 training script we verify:
1. peft's LoRA accepts every layer type in BADAS-Open (Linear and the Conv3d that cuts the clip into tokens).
2. No weight is left out: every weight is either the frozen base of a LoRA layer, or trained fully.
3. The predictor (one object listed twice: predictor and backbone.predictor) is wrapped once and stays shared.
4. Right after adding LoRA the outputs are identical to the original model (LoRA starts at zero).
5. After one backward pass EVERY trainable weight gets a non-zero gradient (no dead paths).
Small input (128 x 128) to keep it fast on the CPU; the wiring is the same at 256 x 256.

Output: src/risk/runs/stage1_lora/results/lora_coverage.json (all numbers written by this script).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\check_lora_coverage.py
"""

import copy
import json
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path

import peft
import torch
from peft import LoraConfig, get_peft_model

# ---- CONFIG ----
BADAS = Path(r"C:\safe-distance-data\models\badas-open")
OUT = Path(__file__).resolve().parents[1] / "src/risk/runs/stage1_lora/results/lora_coverage.json"
RANK, ALPHA, DROPOUT = 16, 32, 0.1
# LoRA on: the Conv3d patch embedding, every attention (query/key/value/proj) and MLP (fc1/fc2) Linear of the
# encoder (24 blocks) and predictor (12 blocks), and the predictor's two width-changing Linears.
TARGETS = (r".*backbone\.(encoder\.(embeddings\.patch_embeddings\.proj|layer\.\d+\.(attention\.(query|key|value|proj)|mlp\.fc[12]))"
           r"|predictor\.(embeddings\.predictor_embeddings|proj|layer\.\d+\.(attention\.(query|key|value|proj)|mlp\.fc[12])))")
# Trained fully. Exact suffix "classifier.classifier": plain "classifier" also matches the inner layer (trap).
FULL = ["temporal_processor", "classifier.classifier"]
# ----------------

sys.path.insert(0, str(BADAS / "src"))
from models.vjepa import VJEPAModel  # noqa: E402

torch.manual_seed(0)
badas = VJEPAModel(model_name="facebook/vjepa2-vitl-fpc16-256-ssv2",
                   checkpoint_path=str(BADAS / "weights" / "badas_open.pth"),
                   device="cpu", frame_count=16, img_size=224, target_fps=8.0, use_sliding_window=False)
badas.load()
net = badas.model.eval()
res = {"provenance": {"git_commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                                   text=True).stdout.strip(),
                      "peft": peft.__version__, "torch": torch.__version__, "python": platform.python_version()},
       "config": {"r": RANK, "lora_alpha": ALPHA, "lora_dropout": DROPOUT, "target_modules": TARGETS,
                  "modules_to_save": FULL, "fully_trained_extra": "all LayerNorms + predictor mask tokens"}}

# 1. Which layer types own weights directly
own = Counter(type(m).__name__ for _, m in net.named_modules() if any(True for _ in m.parameters(recurse=False)))
res["module_types_owning_weights"] = dict(own)
res["predictor_listed_twice_same_object"] = net.predictor is net.backbone.predictor

x = torch.randn(2, 16, 3, 128, 128)
with torch.no_grad():
    before = net(x)

cfg = LoraConfig(r=RANK, lora_alpha=ALPHA, lora_dropout=DROPOUT, bias="none", target_modules=TARGETS,
                 modules_to_save=FULL)
model = get_peft_model(copy.deepcopy(net), cfg)
lora = {n: m for n, m in model.named_modules() if hasattr(m, "base_layer") and hasattr(m, "lora_A")}
res["lora_layers"] = len(lora)
res["lora_layers_by_type"] = dict(Counter(type(m.base_layer).__name__ for m in lora.values()))
res["conv3d_patch_embedding_has_lora"] = any("patch_embeddings.proj" in n for n in lora)
res["predictor_embeddings_has_lora"] = any("predictor_embeddings" in n for n in lora)
res["predictor_proj_has_lora"] = any(n.endswith("predictor.proj") for n in lora)
res["predictor_still_shared_after_lora"] = model.base_model.model.predictor is model.base_model.model.backbone.predictor

# LayerNorms and mask tokens: peft leaves them frozen, so switch them on (tiny)
for n, p in model.named_parameters():
    if ("norm" in n or n.endswith("mask_tokens")) and "lora_" not in n and "original_module" not in n:
        p.requires_grad_(True)
res["fully_trained_copies"] = [n for n, m in model.named_modules() if type(m).__name__ == "ModulesToSaveWrapper"]

# 2. Frozen weights that are not the base of a LoRA layer = left out
bases = {f"{n}.base_layer.{pn}" for n, m in lora.items() for pn, _ in m.base_layer.named_parameters()}
left = {n: p.numel() for n, p in model.named_parameters()
        if not p.requires_grad and n not in bases and "original_module" not in n}
res["left_out_weights"] = {"tensors": len(left), "values": sum(left.values()), "names": sorted(left)[:50]}
res["trainable_millions"] = round(sum(p.numel() for p in model.parameters() if p.requires_grad) / 1e6, 2)
res["total_millions"] = round(sum(p.numel() for p in model.parameters()) / 1e6, 1)

# 4. Identical output at the start
model.eval()
with torch.no_grad():
    res["max_logit_difference_after_adding_lora"] = float((model(x) - before).abs().max())

# 5. Gradient reaches every trainable weight. LoRA's B starts at 0, so A gets no gradient on the very first
# step (normal); give B small values to test the wiring. drop_path (random block skipping) off for this check.
with torch.no_grad():
    for n, p in model.named_parameters():
        if "lora_B" in n:
            p.normal_(0, 1e-3)
model.train()
for m in model.modules():
    if type(m).__name__ == "VJEPA2DropPath":
        m.eval()
torch.nn.functional.cross_entropy(model(x), torch.tensor([0, 1])).backward()
dead = [n for n, p in model.named_parameters() if p.requires_grad and (p.grad is None or float(p.grad.abs().sum()) == 0)]
res["trainable_tensors_without_gradient"] = {"count": len(dead), "names": dead[:50]}
res["passed"] = (res["conv3d_patch_embedding_has_lora"] and not left and not dead
                 and res["max_logit_difference_after_adding_lora"] == 0.0 and res["predictor_still_shared_after_lora"])

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k not in ("config", "provenance")}, indent=1))
print(f"saved {OUT}")
