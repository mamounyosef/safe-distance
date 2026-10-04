"""Contact sheet of the false-warning moments on Nexar normal-driving clips.

For every false warning found by diagnose_nexar.py: the video frame at that
moment, the object that raised it (red box), and our path at its distance
(yellow lines: 1.2 m each side of our centre line, using the guessed lens).
Only the clips needed are downloaded from Modal (free), one at a time.

RUN IT (from the repo root, after diagnose_nexar.py):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\nexar\\false_warning_sheet.py

Writes results/<RUN>/false_warnings_<n>.jpg (several pages).
"""

from __future__ import annotations

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
VIDEOS = Path(r"C:\safe-distance-data\nexar\train\negative")   # local copies of the needed clips
MODAL = Path(sn.REPO) / ".venv" / "Scripts" / "modal.exe"
TILE_W = 480                 # width of one picture on the sheet (px)
COLS, ROWS = 4, 4            # pictures per page
# ----------------


def fetch(clip: str) -> Path:
    """Download one normal clip from the Modal Volume, unless it is already here."""
    path = VIDEOS / f"{clip}.mp4"
    if not path.exists():
        VIDEOS.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(MODAL), "volume", "get", "safe-distance-data",
                        f"nexar/train/negative/{clip}.mp4", str(path)], check=True)
    return path


def tile(video: Path, row: dict) -> np.ndarray:
    """The frame at the warning, with the object and our path drawn, shrunk to TILE_W."""
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.set(cv2.CAP_PROP_POS_FRAMES, round(row["t"] * fps))
    ok, img = cap.read()
    cap.release()
    if not ok:
        img = np.zeros((720, 1280, 3), np.uint8)
    h, w = img.shape[:2]
    fx = (w / 2) / math.tan(math.radians(110.0) / 2)       # same guessed lens as the Modal run
    x1, y1, x2, y2 = (int(v) for v in row["box"])
    # Our path (1.2 m each side) at the object's distance, drawn at the box's bottom.
    half = sn.CORRIDOR_M * fx / max(row["distance_m"], 0.1)
    for x in (w / 2 - half, w / 2 + half):
        cv2.line(img, (int(x), y2 - 60), (int(x), y2 + 20), (0, 255, 255), 3)
    cv2.line(img, (w // 2, h - 40), (w // 2, h), (0, 255, 255), 3)    # our centre line
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
    img = cv2.resize(img, (TILE_W, round(h * TILE_W / w)))
    label = (f"{row['clip']} t={row['t']:.1f}s {row['cls']} {row['distance_m']:.0f}m "
             f"close {row['closing_mps']:.0f}m/s TTC {row['ttc_s']:.1f}s gap {row['lateral_gap_m']:.1f}m")
    cv2.rectangle(img, (0, 0), (TILE_W, 18), (0, 0, 0), -1)
    cv2.putText(img, label, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def main() -> None:
    rows = json.loads((sn.OUT / "diagnosis.json").read_text())["false_rows"]
    if not rows or "box" not in rows[0]:
        sys.exit("diagnosis.json has no boxes: re-run diagnose_nexar.py first")
    rows.sort(key=lambda r: (r["clip"], r["t"]))
    tiles = []
    for r in rows:
        tiles.append(tile(fetch(r["clip"]), r))
    per_page = COLS * ROWS
    blank = np.zeros_like(tiles[0])
    for page in range(math.ceil(len(tiles) / per_page)):
        chunk = tiles[page * per_page:(page + 1) * per_page]
        chunk += [blank] * (per_page - len(chunk))
        sheet = np.vstack([np.hstack(chunk[i * COLS:(i + 1) * COLS]) for i in range(ROWS)])
        out = sn.OUT / f"false_warnings_{page + 1}.jpg"
        cv2.imwrite(str(out), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
        print(f"saved {out}")


if __name__ == "__main__":
    main()
