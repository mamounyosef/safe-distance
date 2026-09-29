"""Depth models as distance estimators.

A monocular depth model predicts a distance in metres for EVERY pixel of an
image. To turn that into one distance per object, the depth values inside the
object's segmentation mask are summarised by a statistic:

    median   the typical depth of the object's pixels.
    p10      the 10th percentile: the nearer part of the object. Closer to
             the nearest-surface distance that matters for braking.
    p25      in between.

Each model family has a backend with the same interface:

    backend.predict(frame_bgr, camera) -> depth map, float32 metres, same size as frame

Backends load lazily (on first use) and are shared: several
DepthModelEstimator objects with different statistics reuse ONE depth map per
frame, so comparing statistics costs no extra inference.

Models whose output needs the camera's focal length to be in metres get it
from the Camera object; the rest estimate scale on their own.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F

from src.detection.detector import Detection
from src.distance.camera import Camera

REPO = Path(__file__).resolve().parents[2]

# Where the (large, several GB) depth models are downloaded to. Kept outside
# the repo, on C:, because D: ran out of space. Set SAFE_DISTANCE_MODELS to
# use another folder.
MODELS_DIR = Path(os.environ.get("SAFE_DISTANCE_MODELS", r"C:\safe-distance-models"))
HF_CACHE = MODELS_DIR / "hf"
# Every library downloads into MODELS_DIR: Hugging Face models (Depth
# Anything, Depth Pro, UniDepth) via HF_HOME, and Metric3D via torch.hub.
os.environ.setdefault("HF_HOME", str(HF_CACHE))
os.environ.setdefault("HF_HUB_CACHE", str(HF_CACHE))
os.environ.setdefault("TORCH_HOME", str(MODELS_DIR / "torch"))


def _resize_depth(depth: torch.Tensor, height: int, width: int) -> np.ndarray:
    """Resize a (h, w) or (1, 1, h, w) depth tensor to the frame size."""
    d = depth.float().reshape(1, 1, *depth.shape[-2:])
    d = F.interpolate(d, size=(height, width), mode="bilinear", align_corners=False)
    return d[0, 0].cpu().numpy().astype(np.float32)


class DepthBackend:
    """Base class: lazy loading, per-frame caching and timing."""

    name = "base"
    uses_focal_length = False
    # The numeric precision inference actually runs in, for the reports.
    precision = "fp32"

    def __init__(self) -> None:
        self._model = None
        self._cache_key = None
        self._cache_value = None
        self.times_ms: list[float] = []

    def load(self) -> None:
        raise NotImplementedError

    def _predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        raise NotImplementedError

    def predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        key = (id(frame), frame.shape, camera)
        if key == self._cache_key:
            return self._cache_value
        if self._model is None:
            self.load()
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        with torch.inference_mode():
            depth = self._predict(frame, camera)
        torch.cuda.synchronize()
        self.times_ms.append((time.perf_counter() - t0) * 1000.0)
        self._cache_key, self._cache_value = key, depth
        return depth


class HuggingFaceBackend(DepthBackend):
    """Depth Anything V2 Metric and Depth Pro, through Hugging Face transformers.

    Depth Pro is given our focal length, which it would otherwise estimate.
    """

    def __init__(self, name: str, model_id: str, pass_focal_length: bool = False) -> None:
        super().__init__()
        self.name = name
        self.model_id = model_id
        self.uses_focal_length = pass_focal_length
        self.precision = "fp16"

    def load(self) -> None:
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation

        self.processor = AutoImageProcessor.from_pretrained(self.model_id, cache_dir=str(HF_CACHE))
        self._model = AutoModelForDepthEstimation.from_pretrained(
            self.model_id, cache_dir=str(HF_CACHE), dtype=torch.float16
        ).cuda().eval()

    def _predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        inputs = self.processor(images=rgb, return_tensors="pt").to("cuda")
        inputs = {k: (v.half() if v.is_floating_point() else v) for k, v in inputs.items()}
        outputs = self._model(**inputs)
        if self.uses_focal_length:
            # Depth Pro outputs canonical inverse depth; its own post-processing
            # converts it with a focal length it ESTIMATES from the image:
            # depth = 1 / (output * width / focal). We know the real focal
            # length, so the same formula is applied with ours instead.
            inv = outputs.predicted_depth[0].float() * w / camera.fx
            inv = F.interpolate(inv[None, None], size=(h, w), mode="bilinear", align_corners=False)[0, 0]
            return (1.0 / torch.clamp(inv, min=1e-4, max=1e4)).cpu().numpy().astype(np.float32)
        post = self.processor.post_process_depth_estimation(outputs, target_sizes=[(h, w)])[0]
        return post["predicted_depth"].float().cpu().numpy().astype(np.float32)


class Metric3DBackend(DepthBackend):
    """Metric3D v2 through torch.hub, following the authors' published example.

    It predicts depth for a "canonical" camera with a 1000-pixel focal length;
    rescaling by our real focal length turns that into metres.
    """

    uses_focal_length = True
    INPUT_SIZE = (616, 1064)  # the authors' input size for the ViT models
    MEAN = torch.tensor([123.675, 116.28, 103.53]).view(3, 1, 1)
    STD = torch.tensor([58.395, 57.12, 57.375]).view(3, 1, 1)

    def __init__(self, name: str, hub_name: str, fp16: bool = False) -> None:
        super().__init__()
        self.name = name
        self.hub_name = hub_name
        # The library runs in full FP32 precision; fp16=True wraps inference
        # in automatic mixed precision (FP16), like UniDepth does internally.
        self.fp16 = fp16
        self.precision = "fp16 (autocast)" if fp16 else "fp32"

    def load(self) -> None:
        self._model = torch.hub.load("yvanyin/metric3d", self.hub_name, pretrain=True, trust_repo=True)
        self._model = self._model.cuda().eval()

    def _predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        scale = min(self.INPUT_SIZE[0] / h, self.INPUT_SIZE[1] / w)
        rgb = cv2.resize(rgb, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)
        focal = camera.fx * scale
        # Pad to the input size with the mean colour, remembering the padding.
        ph, pw = self.INPUT_SIZE[0] - rgb.shape[0], self.INPUT_SIZE[1] - rgb.shape[1]
        pad = (ph // 2, ph - ph // 2, pw // 2, pw - pw // 2)
        rgb = cv2.copyMakeBorder(rgb, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_CONSTANT,
                                 value=[123.675, 116.28, 103.53])
        x = (torch.from_numpy(rgb.transpose(2, 0, 1)).float() - self.MEAN) / self.STD
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=self.fp16):
            pred, _, _ = self._model.inference({"input": x[None].cuda()})
        pred = pred[0, 0].float()
        pred = pred[pad[0]: pred.shape[0] - pad[1], pad[2]: pred.shape[1] - pad[3]]
        depth = _resize_depth(pred, h, w)
        return depth * (focal / 1000.0)  # canonical camera -> our camera


class UniDepthBackend(DepthBackend):
    """UniDepth v2, given our camera's intrinsic matrix."""

    uses_focal_length = True
    precision = "fp16 (library autocast)"

    def __init__(self, name: str, model_id: str) -> None:
        super().__init__()
        self.name = name
        self.model_id = model_id

    def load(self) -> None:
        from unidepth.models import UniDepthV2

        self._model = UniDepthV2.from_pretrained(self.model_id).cuda().eval()

    def _predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        h, w = frame.shape[:2]
        rgb = torch.from_numpy(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).transpose(2, 0, 1)).cuda()
        K = torch.tensor([[camera.fx, 0, camera.cx], [0, camera.fy, camera.cy], [0, 0, 1]],
                         dtype=torch.float32).cuda()
        pred = self._model.infer(rgb, K)["depth"]
        return _resize_depth(pred, h, w)


class DepthAnything3MetricBackend(DepthBackend):
    """Depth Anything 3 Metric Large.

    Per the authors: metres = focal length in pixels * network output / 300,
    with the focal length at the resolution the network actually processed.
    """

    uses_focal_length = True
    precision = "bf16 or fp16 (library autocast)"

    def __init__(self, name: str = "da3-metric-large", model_id: str = "depth-anything/DA3METRIC-LARGE") -> None:
        super().__init__()
        self.name = name
        self.model_id = model_id

    def load(self) -> None:
        from depth_anything_3.api import DepthAnything3

        self._model = DepthAnything3.from_pretrained(self.model_id, cache_dir=str(HF_CACHE)).cuda().eval()

    def _predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pred = self._model.inference([rgb])
        raw = torch.as_tensor(np.asarray(pred.depth[0]))
        # The network ran at a smaller size; scale our focal length to it.
        focal = 0.5 * (camera.fx + camera.fy) * raw.shape[-1] / w
        return _resize_depth(raw, h, w) * (focal / 300.0)


class YoloDepthBackend(DepthBackend):
    """YOLO26-depth through Ultralytics, used as shipped (no calibration)."""

    precision = "fp16"

    def __init__(self, name: str = "yolo26s-depth", weights: str = "weights/yolo26s-depth.pt",
                 imgsz: int = 768) -> None:
        super().__init__()
        self.name = name
        self.weights = weights
        self.imgsz = imgsz

    def load(self) -> None:
        from ultralytics import YOLO

        self._model = YOLO(str(REPO / self.weights))

    def _predict(self, frame: np.ndarray, camera: Camera) -> np.ndarray:
        r = self._model.predict(frame, imgsz=self.imgsz, half=True, verbose=False)[0]
        return r.depth.data.float().cpu().numpy().astype(np.float32)


# Every candidate, by name. Built lazily: nothing downloads until used.
BACKENDS = {
    "da2-metric-small": lambda: HuggingFaceBackend("da2-metric-small", "depth-anything/Depth-Anything-V2-Metric-Outdoor-Small-hf"),
    "da2-metric-base": lambda: HuggingFaceBackend("da2-metric-base", "depth-anything/Depth-Anything-V2-Metric-Outdoor-Base-hf"),
    "da2-metric-large": lambda: HuggingFaceBackend("da2-metric-large", "depth-anything/Depth-Anything-V2-Metric-Outdoor-Large-hf"),
    "depth-pro": lambda: HuggingFaceBackend("depth-pro", "apple/DepthPro-hf", pass_focal_length=True),
    "metric3d-v2-small": lambda: Metric3DBackend("metric3d-v2-small", "metric3d_vit_small"),
    "metric3d-v2-large": lambda: Metric3DBackend("metric3d-v2-large", "metric3d_vit_large"),
    "metric3d-v2-small-fp16": lambda: Metric3DBackend("metric3d-v2-small-fp16", "metric3d_vit_small", fp16=True),
    "metric3d-v2-large-fp16": lambda: Metric3DBackend("metric3d-v2-large-fp16", "metric3d_vit_large", fp16=True),
    "unidepth-v2-small": lambda: UniDepthBackend("unidepth-v2-small", "lpiccinelli/unidepth-v2-vits14"),
    "unidepth-v2-base": lambda: UniDepthBackend("unidepth-v2-base", "lpiccinelli/unidepth-v2-vitb14"),
    "unidepth-v2-large": lambda: UniDepthBackend("unidepth-v2-large", "lpiccinelli/unidepth-v2-vitl14"),
    "da3-metric-large": lambda: DepthAnything3MetricBackend(),
    "yolo26s-depth": lambda: YoloDepthBackend(),
}

STATISTICS = {
    "median": lambda v: float(np.median(v)),
    "p10": lambda v: float(np.percentile(v, 10)),
    "p25": lambda v: float(np.percentile(v, 25)),
}


class DepthModelEstimator:
    """Distance of each detection from a depth model, read inside its mask.

    Returns None when the detection has no usable mask pixels with a valid
    depth, rather than guessing.
    """

    def __init__(self, backend: DepthBackend, statistic: str = "median") -> None:
        self.backend = backend
        self.statistic = statistic
        self.name = f"{backend.name}_{statistic}"

    def estimate(self, frame: np.ndarray, detections: list[Detection], camera: Camera) -> list[float | None]:
        if not detections:
            return []
        depth = self.backend.predict(frame, camera)
        stat = STATISTICS[self.statistic]
        out = []
        for d in detections:
            region = np.zeros(frame.shape[:2], dtype=np.uint8)
            if d.mask is not None and len(d.mask) >= 3:
                cv2.fillPoly(region, [d.mask.astype(np.int32)], 1)
            else:
                cv2.rectangle(region, (int(d.x1), int(d.y1)), (int(d.x2), int(d.y2)), 1, -1)
            values = depth[region.astype(bool)]
            values = values[np.isfinite(values) & (values > 0)]
            out.append(stat(values) if values.size else None)
        return out


def depth_estimators(backend_name: str) -> list[DepthModelEstimator]:
    """One estimator per statistic, all sharing one backend (one inference per frame)."""
    backend = BACKENDS[backend_name]()
    return [DepthModelEstimator(backend, s) for s in STATISTICS]
