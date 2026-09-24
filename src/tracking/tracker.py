"""Multi-object tracking: give each detected object a stable ID across frames.

This module has one job: take video frames and return the same Detection
objects the detector produces, but with track_id filled in, so the rest of
the pipeline can follow one car over time and measure how it moves.

How the trackers work, every frame:
    1. Predict where each tracked object should be now, with a Kalman filter
       (its last position plus its estimated speed).
    2. Match those predictions to the new detections by box overlap.
    3. Give unmatched tracks a second chance against low-confidence
       detections, so a half-hidden car keeps its ID (ByteTrack's key idea).
    4. Start a new track for a confident detection that matched nothing.
    5. Keep an unmatched track alive for track_buffer frames before deleting
       it, so a briefly hidden object keeps its ID when it reappears.

Two trackers are available:
    bytetrack   exactly the steps above.
    botsort     the same, plus camera motion compensation: it estimates how
                the whole image shifted between frames (our camera moves) and
                corrects the predictions for it. Costs some CPU time.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import yaml
from ultralytics.utils import ROOT

from src.detection.detector import Detection, Detector

TRACKERS = ("bytetrack", "botsort")


class Tracker:
    """Tracks objects through a video, one frame at a time.

    Args:
        detector: the Detector whose model and settings are used. Detection
            and tracking always run the model identically.
        method: "bytetrack" or "botsort".
        **settings: overrides for the tracker's own settings, for example
            track_low_thresh=0.05. Anything not given keeps the Ultralytics
            default for that tracker.

    Create one Tracker per video: it remembers objects between calls, so
    feeding it frames from a different video would carry old IDs over.
    """

    def __init__(self, detector: Detector, method: str = "bytetrack", **settings) -> None:
        if method not in TRACKERS:
            raise ValueError(f"method must be one of {TRACKERS}, got {method!r}")
        self.detector = detector
        self.method = method

        # Start from the library's defaults for this tracker, apply our
        # overrides, and hand Ultralytics the result as a config file.
        defaults = yaml.safe_load((ROOT / "cfg" / "trackers" / f"{method}.yaml").read_text())
        unknown = set(settings) - set(defaults)
        if unknown:
            raise ValueError(f"unknown {method} settings: {sorted(unknown)}")
        self.settings = {**defaults, **settings}
        with tempfile.NamedTemporaryFile("w", suffix=f"_{method}.yaml", delete=False) as f:
            yaml.safe_dump(self.settings, f)
            self.config_path = Path(f.name)

        # Ultralytics keeps the tracker's memory on the model, which may be
        # shared with an earlier Tracker. The first frame therefore asks for a
        # fresh tracker, so IDs from a previous video never carry over.
        self._first_frame = True

    def update(self, frame: np.ndarray) -> list[Detection]:
        """Track objects in the next frame of the video.

        Returns only objects the tracker is currently following, each with
        its track_id set. A detection too weak to start or continue a track
        is left out.
        """
        results = self.detector.model.track(
            frame,
            # Keep the tracker's memory between calls, except on the first
            # frame, where a new tracker is built from our settings.
            persist=not self._first_frame,
            tracker=str(self.config_path),
            **self.detector.inference_args,
        )
        self._first_frame = False
        return self.detector.parse(results[0])
