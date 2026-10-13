"""Sample DoTA crash clips, with their labels drawn on, joined into ONE video to watch (this PC, free).

Picks N_OURS clips where our own camera car crashes and N_OTHERS where other road
users crash (seeded, random), downloads just those seconds from YouTube (yt-dlp),
and writes one long video. Each clip is preceded by a title card, and shows:
    time relative to the labelled anomaly start (negative = before)
    red frame + "ANOMALY" while inside the labelled anomaly window
    the labelled boxes of the involved road users (DoTA starts them at the anomaly start)
    a 1.5 s freeze on the anomaly-start frame, so you can judge how early the danger is visible

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\dota_samples.py

Output: C:\\Users\\mamou\\Downloads\\dota_samples.mp4 (+ dota_samples.json: which clips, in order).
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

# ---- CONFIG ----
DOTA_META = Path(r"C:\safe-distance-data\dota\meta")
CLIP_DIR = Path(r"C:\safe-distance-data\dota\samples\videos")   # downloaded YouTube sections
OUT = Path.home() / "Downloads" / "dota_samples.mp4"
N_OURS, N_OTHERS = 20, 10
SEED = 7
FPS = 10                         # DoTA labels are at 10 frames per second; the output plays at real speed
WIDTH = 1280                     # output size (DoTA boxes are in 1280x720 pixels)
HEIGHT = 720
TITLE_S, FREEZE_S = 2.0, 1.5
# ----------------


def pick() -> list[dict]:
    """Random clips that are not marked 'ignore' and have boxes, from videos still online."""
    broken = {u.strip().split("=")[-1] for u in (DOTA_META / "broken_urls.txt").read_text().splitlines() if u.strip()}
    ours, others = [], []
    for f in sorted((DOTA_META / "annotations" / "annotations").glob("*.json")):
        a = json.loads(f.read_text())
        yt = a["video_name"].rsplit("_", 1)[0]
        if a["ignore"] or yt in broken or not any(fr["objects"] for fr in a["labels"]):
            continue
        (ours if a["ego_involve"] else others).append(a)
    rng = random.Random(SEED)
    return rng.sample(ours, N_OURS) + rng.sample(others, N_OTHERS)


def download(a: dict) -> Path | None:
    """Only this clip's seconds of the YouTube video, cut exactly (re-encoded at the cut)."""
    out = CLIP_DIR / f"{a['video_name']}.mp4"
    if out.exists():
        return out
    yt = a["video_name"].rsplit("_", 1)[0]
    # Label frame n (1-based, extracted at 10 per second) sits at about (n - 1) / 10 s in the video.
    start, end = (a["video_start"] - 1) / FPS, a["video_end"] / FPS
    cmd = [sys.executable, "-m", "yt_dlp", "-q", "--no-warnings", "-f", "bv*[height<=720][ext=mp4]/bv*[height<=720]/b",
           "--download-sections", f"*{start:.2f}-{end:.2f}", "--force-keyframes-at-cuts",
           "-o", str(out), f"https://www.youtube.com/watch?v={yt}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        print(f"   download failed: {r.stderr.strip()[:200]}")
        return None
    return out


def frames_at_10fps(path: Path, n: int) -> list[np.ndarray]:
    """The clip resampled to 10 per second (frame j = the video frame at j / 10 s), as DoTA did."""
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    allf = []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        allf.append(img)
    cap.release()
    if not allf:
        return []
    pick_idx = [min(int(round(j * fps / FPS)), len(allf) - 1) for j in range(n)]
    return [cv2.resize(allf[i], (WIDTH, HEIGHT)) for i in pick_idx]


def text(img, s, xy, scale=0.8, colour=(255, 255, 255), thick=2):
    """White text with a black outline (readable on any background)."""
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 3, cv2.LINE_AA)
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, colour, thick, cv2.LINE_AA)


def title_card(k: int, total: int, a: dict) -> np.ndarray:
    """Black card naming the clip before it plays."""
    img = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    who = "OUR CAR CRASHES" if a["ego_involve"] else "OTHER ROAD USERS CRASH (our car only watches)"
    text(img, f"Clip {k}/{total}", (60, 200), 1.6, thick=3)
    text(img, who, (60, 290), 1.1, (0, 200, 255) if a["ego_involve"] else (255, 200, 0), 3)
    text(img, f"type: {a['accident_name']}   {'night' if a['night'] else 'day'}", (60, 360), 1.0)
    text(img, f"anomaly starts {a['anomaly_start'] / FPS:.1f} s into the clip   id {a['video_name']}", (60, 420), 0.8)
    return img


def annotate(img, j: int, a: dict) -> np.ndarray:
    """Overlay time, anomaly window and labelled boxes on clip frame j."""
    img = img.copy()
    fr = a["labels"][j] if j < len(a["labels"]) else {"objects": []}
    for o in fr["objects"]:
        x1, y1, x2, y2 = (int(v) for v in o["bbox"])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 3)
        text(img, f"{o['category']} #{o['obj_track_id']}", (x1 + 4, max(y1 - 8, 24)), 0.7, (0, 255, 255))
    t = (j - a["anomaly_start"]) / FPS
    inside = a["anomaly_start"] <= j <= a["anomaly_end"]
    if inside:
        cv2.rectangle(img, (0, 0), (WIDTH - 1, HEIGHT - 1), (0, 0, 255), 12)
        text(img, "ANOMALY (labelled)", (WIDTH - 360, 50), 1.0, (0, 0, 255))
    text(img, f"{t:+.1f} s {'before' if t < 0 else 'after'} anomaly start", (20, 50), 1.0,
         (255, 255, 255) if t < 0 else (0, 0, 255))
    text(img, "OUR CAR" if a["ego_involve"] else "OTHERS", (20, HEIGHT - 25), 0.8,
         (0, 200, 255) if a["ego_involve"] else (255, 200, 0))
    return img


def main() -> None:
    CLIP_DIR.mkdir(parents=True, exist_ok=True)
    clips = pick()
    tmp = OUT.with_suffix(".tmp.mp4")
    wr = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT))
    shown = []
    for k, a in enumerate(clips, 1):
        print(f"[{k}/{len(clips)}] {a['video_name']} ({'ours' if a['ego_involve'] else 'others'}, "
              f"{a['accident_name']})", flush=True)
        path = download(a)
        frames = frames_at_10fps(path, a["num_frames"]) if path else []
        if not frames:
            continue
        for _ in range(int(TITLE_S * FPS)):
            wr.write(title_card(len(shown) + 1, len(clips), a))
        for j, img in enumerate(frames):
            out = annotate(img, j, a)
            wr.write(out)
            if j == a["anomaly_start"]:                 # hold the anomaly-start frame
                for _ in range(int(FREEZE_S * FPS)):
                    wr.write(out)
        shown.append({"n": len(shown) + 1, "id": a["video_name"], "our_car": a["ego_involve"],
                      "type": a["accident_name"], "night": a["night"],
                      "anomaly_start_s": a["anomaly_start"] / FPS, "clip_s": a["num_frames"] / FPS})
    wr.release()
    # Re-encode to H.264 so any player opens it.
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "23", str(OUT)], check=True)
    tmp.unlink()
    OUT.with_suffix(".json").write_text(json.dumps(shown, indent=1))
    print(f"{len(shown)} of {len(clips)} clips in {OUT}")


if __name__ == "__main__":
    main()
