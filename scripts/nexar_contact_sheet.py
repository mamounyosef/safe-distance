"""Contact sheet of the downloaded Nexar collision clips: one row per clip, frames
at 2 s and 1 s before the collision and at the collision (time_of_event), to see
what kind of collision each clip shows (car ahead, from the side, ...).

Run: .venv\\Scripts\\python.exe scripts\\nexar_contact_sheet.py
"""

import csv
from pathlib import Path

import cv2
import numpy as np

# ---- CONFIG ----
SPLIT_DIR = Path(r"C:\safe-distance-data\nexar\train\positive")
OUT = Path(r"C:\safe-distance-data\nexar\contact_sheet")
OFFSETS_S = [-2.0, -1.0, 0.0]   # seconds relative to the collision
THUMB_W = 400
PER_SHEET = 10
# ----------------


def main() -> None:
    meta = {r["file_name"][:-4]: r for r in csv.DictReader((SPLIT_DIR / "metadata.csv").open())}
    clips = sorted(p.stem for p in SPLIT_DIR.glob("*.mp4"))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for clip in clips:
        cap = cv2.VideoCapture(str(SPLIT_DIR / f"{clip}.mp4"))
        event = float(meta[clip]["time_of_event"])
        thumbs = []
        for off in OFFSETS_S:
            cap.set(cv2.CAP_PROP_POS_MSEC, max(event + off, 0) * 1000)
            ok, img = cap.read()
            img = img if ok else np.zeros((720, 1280, 3), np.uint8)
            img = cv2.resize(img, (THUMB_W, int(img.shape[0] * THUMB_W / img.shape[1])))
            cv2.putText(img, f"{clip}  t{off:+.0f}s", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            thumbs.append(img)
        rows.append(np.hstack(thumbs))
    for i in range(0, len(rows), PER_SHEET):
        path = OUT / f"sheet_{i // PER_SHEET + 1}.jpg"
        cv2.imwrite(str(path), np.vstack(rows[i:i + PER_SHEET]), [cv2.IMWRITE_JPEG_QUALITY, 80])
        print("wrote", path)


if __name__ == "__main__":
    main()
