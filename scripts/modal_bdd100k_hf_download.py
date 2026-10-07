"""Download 608 BDD100K driving videos (40 s each, about 6.7 h) into the Modal Volume.

BDD100K's own download pages are down. The ShareGPT4Video dataset on Hugging
Face (licence CC BY-NC 4.0) re-hosts 608 original BDD100K clips in one zip
(zip_folder/bdd100k/bdd100k_videos.zip, 12 GB). This job downloads it inside
Modal and unpacks the videos to /data/bdd100k/videos/sharegpt4video/<clip>.mov.

RUN IT (PowerShell, from the repo root; Modal account ahmad-yonis):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run scripts\\modal_bdd100k_hf_download.py
"""

import modal
from huggingface_hub import get_token

# ---- CONFIG ----
VOLUME = "safe-distance-data"
REPO = "ShareGPT4Video/ShareGPT4Video"
FILE = "zip_folder/bdd100k/bdd100k_videos.zip"
TARGET = "/data/bdd100k/videos/sharegpt4video"
# ----------------

app = modal.App("safe-distance-bdd100k-hf")
volume = modal.Volume.from_name(VOLUME)
image = modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub[hf_transfer]")


@app.function(image=image, volumes={"/data": volume}, cpu=2, memory=4096, timeout=3 * 3600,
              secrets=[modal.Secret.from_dict({"HF_TOKEN": get_token() or "", "HF_HUB_ENABLE_HF_TRANSFER": "1"})])
def download() -> dict:
    """Download the zip to the container's disk, unpack the videos into the Volume."""
    import os
    import time
    import zipfile
    from pathlib import Path

    from huggingface_hub import hf_hub_download

    start = time.time()
    z = hf_hub_download(REPO, FILE, repo_type="dataset", local_dir="/tmp/hf", token=os.environ["HF_TOKEN"] or None)
    took = time.time() - start
    out = Path(TARGET)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".mov")]
        for n in names:
            (out / Path(n).name).write_bytes(zf.read(n))
    volume.commit()
    return {"videos": len(names), "gigabytes": round(sum((out / Path(n).name).stat().st_size for n in names) / 1e9, 2),
            "download_minutes": round(took / 60, 1), "saved_to": TARGET}


@app.local_entrypoint()
def main() -> None:
    print(download.remote())
