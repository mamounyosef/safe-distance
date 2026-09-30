"""Download a nuScenes archive and unpack it on the fly, keeping only chosen folders.

The archive is never saved: each file inside it is read as it arrives and either
written to disk (if its path starts with one of KEEP_PREFIXES) or skipped.
If the connection drops, it has to start again from the beginning.

Run: python scripts/stream_extract_nuscenes.py
"""

import tarfile
import time
import urllib.request
from pathlib import Path

# ---- CONFIG ----
# CloudFront mirror: 4.7 MB/s vs 0.5 MB/s from the S3 host on 2026-09-30.
URL = "https://d36yt3mvayqw5m.cloudfront.net/public/v1.0/v1.0-trainval10_blobs.tgz"   # part 10: 85 of the 99 night scenes
OUT_DIR = Path(r"C:\safe-distance-data\nuscenes-trainval")
KEEP_PREFIXES = ("samples/CAM_FRONT/",)   # keyframe images of the front camera only
LOG_EVERY_S = 30
# ----------------


class CountingReader:
    """Wraps the download stream and counts bytes so progress can be printed."""

    def __init__(self, raw, total):
        self.raw, self.total, self.done = raw, total, 0

    def read(self, n=-1):
        data = self.raw.read(n)
        self.done += len(data)
        return data


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    response = urllib.request.urlopen(URL)
    total = int(response.headers.get("Content-Length", 0))
    reader = CountingReader(response, total)
    kept = skipped = kept_bytes = 0
    start = last_log = time.time()
    with tarfile.open(fileobj=reader, mode="r|gz") as archive:
        for member in archive:
            if member.isfile() and member.name.startswith(KEEP_PREFIXES):
                archive.extract(member, OUT_DIR, filter="data")
                kept += 1
                kept_bytes += member.size
            else:
                skipped += 1
            now = time.time()
            if now - last_log > LOG_EVERY_S:
                last_log = now
                speed = reader.done / (now - start) / 1e6
                left_min = (total - reader.done) / (speed * 1e6) / 60 if speed else 0
                print(f"{reader.done / 1e9:6.1f} / {total / 1e9:.1f} GB  {speed:5.1f} MB/s  "
                      f"~{left_min:4.0f} min left  kept {kept} files ({kept_bytes / 1e9:.2f} GB), "
                      f"skipped {skipped}", flush=True)
    print(f"DONE in {(time.time() - start) / 60:.0f} min: kept {kept} files "
          f"({kept_bytes / 1e9:.2f} GB), skipped {skipped}", flush=True)


if __name__ == "__main__":
    main()
