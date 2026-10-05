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
    jobs = jobs[:limit] if limit else jobs
    print(f"{len(jobs)} clips")
    badas = Badas()
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
