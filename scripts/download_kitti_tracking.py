"""Download the labelled KITTI tracking sequences.

KITTI tracking is 21 continuous driving sequences where every car, van,
pedestrian and cyclist keeps its true ID across frames, which is exactly the
ground truth needed to measure a tracker. Only the training split has public
labels.

The image archive is 15.8 GB, mostly the unlabelled test split, so this pulls
only the labelled training sequences listed in SEQUENCES out of the remote
zip, using HTTP range requests. The small archives (labels, calibration and
oxts: GPS and ego vehicle speed per frame) are downloaded whole.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_kitti_tracking.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
Already downloaded files are skipped, so re-running resumes.

Licence: CC BY-NC-SA 3.0 (non-commercial, attribution).
See https://www.cvlibs.net/datasets/kitti/eval_tracking.php
"""

from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import requests
from remotezip import RemoteZip

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Where the dataset is unpacked.
DEST = Path("data/kitti_tracking")

# Training sequences to fetch, "0000" to "0020". None = all 21 (6.5 GB).
SEQUENCES = None

# Attempts per image before giving up, for flaky network connections.
RETRIES = 4

# ----------------------------------------------------------------------------

BASE = "https://s3.eu-central-1.amazonaws.com/avg-kitti"
SMALL_ARCHIVES = ["data_tracking_label_2.zip", "data_tracking_calib.zip", "data_tracking_oxts.zip"]
IMAGE_ARCHIVE = "data_tracking_image_2.zip"


def fetch_small(name: str) -> None:
    print(f"{name}: downloading whole archive")
    response = requests.get(f"{BASE}/{name}", timeout=600)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(DEST)
    print(f"{name}: extracted, {len(response.content) / 1e6:.1f} MB")


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"destination: {DEST.resolve()}")

    for name in SMALL_ARCHIVES:
        fetch_small(name)

    print(f"\n{IMAGE_ARCHIVE}: selecting training sequences remotely")
    with RemoteZip(f"{BASE}/{IMAGE_ARCHIVE}") as z:
        # Paths look like training/image_02/0007/000123.png
        wanted = []
        for n in z.namelist():
            parts = n.split("/")
            if len(parts) == 4 and parts[0] == "training" and parts[3].endswith(".png"):
                if SEQUENCES is None or parts[2] in SEQUENCES:
                    wanted.append(n)
        wanted.sort()
        print(f"{IMAGE_ARCHIVE}: {len(wanted)} frames to fetch")

        for i, name in enumerate(wanted, 1):
            target = DEST / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                # A single slow response should not abort an 8000-file download.
                for attempt in range(1, RETRIES + 1):
                    try:
                        target.write_bytes(z.read(name))
                        break
                    except Exception as e:  # remotezip wraps network errors in its own type
                        if attempt == RETRIES:
                            raise
                        print(f"  retry {attempt}/{RETRIES - 1} for {name}: {e}", flush=True)
                        time.sleep(5 * attempt)
            if i % 250 == 0 or i == len(wanted):
                print(f"  {i}/{len(wanted)}", flush=True)

    total = sum(f.stat().st_size for f in DEST.rglob("*") if f.is_file())
    print(f"\ndone: {total / 1e9:.2f} GB in {DEST}")


if __name__ == "__main__":
    main()
