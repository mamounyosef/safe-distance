"""20 random hard-braking moments from the NVIDIA PhysicalAI-AV clips, as ONE video (this PC, free).

Picks clips whose strongest braking (nvidia_av_braking.py) is at least MIN_BRAKE m/s^2,
and pulls just those clips out of the 5 GB tar shards on Hugging Face with byte-range
requests (shards hold the clips in the manifest's order, so a binary search over each
shard's first clip finds the right shard; then we hop tar headers to the clip).

Each clip: title card, then from BEFORE_S before the brake to AFTER_S after, with the
time relative to the brake and a red frame + "HARD BRAKE" from the brake on, and a 1.5 s
freeze at the brake moment.

RUN IT (from the repo root, after nvidia_av_braking.py):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\nvidia_av_samples.py

Output: C:\\Users\\mamou\\Downloads\\nvidia_av_braking_samples.mp4 (+ .json).

Everyday driving instead (20 random clips of any kind, each shown whole, no braking marks):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\nvidia_av_samples.py --random --out "%USERPROFILE%\\Downloads\\nvidia_av_random_samples.mp4"
"""

from __future__ import annotations

import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample_video import Writer, card, text  # noqa: E402

# ---- CONFIG ----
BASE = "https://huggingface.co/datasets/nexar-ai/nvidia-av-trajectory/resolve/main/shards/videos-{:05d}-of-00591.tar"
N_SHARDS_PRESENT = 490                     # videos-00000 .. 00489 are uploaded (README)
BRAKING_CSV = Path(r"C:\safe-distance-data\nvidia_av\braking.csv")
CACHE = Path(r"C:\safe-distance-data\nvidia_av\samples")
OUT = Path.home() / "Downloads" / "nvidia_av_braking_samples.mp4"
MIN_BRAKE, N, SEED = 6.0, 20, 3
BEFORE_S, AFTER_S = 4.0, 2.0
SIZE, FPS = (1280, 720), 30.0
# ----------------

session = requests.Session()
_tok = __import__("huggingface_hub").get_token()
if _tok:                                       # logged-in requests get far higher rate limits
    session.headers["Authorization"] = f"Bearer {_tok}"


def get_range(shard: int, start: int, end: int, timeout: int = 60) -> bytes:
    """Bytes start..end of a shard; waits and retries when Hugging Face rate-limits (non-206 answer)."""
    import time
    for attempt in range(8):
        r = session.get(BASE.format(shard), headers={"Range": f"bytes={start}-{end}"}, timeout=timeout)
        if r.status_code == 206:
            return r.content
        time.sleep(min(60, 5 * 2 ** attempt))
    raise RuntimeError(f"shard {shard}: no byte range after retries (last status {r.status_code})")


def header(shard: int, off: int) -> tuple[str, int]:
    """Name and size of the tar entry starting at byte `off` of a shard (one 512-byte request)."""
    h = get_range(shard, off, off + 511)
    return h[:100].rstrip(b"\0").decode(errors="ignore"), int(h[124:136].rstrip(b"\0 ").decode() or "0", 8)


def first_clip(shard: int) -> str:
    """The first clip id in a shard (entry 0 is a small 'PaxHeader', entry 1 the first mp4)."""
    name, size = header(shard, 0)
    return header(shard, 512 + (size + 511) // 512 * 512)[0].split(".")[0]


def find_shard(target: int, pos: dict[str, int], firsts: dict[int, int]) -> int:
    """Binary search: the last shard whose first clip comes at or before the target clip."""
    lo, hi = 0, N_SHARDS_PRESENT - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid not in firsts:
            firsts[mid] = pos[first_clip(mid)]
        lo, hi = (mid, hi) if firsts[mid] <= target else (lo, mid - 1)
    return lo


def fetch(uuid: str, shard: int) -> Path | None:
    """Hop tar headers in the shard until the clip, then download only its bytes."""
    out = CACHE / f"{uuid}.mp4"
    if out.exists():
        return out
    off = 0
    while True:
        name, size = header(shard, off)
        if not name:
            return None                                    # end of the tar: not in this shard
        data_off = off + 512
        if name.split(".")[0] == uuid:
            data = get_range(shard, data_off, data_off + size - 1, timeout=300)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            return out
        off = data_off + (size + 511) // 512 * 512


def main() -> None:
    global OUT
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--random", action="store_true", help="random clips of any kind, shown whole")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    OUT = a.out
    df = pd.read_csv(BRAKING_CSV)                           # rows in manifest order
    pos = {u: i for i, u in enumerate(df["uuid"])}
    firsts: dict[int, int] = {}
    last_present = pos[first_clip(N_SHARDS_PRESENT - 1)] + 600   # clips beyond the uploaded shards: skip
    min_brake = -1e9 if a.random else MIN_BRAKE
    cand = df[(df["max_brake"] >= min_brake) & (df.index < last_present)]
    picks = cand.sample(n=N, random_state=a.seed)
    print(f"{len(cand)} candidate clips in the uploaded shards; drawing {N}")
    jobs = [(r.uuid, find_shard(pos[r.uuid], pos, firsts)) for r in picks.itertuples()]
    with ThreadPoolExecutor(3) as ex:                       # fetch a few clips in parallel (rate limits)
        paths = list(ex.map(lambda j: fetch(*j), jobs))
    wr, shown = Writer(OUT, SIZE, FPS), []
    for k, (r, path) in enumerate(zip(picks.itertuples(), paths), 1):
        if path is None:
            print(f"[{k}] {r.uuid}: not found in shard")
            continue
        cap = cv2.VideoCapture(str(path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if a.random:                                       # everyday clip: show it whole
            w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            wr.write(card(SIZE, [f"NVIDIA AV clip {k}/{N}   ({r.uuid[:8]})",
                                 f"random clip, {w}x{h} at {fps:.0f} fps",
                                 f"hardest brake in it: {r.max_brake:.1f} m/s2"]), 1.5)
            f = 0
            while True:
                ok, img = cap.read()
                if not ok:
                    break
                img = cv2.resize(img, SIZE)
                text(img, f"{r.uuid[:8]}   {f / fps:.1f} s", (15, 40), 0.9)
                wr.write(img)
                f += 1
            cap.release()
            shown.append({"n": k, "uuid": r.uuid, "width": w, "height": h, "fps": round(fps, 2),
                          "length_s": round(f / fps, 1), "max_brake": r.max_brake})
            print(f"[{k}/{N}] {r.uuid[:8]}: {w}x{h}, {f / fps:.1f} s", flush=True)
            continue
        wr.write(card(SIZE, [f"NVIDIA AV clip {k}/{N}   ({r.uuid[:8]})",
                             f"hardest brake {r.max_brake:.1f} m/s2 at {r.at_s:.1f} s",
                             f"speed {r.speed_before * 3.6:.0f} km/h -> {r.speed_after * 3.6:.0f} km/h one second later"]),
                 1.5)
        f, frozen = 0, False
        while True:
            ok, img = cap.read()
            if not ok:
                break
            t = f / fps
            f += 1
            if t < r.at_s - BEFORE_S or t > r.at_s + AFTER_S:
                continue
            img = cv2.resize(img, SIZE)
            text(img, f"{t - r.at_s:+.1f} s {'before' if t < r.at_s else 'after'} the brake", (15, 40), 1.0)
            if t >= r.at_s:
                cv2.rectangle(img, (0, 0), (SIZE[0] - 1, SIZE[1] - 1), (0, 0, 255), 10)
                text(img, f"HARD BRAKE ({r.max_brake:.1f} m/s2)", (15, 85), 0.9, (0, 0, 255))
            wr.write(img, 1.5 if (t >= r.at_s and not frozen) else 0.0)
            frozen = frozen or t >= r.at_s
        cap.release()
        shown.append({"n": k, "uuid": r.uuid, "max_brake": r.max_brake, "at_s": r.at_s,
                      "speed_before_kmh": round(r.speed_before * 3.6), "speed_after_kmh": round(r.speed_after * 3.6),
                      "frames_read": f})
        print(f"[{k}/{N}] {r.uuid[:8]}: {r.max_brake:.1f} m/s2 at {r.at_s:.1f} s, {f} frames", flush=True)
    wr.close()
    OUT.with_suffix(".json").write_text(json.dumps(shown, indent=1))
    print(f"saved {OUT} ({len(shown)} clips)")


if __name__ == "__main__":
    main()
