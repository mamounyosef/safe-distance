"""The camera model: what the distance estimators need to know about the camera.

A camera flattens the 3D world onto a 2D image. The pinhole model describes
that flattening with a few numbers:

    fx, fy   focal length in pixels (horizontal, vertical): how "zoomed in"
             the camera is. Larger means distant things look bigger.
    cx, cy   the principal point: the pixel the camera's optical axis passes
             through, usually close to the image centre.

The ground-plane estimator also needs how the camera is mounted:

    height_m   camera height above the road, in metres.
    pitch_rad  how far the camera is tilted down from horizontal, in radians
               (positive = looking slightly down at the road).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Camera:
    fx: float
    fy: float
    cx: float
    cy: float
    height_m: float
    pitch_rad: float = 0.0

    @classmethod
    def from_kitti_calib(cls, path: Path, height_m: float = 1.65, pitch_rad: float = 0.0) -> "Camera":
        """Read a KITTI calibration file (object or tracking dataset).

        Uses P2, the left colour camera the images come from. KITTI's camera
        is mounted 1.65 m above the road and level (published in the dataset
        paper); the calibration file itself does not record the mounting.
        """
        for line in Path(path).read_text().splitlines():
            key, _, values = line.partition(":")
            if key.strip() == "P2" or key.startswith("P2 "):
                p = [float(v) for v in values.split()]
                # P2 is a 3x4 projection matrix, row by row:
                # [fx 0 cx tx; 0 fy cy ty; 0 0 1 tz]
                return cls(fx=p[0], fy=p[5], cx=p[2], cy=p[6], height_m=height_m, pitch_rad=pitch_rad)
        raise ValueError(f"no P2 line in {path}")

    @classmethod
    def from_lost_and_found(cls, path: Path) -> "Camera":
        """Read a Lost and Found per-frame camera file, which records everything."""
        cam = json.loads(Path(path).read_text())
        i, e = cam["intrinsic"], cam["extrinsic"]
        return cls(fx=i["fx"], fy=i["fy"], cx=i["u0"], cy=i["v0"], height_m=e["z"], pitch_rad=e["pitch"])
