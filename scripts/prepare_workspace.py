"""Make a fresh Modal workspace ready for stage 1: the same data volume as the first one, rebuilt from the sources.

Modal volumes belong to one account, so each new workspace needs its own copy. Three steps, all CPU only, each
resume-safe (a re-run skips what is already done):
    1. scripts/modal_nexar_download.py              Nexar dataset from Hugging Face (31 GB)        about $0.30
    2. src/risk/data/data_code/bdd100k_extract.py   the 4,500 drawn BDD100K clips                  about $0.80
    3. src/risk/data/data_code/wide_cache.py        the 16:9 frame cache (6,243 clips)             about $1.90
The frame counts (src/risk/data/wide_frame_counts.json) need no re-run: the same decoder gives the same frames.
Hugging Face downloads use this PC's Hugging Face login (passed to the job for that run only).

RUN IT (from the repo root; one workspace per run, by its session number):
    .venv\\Scripts\\python.exe scripts\\prepare_workspace.py 19

Log: src/risk/data/prepare_workspace_session<N>.log (everything the three steps print)
"""

import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STEPS = [("Nexar download", ["scripts/modal_nexar_download.py"]),
         ("BDD100K clips", ["src/risk/data/data_code/bdd100k_extract.py"]),
         ("16:9 frame cache", ["src/risk/data/data_code/wide_cache.py"])]


def main() -> None:
    session = sys.argv[1]                                             # e.g. 19
    tag = f"session{session}"
    env = dict(os.environ, MODAL_CONFIG_PATH=str(Path.home() / f".modal_session{session}.toml"),
               PYTHONIOENCODING="utf-8")
    log = REPO / f"src/risk/data/prepare_workspace_{tag}.log"
    with open(log, "a", encoding="utf-8") as f:
        for name, script in STEPS:
            extra = [] if "nexar_download" in script[0] else ["--tag", tag]   # summary files kept per workspace
            cmd = [sys.executable, "-m", "modal", "run", *script, *extra]
            t = time.time()
            head = f"\n===== {tag}: {name}  ({time.strftime('%H:%M:%S')}) =====\n"
            print(head, flush=True)
            f.write(head)
            f.flush()
            r = subprocess.run(cmd, cwd=REPO, env=env, stdout=f, stderr=subprocess.STDOUT)
            done = f"===== {name}: exit {r.returncode}, {(time.time() - t) / 60:.1f} min =====\n"
            print(done, flush=True)
            f.write(done)
            if r.returncode != 0:
                sys.exit(f"STOP: {name} failed on {tag} (see {log})")
    print(f"{tag} ready; log {log}")


if __name__ == "__main__":
    main()
