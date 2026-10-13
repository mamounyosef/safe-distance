"""Shared helpers for the sample videos (title cards, outlined text, writing one H.264 video)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import cv2
import numpy as np


def text(img, s, xy, scale=0.8, colour=(255, 255, 255), thick=2):
    """Text with a black outline, readable on any background."""
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 3, cv2.LINE_AA)
    cv2.putText(img, s, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, colour, thick, cv2.LINE_AA)


def card(size: tuple[int, int], lines: list[str]) -> np.ndarray:
    """Black title card with a few lines of text."""
    img = np.zeros((size[1], size[0], 3), np.uint8)
    for i, s in enumerate(lines):
        text(img, s, (40, size[1] // 2 - 60 + 55 * i), 1.1 if i == 0 else 0.8, thick=3 if i == 0 else 2)
    return img


class Writer:
    """Collects frames into one video (fixed size and rate), then re-encodes to H.264 so any player opens it."""

    def __init__(self, out: Path, size: tuple[int, int], fps: float):
        self.out, self.size, self.fps = out, size, fps
        self.tmp = out.with_suffix(".tmp.mp4")
        self.wr = cv2.VideoWriter(str(self.tmp), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)

    def write(self, img: np.ndarray, seconds: float = 0.0) -> None:
        """Write one frame, or hold it for `seconds`."""
        img = cv2.resize(img, self.size)
        for _ in range(max(1, int(round(seconds * self.fps)))):
            self.wr.write(img)

    def close(self) -> None:
        self.wr.release()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(self.tmp), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "23", str(self.out)], check=True)
        self.tmp.unlink()
