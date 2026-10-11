"""Download BADAS-Open's code (and optionally its weights) from Hugging Face.

The repo nexar-ai/BADAS-Open is gated: accept its terms on Hugging Face and be
logged in on this PC (huggingface-cli login) first.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\get_badas_source.py            # code only (small)
    .venv\\Scripts\\python.exe scripts\\get_badas_source.py --weights  # code + weights (about 1.2 GB)
"""

import sys

from huggingface_hub import snapshot_download

# ---- CONFIG ----
REPO = "nexar-ai/BADAS-Open"
DEST = r"C:\safe-distance-data\models\badas-open"
# ----------------

patterns = ["src/*", "src/**/*", "requirements.txt", "README.md", "badas_loader.py", "config.json"]
if "--weights" in sys.argv:
    patterns.append("weights/*")
print(snapshot_download(REPO, allow_patterns=patterns, local_dir=DEST))
