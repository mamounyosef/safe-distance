"""Build the visible-danger labelling set (this PC, free; clips come from the Modal data volume).

Which windows: the 192 late-validation crash windows that end 1.5 s before the crash (group 1's 2nd window, group
2's last-frame window). Order: random (seed 42). Batch 1 = the first 50 of them + 15 decoys (Nexar Public normal
windows at the same positions), shuffled together; batch 2 = the other 142 crash windows (Gemma only, if the
agreement on batch 1 is good). Every window gets an anonymous name (w001, w002, ...): nothing on screen or in the
frame names says crash or normal.

For each window, from the original Nexar video (exactly the 16 frames the model saw: cache frame i = video frame
round(i x fps / 8)):
    frames/<name>/01.jpg ... 16.jpg   the 16 frames at 960 x 540, oldest first (what Gemma gets)
    clips/<name>.mp4                  the same 2 s at full speed, 960 x 540, H.264 (what the person sees, looped)

Outputs (NOT in git: the list says which windows are crashes):
    <data_dir>/set.json, <data_dir>/frames/, <data_dir>/clips/      (data_dir in config.yaml)
    results/set_summary.json                                          (counts only, in git)

RUN IT (from the repo root; MODAL_CONFIG_PATH = a workspace whose data volume has Nexar):
    python src\\risk\\runs\\stage1_lora\\late_validation\\visible_labels\\make_set.py
"""

import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
import yaml

HERE = Path(__file__).resolve().parent                            # visible_labels/
LV = HERE.parent                                                  # late_validation/
RISK = LV.parents[2]                                              # src/risk
CFG = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
S = CFG["set"]
TRAIN_DATA = yaml.safe_load((LV.parent / "config.yaml").read_text(encoding="utf-8"))["data"]

# ---- CONFIG ----
DATA = Path(S["data_dir"])
RAW = Path(r"C:\safe-distance-data\nexar\test-public")             # original Nexar test videos (shared with the review)
COUNTS = json.loads((RISK / TRAIN_DATA["frame_counts"]).read_text())   # frames per cached clip (8 fps)
FPS_CACHE, WINDOW = TRAIN_DATA["fps"], TRAIN_DATA["window_frames"]     # 8 frames per second, 16 frames
GROUP_S = {0: 0.5, 1: 1.0, 2: 1.5}                                 # Nexar group -> clip stops this long before the crash
W, H = S["frame_w"], S["frame_h"]
WORKERS = 8                                                       # windows cut in parallel (i5-12400: 12 threads)
# ----------------


def crash_windows() -> list[dict]:
    """The late-validation crash windows ending exactly timing_s before the crash."""
    out = []
    for w in json.loads((LV / "windows.json").read_text()):
        if w["group"] != "nexar_crash":
            continue
        before = GROUP_S[w["nexar_group"]] + w["end_back"] / FPS_CACHE
        if abs(before - S["timing_s"]) < 1e-9:
            out.append({"kind": "crash", "clip": w["clip"], "folder": "positive", "nexar_group": w["nexar_group"],
                        "end_back": w["end_back"], "before_crash_s": before})
    return out


def decoy_windows(rng: np.random.Generator, n: int) -> list[dict]:
    """n Nexar Public normal windows at the same positions as the crash windows (groups 1 and 2; last frame or
    0.5 s earlier), one per clip, random."""
    pool = {}
    for w in json.loads((LV / "windows.json").read_text()):
        if w["group"] == "nexar_normal" and w["nexar_group"] in (1, 2):
            pool[w["clip"]] = w["nexar_group"]
    clips = sorted(pool)
    out = []
    for k in rng.choice(len(clips), size=n, replace=False):
        c = clips[k]
        back = 4 if pool[c] == 1 else 0                            # mirror the crash windows of the same group
        out.append({"kind": "decoy", "clip": c, "folder": "negative", "nexar_group": pool[c], "end_back": back,
                    "before_crash_s": None})
    return out


def download(items: list[dict]) -> None:
    """Fetch the original videos not yet on this PC (resume-safe: complete files only)."""
    need = sorted({(it["folder"], it["clip"]) for it in items if not (RAW / it["folder"] / f"{it['clip']}.mp4").exists()})
    if not need:
        return
    import modal
    vol = modal.Volume.from_name(TRAIN_DATA["data_volume"])
    for k, (folder, clip) in enumerate(need, 1):
        dst = RAW / folder / f"{clip}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in vol.read_file(f"nexar/test-public/{folder}/{clip}.mp4"):
                f.write(chunk)
        tmp.replace(dst)
        print(f"  downloaded {k}/{len(need)} {folder}/{clip}.mp4 ({dst.stat().st_size / 1e6:.1f} MB)", flush=True)


def cut(it: dict) -> dict:
    """The 16 frames (for Gemma) and the 2 s clip (for the person) of one window, from the original video."""
    src = RAW / it["folder"] / f"{it['clip']}.mp4"
    n_cache = COUNTS[f"nexar_test-public_{it['folder']}/{it['clip']}"]     # frames in the 8 fps cache
    end = n_cache - it["end_back"]                                          # the window's end (cache frame)
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS)
    idx = [int(round(i * fps / FPS_CACHE)) for i in range(end - WINDOW, end)]   # the 16 video frames the model saw
    it.update(end_cache_frame=end, video_fps=round(fps, 3), video_frames=idx,
              window_start_s=round(idx[0] / fps, 3), window_end_s=round((idx[-1] + 1) / fps, 3))

    fdir = DATA / "frames" / it["name"]
    if not (fdir / f"{WINDOW:02d}.jpg").exists():
        fdir.mkdir(parents=True, exist_ok=True)
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx[0])                # ONE seek to the window's first frame ...
        want, pos = {i: k for k, i in enumerate(idx, 1)}, idx[0]
        while pos <= idx[-1]:                                    # ... then read straight through the 2 s
            ok, fr = cap.read()
            if not ok:
                raise SystemExit(f"{src.name}: frame {pos} unreadable")
            if pos in want:
                cv2.imwrite(str(fdir / f"{want[pos]:02d}.jpg"), cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA),
                            [cv2.IMWRITE_JPEG_QUALITY, 92])
            pos += 1
    cap.release()

    clip = DATA / "clips" / f"{it['name']}.mp4"
    if not clip.exists():
        clip.parent.mkdir(parents=True, exist_ok=True)
        tmp = clip.with_suffix(".part.mp4")
        p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{idx[0] / fps:.3f}", "-i", str(src),
                            "-t", f"{(idx[-1] + 1 - idx[0]) / fps:.3f}", "-vf", f"scale={W}:{H}", "-an",
                            "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(tmp)], capture_output=True, text=True)
        if p.returncode:
            raise SystemExit(f"ffmpeg failed on {src.name}: {p.stderr[-500:]}")
        tmp.replace(clip)
    return it


def main() -> None:
    rng = np.random.default_rng(S["seed"])
    crashes = crash_windows()
    crashes = [crashes[k] for k in rng.permutation(len(crashes))]          # random order (seed 42)
    decoys = decoy_windows(rng, S["first_batch_decoys"])
    batch1 = crashes[:S["first_batch_crash"]] + decoys
    batch1 = [batch1[k] for k in rng.permutation(len(batch1))]             # decoys hidden among the crashes
    items = [dict(it, batch=1) for it in batch1] + [dict(it, batch=2) for it in crashes[S["first_batch_crash"]:]]
    for k, it in enumerate(items, 1):
        it["name"] = f"w{k:03d}"                                           # anonymous name

    download(items)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(WORKERS) as pool:                 # several windows at once (one per CPU process)
        cut_items = []
        for k, it in enumerate(pool.map(cut, items), 1):
            cut_items.append(it)
            if k % 25 == 0 or k == len(items):
                print(f"  cut {k}/{len(items)}", flush=True)
    items = cut_items

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "set.json").write_text(json.dumps(items, indent=1))
    summary = {"windows": len(items), "batch1": len(batch1),
               "batch1_crash": sum(it["kind"] == "crash" for it in batch1),
               "batch1_decoys": sum(it["kind"] == "decoy" for it in batch1),
               "batch2_crash": sum(it["batch"] == 2 for it in items),
               "crash_windows_total": len(crashes), "settings": S}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "set_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"saved {DATA / 'set.json'}: {summary}")


if __name__ == "__main__":
    main()
