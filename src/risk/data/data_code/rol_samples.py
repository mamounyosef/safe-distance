"""Sample ROL crash clips with their risky-object labels drawn on, joined into ONE video (this PC, free).

ROL (Risky Object Localization, Karim et al. 2023, MIT licence): 1,000 dashcam crash
clips of 100 frames. Its released files give, per frame, every tracked road user's
box and a flag saying whether it is THE risky object (the one that will crash), plus
the accident frame (toa). This shows how early people marked the risky object.

Each clip: title card, then the clip with
    every tracked road user (thin grey box)
    the risky object (thick red box, "RISKY")
    time relative to the accident ("-1.8 s before accident")
    a 1.5 s freeze on the first frame where the risky object is marked, and on the accident frame

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\rol_samples.py

Output: C:\\Users\\mamou\\Downloads\\rol_samples.mp4 (+ rol_samples.json).
"""

from __future__ import annotations

import json
import random
import subprocess
from pathlib import Path

import cv2
import gdown
import numpy as np

# ---- CONFIG ----
VIDEO_FOLDER = "https://drive.google.com/drive/folders/164J2F4aI4DpZEEgIUZlvabOMVxWxP2O9"   # ROL videos
FEATURE_FOLDER = "https://drive.google.com/drive/folders/1V5BoyF8QJOxjoPwSDYKuAO8r76gpPg8v"  # ROL labels (.npz)
CACHE = Path(r"C:\safe-distance-data\rol\samples")
OUT = Path.home() / "Downloads" / "rol_samples.mp4"
N, SEED = 20, 7
FREEZE_S, TITLE_S = 1.5, 1.5
# ----------------


def listing(url: str) -> dict[str, str]:
    """File name (e.g. train/103_M) -> Google Drive id, without downloading."""
    files = gdown.download_folder(url, skip_download=True, quiet=True) or []
    return {Path(f.path).with_suffix("").as_posix(): f.id for f in files}


def fetch(fid: str, out: Path) -> Path:
    """Download one Drive file once."""
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        gdown.download(id=fid, output=str(out), quiet=True)
    return out


def text(img, s, xy, scale=0.8, colour=(255, 255, 255), thick=2):
    """Text with a black outline."""
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 3, cv2.LINE_AA)
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, colour, thick, cv2.LINE_AA)


def main() -> None:
    global OUT
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    OUT = a.out
    OUT.parent.mkdir(parents=True, exist_ok=True)
    videos, labels = listing(VIDEO_FOLDER), listing(FEATURE_FOLDER)
    names = sorted(set(videos) & set(labels))
    print(f"{len(videos)} videos, {len(labels)} label files, {len(names)} with both")
    picks = random.Random(a.seed).sample(names, N)
    wr, size, fps_out, shown = None, None, None, []
    for k, name in enumerate(picks, 1):
        d = np.load(fetch(labels[name], CACHE / f"{name}.npz"))
        cap = cv2.VideoCapture(str(fetch(videos[name], CACHE / f"{name}.mp4")))
        fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
        frames = []
        while True:
            ok, img = cap.read()
            if not ok:
                break
            frames.append(img)
        cap.release()
        det, toa = d["detection"], int(d["toa"])          # det: (frames, objects, [track, x1, y1, x2, y2, risky])
        h, w = frames[0].shape[:2]
        # Boxes may be stored for a different image size than the video: scale by the largest coordinate seen.
        bx = det[..., 1:5]
        sx = w / max(1280.0, bx[..., [0, 2]].max()) if bx[..., [0, 2]].max() > w else 1.0
        sy = h / max(720.0, bx[..., [1, 3]].max()) if bx[..., [1, 3]].max() > h else 1.0
        risky_frames = [f for f in range(len(det)) if (det[f, :, 5] == 1).any()]
        first = risky_frames[0] if risky_frames else None
        if wr is None:
            size, fps_out = (w, h), fps
            tmp = OUT.with_suffix(".tmp.mp4")
            wr = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"), fps_out, size)
        card = np.zeros((size[1], size[0], 3), np.uint8)
        text(card, f"Clip {k}/{N}   {name}", (40, size[1] // 2 - 40), 1.2, thick=3)
        text(card, f"accident at {toa / fps:.1f} s; risky object first marked at "
                   f"{'-' if first is None else f'{first / fps:.1f} s'}", (40, size[1] // 2 + 20), 0.8)
        for _ in range(int(TITLE_S * fps_out)):
            wr.write(card)
        for f, img in enumerate(frames):
            img = cv2.resize(img, size).copy()
            if f < len(det):
                for r in det[f]:
                    if r[1:5].sum() == 0:
                        continue
                    x1, y1, x2, y2 = int(r[1] * sx), int(r[2] * sy), int(r[3] * sx), int(r[4] * sy)
                    if r[5] == 1:
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        text(img, "RISKY", (x1, max(y1 - 8, 22)), 0.7, (0, 0, 255))
                    else:
                        cv2.rectangle(img, (x1, y1), (x2, y2), (170, 170, 170), 1)
            t = (f - toa) / fps
            text(img, f"{t:+.1f} s {'before' if t < 0 else 'after'} accident", (15, 35), 0.8,
                 (255, 255, 255) if t < 0 else (0, 0, 255))
            if f >= toa:
                cv2.rectangle(img, (0, 0), (size[0] - 1, size[1] - 1), (0, 0, 255), 8)
            wr.write(img)
            if f in (first, toa):                         # hold: first risky mark, and the accident frame
                label = "RISKY OBJECT FIRST MARKED" if f == first else "ACCIDENT"
                held = img.copy()
                text(held, label, (15, size[1] - 20), 0.9, (0, 0, 255))
                for _ in range(int(FREEZE_S * fps_out)):
                    wr.write(held)
        shown.append({"n": k, "clip": name, "fps": round(fps, 2), "frames": len(frames), "accident_s": round(toa / fps, 2),
                      "risky_first_marked_s": None if first is None else round(first / fps, 2),
                      "marked_seconds_before_accident": None if first is None else round((toa - first) / fps, 2)})
        print(f"[{k}/{N}] {name}: accident {toa / fps:.1f} s, risky marked from "
              f"{shown[-1]['risky_first_marked_s']} s ({shown[-1]['marked_seconds_before_accident']} s before)", flush=True)
    wr.release()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT.with_suffix(".tmp.mp4")), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "23", str(OUT)], check=True)
    OUT.with_suffix(".tmp.mp4").unlink()
    OUT.with_suffix(".json").write_text(json.dumps(shown, indent=1))
    lead = sorted(s["marked_seconds_before_accident"] for s in shown if s["marked_seconds_before_accident"] is not None)
    print(f"saved {OUT}; risky object marked before the accident: median {lead[len(lead) // 2]} s, "
          f"min {lead[0]} s, max {lead[-1]} s")


if __name__ == "__main__":
    main()
