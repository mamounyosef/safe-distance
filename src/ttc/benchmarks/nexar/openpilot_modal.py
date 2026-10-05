"""openpilot's driving model (comma.ai) on Nexar's TEST set, on Modal (CPU only).

openpilot's model (driving_supercombo.onnx, 30M parameters, from the openpilot
repo, MIT licence) runs at 20 steps per second on two views of the road (a
normal one about 31 degrees wide and a wide one about 58 degrees), and keeps
its own memory of the last few seconds. Among its outputs:
    meta        probabilities that the driver will brake harder than 3 / 4 / 5 m/s^2
                within the next 2, 4, 6, 8, 10 s (openpilot's collision warning uses these)
    lead        the car ahead: distance x (m), sideways y, speed v, acceleration a
    lead_prob   probability there is a car ahead
    plan        the path and speed it would drive (incl. planned acceleration)

How each clip is fed (as openpilot's modeld.py does, without a comma device):
    - frames taken at 20 per second (the nearest video frame to each 0.05 s step)
    - each frame warped into the model's two views with a homography
      camera_from_model = K_camera @ inv(K_model), which is openpilot's
      get_warp_matrix when the camera is assumed straight and level
      (calibration angles 0). Our dashcam lens is unknown: K_camera uses the
      same guessed 110 degree field of view as the rest of the project.
    - each view converted to YUV 4:2:0 and packed into openpilot's 6 channels
      (4 sub-sampled Y planes, U, V)
    - desire = none (no lane change), traffic = right-hand driving, action_t
      = openpilot's default delays
openpilot's warning rule (fill_model_msg.py): the 2 s hard-brake probability
over 5 m/s^2 above [0.05, 0.05, 0.15, 0.15, 0.15] for the last 5 steps AND
over 3 m/s^2 above [0.7, 0.7] for the last 2 steps.

RUN IT (PowerShell, from the repo root; Modal account ahmad-yonis):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run src\\ttc\\benchmarks\\nexar\\openpilot_modal.py --limit 4    # test on 4 clips
    .venv\\Scripts\\modal.exe run src\\ttc\\benchmarks\\nexar\\openpilot_modal.py              # all 1,344

Writes results/test1/openpilot_series.json: per clip, per step [t, fcw (0/1),
P(brake > 3 m/s^2 in 2 s), P(> 4), P(> 5), lead prob, lead distance m, lead speed m/s,
lead acceleration m/s^2, planned acceleration m/s^2].
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import modal

# ---- CONFIG ----
VOLUME = "safe-distance-data"
MAX_CONTAINERS = 4
CPUS = 8                          # per container (the model is small: no GPU needed)
MODEL_URL = ("https://media.githubusercontent.com/media/commaai/openpilot/master/"
             "openpilot/selfdrive/modeld/models/driving_supercombo.onnx")
MODEL_PATH = "/data/models/openpilot/driving_supercombo.onnx"
HFOV_DEG = 110.0                  # assumed dashcam field of view (same guess as our pipeline)
STEP_S = 0.05                     # openpilot runs at 20 steps per second
ACTION_T = (0.275, 0.275)         # [lateral, longitudinal] delays (s): openpilot's default-ish values
OUT = Path(__file__).resolve().parent / "results" / "test1" / "openpilot_series.json"
# ----------------

# openpilot's virtual cameras (common/transformations/model.py)
MED_FL, MED_SIZE, MED_CY = 910.0, (512, 256), 47.6         # normal view
SBIG_FL = 455.0                                             # wide view, same image size
# Where each part of the single output vector sits (from the model's own metadata)
META, LEAD, LEAD_PROB, PLAN = slice(0, 55), slice(917, 1061), slice(1061, 1064), slice(1576, 2566)
HARD_BRAKE_3, HARD_BRAKE_4, HARD_BRAKE_5 = slice(4, 31, 6), slice(5, 31, 6), slice(6, 31, 6)   # inside meta
FCW_5, FCW_3 = (0.05, 0.05, 0.15, 0.15, 0.15), (0.7, 0.7)

app = modal.App("safe-distance-openpilot")
volume = modal.Volume.from_name(VOLUME)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install("onnxruntime==1.23.2", "opencv-python-headless", "numpy")
)


@app.cls(image=image, cpu=CPUS, volumes={"/data": volume}, timeout=3600, max_containers=MAX_CONTAINERS)
class Openpilot:
    @modal.enter()
    def load(self) -> None:
        """Load the model once per container (downloaded into the Volume the first time)."""
        import os
        import urllib.request

        import onnxruntime as ort

        if not os.path.exists(MODEL_PATH):
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH + ".part")
            os.replace(MODEL_PATH + ".part", MODEL_PATH)
            volume.commit()
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = CPUS
        self.sess = ort.InferenceSession(MODEL_PATH, opts, providers=["CPUExecutionProvider"])

    @modal.method()
    def run(self, sub: str, clip: str) -> tuple[str, list]:
        """Run openpilot's model through one clip at 20 steps per second."""
        import cv2
        import numpy as np

        def k(fl, w, h, cy):
            return np.array([[fl, 0, w / 2], [0, fl, cy], [0, 0, 1]], dtype=np.float64)

        cap = cv2.VideoCapture(f"/data/nexar/{sub}/{clip}.mp4")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w, h = int(cap.get(3)), int(cap.get(4))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fx = (w / 2) / math.tan(math.radians(HFOV_DEG) / 2)
        cam = k(fx, w, h, h / 2)
        # Model pixel -> camera pixel, for the normal and the wide view.
        warps = [cam @ np.linalg.inv(k(MED_FL, *MED_SIZE, MED_CY)),
                 cam @ np.linalg.inv(k(SBIG_FL, *MED_SIZE, 0.5 * (256 + MED_CY)))]

        def pack(bgr):
            """One frame -> openpilot's input for both views: uint8 (2, 6, 128, 256)."""
            out = np.empty((2, 6, 128, 256), np.uint8)
            for i, m in enumerate(warps):
                view = cv2.warpPerspective(bgr, m, MED_SIZE, flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
                yuv = cv2.cvtColor(view, cv2.COLOR_BGR2YUV_I420)        # (384, 512): Y, then U, then V
                y = yuv[:256]
                # openpilot's order: (even rows, even cols), (odd, even), (even, odd), (odd, odd)
                out[i, 0], out[i, 1] = y[0::2, 0::2], y[1::2, 0::2]
                out[i, 2], out[i, 3] = y[0::2, 1::2], y[1::2, 1::2]
                out[i, 4] = yuv[256:320].reshape(128, 256)
                out[i, 5] = yuv[320:384].reshape(128, 256)
            return out

        # The model's memory starts empty and is fed back each step.
        state = {"state_img_q": np.zeros((2, 5, 6, 128, 256), np.uint8),
                 "state_desire_q": np.zeros((100, 1, 8), np.float32),
                 "state_feat_q": np.zeros((96, 1, 512), np.float32)}
        fixed = {"desire": np.zeros(8, np.float32),
                 "traffic_convention": np.array([[1, 0]], np.float32),     # right-hand driving (US)
                 "action_t": np.array([ACTION_T], np.float32)}
        prev5, prev3 = np.zeros(5, np.float32), np.zeros(2, np.float32)
        sig = lambda x: 1 / (1 + np.exp(-np.clip(x, -50, 50)))  # noqa: E731

        rows, frame_idx, frame, t = [], -1, None, 0.0
        while True:
            want = round(t * fps)                 # nearest video frame to this 0.05 s step
            if want >= n:
                break
            while frame_idx < want:
                ok, img = cap.read()
                if not ok:
                    break
                frame_idx, frame = frame_idx + 1, img
            if frame_idx < want:
                break
            out = self.sess.run(None, {"new_img": pack(frame), **fixed, **state})
            vec = out[0][0]
            state = {"state_img_q": out[1], "state_desire_q": out[2], "state_feat_q": out[3]}
            meta = sig(vec[META])
            b3, b4, b5 = meta[HARD_BRAKE_3][0], meta[HARD_BRAKE_4][0], meta[HARD_BRAKE_5][0]   # within 2 s
            prev5 = np.roll(prev5, -1)
            prev5[-1] = b5
            prev3 = np.roll(prev3, -1)
            prev3[-1] = b3
            fcw = bool((prev5 > FCW_5).all() and (prev3 > FCW_3).all())
            lead = vec[LEAD].reshape(2, 72)[0].reshape(3, 6, 4)     # mean of (3 time offsets, 6 times, x/y/v/a)
            plan = vec[PLAN].reshape(2, 33 * 15)[0].reshape(33, 15)  # mean of the planned trajectory
            rows.append([round(t, 3), int(fcw), round(float(b3), 4), round(float(b4), 4), round(float(b5), 4),
                         round(float(sig(vec[LEAD_PROB])[0]), 4), round(float(lead[0, 0, 0]), 2),
                         round(float(lead[0, 0, 2]), 2), round(float(lead[0, 0, 3]), 2), round(float(plan[0, 6]), 3)])
            t = round(t + STEP_S, 3)
        return clip, rows


@app.function(image=image, volumes={"/data": volume})
def test_clips() -> list[tuple[str, str]]:
    """(folder, clip id) for every test clip."""
    jobs = []
    for sub in ("test-public/positive", "test-public/negative", "test-private/positive", "test-private/negative"):
        for r in csv.DictReader(open(f"/data/nexar/{sub}/metadata.csv")):
            jobs.append((sub, r["file_name"][:-4]))
    return jobs


@app.local_entrypoint()
def main(limit: int = 0) -> None:
    jobs = test_clips.remote()
    if limit:   # test: a few collision clips and a few normal ones
        jobs = [j for j in jobs if j[0].endswith("positive")][:limit // 2] + \
               [j for j in jobs if j[0].endswith("negative")][:limit - limit // 2]
    print(f"{len(jobs)} clips")
    op = Openpilot()
    first = op.run.remote(*jobs[0])          # one first, alone: puts the model file into the Volume once
    res, failed = {first[0]: first[1]}, 0
    for r in op.run.starmap(jobs[1:], return_exceptions=True):
        if isinstance(r, Exception):
            failed += 1
            print(f"FAILED: {r}", flush=True)
        else:
            res[r[0]] = r[1]
    path = OUT if not limit else OUT.with_name("openpilot_series_test.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res))
    print(f"{len(res)} clips, {sum(len(v) for v in res.values())} steps, {failed} failed, saved {path}")
