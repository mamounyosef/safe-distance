"""Download a reproducible random subset of the KITTI object detection set.

KITTI is real driving footage from Karlsruhe, Germany, with every car, van,
truck, pedestrian and cyclist labelled, including its 3D position in metres
measured by a laser scanner. Only the training split has public labels, so
that is the one used for evaluation.

The image archive is 12.6 GB, so this downloads the small label and
calibration archives whole, then pulls only N_IMAGES randomly chosen images
out of the remote image zip, using HTTP range requests.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\download_kitti.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
Already downloaded files are skipped, so re-running resumes.

Licence: CC BY-NC-SA 3.0 (non-commercial, attribution).
See https://www.cvlibs.net/datasets/kitti/eval_object.php
"""

from __future__ import annotations

import io
import random
import time
import zipfile
from pathlib import Path

import requests
from remotezip import RemoteZip

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Where the dataset is unpacked.
DEST = Path("data/kitti")

# How many images to fetch out of the 7481 labelled ones. 0 = all (12.6 GB).
N_IMAGES = 1500

# Fixed seed, so the same subset is chosen every time and results are
# reproducible. Changing it picks a different subset.
SEED = 0

# Attempts per image before giving up, for flaky network connections.
RETRIES = 4

# ----------------------------------------------------------------------------

BASE = "https://s3.eu-central-1.amazonaws.com/avg-kitti"

# Labels (5.6 MB) and calibration (27 MB), downloaded whole.
SMALL_ARCHIVES = ["data_object_label_2.zip", "data_object_calib.zip"]
IMAGE_ARCHIVE = "data_object_image_2.zip"


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

    print(f"\n{IMAGE_ARCHIVE}: selecting images remotely")
    with RemoteZip(f"{BASE}/{IMAGE_ARCHIVE}") as z:
        names = sorted(n for n in z.namelist() if n.startswith("training/image_2/") and n.endswith(".png"))
        chosen = names if not N_IMAGES else sorted(random.Random(SEED).sample(names, N_IMAGES))

        # Record the subset so the benchmark evaluates exactly these images.
        ids = [Path(n).stem for n in chosen]
        (DEST / "subset.txt").write_text("\n".join(ids) + "\n")
        print(f"{IMAGE_ARCHIVE}: {len(chosen)} of {len(names)} images, seed {SEED}")

        for i, name in enumerate(chosen, 1):
            target = DEST / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                # A single slow response from the server should not abort a
                # 1500-file download, so each file gets a few attempts.
                for attempt in range(1, RETRIES + 1):
                    try:
                        target.write_bytes(z.read(name))
                        break
                    except Exception as e:  # remotezip wraps network errors in its own type
                        if attempt == RETRIES:
                            raise
                        print(f"  retry {attempt}/{RETRIES - 1} for {name}: {e}", flush=True)
                        time.sleep(5 * attempt)
            if i % 100 == 0 or i == len(chosen):
                print(f"  {i}/{len(chosen)}", flush=True)

    total = sum(f.stat().st_size for f in DEST.rglob("*") if f.is_file())
    print(f"\ndone: {total / 1e9:.2f} GB in {DEST}")


if __name__ == "__main__":
    main()
