"""Contact sheet of the Nexar crash clips where we gave NO warning in time.

For every crash / near-miss clip that the current rule missed (score_nexar.py,
variant "as_now"): the video frame SHOW_BEFORE_S before the event, with every
tracked object boxed and labelled (distance, TTC). Box colours: yellow = in our
path (within 1.2 m of our centre line), grey = outside it. No box at all = the
detector did not find anything there. Clips are downloaded from Modal (free)
one at a time and, if DELETE_AFTER, deleted again once the sheet is made.

RUN IT (from the repo root, after score_nexar.py):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\missed_crash_sheet.py

Writes results/<RUN>/missed_crashes_<n>.jpg (several pages).
"""

from __future__ import annotations

import gzip
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_nexar as sn  # noqa: E402

# ---- CONFIG ----
VARIANT = "as_now"            # which rule's misses to show
SHOW_BEFORE_S = 1.0           # frame shown: this long before the event
VIDEOS = Path(r"C:\safe-distance-data\nexar\train\positive")
DELETE_AFTER = True           # delete the clips this script downloaded, once done
MODAL = Path(sn.REPO) / ".venv" / "Scripts" / "modal.exe"
TILE_W = 480
COLS, ROWS = 4, 4
# ----------------


def fetch(clip: str) -> tuple[Path, bool]:
    """Local path of a crash clip, downloading it from Modal if needed. Returns (path, downloaded now)."""
    path = VIDEOS / f"{clip}.mp4"
    if path.exists():
        return path, False
    subprocess.run([str(MODAL), "volume", "get", "safe-distance-data",
                    f"nexar/train/positive/{clip}.mp4", str(path)], check=True, capture_output=True)
    return path, True


def tile(video: Path, row: dict, objs: list[dict]) -> np.ndarray:
    """The frame before the event with every object drawn, shrunk to TILE_W."""
    t = row["event_s"] - SHOW_BEFORE_S
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.set(cv2.CAP_PROP_POS_FRAMES, round(t * fps))
    ok, img = cap.read()
    cap.release()
    if not ok:
        img = np.zeros((720, 1280, 3), np.uint8)
    h, w = img.shape[:2]
    scale = TILE_W / w
    cv2.line(img, (w // 2, h - 40), (w // 2, h), (0, 255, 255), 3)      # our centre line
    for o in objs:
        in_path = o["gap"] <= sn.CORRIDOR_M
        colour = (0, 255, 255) if in_path else (160, 160, 160)
        x1, y1, x2, y2 = (int(v) for v in o["box"])
        cv2.rectangle(img, (x1, y1), (x2, y2), colour, 4 if in_path else 2)
        ttc = "--" if o["ttc"] is None else ("never" if math.isinf(o["ttc"]) else f"{o['ttc']:.1f}s")
        cv2.putText(img, f"{o['distance']:.0f}m {ttc}", (x1, max(y1 - 8, 30)), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, colour, 2, cv2.LINE_AA)
    img = cv2.resize(img, (TILE_W, round(h * scale)))
    label = f"{row['clip']} event {row['event_s']:.1f}s, shown {SHOW_BEFORE_S:g}s before ({row['light']})"
    cv2.rectangle(img, (0, 0), (TILE_W, 18), (0, 0, 0), -1)
    cv2.putText(img, label, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def main() -> None:
    results = json.loads((sn.OUT / "results.json").read_text())
    rules = results["variants"][VARIANT]["rules"]
    missed = [r for r in results["variants"][VARIANT]["per_clip"] if not r["warned"]]
    print(f"{len(missed)} missed crash clips ({VARIANT})")
    tiles, downloaded = [], []
    for i, row in enumerate(missed):
        with gzip.open(next(sn.DATA.rglob(f"{sn.RUN}/train/positive/{row['clip']}.json.gz")), "rt") as fh:
            clip = json.load(fh)
        frames = sn.filter_clip(clip, rules["clahe"])
        target = row["event_s"] - SHOW_BEFORE_S
        _, objs = min(frames, key=lambda f: abs(f[0] - target))        # saved frame nearest the shown time
        video, new = fetch(row["clip"])
        if new:
            downloaded.append(video)
        tiles.append(tile(video, row, objs))
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(missed)}", flush=True)
    per_page = COLS * ROWS
    blank = np.zeros_like(tiles[0])
    for page in range(math.ceil(len(tiles) / per_page)):
        chunk = tiles[page * per_page:(page + 1) * per_page]
        chunk += [blank] * (per_page - len(chunk))
        sheet = np.vstack([np.hstack(chunk[r * COLS:(r + 1) * COLS]) for r in range(ROWS)])
        out = sn.OUT / f"missed_crashes_{page + 1}.jpg"
        cv2.imwrite(str(out), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(f"saved {out}")
    if DELETE_AFTER:
        for v in downloaded:
            v.unlink()
        print(f"deleted {len(downloaded)} downloaded clips")


if __name__ == "__main__":
    main()
