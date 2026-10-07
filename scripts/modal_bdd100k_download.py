"""Download ONE BDD100K video zip (1,000 normal-driving clips, 40 s each) into the Modal Volume.

BDD100K's download pages are down, so this uses the dataset's torrent
(bdd100k.torrent, from hyper.ai) and fetches only the selected file inside it.
Runs on a Modal CPU container: the zip goes to the container's own disk first
(torrent pieces arrive out of order, which a network volume handles badly),
then the videos are unpacked into the Volume at /data/bdd100k/videos/<split>/.

File numbers inside the torrent: see scripts/torrent_files.py
(99 = bdd100k_videos_val_00.zip).

RUN IT (PowerShell, from the repo root; Modal account ahmad-yonis):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run --detach scripts\\modal_bdd100k_download.py --torrent C:\\Users\\mamou\\Downloads\\bdd100k.torrent --file 99

Cost: one small CPU container while the torrent downloads (cents per hour);
the download speed depends on how many people are sharing the torrent.
"""

from __future__ import annotations

from pathlib import Path

import modal

# ---- CONFIG ----
VOLUME = "safe-distance-data"
TARGET = "/data/bdd100k/videos"
TIMEOUT_H = 12                   # give up after this long (a slow torrent)
STALL_MIN = 30                   # aria2 gives up if the speed stays near zero this long
# ----------------

app = modal.App("safe-distance-bdd100k-download")
volume = modal.Volume.from_name(VOLUME)
image = modal.Image.debian_slim(python_version="3.12").apt_install("aria2", "unzip")


@app.function(image=image, volumes={"/data": volume}, cpu=2, memory=4096,
              timeout=TIMEOUT_H * 3600)     # default container disk (a custom size must be >= 512 GB)
def download(torrent: bytes, file_index: int) -> dict:
    """Fetch file `file_index` of the torrent, unzip its videos into the Volume, report."""
    import subprocess
    import time
    import zipfile

    work = Path("/tmp/bdd")
    work.mkdir(parents=True, exist_ok=True)
    (work / "bdd100k.torrent").write_bytes(torrent)
    start = time.time()
    subprocess.run(["aria2c", "--select-file", str(file_index), "--seed-time=0", "--file-allocation=none",
                    "--summary-interval=60", "--console-log-level=warn", "--bt-stop-timeout", str(STALL_MIN * 60),
                    "--dir", str(work), str(work / "bdd100k.torrent")], check=True)
    took = time.time() - start
    zips = [p for p in work.rglob("*.zip") if p.stat().st_size > 0]
    if not zips:
        raise RuntimeError("no zip downloaded")
    z = zips[0]
    split = z.stem.split("_")[-2]                      # bdd100k_videos_val_00 -> val
    out = Path(TARGET) / split
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        videos = [n for n in zf.namelist() if n.lower().endswith((".mov", ".mp4"))]
        for n in videos:                                # flat: <TARGET>/<split>/<clip>.mov
            (out / Path(n).name).write_bytes(zf.read(n))
    volume.commit()
    return {"zip": z.name, "gigabytes": round(z.stat().st_size / 1e9, 2), "download_minutes": round(took / 60, 1),
            "videos": len(videos), "saved_to": str(out)}


@app.local_entrypoint()
def main(torrent: str, file: int = 99) -> None:
    print(download.remote(Path(torrent).read_bytes(), file))
