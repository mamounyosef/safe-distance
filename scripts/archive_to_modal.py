"""Move finished datasets off this PC into the Modal Volume, to free disk space.

For each folder in FOLDERS: upload it to /archive/<name> in the Volume, check
that the Volume holds exactly the same number of files and bytes, and only
then delete the local copy. A folder whose check fails is NOT deleted.

RUN IT (PowerShell, from the repo root; Modal account ahmad-yonis):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run scripts\\archive_to_modal.py

GET ONE BACK later (example: kitti back into the repo's data folder):

    .venv\\Scripts\\modal.exe volume get safe-distance-data archive/kitti "D:\\My Projects\\safe-distance\\data\\"

Modal cost: only a few seconds of a small CPU per check (well under one cent);
storage is within the Volume's free allowance.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import modal

# ---- CONFIG ----
VOLUME = "safe-distance-data"
FOLDERS = [
    r"C:\safe-distance-data\nuscenes-mini",
    r"C:\safe-distance-data\nuscenes-trainval",
    r"D:\My Projects\safe-distance\data\lost_and_found",
    r"D:\My Projects\safe-distance\data\kitti",
]
DELETE_AFTER_CHECK = True        # delete the local copy once the Volume copy is verified
# ----------------

app = modal.App("safe-distance-archive")
volume = modal.Volume.from_name(VOLUME)
MODAL_CLI = Path(sys.executable).parent / "modal.exe"


@app.function(volumes={"/data": volume}, cpu=0.25, timeout=600)
def remote_stats(path: str) -> tuple[int, int]:
    """(number of files, total bytes) under a folder of the Volume."""
    volume.reload()       # see uploads made since this container started (else it can report 0 files)
    root = Path("/data") / path
    files = [p for p in root.rglob("*") if p.is_file()] if root.exists() else []
    return len(files), sum(p.stat().st_size for p in files)


def local_stats(folder: Path) -> tuple[int, int]:
    """(number of files, total bytes) under a local folder."""
    files = [p for p in folder.rglob("*") if p.is_file()]
    return len(files), sum(p.stat().st_size for p in files)


@app.local_entrypoint()
def main() -> None:
    for f in FOLDERS:
        folder = Path(f)
        if not folder.exists():
            print(f"{folder}: not here (already archived?), skipped")
            continue
        here = local_stats(folder)
        target = f"archive/{folder.name}"
        print(f"{folder}: {here[0]} files, {here[1] / 1e9:.2f} GB -> {VOLUME}:/{target}", flush=True)
        if remote_stats.remote(target) != here:          # not uploaded yet (or incomplete): upload
            subprocess.run([str(MODAL_CLI), "volume", "put", "--force", VOLUME, str(folder), "/" + target],
                           check=True)
        there = remote_stats.remote(target)
        if there != here:
            print(f"   CHECK FAILED: Volume has {there[0]} files, {there[1]} bytes; local copy kept")
            continue
        print("   verified: same files and bytes on the Volume", flush=True)
        if DELETE_AFTER_CHECK:
            shutil.rmtree(folder)
            print("   local copy deleted", flush=True)
