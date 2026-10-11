"""Read single files out of a huge zip that is stored on the web as several byte-for-byte parts.

The full BDD100K video zip (1.97 TB) is on Hugging Face as 19 parts
(linxxx3/bdd100k_videos: bdd100k_videos.zip.part-00000 ... part-00018). A zip
keeps its table of contents at the end, and each file's bytes in one place, so
by treating the parts as one long file and asking the server for byte ranges
only, we can list the archive and extract chosen clips without downloading the
rest.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\split_zip_remote.py list            # summary of the archive
    .venv\\Scripts\\python.exe scripts\\split_zip_remote.py list train 5    # 5 names containing "train"

Other scripts import SplitHttpFile / open_archive to extract clips.
"""

from __future__ import annotations

import io
import sys
import zipfile
from collections import Counter

import requests

# ---- CONFIG ----
BASE = "https://huggingface.co/datasets/linxxx3/bdd100k_videos/resolve/main/bdd100k_videos/bdd100k_videos.zip.part-"
PART_SIZE = 107_374_182_400            # every part except the last (from the repo's manifest.json)
TOTAL_SIZE = 1_969_155_915_058         # whole zip (manifest.json)
N_PARTS = 19
# ----------------


class SplitHttpFile(io.RawIOBase):
    """A read-only, seekable file made of N_PARTS web files, read with HTTP range requests."""

    def __init__(self, token: str | None = None):
        self.pos = 0
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = 0) -> int:
        self.pos = {0: offset, 1: self.pos + offset, 2: TOTAL_SIZE + offset}[whence]
        return self.pos

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = TOTAL_SIZE - self.pos
        n = min(n, TOTAL_SIZE - self.pos)
        out = bytearray()
        while n > 0:
            part, off = divmod(self.pos, PART_SIZE)          # which part, and where inside it
            take = min(n, PART_SIZE - off)
            r = self.session.get(f"{BASE}{part:05d}", headers={"Range": f"bytes={off}-{off + take - 1}"},
                                 timeout=120, allow_redirects=True)
            r.raise_for_status()
            if r.status_code != 206:
                raise RuntimeError(f"server ignored the byte range (status {r.status_code})")
            out += r.content
            self.pos += len(r.content)
            n -= len(r.content)
        return bytes(out)

    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def open_archive(token: str | None = None) -> zipfile.ZipFile:
    """The whole BDD100K video zip, opened remotely (only its table of contents is read now)."""
    return zipfile.ZipFile(io.BufferedReader(SplitHttpFile(token), buffer_size=1 << 20))


def main() -> None:
    from huggingface_hub import get_token
    z = open_archive(get_token())
    infos = [i for i in z.infolist() if not i.is_dir()]
    if len(sys.argv) > 2:
        hits = [i for i in infos if sys.argv[2] in i.filename]
        for i in hits[:int(sys.argv[3]) if len(sys.argv) > 3 else 10]:
            print(f"  {i.file_size / 1e6:7.1f} MB  stored={i.compress_type == zipfile.ZIP_STORED}  {i.filename}")
        print(f"{len(hits)} names contain {sys.argv[2]!r}")
        return
    folders = Counter("/".join(i.filename.split("/")[:-1]) for i in infos)
    print(f"{len(infos)} files, {sum(i.file_size for i in infos) / 1e12:.2f} TB")
    for f, c in folders.most_common(20):
        print(f"  {c:7d}  {f}")


if __name__ == "__main__":
    main()
