"""What exactly is inside BADAS-Open's checkpoint: its saved config and how many weights each part has.

Memory-mapped (the 3.8 GB file is not loaded into RAM). CPU only, free.

RUN IT (from the repo root, after scripts/get_badas_source.py --weights):

    .venv\\Scripts\\python.exe scripts\\inspect_badas_checkpoint.py

Writes src/risk/badas_checkpoint.json (numbers only, for reference).
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import torch

CKPT = Path(r"C:\safe-distance-data\models\badas-open\weights\badas_open.pth")
OUT = Path(__file__).resolve().parents[1] / "src" / "risk" / "badas_checkpoint.json"
DEPTH = 3          # group weights by the first 3 parts of their names (e.g. backbone.encoder.layer)


def main() -> None:
    ck = torch.load(CKPT, map_location="cpu", mmap=True, weights_only=False)
    print("checkpoint keys:", list(ck))
    sd = ck.get("model") or ck.get("model_state_dict")
    cfg = {k: v for k, v in (ck.get("config") or {}).items() if isinstance(v, (int, float, str, bool, type(None)))}
    groups, dtypes = defaultdict(int), defaultdict(int)
    blocks = set()
    for name, t in sd.items():
        groups[".".join(name.split(".")[:DEPTH])] += t.numel()
        dtypes[str(t.dtype)] += t.numel()
        parts = name.split(".")
        if "layer" in parts:                                  # transformer block index, per module
            i = parts.index("layer")
            blocks.add((".".join(parts[:i]), int(parts[i + 1])))
    n_blocks = defaultdict(int)
    for mod, _ in blocks:
        n_blocks[mod] += 1
    res = {"checkpoint_keys": list(ck), "config": cfg,
           "params_total": sum(groups.values()), "dtypes": dict(dtypes),
           "params_by_part": dict(sorted(groups.items(), key=lambda kv: -kv[1])),
           "transformer_blocks": dict(n_blocks),
           "head_weights": {k: list(v.shape) for k, v in sd.items() if not k.startswith("backbone.")}}
    OUT.write_text(json.dumps(res, indent=1))
    # Short printout; everything (incl. every head weight's shape) is in the JSON.
    print(f"params: {res['params_total']:,}  blocks: {res['transformer_blocks']}")
    for part, n in list(res["params_by_part"].items())[:8]:
        print(f"  {n:12,d}  {part}")
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
