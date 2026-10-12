"""Decode the frames BADAS sees from a video (shared by the data jobs on Modal)."""

from __future__ import annotations


def decode_frames(path: str):
    """The frames BADAS sees, in ONE pass: frame round(i x fps / 8) for i = 0, 1, 2 ...,
    resized to 224x224, BGR turned into RGB. Identical to badas_modal.decode_frames.
    Returns (frames as uint8 array n x 224 x 224 x 3, video fps)."""
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(path)
    fps, total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    wanted = [w for w in (int(round(i * fps / 8.0)) for i in range(int(round(total / fps * 8.0)))) if w < total]
    frames, k, j = [], 0, 0
    while j < len(wanted):
        ok, img = cap.read()
        if not ok:
            break
        while j < len(wanted) and wanted[j] == k:     # this video frame is one BADAS uses
            frames.append(cv2.cvtColor(cv2.resize(img, (224, 224)), cv2.COLOR_BGR2RGB))
            j += 1
        k += 1
    cap.release()
    return (np.stack(frames) if frames else np.zeros((0, 224, 224, 3), np.uint8)), fps
