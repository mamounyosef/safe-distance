"""Drawing detections onto frames, shared by the detection and tracking videos."""

from __future__ import annotations

import cv2
import numpy as np

from src.detection.detector import OTHER_CLASS, Detection

# Colours are BGR (Blue, Green, Red), which is the order OpenCV uses.
COLOURS: dict[str, tuple[int, int, int]] = {
    "person": (0, 200, 255),
    "pedestrian": (0, 200, 255),
    "cyclist": (0, 200, 255),
    "bicycle": (0, 200, 255),
    "motorcycle": (0, 200, 255),
    "car": (0, 255, 0),
    "van": (0, 255, 0),
    "bus": (0, 255, 0),
    "truck": (0, 255, 0),
    "train": (0, 255, 0),
    "cat": (255, 200, 0),
    "dog": (255, 200, 0),
    "animal": (255, 200, 0),
    # Open-vocabulary hazards, drawn in magenta so they stand out.
    # These names must match ROAD_PROMPTS in src/detection/detector.py.
    "traffic cone": (255, 0, 255),
    "construction barrier": (255, 0, 255),
    "traffic barricade": (255, 0, 255),
    "obstacle": (255, 0, 255),
    "box": (255, 0, 255),
    "bucket": (255, 0, 255),
    "ball": (255, 0, 255),
    OTHER_CLASS: (160, 160, 160),
}


def colour_of(d: Detection) -> tuple[int, int, int]:
    return COLOURS.get(d.class_name, COLOURS[OTHER_CLASS])


def draw(frame: np.ndarray, detections: list[Detection], mask_alpha: float = 0.4) -> np.ndarray:
    """Draw one box, label and (if present) mask per detection.

    The label shows the track ID when the detection came from the tracker.
    """
    out = frame.copy()

    # Masks are filled on a separate layer and blended once, so overlapping
    # objects do not stack into an opaque blob.
    if any(d.mask is not None for d in detections):
        layer = out.copy()
        for d in detections:
            if d.mask is not None and len(d.mask) >= 3:
                cv2.fillPoly(layer, [d.mask.astype(np.int32)], colour_of(d))
        cv2.addWeighted(layer, mask_alpha, out, 1 - mask_alpha, 0, out)

    for d in detections:
        colour = colour_of(d)
        p1 = (int(d.x1), int(d.y1))
        p2 = (int(d.x2), int(d.y2))
        cv2.rectangle(out, p1, p2, colour, 2)

        prefix = f"#{d.track_id} " if d.track_id is not None else ""
        label = f"{prefix}{d.class_name} {d.confidence:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(out, (p1[0], p1[1] - th - 6), (p1[0] + tw + 4, p1[1]), colour, -1)
        cv2.putText(
            out, label, (p1[0] + 2, p1[1] - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA,
        )

        # The road contact point the ground-plane distance estimator will use.
        # Filled white ring = taken from the mask, so it sits on a tyre.
        # Hollow ring = box fallback, which sits on empty road if the car is angled.
        cx, cy = d.contact_point
        cv2.circle(out, (int(cx), int(cy)), 5, (255, 255, 255), -1 if d.mask is not None else 2)
        cv2.circle(out, (int(cx), int(cy)), 3, colour, -1)
    return out
