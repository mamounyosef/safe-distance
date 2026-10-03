"""Download a few Nexar dashcam collision clips for local viewing and testing.

The Nexar Dashcam Collision Prediction dataset (Hugging Face, gated: accept its
licence once with your account) has 1,500 real dashcam clips, 1280x720, 30 fps.
Each collision clip ("positive") is marked with the moment of the collision
(time_of_event) and when a warning should come (time_of_alert). The full set
(31 GB) lives on Modal; this script fetches only the metadata and a few clips.

Run: .venv\\Scripts\\python.exe scripts\\download_nexar_samples.py
"""

from __future__ import annotations

import csv
import random
import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download

# ---- CONFIG ----
REPO = "nexar-ai/nexar_collision_prediction"
OUT = Path(r"C:\safe-distance-data\nexar")
METADATA = ["train/positive/metadata.csv", "train/negative/metadata.csv"]
CLIPS = []          # clip ids to download, e.g. ["00022", "00043"]
SPLIT = "train/positive"
PICK = 20           # also download this many collision clips, daylight only, chosen at random (seed 0)
PICK_SEED = 0
# ----------------


def fetch(path: str) -> Path:
    """Download one file from the dataset into OUT, keeping its folder layout."""
    cached = hf_hub_download(REPO, path, repo_type="dataset")
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cached, target)
    return target


def main() -> None:
    for path in METADATA:
        p = fetch(path)
        rows = list(csv.DictReader(p.open()))
        print(f"{path}: {len(rows)} clips; columns: {list(rows[0])}")
    clips = list(CLIPS)
    if PICK:
        positives = list(csv.DictReader((OUT / SPLIT / "metadata.csv").open()))
        daylight = sorted(r["file_name"][:-4] for r in positives if r["light_conditions"] == "Normal")
        clips += [c for c in random.Random(PICK_SEED).sample(daylight, PICK) if c not in clips]
    for clip in clips:
        p = fetch(f"{SPLIT}/{clip}.mp4")
        print(f"  {p} ({p.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
