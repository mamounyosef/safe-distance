"""Download the full Nexar collision dataset (31 GB) into a Modal Volume.

Runs in Modal's cloud, not on this PC: the files go straight from Hugging Face
to Modal storage, so nothing is downloaded locally. Later Modal jobs (GPU
benchmarks) read it from the same Volume at /data/nexar.

Needs: the Nexar licence accepted on Hugging Face, and this PC logged in to
Hugging Face (the login token is passed to the job for this run only).

RUN IT (PowerShell, from the repo root):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run scripts\\modal_nexar_download.py
"""

import modal
from huggingface_hub import get_token

# ---- CONFIG ----
REPO = "nexar-ai/nexar_collision_prediction"
VOLUME = "safe-distance-data"          # Modal Volume (cloud disk) shared by our Modal jobs
TARGET = "/data/nexar"                 # where the dataset lands inside the Volume
# ----------------

app = modal.App("safe-distance-nexar-download")
volume = modal.Volume.from_name(VOLUME, create_if_missing=True)
image = modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]")


@app.function(image=image, volumes={"/data": volume}, timeout=4 * 3600, cpu=4, memory=8192,
              secrets=[modal.Secret.from_dict({"HF_TOKEN": get_token() or "",
                                               "HF_HUB_ENABLE_HF_TRANSFER": "1"})])
def download() -> dict:
    """Download every file of the dataset into the Volume; return a summary."""
    import os
    from pathlib import Path

    from huggingface_hub import snapshot_download

    snapshot_download(REPO, repo_type="dataset", local_dir=TARGET, max_workers=16,
                      token=os.environ["HF_TOKEN"])
    volume.commit()   # make the files visible to later jobs
    files = [p for p in Path(TARGET).rglob("*") if p.is_file() and ".cache" not in p.parts]
    videos = [p for p in files if p.suffix == ".mp4"]
    return {"files": len(files), "videos": len(videos),
            "gigabytes": round(sum(p.stat().st_size for p in files) / 1e9, 2)}


@app.local_entrypoint()
def main() -> None:
    print(download.remote())
