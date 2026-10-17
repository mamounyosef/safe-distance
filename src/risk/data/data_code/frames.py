"""Decode the frames BADAS sees from a video (shared by the data jobs on Modal)."""

from __future__ import annotations


def decode_frames(path: str, wide: bool = False):
    """The frames BADAS sees, in ONE pass: frame round(i x fps / 8) for i = 0, 1, 2 ..., BGR turned into RGB.
    wide=False: squashed to 224 x 224 (BADAS's released inference code; identical to badas_modal.decode_frames).
    wide=True:  256 x 448 with the frame's shape kept (wide_input.wide_frame: no squash, ~3 px off each side).
    Returns (frames as uint8 array n x H x W x 3, video fps)."""
    import cv2
    import numpy as np
    if wide:
        from wide_input import wide_frame

    cap = cv2.VideoCapture(path)
    fps, total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    wanted = [w for w in (int(round(i * fps / 8.0)) for i in range(int(round(total / fps * 8.0)))) if w < total]
    frames, k, j = [], 0, 0
    while j < len(wanted):
        ok, img = cap.read()
        if not ok:
            break
        while j < len(wanted) and wanted[j] == k:     # this video frame is one BADAS uses
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frames.append(wide_frame(rgb) if wide else cv2.resize(rgb, (224, 224)))
            j += 1
        k += 1
    cap.release()
    return (np.stack(frames) if frames else np.zeros((0, 1, 1, 3), np.uint8)), fps
