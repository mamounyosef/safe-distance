"""Download the CCD (Car Crash Dataset) crash videos for local viewing.

CCD (Bao et al., Rochester Institute of Technology, MIT licence) has 1,500
dashcam clips that each show a REAL crash: 50 frames (5 s, 10 fps), with the
crash frames marked. It is shared as a public Google Drive folder, linked from
https://github.com/Cogito2012/CarCrashDataset. All crash videos are in one
small zip (0.79 GB): it is downloaded, unpacked, and deleted.

Annotation line (Crash-1500.txt):
    vidname, 50 binary labels (1 = crash frame), start frame, YouTube ID,
    timing (Day/Night), weather, egoinvolve (Yes = our own car crashes)

Run: .venv\\Scripts\\python.exe scripts\\download_ccd_samples.py
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import gdown

# ---- CONFIG ----
OUT = Path(r"C:\safe-distance-data\ccd")
ANNOTATIONS_ID = "13OgrD0-8cKG0X00MlA6JXr0G_JJmHYXg"   # videos/Crash-1500.txt
CRASH_ZIP_ID = "1fmcwGhr8JT9YfLUrlcvuCZ3ychi2eyFP"     # videos/Crash-1500.zip
# ----------------


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = OUT / "Crash-1500.txt"
    if not ann.exists():
        gdown.download(id=ANNOTATIONS_ID, output=str(ann), quiet=True)
    lines = ann.read_text().splitlines()
    ego = [l for l in lines if l.strip().endswith("Yes")]
    print(f"annotations: {len(lines)} crash clips, {len(ego)} with our own car involved")

    # The whole zip is small (0.79 GB), so download it, unpack, delete the zip.
    if not any(OUT.glob("*.mp4")):   # the zip unpacks its videos straight into OUT
        zip_path = OUT / "Crash-1500.zip"
        gdown.download(id=CRASH_ZIP_ID, output=str(zip_path), quiet=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(OUT)
        zip_path.unlink()
    n = len(list(OUT.rglob("*.mp4")))
    size = sum(p.stat().st_size for p in OUT.rglob("*.mp4")) / 1e9
    print(f"{n} crash videos in {OUT} ({size:.2f} GB)")


if __name__ == "__main__":
    main()
