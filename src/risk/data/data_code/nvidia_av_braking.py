"""Find hard-braking moments in the NVIDIA PhysicalAI-AV driving clips (Modal, CPU only, no videos).

nexar-ai/nvidia-av-trajectory (Hugging Face): 239,027 normal-driving clips (1920x1080,
30 fps, about 20 s) with a per-frame track of our car's speed (manifest.parquet, 7.5 GB,
144.5 million rows). A sudden hard brake in ordinary driving is a possible near-miss:
    - remove it from the "normal" set (never tell the model a real near-miss is normal)
    - after checking, a real one can become an extra "crash coming" example

Per clip: the strongest braking over any 0.5 s span (speed smoothed over 0.5 s first,
since speed from positioning is noisy), when it happens, and the speeds around it.

Resume-safe: the manifest is downloaded into the Volume once; the per-clip result is
saved to the Volume and re-used on a re-run.

RUN IT (see current_modal_commands.txt):

    python -m modal run src\\risk\\data\\data_code\\nvidia_av_braking.py --limit 2000   # timed test: first 2,000 clips
    python -m modal run src\\risk\\data\\data_code\\nvidia_av_braking.py                # all 239,027

Writes, on this PC:
    src/risk/data/nvidia_av_braking_summary.json   counts per braking level (numbers only)
    C:/safe-distance-data/nvidia_av/braking.csv    one row per clip (too big for git)
"""

import json
import time
from pathlib import Path

import modal

LOCAL = modal.is_local()
REPO = Path(__file__).resolve().parents[4] if LOCAL else Path("/root")

# ---- CONFIG ----
VOLUME = "safe-distance-data"
HF_REPO = "nexar-ai/nvidia-av-trajectory"
VOL_DIR = "/data/nvidia_av"                         # manifest + results in the Volume
SMOOTH_S = 0.5                                      # moving average of speed before measuring braking
SPAN_S = 0.5                                        # braking = speed drop over this span / span
LEVELS = [3.0, 4.0, 5.0, 6.0, 8.0]                  # m/s^2: count clips braking at least this hard
MIN_SPEED = 3.0                                     # m/s: ignore braking that starts below about 11 km/h
SUMMARY = REPO / "src/risk/data/nvidia_av_braking_summary.json"
CSV_OUT = Path(r"C:\safe-distance-data\nvidia_av\braking.csv")
CPU, MEMORY_MB = 4, 16384
# ----------------

app = modal.App("safe-distance-nvidia-av-braking")
volume = modal.Volume.from_name(VOLUME)
image = modal.Image.debian_slim(python_version="3.12").pip_install("pyarrow", "numpy", "pandas", "huggingface_hub")


def clip_braking(t_us, v) -> dict:
    """Strongest braking in one clip: max over time of (speed now - speed SPAN_S later) / SPAN_S."""
    import numpy as np

    t = (t_us - t_us[0]) / 1e6
    dt = float(np.median(np.diff(t))) if len(t) > 1 else 1 / 30
    k = max(1, int(round(SMOOTH_S / dt)))
    vs = np.convolve(v, np.ones(k) / k, mode="same")              # smoothed speed
    s = max(1, int(round(SPAN_S / dt)))
    if len(vs) <= s + k:
        return {"frames": len(v), "max_brake": 0.0, "at_s": None, "speed_before": None, "speed_after": None}
    drop = (vs[:-s] - vs[s:]) / (s * dt)                          # deceleration, m/s^2
    drop[vs[:-s] < MIN_SPEED] = 0.0
    drop[: k] = drop[-k:] = 0.0                                   # edges of the smoothing are unreliable
    i = int(np.argmax(drop))
    after = min(len(vs) - 1, i + int(round(1.0 / dt)))
    return {"frames": len(v), "max_brake": round(float(drop[i]), 2), "at_s": round(float(t[i]), 2),
            "speed_before": round(float(vs[i]), 2), "speed_after": round(float(vs[after]), 2),
            "max_speed": round(float(vs.max()), 2)}


@app.function(image=image, cpu=CPU, memory=MEMORY_MB, volumes={"/data": volume}, timeout=3 * 3600)
def scan(limit: int) -> dict:
    """Download the manifest once, then measure braking per clip, row group by row group."""
    import io

    import numpy as np
    import pandas as pd
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    t0 = time.time()
    out_csv = Path(VOL_DIR, f"braking{'_test' if limit else ''}.csv")
    if out_csv.exists():
        print(f"already done, re-using {out_csv}")
        return {"csv": out_csv.read_text(), "download_s": 0, "scan_s": 0, "reused": True}
    path = hf_hub_download(HF_REPO, "manifest.parquet", repo_type="dataset", local_dir=VOL_DIR)
    volume.commit()
    download_s = round(time.time() - t0)
    print(f"manifest ready ({Path(path).stat().st_size / 1e9:.2f} GB) after {download_s} s", flush=True)

    pf = pq.ParquetFile(path)
    rows, carry, done_ids, repeats, t1 = [], None, set(), 0, time.time()
    for g in range(pf.num_row_groups):
        df = pf.read_row_group(g, columns=["uuid", "timestamp_us", "speed_mps"]).to_pandas()
        if carry is not None:                                     # a clip may continue from the last group
            df = pd.concat([carry, df], ignore_index=True)
        last = df["uuid"].iloc[-1]
        carry = df[df["uuid"] == last]
        for uid, c in df[df["uuid"] != last].groupby("uuid", sort=False):
            repeats += uid in done_ids                            # should stay 0 if clips are contiguous
            done_ids.add(uid)
            c = c.sort_values("timestamp_us")
            rows.append({"uuid": uid, **clip_braking(c["timestamp_us"].to_numpy(), c["speed_mps"].to_numpy())})
        if g % 20 == 0:
            el = time.time() - t1
            print(f"  row group {g + 1}/{pf.num_row_groups}: {len(rows):,} clips  {el:.0f} s  "
                  f"ETA {el / (g + 1) * (pf.num_row_groups - g - 1):.0f} s", flush=True)
        if limit and len(rows) >= limit:
            break
    if carry is not None and not (limit and len(rows) >= limit):
        c = carry.sort_values("timestamp_us")
        rows.append({"uuid": carry["uuid"].iloc[0],
                     **clip_braking(c["timestamp_us"].to_numpy(), c["speed_mps"].to_numpy())})
    res = pd.DataFrame(rows[: limit or None])
    buf = io.StringIO()
    res.to_csv(buf, index=False)
    out_csv.write_text(buf.getvalue())                            # saved: a re-run re-uses it
    volume.commit()
    return {"csv": buf.getvalue(), "download_s": download_s, "scan_s": round(time.time() - t1),
            "repeated_uuids": repeats, "reused": False}


@app.local_entrypoint()
def main(limit: int = 0) -> None:
    import io

    import pandas as pd

    t0 = time.time()
    r = scan.remote(limit)
    df = pd.read_csv(io.StringIO(r["csv"]))
    moving = df[df["max_speed"] >= MIN_SPEED]
    s = {"clips": len(df), "clips_moving": len(moving), "limit": limit,
         "download_s": r["download_s"], "scan_s": r["scan_s"], "repeated_uuids": r.get("repeated_uuids"),
         "wall_s": round(time.time() - t0),
         "cost_usd_estimate": round((r["download_s"] + r["scan_s"]) / 3600 * (CPU * 0.0473 + MEMORY_MB / 1024 * 0.008), 3),
         "max_brake_percentiles": {p: round(float(df["max_brake"].quantile(p / 100)), 2) for p in (50, 90, 99, 99.9)},
         "clips_braking_at_least": {f"{lv:g} m/s2": int((df["max_brake"] >= lv).sum()) for lv in LEVELS}}
    if limit:
        per_clip = (r["scan_s"] or 1) / max(len(df), 1)
        s["full_run_estimate_s"] = round(r["download_s"] + per_clip * 239027)
    out = SUMMARY.with_name("nvidia_av_braking_summary_test.json") if limit else SUMMARY
    out.write_text(json.dumps(s, indent=1))
    csv_out = CSV_OUT.with_name("braking_test.csv") if limit else CSV_OUT
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    csv_out.write_text(r["csv"])
    print(json.dumps(s, indent=1))
    print(f"saved {out} and {csv_out}")
