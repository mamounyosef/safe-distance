"""YOLO object detection for the forward-collision pipeline.

This module has one job: turn a video frame into a list of road objects with
pixel bounding boxes. It knows nothing about tracking, distance or collisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from ultralytics import YOLO, YOLOE
from ultralytics.utils import SETTINGS

# Ultralytics looks for helper downloads (such as YOLOE's text encoder) in its
# configured weights directory, so point that at our own weights/ folder.
WEIGHTS_DIR = Path(__file__).resolve().parents[2] / "weights"
if SETTINGS.get("weights_dir") != str(WEIGHTS_DIR):
    SETTINGS["weights_dir"] = str(WEIGHTS_DIR)

# Words handed to YOLOE when open-vocabulary mode is used. Unlike the fixed
# COCO list below, these can be anything: the model matches image regions
# against the text itself, so adding a hazard costs nothing but a word.
#
# Wording matters: these were picked by testing alternatives on real frames
# and on the Lost and Found benchmark (src/detection/benchmarks/lost_and_found).
# "construction barrier" beat "road barrier" and "roadblock" on the orange
# water-filled barriers found at roadworks. Specific nouns generally beat
# generic ones, though bare "obstacle" still earns its place.
ROAD_PROMPTS: list[str] = [
    "car",
    "van",
    "truck",
    "bus",
    "motorcycle",
    "bicycle",
    "person",
    # Tested and rejected (prompts v3): adding "pedestrian" and "cyclist"
    # moved KITTI pedestrian AP only 51.0% -> 52.5% and dropped cyclist AP
    # 24.5% -> 15.9%. The gap to YOLO26 on people is the model, not the words.
    "traffic cone",
    "construction barrier",
    "traffic barricade",
    "animal",
    # Specific nouns beat generic ones: with only "animal", YOLOE found 30 to
    # 36% of dogs on Lost and Found while YOLO26 (exact COCO "dog") found 49
    # to 55%, so the specific words are listed too.
    "dog",
    "cat",
    "ball",
    # Generic hazard words that tested clean (small boxes, never the road):
    "obstacle",
    "box",
    "bucket",
]
# Tested and rejected on real crash footage:
#   "debris", "rock", "metal scrap", "bumper", "car door", "obstacle"
#       never fired at all, at any resolution.
#   "object on road" matched the ROAD SURFACE, producing boxes covering 45%
#       of the frame. Generic phrases containing a scene word are dangerous:
#       the model happily matches the scene rather than the object. Note that
#       bare "obstacle" is fine and is kept above; it is the words "on road"
#       that drag the match onto the road surface itself.
#   "car wreck", "wreckage", "tire" fired weakly (0.08 to 0.13) and
#       inconsistently, not enough to rely on.
#   "road barrier" lost to "construction barrier".
# Lesson: judge a prompt by the box it draws, not by its confidence score.
# Conclusion: no prompt reliably detects scattered crash debris. The gap is
# semantic, not a lack of pixels, so raising resolution does not help either.
# Closing it needs a class-agnostic obstacle check (is something solid
# sticking up off the road surface?), not a better word.

# COCO (Common Objects in Context) class ids we care about by name, because
# the rest of the pipeline treats them differently: a pedestrian gets a wider
# safety margin than a parked car, and known real-world widths differ per class.
NAMED_CLASSES: dict[int, str] = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    6: "train",
    7: "truck",
    15: "cat",
    16: "dog",
}

# Anything else COCO recognises is still something we must not hit, so it is
# kept under one catch-all label instead of being discarded. This does not
# solve the open-set problem (an object COCO knows nothing about is still
# invisible), it only stops us throwing away detections we already have.
OTHER_CLASS = "other"


@dataclass(frozen=True)
class Detection:
    """One detected object in one frame.

    Coordinates are pixels in the source frame, with the origin at the
    top-left corner, so y grows downwards.
    """

    x1: float
    y1: float
    x2: float
    y2: float
    class_id: int
    class_name: str
    confidence: float
    track_id: int | None = None

    # Outline of the object as an (N, 2) array of x,y pixel points, but only
    # when a segmentation model was used. None for a plain detection model.
    mask: np.ndarray | None = field(default=None, compare=False, repr=False)

    @property
    def width(self) -> float:
        """Box width in pixels. Used by the known-size distance estimator."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def bottom_center(self) -> tuple[float, float]:
        """Middle of the box's bottom edge."""
        return ((self.x1 + self.x2) / 2.0, self.y2)

    @property
    def contact_point(self) -> tuple[float, float]:
        """Where the object actually meets the road.

        This is what the ground-plane distance estimator measures against.
        With a segmentation mask it is the lowest point of the object's real
        outline, which is a tyre. Without one it falls back to the middle of
        the box's bottom edge, which sits on empty road for an angled vehicle.
        """
        if self.mask is None or len(self.mask) == 0:
            return self.bottom_center

        ys = self.mask[:, 1]
        lowest = float(ys.max())
        # Several outline points can share the lowest row, so take their middle.
        xs = self.mask[ys >= lowest - 1.0, 0]
        return (float(np.median(xs)), lowest)


class Detector:
    """Thin wrapper over an Ultralytics YOLO model.

    Args:
        weights: model checkpoint name or path. Downloaded on first use.
        device: "cuda" for the GPU, "cpu" to force the processor.
        conf: minimum confidence for a detection to be reported.
        imgsz: size the longest side of the frame is scaled to before
            inference. The aspect ratio is kept and the short side is padded
            with grey bars (letterboxing), so a 1920x1080 frame at 640 becomes
            about 640x384. Larger sees small distant objects better but costs
            roughly the square of the size in time.
        half: run inference in FP16 (16-bit floating point). Faster on a GPU
            with negligible accuracy loss. Ignored on CPU.
        max_det: maximum detections reported per frame.
        classes: mapping of class id to name for the classes we label by name.
            Every other class the model reports is kept as OTHER_CLASS.
            Ignored in open-vocabulary mode, where the prompts are the names.
        prompts: word list for open-vocabulary mode. Only used when the
            weights are a YOLOE model, which is detected from the filename.

    Open-vocabulary mode: a normal YOLO model has a fixed list of 80 class
    slots baked into its final layer, so an object with no slot (a traffic
    cone, debris) can never be reported. A YOLOE model instead compares image
    regions against text you supply at runtime, so the vocabulary is whatever
    words you pass in. It costs accuracy on the common classes and some speed.
    """

    def __init__(
        self,
        weights: str = "weights/yolo26s-seg.pt",
        device: str = "cuda",
        conf: float = 0.25,
        imgsz: int = 640,
        half: bool = True,
        max_det: int = 300,
        classes: dict[int, str] | None = None,
        prompts: list[str] | None = None,
    ) -> None:
        self.open_vocab = "yoloe" in Path(weights).name.lower()
        if self.open_vocab:
            self.model = YOLOE(weights)
            self.prompts = ROAD_PROMPTS if prompts is None else prompts
            # Encoding the words is a one-off cost of tens of seconds, paid
            # here at startup rather than per frame.
            self.model.set_classes(self.prompts)
        else:
            self.model = YOLO(weights)
            self.prompts = None
        self.device = device
        self.conf = conf
        self.imgsz = imgsz
        # FP16 only exists on the GPU, so silently fall back on CPU.
        self.half = half and device != "cpu"
        self.max_det = max_det
        self.classes = NAMED_CLASSES if classes is None else classes

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Detect road objects in a single frame.

        Args:
            frame: an image as a numpy array in BGR order, which is what
                OpenCV gives you when it reads a video.

        Returns:
            One Detection per object found, with track_id left as None.
        """
        results = self.model.predict(frame, **self.inference_args)
        return self.parse(results[0])

    @property
    def inference_args(self) -> dict:
        """Settings passed to every model call, shared with the tracker so
        detection and tracking always run the model identically."""
        return {
            "device": self.device,
            "conf": self.conf,
            "imgsz": self.imgsz,
            # Ultralytics replaced the old `half` flag with `quantize`:
            # 16 means FP16, 32 means full FP32 precision.
            "quantize": 16 if self.half else 32,
            "max_det": self.max_det,
            "verbose": False,
        }

    def _name_for(self, class_id: int, result) -> str:
        """Label for a class id.

        In open-vocabulary mode the model's own names are the prompts we gave
        it, so they are used directly. Otherwise we keep our short named list
        and fold everything else into OTHER_CLASS.
        """
        if self.open_vocab:
            return result.names[class_id]
        return self.classes.get(class_id, OTHER_CLASS)

    def parse(self, result) -> list[Detection]:
        """Convert one Ultralytics Results object into our own Detection list.

        Public because the tracker also produces Results objects, from the
        same model, and turns them into Detections the same way.
        """
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return []

        xyxy = boxes.xyxy.cpu().numpy()
        class_ids = boxes.cls.cpu().numpy().astype(int)
        confs = boxes.conf.cpu().numpy()
        # track_id is only present when the model was run in tracking mode.
        track_ids = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else None
        # masks.xy is a list of outlines already scaled to the original frame.
        # It is None unless the weights are a segmentation model (*-seg.pt).
        masks = result.masks.xy if result.masks is not None else None

        detections = []
        for i, (x1, y1, x2, y2) in enumerate(xyxy):
            class_id = int(class_ids[i])
            detections.append(
                Detection(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                    class_id=class_id,
                    class_name=self._name_for(class_id, result),
                    confidence=float(confs[i]),
                    track_id=int(track_ids[i]) if track_ids is not None else None,
                    mask=masks[i] if masks is not None else None,
                )
            )
        return detections
