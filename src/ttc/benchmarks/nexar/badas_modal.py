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
hour of normal driving and how early it warns.
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
SERIES_STEP = 4               # --series: one reading every 4 frames at 8 per second = every 0.5 s
SERIES_BATCH = 8              # windows per GPU pass
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
    def score(self, sub: str, clip: str) -> tuple[str, float]:
        """Collision probability for one test clip."""
        probs = self.model.predict(f"/data/nexar/{sub}/{clip}.mp4")
        return clip, float(probs[-1])

    @modal.method()
    def series(self, sub: str, clip: str) -> tuple[str, list]:
        """Collision probability every SERIES_STEP frames (0.5 s) through the whole clip, as it
        would run live in the car: each reading uses the 16 frames (2 s) up to that moment.
        Returns [(time in s at the end of the window, probability), ...]."""
        import torch
        from utils.video import apply_temperature_scaling, load_full_video_frames

        frames = load_full_video_frames(video_path=f"/data/nexar/{sub}/{clip}.mp4", target_size=(224, 224),
                                        target_fps=8.0)
        ends = list(range(16, len(frames) + 1, SERIES_STEP))
        out = []
        for i in range(0, len(ends), SERIES_BATCH):
            # Same preprocessing and output as BADAS's own sliding window (vjepa.py).
            batch = [self.model.processor(videos=frames[e - 16:e], return_tensors="pt")["pixel_values_videos"]
                     .squeeze(0) for e in ends[i:i + SERIES_BATCH]]
            with torch.no_grad():
                logits = self.model.model(torch.stack(batch).to(self.model.device))
                probs = torch.softmax(apply_temperature_scaling(logits, temperature=2.0), dim=1)[:, 1]
            out += [(round(e / 8.0, 3), round(float(p), 5)) for e, p in zip(ends[i:i + SERIES_BATCH], probs)]
        return clip, out


@app.function(image=image, volumes={"/data": volume})
def test_clips() -> list[tuple[str, str]]:
    """(folder, clip id) for every test clip."""
    jobs = []
    for sub in ("test-public/positive", "test-public/negative", "test-private/positive", "test-private/negative"):
        for r in csv.DictReader(open(f"/data/nexar/{sub}/metadata.csv")):
            jobs.append((sub, r["file_name"][:-4]))
    return jobs


@app.local_entrypoint()
def main(limit: int = 0, series: bool = False) -> None:
    import json

    jobs = test_clips.remote()
    jobs = jobs[:limit] if limit else jobs
    print(f"{len(jobs)} clips")
    badas = Badas()
    if series:   # readings every 0.5 s through every clip (for false warnings per hour and warning time)
        res, failed = {}, 0
        for r in badas.series.starmap(jobs, return_exceptions=True):
            if isinstance(r, Exception):
                failed += 1
                print(f"FAILED: {r}", flush=True)
            else:
                res[r[0]] = r[1]
        path = SERIES_OUT if not limit else SERIES_OUT.with_name("badas_series_test.json")
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
