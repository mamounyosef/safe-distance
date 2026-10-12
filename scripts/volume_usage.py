"""How much space every Modal Volume of the current account uses, by top-level folder.

Reads only the file listing (no container is started, no cost).

RUN IT (PowerShell, from the repo root; account picked by MODAL_CONFIG_PATH):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\python.exe scripts\\volume_usage.py
"""

from __future__ import annotations

import subprocess
from collections import defaultdict

import modal

TOP = 10      # folders shown per volume; the rest are summed in one line


def volume_names() -> list[str]:
    """Names of all Volumes in the account (from the modal CLI)."""
    out = subprocess.run(["modal", "volume", "list", "--json"], capture_output=True, text=True, check=True).stdout
    import json
    return [v["name"] for v in json.loads(out)]


def main() -> None:
    grand = 0
    for name in volume_names():
        vol = modal.Volume.from_name(name)
        by_top = defaultdict(lambda: [0, 0])          # top-level folder -> [bytes, files]
        for e in vol.listdir("/", recursive=True):
            if e.type == modal.volume.FileEntryType.FILE:
                top = e.path.lstrip("/").split("/")[0]
                by_top[top][0] += e.size
                by_top[top][1] += 1
        total = sum(b for b, _ in by_top.values())
        grand += total
        print(f"\n{name}: {total / 1e9:,.1f} GB in {sum(n for _, n in by_top.values()):,} files")
        rows = sorted(by_top.items(), key=lambda kv: -kv[1][0])
        for top, (b, n) in rows[:TOP]:
            print(f"  {b / 1e9:10,.1f} GB  {n:9,d} files  {top}")
        if len(rows) > TOP:                            # files at the volume's root, folded into one line
            rest = rows[TOP:]
            print(f"  {sum(b for _, (b, _) in rest) / 1e9:10,.1f} GB  {sum(n for _, (_, n) in rest):9,d} files  "
                  f"({len(rest):,} more entries)")
    print(f"\nall volumes: {grand / 1e9:,.1f} GB")


if __name__ == "__main__":
    main()
