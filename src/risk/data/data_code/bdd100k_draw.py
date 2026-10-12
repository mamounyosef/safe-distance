"""Draw our BDD100K normal-driving clips from the official splits (runs on this PC, free).

BDD100K has 100,000 clips of 40 s: 70,000 train / 10,000 val / 20,000 test.
We draw, with a fixed seed:
    train 3,000   training (stage 1 learning curve uses the FIRST 250 / 500 / 1,000 / 3,000 lines)
    val     500   development checks (false warnings per hour)
    test  1,000   the final score only, once
The 608 ShareGPT4Video clips we used before are all in train; they are left out
of the draw so they stay an independent check.

The full zip (1.97 TB) is read remotely: only its table of contents is downloaded
(scripts/split_zip_remote.py). Needs this PC logged in to Hugging Face.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\bdd100k_draw.py

Writes to src/risk/data/bdd100k_ids/:
    train_3000.txt, val_500.txt, test_1000.txt   one clip id per line, in draw order
    zip_index.json                               where each drawn clip sits in the zip
                                                 (read by bdd100k_extract.py on Modal)
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
from split_zip_remote import open_archive  # noqa: E402

# ---- CONFIG ----
SEED = 20261012
COUNTS = {"train": 3000, "val": 500, "test": 1000}
EXCLUDE = REPO / "src/ttc/benchmarks/bdd100k/clip_ids.txt"     # the 608 clips used earlier
OUT_DIR = REPO / "src/risk/data/bdd100k_ids"
# ----------------


def main() -> None:
    from huggingface_hub import get_token

    start = time.time()
    z = open_archive(get_token())
    print(f"table of contents read in {time.time() - start:.0f} s: {len(z.infolist()):,} entries")
    excluded = {s.strip() for s in EXCLUDE.read_text().splitlines() if s.strip() and not s.startswith("#")}

    # Clips of each official split, sorted by name so the draw only depends on the seed.
    by_split = {s: [] for s in COUNTS}
    for info in z.infolist():
        parts = info.filename.split("/")                  # bdd100k/videos/100k/<split>/<id>.mov
        if len(parts) == 5 and parts[3] in by_split and parts[4].endswith(".mov"):
            by_split[parts[3]].append(info)
    rng = random.Random(SEED)
    index, summary = {}, {"seed": SEED, "excluded_sharegpt4video": len(excluded), "splits": {}}
    for split, n in COUNTS.items():
        pool = sorted((i for i in by_split[split] if Path(i.filename).stem not in excluded),
                      key=lambda i: i.filename)
        drawn = rng.sample(pool, n)
        assert all(i.compress_type == 0 for i in drawn), "expected stored (uncompressed) entries"
        ids = [Path(i.filename).stem for i in drawn]
        (OUT_DIR / f"{split}_{n}.txt").write_text("\n".join(ids) + "\n")
        for i, cid in zip(drawn, ids):
            # header_offset: start of the clip's local header; size and crc to check the download
            index[cid] = {"split": split, "path": i.filename, "header_offset": i.header_offset,
                          "size": i.compress_size, "crc": i.CRC}
        gb = sum(i.compress_size for i in drawn) / 1e9
        summary["splits"][split] = {"official": len(by_split[split]), "pool": len(pool), "drawn": n,
                                    "gb": round(gb, 2)}
        print(f"  {split:5s}: {n:5,d} drawn of {len(pool):,} ({len(by_split[split]):,} official), {gb:.1f} GB")
    (OUT_DIR / "zip_index.json").write_text(json.dumps({"summary": summary, "clips": index}, indent=0))
    print(f"saved to {OUT_DIR} ({time.time() - start:.0f} s)")


if __name__ == "__main__":
    main()
