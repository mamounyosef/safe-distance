"""Move a training run from one Modal workspace to another, so `resume: last` continues there.

Copies <experiment>/ from the source workspace's runs volume to the target's (the target volume is created if
missing): every log, config and run-id file, plus the checkpoints a resume and the later checks need:
    the NEWEST rolling step<N>.pt, last.pt, best.pt, every top_step<N>.pt, top_k.json.
Older rolling checkpoints are left behind (each is about 0.2 GB and a resume never reads them).
Files pass through a temporary folder on this PC. Nothing is deleted on either side.

RUN IT (from the repo root): source session, target session, experiment folder
    python scripts\\move_run.py 18 19 stage1_lora
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

VOLUME = "safe-distance-runs"


def env_for(session: str) -> dict:
    """Environment that points Modal at one workspace."""
    return dict(os.environ, MODAL_CONFIG_PATH=str(Path.home() / f".modal_session{session}.toml"),
                PYTHONIOENCODING="utf-8")


def side_list(exp: str) -> None:
    """(Runs inside the source's environment.) Print every file under <exp>/ with its size and time, as JSON."""
    import modal
    vol = modal.Volume.from_name(VOLUME)
    out = [{"path": e.path, "size": e.size, "mtime": e.mtime} for e in vol.listdir(exp, recursive=True)
           if e.type == modal.volume.FileEntryType.FILE]
    print(json.dumps(out))


def side_get(paths_file: str, dest: str) -> None:
    """(Source side.) Download the listed files into dest, keeping their paths."""
    import modal
    vol = modal.Volume.from_name(VOLUME)
    for p in json.loads(Path(paths_file).read_text()):
        target = Path(dest) / p
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            for chunk in vol.read_file(p):
                f.write(chunk)
        print(f"  got  {p}  ({target.stat().st_size / 1e6:.1f} MB)", flush=True)


def side_put(src: str, exp: str) -> None:
    """(Target side.) Upload everything under src/<exp> into the target volume (created if missing)."""
    import modal
    vol = modal.Volume.from_name(VOLUME, create_if_missing=True)
    base = Path(src)
    files = [p for p in (base / exp).rglob("*") if p.is_file()]
    # `resume: last` loads the checkpoint with the NEWEST file time, and an upload resets the times. So the newest
    # rolling step<N>.pt goes up last, on its own, a few seconds later: it is then clearly the newest file.
    rolling = [p for p in files if re.fullmatch(r"step\d+\.pt", p.name) and p.parent.name == "checkpoints"]
    newest = max(rolling, key=lambda p: int(re.search(r"\d+", p.name).group()), default=None)
    with vol.batch_upload(force=True) as batch:
        for p in files:
            if p != newest:
                batch.put_file(str(p), "/" + p.relative_to(base).as_posix())
    if newest:
        import time
        time.sleep(3)
        with vol.batch_upload(force=True) as batch:
            batch.put_file(str(newest), "/" + newest.relative_to(base).as_posix())
    print(f"  put  {len(files)} files into {VOLUME}:/{exp} (newest checkpoint last: {newest.name if newest else '-'})",
          flush=True)


def run_side(session: str, *args: str) -> str:
    """Run this script's side function in another workspace's environment; return what it printed."""
    r = subprocess.run([sys.executable, __file__, "--side", *args], env=env_for(session),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(f"STOP: {args[0]} on session {session} failed:\n{r.stderr[-2000:]}")
    return r.stdout


def choose(files: list[dict]) -> list[str]:
    """Which files to copy: all but the older rolling step<N>.pt checkpoints."""
    rolling = [f for f in files if re.search(r"/checkpoints/step\d+\.pt$", f["path"])]
    newest = max(rolling, key=lambda f: int(re.search(r"step(\d+)\.pt$", f["path"]).group(1)), default=None)
    keep = [f["path"] for f in files if f not in rolling]
    if newest:
        keep.append(newest["path"])
    return keep


def main() -> None:
    if sys.argv[1] == "--side":                                       # a side job (see run_side)
        {"list": lambda: side_list(sys.argv[3]), "get": lambda: side_get(sys.argv[3], sys.argv[4]),
         "put": lambda: side_put(sys.argv[3], sys.argv[4])}[sys.argv[2]]()
        return
    src, dst, exp = sys.argv[1], sys.argv[2], sys.argv[3]
    files = json.loads(run_side(src, "list", exp).strip().splitlines()[-1])
    keep = choose(files)
    ckpts = sorted(Path(p).name for p in keep if p.endswith(".pt"))
    size = sum(f["size"] for f in files if f["path"] in keep) / 1e9
    print(f"session {src} -> {dst}: {len(keep)} of {len(files)} files ({size:.2f} GB); checkpoints: {ckpts}")
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "paths.json").write_text(json.dumps(keep))
        print(run_side(src, "get", str(Path(td) / "paths.json"), str(Path(td) / "files")), end="")
        print(run_side(dst, "put", str(Path(td) / "files"), exp), end="")
    after = {f["path"]: f["size"] for f in json.loads(run_side(dst, "list", exp).strip().splitlines()[-1])}
    missing = [p for p in keep if after.get(p) != next(f["size"] for f in files if f["path"] == p)]
    print("check: every copied file present with the same size" if not missing else f"STOP: missing or wrong size: {missing}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
