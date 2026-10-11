"""BADAS-Open (Nexar's learned collision-risk model) on the Nexar TEST set, on Modal.

BADAS-Open looks at the last 2 s of a clip (16 frames at 8 per second, 224 px)
and outputs one number: the probability that a collision is about to happen.
It was trained on Nexar's 1,500 TRAINING clips, so the test set is new to it.
We run it exactly as its own loader does (badas_loader.py: V-JEPA 2 ViT-L
backbone + Nexar's trained head), one score per test clip, and save them as a
submission CSV that score_nexar_test.py and Nexar's evaluate_submission.py read.

Needs: access to the gated Hugging Face repo nexar-ai/BADAS-Open (granted), and
this PC logged in to Hugging Face (the token is passed to the job for this run only).

RUN IT (PowerShell, from the repo root; Modal account ahmad-yonis):

    $env:MODAL_CONFIG_PATH = "$HOME\\.modal_session22.toml"
    .venv\\Scripts\\modal.exe run src\\ttc\\benchmarks\\nexar\\badas_modal.py --limit 4    # test on 4 clips
    .venv\\Scripts\\modal.exe run src\\ttc\\benchmarks\\nexar\\badas_modal.py              # all 1,344

Writes results/test1/submission_badas_open.csv (id,score).

With --series: a reading every 0.5 s through every clip instead (as it would
run live), saved to results/test1/badas_series.json, for false warnings per
hour of normal driving and how early it warns. Resume-safe: each clip is saved
to the Volume (results/badas_series/...) as it finishes, a re-run skips saved
clips, and progress = the number of saved files:
    .venv\\Scripts\\modal.exe volume ls safe-distance-data results/badas_series/bdd100k_videos_sharegpt4video
Add --dataset bdd100k to run it
on the 608 BDD100K normal-driving clips instead (saved to
src/ttc/benchmarks/bdd100k/results/badas_series.json).
"""

from __future__ import annotations

import csv
from pathlib import Path

import modal
from huggingface_hub import get_token

# ---- CONFIG ----
VOLUME = "safe-distance-data"
GPU = "L4"
MAX_CONTAINERS = 4
REPO = "nexar-ai/BADAS-Open"
BASE_MODEL = "facebook/vjepa2-vitl-fpc16-256-ssv2"   # backbone named in badas_loader.py
CACHE = "/data/models/hf"                            # Hugging Face downloads kept in the Volume
OUT = Path(__file__).resolve().parent / "results" / "test1" / "submission_badas_open.csv"
SERIES_OUT = Path(__file__).resolve().parent / "results" / "test1" / "badas_series.json"
BDD_DIR = "bdd100k/videos/sharegpt4video"     # --dataset bdd100k: 608 BDD100K normal-driving clips
BDD_SERIES_OUT = Path(__file__).resolve().parents[1] / "bdd100k" / "results" / "badas_series.json"
SERIES_SAVE_DIR = "results/badas_series"   # per-clip readings in the Volume (progress = number of files)
SERIES_STEP = 4             # --series: one reading every 4 frames at 8 per second = every 0.5 s
SERIES_BATCH = 8              # windows per GPU pass
SERIES_FP16 = True            # half precision on the GPU (about 2x faster; checked with --check)
FRAME_CACHE_DIR = "cache/badas224"   # --cache: each clip's frames, decoded once (8 per second, 224x224 RGB)
CACHE_CONTAINERS = 16         # small CPU containers decoding in parallel (cheap: no GPU)
# ----------------

app = modal.App("safe-distance-badas")
volume = modal.Volume.from_name(VOLUME)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install("torch==2.6.0", "torchvision==0.21.0", index_url="https://download.pytorch.org/whl/cu124")
    .pip_install("transformers==4.53.0", "huggingface_hub", "opencv-python-headless", "numpy", "pillow",
                 "albumentations", "psutil")
    .env({"HF_HOME": CACHE})
)
secret = modal.Secret.from_dict({"HF_TOKEN": get_token() or ""})
cpu_image = modal.Image.debian_slim(python_version="3.12").apt_install("libgl1", "libglib2.0-0") \
    .pip_install("opencv-python-headless", "numpy")


def decode_frames(path: str):
    """The frames BADAS sees, read in ONE pass through the video: frame round(i x fps / 8)
    for i = 0, 1, 2 ..., resized to 224x224 and turned into RGB, exactly the frames and
    the resize of BADAS's own loader (utils/video.py load_full_video_frames), which
    instead seeks separately to every frame (slow: each seek re-decodes from a keyframe)."""
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(path)
    fps, total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    count = int(round(total / fps * 8.0))
    wanted = [int(round(i * fps / 8.0)) for i in range(count)]
    wanted = [w for w in wanted if w < total]
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
    return np.stack(frames) if frames else np.zeros((0, 224, 224, 3), np.uint8)


def cache_path(video: str, clip: str) -> Path:
    """Where a clip's decoded frames are kept in the Volume."""
    return Path("/data", FRAME_CACHE_DIR, Path(video).parent.as_posix().replace("/", "_"), f"{clip}.npy")


@app.function(image=cpu_image, cpu=2, memory=2048, volumes={"/data": volume}, timeout=1800,
              max_containers=CACHE_CONTAINERS)
def cache_frames(video: str, clip: str) -> tuple[str, float]:
    """Decode one clip once and save its frames to the Volume (skipped if already saved).
    Returns (clip id, seconds it took; 0 if it was already there)."""
    import time

    import numpy as np

    out = cache_path(video, clip)
    if out.exists():
        return clip, 0.0
    start = time.time()
    frames = decode_frames(f"/data/{video}")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(out) + ".part.npy", frames)               # write, then rename: no half-written files
    Path(str(out) + ".part.npy").rename(out)
    volume.commit()
    return clip, round(time.time() - start, 1)


@app.cls(image=image, gpu=GPU, volumes={"/data": volume}, secrets=[secret], timeout=3600,
         max_containers=MAX_CONTAINERS)
class Badas:
    @modal.enter()
    def load(self) -> None:
        """Load the model once per container (as badas_loader.py, but from the BADAS-Open repo)."""
        import sys

        from huggingface_hub import snapshot_download

        repo = Path(snapshot_download(REPO, allow_patterns=["src/*", "src/**/*", "weights/*"]))
        sys.path.insert(0, str(repo / "src"))
        from models.vjepa import VJEPAModel

        # One prediction from the clip's LAST 16 frames at 8 per second (no sliding window):
        # the official test asks "is a collision coming?" at the end of each clip.
        self.model = VJEPAModel(model_name=BASE_MODEL, checkpoint_path=str(repo / "weights" / "badas_open.pth"),
                                frame_count=16, img_size=224, target_fps=8.0, take_last_frames=True,
                                use_sliding_window=False)
        self.model.load()
        volume.commit()   # keep the downloaded weights in the Volume for the other containers

    @modal.method()
    def score(self, video: str, clip: str) -> tuple[str, float]:
        """Collision probability for one clip (video = its path inside the Volume)."""
        probs = self.model.predict(f"/data/{video}")
        return clip, float(probs[-1])

    @modal.method()
    def series(self, video: str, clip: str) -> tuple[str, list]:
        """Collision probability every SERIES_STEP frames (0.5 s) through the whole clip, as it
        would run live in the car: each reading uses the 16 frames (2 s) up to that moment.
        Returns [(time in s at the end of the window, probability), ...]."""
        import json

        import numpy as np

        # Resume-safe: each clip's readings are saved to the Volume as soon as they are done,
        # and a clip already saved by an earlier (stopped) run is not computed again.
        saved = Path("/data", SERIES_SAVE_DIR, Path(video).parent.as_posix().replace("/", "_"), f"{clip}.json")
        if saved.exists():
            return clip, json.loads(saved.read_text())
        cached = cache_path(video, clip)          # frames decoded beforehand on cheap CPUs (--cache)
        frames = np.load(cached) if cached.exists() else decode_frames(f"/data/{video}")
        out = self._readings(frames, SERIES_FP16)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text(json.dumps(out))
        volume.commit()
        return clip, out

    def _readings(self, frames, fp16: bool) -> list:
        """BADAS's probability every SERIES_STEP frames, from 224x224 RGB frames at 8 per second.
        Same preprocessing and output as BADAS's own sliding window (models/vjepa.py)."""
        import torch
        from utils.video import apply_temperature_scaling

        ends = list(range(16, len(frames) + 1, SERIES_STEP))
        out = []
        for i in range(0, len(ends), SERIES_BATCH):
            batch = [self.model.processor(videos=frames[e - 16:e], return_tensors="pt")["pixel_values_videos"]
                     .squeeze(0) for e in ends[i:i + SERIES_BATCH]]
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16, enabled=fp16):
                logits = self.model.model(torch.stack(batch).to(self.model.device)).float()
                probs = torch.softmax(apply_temperature_scaling(logits, temperature=2.0), dim=1)[:, 1]
            out += [(round(e / 8.0, 3), round(float(p), 5)) for e, p in zip(ends[i:i + SERIES_BATCH], probs)]
        return out

    @modal.method()
    def check(self, video: str) -> dict:
        """Is the fast path the same as BADAS's own? Compares, on one clip: frames from our
        one-pass decoder vs BADAS's loader, and readings in half vs full precision. Also times each."""
        import time

        import numpy as np
        from utils.video import load_full_video_frames

        t = time.time()
        theirs = load_full_video_frames(video_path=f"/data/{video}", target_size=(224, 224), target_fps=8.0)
        t_theirs = time.time() - t
        t = time.time()
        ours = decode_frames(f"/data/{video}")
        t_ours = time.time() - t
        n = min(len(theirs), len(ours))
        t = time.time()
        p32 = [p for _, p in self._readings(ours, False)]
        t32 = time.time() - t
        t = time.time()
        p16 = [p for _, p in self._readings(ours, True)]
        t16 = time.time() - t
        diff = np.abs(np.array(p32) - np.array(p16))
        # Which frames differ, and is it just a shift by one frame (seeking landing next door)?
        same = [bool(np.array_equal(theirs[i], ours[i])) for i in range(n)]
        shifted = [bool(not same[i] and any(np.array_equal(theirs[i], ours[j]) for j in (i - 1, i + 1)
                                            if 0 <= j < n)) for i in range(n)]
        p_theirs = [p for _, p in self._readings(theirs, False)]
        dd = np.abs(np.array(p_theirs[:len(p32)]) - np.array(p32[:len(p_theirs)]))
        # Ground truth: decode EVERY video frame in order, and find which one each of
        # BADAS's frames really is (closest picture). Offset 0 = the frame it meant to take.
        import cv2
        cap = cv2.VideoCapture(f"/data/{video}")
        fps = cap.get(cv2.CAP_PROP_FPS)
        allf = []
        while True:
            ok, img = cap.read()
            if not ok:
                break
            allf.append(cv2.cvtColor(cv2.resize(img, (224, 224)), cv2.COLOR_BGR2RGB).astype(np.int16))
        allf = np.stack(allf)
        offsets = []
        for i in range(0, n, 10):                                  # every 10th frame is enough
            want = int(round(i * fps / 8.0))
            lo, hi = max(0, want - 45), min(len(allf), want + 46)
            err = np.abs(allf[lo:hi] - theirs[i].astype(np.int16)).mean(axis=(1, 2, 3))
            offsets.append(int(lo + err.argmin() - want))
        return {"video_frames": len(allf), "fps": round(fps, 3),
                "theirs_offset_from_intended_frame (every 10th)": offsets,
                "frames_same": sum(same), "frames_off_by_one": sum(shifted),
                "frames_other": n - sum(same) - sum(shifted),
                "ours_vs_theirs_max_prob_difference": round(float(dd.max()), 5),
                "ours_vs_theirs_mean_prob_difference": round(float(dd.mean()), 5),"frames_theirs": len(theirs), "frames_ours": len(ours),
                "frames_identical": bool(len(theirs) == len(ours) and np.array_equal(theirs[:n], ours[:n])),
                "max_pixel_difference": int(np.abs(theirs[:n].astype(int) - ours[:n].astype(int)).max()) if n else None,
                "decode_seconds_theirs": round(t_theirs, 1), "decode_seconds_ours": round(t_ours, 1),
                "readings": len(p32), "model_seconds_fp32": round(t32, 1), "model_seconds_fp16": round(t16, 1),
                "fp16_vs_fp32_max_prob_difference": round(float(diff.max()), 5),
                "fp16_vs_fp32_mean_prob_difference": round(float(diff.mean()), 5)}


@app.function(image=image, volumes={"/data": volume})
def clip_list(dataset: str) -> list[tuple[str, str]]:
    """(video path inside the Volume, clip id) for every clip of a dataset:
    "nexar" = Nexar's test set, "bdd100k" = the 608 BDD100K normal-driving clips."""
    jobs = []
    if dataset == "bdd100k":
        return [(f"{BDD_DIR}/{p.name}", p.stem) for p in sorted(Path("/data", BDD_DIR).glob("*.mov"))]
    for sub in ("test-public/positive", "test-public/negative", "test-private/positive", "test-private/negative"):
        for r in csv.DictReader(open(f"/data/nexar/{sub}/metadata.csv")):
            jobs.append((f"nexar/{sub}/{r['file_name']}", r["file_name"][:-4]))
    return jobs


@app.local_entrypoint()
def main(limit: int = 0, series: bool = False, dataset: str = "nexar", check: bool = False,
         cache: bool = False) -> None:
    import json
    import time

    jobs = clip_list.remote(dataset)
    jobs = jobs[:limit] if limit else jobs
    print(f"{len(jobs)} clips")
    if cache:    # decode every clip once on small CPU containers (resume-safe: done clips are skipped)
        start, done, secs = time.time(), 0, []
        for r in cache_frames.starmap(jobs, return_exceptions=True):
            if isinstance(r, Exception):
                print(f"FAILED: {r}", flush=True)
                continue
            done += 1
            if r[1]:
                secs.append(r[1])
            if done % 50 == 0 or done == len(jobs):
                print(f"  cached {done}/{len(jobs)} ({time.time() - start:.0f} s so far)", flush=True)
        if secs:
            print(f"decoding: {sum(secs) / len(secs):.1f} s per clip on average, {sum(secs) / 60:.1f} CPU-container "
                  f"minutes in total")
        return
    badas = Badas()
    if check:    # compare the fast path with BADAS's own, on the first clip
        print(json.dumps(badas.check.remote(jobs[0][0]), indent=1))
        return
    if series:   # readings every 0.5 s through every clip (for false warnings per hour and warning time)
        res, failed, start = {}, 0, time.time()
        for r in badas.series.starmap(jobs, return_exceptions=True):
            if isinstance(r, Exception):
                failed += 1
                print(f"FAILED: {r}", flush=True)
            else:
                res[r[0]] = r[1]
            if (len(res) + failed) % 50 == 0:
                print(f"  {len(res) + failed}/{len(jobs)} clips ({time.time() - start:.0f} s so far)", flush=True)
        print(f"series: {time.time() - start:.0f} s for {len(jobs)} clips")
        path = SERIES_OUT if dataset == "nexar" else BDD_SERIES_OUT
        path = path if not limit else path.with_name("badas_series_test.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(res))
        print(f"{len(res)} clips, {sum(len(v) for v in res.values())} readings, {failed} failed, saved {path}")
        return
    first = badas.score.remote(*jobs[0])      # one first, alone: downloads the weights into the Volume once
    print(first)
    results = [first]
    for r in badas.score.starmap(jobs[1:], return_exceptions=True):
        if isinstance(r, Exception):
            print(f"FAILED: {r}", flush=True)
        else:
            results.append(r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    name = OUT if not limit else OUT.with_name("submission_badas_open_test.csv")
    with name.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "score"])
        for cid, s in sorted(results):
            w.writerow([cid, round(s, 5)])
    print(f"{len(results)} scored, saved {name}")
