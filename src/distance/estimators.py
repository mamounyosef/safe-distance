"""Distance estimators: turn a detected object into a distance in metres.

Every estimator has the same interface, so they are interchangeable and can be
benchmarked side by side:

    estimator.estimate(frame, detections, camera) -> list of distances

one entry per detection, in metres, or None where the method cannot give a
trustworthy answer for that object (for example, its bottom is cut off by the
image edge). Returning None instead of a guess is deliberate: a system that
says "unknown" is safe, one that reports a confident wrong number is not.

Distances are ground distances from the camera: straight-line distance along
the road, combining how far ahead and how far to the side the object is.
"""

from __future__ import annotations

import math

import numpy as np

from src.detection.detector import Detection
from src.distance.camera import Camera

# Pixels from the image border within which a box counts as cut off.
EDGE_MARGIN_PX = 2.0


def ground_distance(camera: Camera, u: float, forward_m: float) -> float:
    """Ground distance to a point at image column u that is forward_m ahead.

    The column tells how far to the side the point is: lateral offset =
    (u - cx) / fx * forward distance.
    """
    lateral_m = (u - camera.cx) / camera.fx * forward_m
    return math.hypot(lateral_m, forward_m)


class GroundPlaneEstimator:
    """Distance from where the object touches the road.

    The road is assumed flat and the camera's height and tilt are known. The
    ray from the camera through the contact pixel (a tyre, thanks to the
    segmentation mask) is followed until it hits the road; where it hits is
    where the object stands. The lower the contact point sits in the image,
    the steeper the ray, and the closer the object.

    Returns None when:
      - the box touches the bottom image edge: the real contact point is out
        of view, so the visible bottom would put the object too close;
      - the contact point is at or above the horizon: the ray never reaches
        the road;
      - the result is beyond max_distance_m, where tiny pixel errors become
        huge distance errors.
    """

    name = "ground_plane"

    def __init__(self, max_distance_m: float = 150.0) -> None:
        self.max_distance_m = max_distance_m

    def estimate_one(self, d: Detection, camera: Camera, image_height: int) -> float | None:
        if d.y2 >= image_height - EDGE_MARGIN_PX:
            return None
        u, v = d.contact_point

        # Direction of the ray through pixel (u, v), in camera coordinates:
        # x to the right, y down, z forward along the optical axis.
        ray_y = (v - camera.cy) / camera.fy
        ray_z = 1.0
        # Undo the camera's downward tilt, giving the ray in a level frame.
        c, s = math.cos(camera.pitch_rad), math.sin(camera.pitch_rad)
        level_down = ray_y * c + ray_z * s
        level_forward = -ray_y * s + ray_z * c
        if level_down <= 1e-6:
            return None  # at or above the horizon

        # Scale the ray until it has dropped by the camera height: the road.
        scale = camera.height_m / level_down
        forward_m = scale * level_forward
        distance = ground_distance(camera, u, forward_m)
        return distance if distance <= self.max_distance_m else None

    def estimate(self, frame: np.ndarray, detections: list[Detection], camera: Camera) -> list[float | None]:
        return [self.estimate_one(d, camera, frame.shape[0]) for d in detections]


# Typical real-world heights in metres, per detected class. General values,
# not fitted to any benchmark, so the benchmark stays an honest test.
TYPICAL_HEIGHTS_M = {
    "car": 1.5,
    "van": 2.0,
    "truck": 3.2,
    "bus": 3.0,
    "train": 3.8,
    "person": 1.7,
    "pedestrian": 1.7,
    "bicycle": 1.1,
    "motorcycle": 1.3,
    "dog": 0.6,
    "cat": 0.3,
}


class KnownSizeEstimator:
    """Distance from how tall the object looks.

    Things look smaller the further away they are, in exact proportion:
    forward distance = focal length * real height / height in pixels.
    Height is used rather than width because a car's height looks the same
    from any angle, while its width depends on which way it faces.

    Returns None when:
      - the class has no typical height (unknown objects, obstacles);
      - the box touches the top or bottom image edge: part of the object is
        cut off, so it looks shorter and therefore too far away.
    """

    name = "known_size"

    def __init__(self, heights_m: dict[str, float] | None = None) -> None:
        self.heights_m = TYPICAL_HEIGHTS_M if heights_m is None else heights_m

    def estimate_one(self, d: Detection, camera: Camera, image_height: int) -> float | None:
        real_height = self.heights_m.get(d.class_name)
        if real_height is None:
            return None
        if d.y1 <= EDGE_MARGIN_PX or d.y2 >= image_height - EDGE_MARGIN_PX:
            return None
        pixel_height = d.y2 - d.y1
        if pixel_height <= 1.0:
            return None
        forward_m = camera.fy * real_height / pixel_height
        return ground_distance(camera, (d.x1 + d.x2) / 2.0, forward_m)

    def estimate(self, frame: np.ndarray, detections: list[Detection], camera: Camera) -> list[float | None]:
        return [self.estimate_one(d, camera, frame.shape[0]) for d in detections]


class FallbackEstimator:
    """Ask estimators in order; use the first one that gives an answer.

    Default: known size first (the more accurate one on KITTI: 77% of in-path
    objects within 10%, against 46% for ground plane), then ground plane for
    whatever known size cannot measure, such as obstacles with no typical
    height.
    """

    name = "combined"

    def __init__(self, estimators: list | None = None) -> None:
        self.estimators = estimators or [KnownSizeEstimator(), GroundPlaneEstimator()]

    def estimate(self, frame: np.ndarray, detections: list[Detection], camera: Camera) -> list[float | None]:
        answers = [e.estimate(frame, detections, camera) for e in self.estimators]
        return [next((a[i] for a in answers if a[i] is not None), None) for i in range(len(detections))]
