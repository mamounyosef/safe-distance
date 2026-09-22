"""Download selected scenes from the Lost and Found dataset.

Lost and Found is real driving footage of debris and lost cargo lying on the
road: 13 scenes, each a sequence of consecutive frames, with obstacle labels,
precomputed stereo depth, camera geometry and ego vehicle speed.

The image archives are 6 GB each, so instead of downloading them whole this
pulls only the scenes listed in SCENES, using HTTP range requests to read
individual files out of the remote zip.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_lost_and_found.py

Every setting lives in the CONFIG block below. Edit it there and re-run.

Licence: free for academic and non-commercial use, attribution required.
See https://huggingface.co/datasets/kumuji/lost_and_found
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import requests
from remotezip import RemoteZip

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Where the dataset is unpacked.
DEST = Path("data/lost_and_found")

# Scenes to fetch. Each is one continuous drive past one or more obstacles.
# Frame counts: 02_Hanns_Klemm_Str_44=371, 05_Schafgasse_1=304,
# 04_Maurener_Weg_8=248, 01_Hanns_Klemm_Str_45=288, 12_Umberto_Nobile_Str=202,
# 15_Rechbergstr_Deckenpfronn=143, 07_Festplatz_Flugfeld=137,
# 03_Hanns_Klemm_Str_19=136, 11_Parkplatz_Flugfeld=100,
# 14_Otto_Lilienthal_Str_24=53. Set to None to fetch every scene (6 GB).
SCENES = [
    "04_Maurener_Weg_8",
    "14_Otto_Lilienthal_Str_24",
]

# Also fetch the precomputed stereo depth for those scenes. This is our
# ground truth for checking distance estimates, so it is worth the extra size.
WITH_DISPARITY = True

# ----------------------------------------------------------------------------

BASE = "https://huggingface.co/datasets/kumuji/lost_and_found/resolve/main"

# Small archives, downloaded whole. camera holds focal length and mounting
# geometry, vehicle holds ego speed and yaw rate, gtCoarse holds the labels.
SMALL_ARCHIVES = ["camera.zip", "vehicle.zip", "gtCoarse.zip"]


def fetch_small(name: str) -> None:
    """Download and extract one of the small archives."""
    print(f"\n{name}: downloading whole archive")
    response = requests.get(f"{BASE}/{name}", timeout=300)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(DEST)
    size_mb = len(response.content) / 1e6
    print(f"{name}: extracted, {size_mb:.1f} MB")


def fetch_scenes(archive: str, scenes: list[str] | None) -> None:
    """Pull only the listed scenes out of a large remote archive."""
    print(f"\n{archive}: selecting scenes remotely")
    with RemoteZip(f"{BASE}/{archive}") as z:
        names = z.namelist()
        if scenes is None:
            wanted = [n for n in names if n.endswith(".png")]
        else:
            wanted = [
                n for n in names
                if n.endswith(".png") and any(f"/{s}/" in n for s in scenes)
            ]

        if not wanted:
            print(f"{archive}: no matching files, check the scene names")
            return

        print(f"{archive}: {len(wanted)} files to fetch")
        for i, name in enumerate(wanted, 1):
            target = DEST / name
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
            if i % 25 == 0 or i == len(wanted):
                print(f"  {i}/{len(wanted)}")


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"destination: {DEST.resolve()}")
    print(f"scenes: {'ALL' if SCENES is None else ', '.join(SCENES)}")

    for name in SMALL_ARCHIVES:
        fetch_small(name)

    fetch_scenes("leftImg8bit.zip", SCENES)
    if WITH_DISPARITY:
        fetch_scenes("disparity.zip", SCENES)

    total = sum(f.stat().st_size for f in DEST.rglob("*") if f.is_file())
    count = sum(1 for f in DEST.rglob("*") if f.is_file())
    print(f"\ndone: {count} files, {total / 1e6:.0f} MB in {DEST}")


if __name__ == "__main__":
    main()
