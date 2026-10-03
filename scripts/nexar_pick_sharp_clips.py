"""Pick the best-quality Nexar collision clips and download them for viewing.

Video quality is judged by bitrate: file size / clip length. More megabytes per
second of video means less compression, so a sharper picture. File sizes come
from Hugging Face's file list (no download needed); clip lengths are all about
40 s, so size alone ranks them. Only daylight clips ("Normal" light) are kept.

Run: .venv\\Scripts\\python.exe scripts\\nexar_pick_sharp_clips.py
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

# ---- CONFIG ----
REPO = "nexar-ai/nexar_collision_prediction"
SPLIT = "train/positive"
OUT = Path(r"C:\safe-distance-data\nexar")
TOP = 30          # download this many of the largest (sharpest) daylight clips
# ----------------


def main() -> None:
    api = HfApi()
    sizes = {Path(f.path).stem: f.size for f in api.list_repo_tree(REPO, SPLIT, repo_type="dataset")
             if f.path.endswith(".mp4")}
    meta = {r["file_name"][:-4]: r for r in csv.DictReader((OUT / SPLIT / "metadata.csv").open())}
    daylight = [c for c in sizes if meta.get(c, {}).get("light_conditions") == "Normal"]
    ranked = sorted(daylight, key=lambda c: -sizes[c])
    mb = sorted(sizes[c] / 1e6 for c in daylight)
    print(f"{len(sizes)} clips, {len(daylight)} daylight; size median {mb[len(mb) // 2]:.1f} MB, "
          f"largest {mb[-1]:.1f} MB")
    for clip in ranked[:TOP]:
        target = OUT / SPLIT / f"{clip}.mp4"
        if not target.exists():
            shutil.copyfile(hf_hub_download(REPO, f"{SPLIT}/{clip}.mp4", repo_type="dataset"), target)
        print(f"  {clip}: {sizes[clip] / 1e6:.1f} MB, {meta[clip]['weather']}, {meta[clip]['scene']}")


if __name__ == "__main__":
    main()
