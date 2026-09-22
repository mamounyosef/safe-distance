"""Turn a folder of dataset frames into an mp4 the detector can run on.

Lost and Found stores each scene as numbered PNG frames rather than a video
file, so this stitches them together. Frames are already sampled at every
10th original frame, so playing them at the original 30 frames per second
would look 10x too fast; FPS below is set low to keep it watchable.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe scripts\\frames_to_video.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

from pathlib import Path

import cv2

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

# Folder of PNG frames. Sorting the filenames gives the correct order.
FRAMES_DIR = Path("data/lost_and_found/leftImg8bit/test/04_Maurener_Weg_8")

# Output video.
OUTPUT = Path("data/videos/lost_and_found_04.mp4")

# Playback rate. The source frames are every 10th of a 30 fps recording, so
# 3 fps plays back at roughly real-world speed; higher just looks faster.
FPS = 6

# ----------------------------------------------------------------------------


def main() -> None:
    frames = sorted(FRAMES_DIR.glob("*.png"))
    if not frames:
        raise SystemExit(f"No PNG frames found in {FRAMES_DIR}")

    first = cv2.imread(str(frames[0]))
    height, width = first.shape[:2]
    print(f"{len(frames)} frames at {width}x{height} -> {OUTPUT} @ {FPS} fps")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(OUTPUT), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (width, height)
    )

    for i, path in enumerate(frames, 1):
        img = cv2.imread(str(path))
        if img is None:
            print(f"  skipped unreadable frame: {path.name}")
            continue
        # Each scene contains several separate drive-pasts; the sequence id is
        # the second-to-last number in the filename. Show it so a jump in the
        # video is understood as a new run, not a tracking failure.
        parts = path.stem.split("_")
        cv2.putText(
            img, f"seq {parts[-3]}  frame {parts[-2]}", (12, 34),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA,
        )
        writer.write(img)
        if i % 50 == 0:
            print(f"  {i}/{len(frames)}")

    writer.release()
    size_mb = OUTPUT.stat().st_size / 1e6
    print(f"done: {OUTPUT} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
