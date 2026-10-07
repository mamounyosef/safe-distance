"""List the files inside a .torrent file (names, sizes, index numbers), without downloading anything.

The index numbers are what a torrent tool needs to fetch only some files
(e.g. aria2c --select-file=5).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe scripts\\torrent_files.py C:\\Users\\mamou\\Downloads\\bdd100k.torrent [filter]
"""

import sys
from pathlib import Path


def bdecode(data: bytes, i: int = 0):
    """Decode one bencoded value starting at data[i]; return (value, next index)."""
    c = data[i:i + 1]
    if c == b"i":                                   # integer: i<digits>e
        end = data.index(b"e", i)
        return int(data[i + 1:end]), end + 1
    if c == b"l":                                   # list: l<items>e
        out, i = [], i + 1
        while data[i:i + 1] != b"e":
            v, i = bdecode(data, i)
            out.append(v)
        return out, i + 1
    if c == b"d":                                   # dictionary: d<key><value>...e
        out, i = {}, i + 1
        while data[i:i + 1] != b"e":
            k, i = bdecode(data, i)
            v, i = bdecode(data, i)
            out[k] = v
        return out, i + 1
    colon = data.index(b":", i)                     # byte string: <length>:<bytes>
    n = int(data[i:colon])
    return data[colon + 1:colon + 1 + n], colon + 1 + n


def main() -> None:
    meta, _ = bdecode(Path(sys.argv[1]).read_bytes())
    filt = sys.argv[2] if len(sys.argv) > 2 else ""
    info = meta[b"info"]
    print("name:", info[b"name"].decode(errors="replace"))
    trackers = [meta.get(b"announce", b"")] + [t for tier in meta.get(b"announce-list", []) for t in tier]
    print("trackers:", sorted({t.decode(errors="replace") for t in trackers if t}))
    files = info.get(b"files") or [{b"length": info[b"length"], b"path": [info[b"name"]]}]
    total = 0
    for idx, f in enumerate(files, start=1):        # aria2c numbers files from 1
        path = "/".join(p.decode(errors="replace") for p in f[b"path"])
        total += f[b"length"]
        if filt in path:
            print(f"{idx:4d}  {f[b'length'] / 1e9:8.2f} GB  {path}")
    print(f"{len(files)} files, {total / 1e12:.2f} TB in total")


if __name__ == "__main__":
    main()
