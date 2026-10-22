"""Show, as ONE video, 15 training windows exactly as stage 1 gives them to the model.

Uses stage1_train.py's own code on local clips, not a copy of it:
    training_sources()  which moments of each clip a window may end on (the label rule, the 4 s safe gap, ...)
    TrainWindows        the random end point of every source for epoch 1, and its label
    __getitem__         reads the 16 frames and runs augment() (the same random draws as in training)
Frames come from frames.decode_frames(wide=True): 8 per second, 256 x 448, the same as the 16:9 cache.

The 15 windows: 6 crash windows (danger zone), 3 safe windows from crash clips (more than 4 s before the crash),
3 Nexar normal, 3 BDD100K clean normal. Each window is 16 frames = 2 s, played at its real speed (8 per second),
twice. Left: the cached frames. Right: the same window after augmentation = what the model gets.
(In real training only 15% of the windows are danger windows; here more are shown, to see them.)

RUN IT (from the repo root, this PC, CPU only, a few minutes):
    .venv\\Scripts\\python.exe scripts\\stage1_window_demo.py

Output: Downloads\\safe-distance-testing\\stage1_windows\\what_the_model_sees.mp4
"""

import csv
import json
import random
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src/risk/data/data_code"))
sys.path.insert(0, str(REPO / "src/risk"))
sys.path.insert(0, str(REPO / "src/risk/runs/stage1_lora"))
from frames import decode_frames  # noqa: E402            (the cache's own decoder)
from sample_video import Writer, card, text  # noqa: E402
import stage1_train as S  # noqa: E402                    (the training script itself)

# ---- CONFIG ----
NEXAR_POS = Path(r"C:\safe-distance-data\nexar\train\positive")   # local Nexar train crash clips + metadata.csv
NEXAR_NEG = Path(r"C:\safe-distance-data\nexar\train\negative")   # local Nexar train normal clips
BDD_DIR = Path(r"C:\safe-distance-data\bdd100k\samples")          # local BDD100K clips (only clean train ones used)
OUT = Path.home() / "Downloads" / "safe-distance-testing" / "stage1_windows" / "what_the_model_sees.mp4"
N_DANGER, N_SAFE, N_NEXAR_NORMAL, N_BDD = 6, 3, 3, 3
N_CRASH_CLIPS = 12                     # crash clips decoded (some have no danger or no safe window)
PICK_SEED = 7                          # which local clips are picked
SCALE = 2                              # each model pixel drawn as a 2 x 2 block (256 x 448 -> 512 x 896)
PLAYS = 2                              # each 2 s window is played this many times
BAR_H = 96                             # text bar above the pictures
# ----------------


def local_clips() -> tuple[list[dict], list[Path], list[Path]]:
    """Pick the local clips: crash rows (with alert / crash times), Nexar normal files, clean BDD100K files."""
    rnd = random.Random(PICK_SEED)
    excluded = set(json.loads(S.NEXAR_EXCLUDED.read_text())["clips"])
    rows = [r for r in csv.DictReader(open(NEXAR_POS / "metadata.csv"))
            if (NEXAR_POS / r["file_name"]).exists() and r["file_name"] not in excluded]
    clean = set(S.BDD_TRAIN_CLEAN.read_text().split())
    bdd = sorted(p for p in BDD_DIR.glob("*.mov") if p.stem in clean)
    return (rnd.sample(rows, N_CRASH_CLIPS), rnd.sample(sorted(NEXAR_NEG.glob("*.mp4")), N_NEXAR_NORMAL),
            rnd.sample(bdd, N_BDD))


def build_cache(tmp: Path, crash_rows, normal, bdd) -> None:
    """Decode the picked clips into a small local cache shaped like the real one, and point the script at it."""
    folders = {"crash": tmp / "nexar_train_positive", "normal": tmp / "nexar_train_negative",
               "bdd": tmp / "bdd100k_videos_100k_train"}
    for f in folders.values():
        f.mkdir()
    counts = {}
    jobs = ([(NEXAR_POS / r["file_name"], folders["crash"]) for r in crash_rows]
            + [(p, folders["normal"]) for p in normal] + [(p, folders["bdd"]) for p in bdd])
    for i, (video, folder) in enumerate(jobs, 1):
        frames, _ = decode_frames(str(video), wide=True)              # 8 per second, 256 x 448
        np.save(folder / f"{video.stem}.npy", frames)
        counts[f"{folder.name}/{video.stem}"] = len(frames)
        print(f"  decoded {i}/{len(jobs)}  {video.name}  {len(frames)} frames", flush=True)

    # point stage1_train at the local cache (the same names it uses on Modal)
    meta = tmp / "metadata.csv"
    with open(meta, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(crash_rows[0].keys()))
        wr.writeheader()
        wr.writerows(crash_rows)
    (tmp / "bdd_clean.txt").write_text("\n".join(p.stem for p in bdd))
    (tmp / "counts.json").write_text(json.dumps(counts))
    S.NEXAR_CRASH_META, S.NEXAR_CRASH_DIR = str(meta), str(folders["crash"])
    S.NEXAR_NORMAL_DIR, S.BDD_TRAIN_DIR = str(folders["normal"]), str(folders["bdd"])
    S.BDD_TRAIN_CLEAN, S.FRAME_COUNTS, S._COUNTS = tmp / "bdd_clean.txt", tmp / "counts.json", None


def describe(s, end: int, label: float) -> list[str]:
    """Two text lines for a window: what it is, and its timing and label."""
    t0, t1 = (end - S.WINDOW_FRAMES) / S.FPS, end / S.FPS
    kind = {"crash_danger": "CRASH CLIP, danger window", "crash_safe": "CRASH CLIP, safe window (early part)",
            "nexar_normal": "NEXAR NORMAL clip", "bdd_normal": "BDD100K NORMAL clip (clean)"}[s.kind]
    line2 = f"window {t0:.2f} - {t1:.2f} s of the clip   label {label:.2f}"
    if s.alert is not None:
        line2 += f"   (alert {s.alert:.2f} s, crash {s.event:.2f} s: window ends {s.event - t1:.2f} s before the crash)"
    return [f"{kind}   clip {s.clip}", line2]


def main() -> None:
    crash_rows, normal, bdd = local_clips()
    with tempfile.TemporaryDirectory() as td:
        build_cache(Path(td), crash_rows, normal, bdd)
        sources = S.training_sources()                             # the script's own rules
        data = S.TrainWindows(sources, S.SEED)                     # epoch 1: one random end point per source
        want = {"crash_danger": N_DANGER, "crash_safe": N_SAFE, "nexar_normal": N_NEXAR_NORMAL, "bdd_normal": N_BDD}
        picked = []
        for kind, n in want.items():
            picked += [i for i, s in enumerate(sources) if s.kind == kind][:n]

        w, h = S.FRAME_W * SCALE, S.FRAME_H * SCALE
        size = (2 * w + 20, h + BAR_H + 40)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        vid = Writer(OUT, size, float(S.FPS))                      # 8 frames per second = the model's own rate
        vid.write(card(size, ["What stage 1 training gives the model",
                              f"{len(picked)} windows, each 16 frames = 2 s at 8 frames per second, 256 x 448",
                              "left: cached frames      right: after augmentation (what the model gets)",
                              "each window plays twice at real speed"]), seconds=4)
        for n, i in enumerate(picked, 1):
            s, end = sources[i], int(data.plan[i])
            raw = np.load(s.path)[end - S.WINDOW_FRAMES:end]       # the cached 16 frames
            aug = data[i][0].numpy()                               # the same window through __getitem__ + augment
            lines = [f"{n}/{len(picked)}   " + describe(s, end, float(data.labels[i]))[0],
                     describe(s, end, float(data.labels[i]))[1]]
            print(f"  window {n}: {lines[0]} | {lines[1]}", flush=True)
            for _ in range(PLAYS):
                for k in range(S.WINDOW_FRAMES):
                    img = np.zeros((size[1], size[0], 3), np.uint8)
                    for x0, fr, name in ((0, raw[k], "cached"), (w + 20, aug[k], "model input (augmented)")):
                        big = cv2.resize(cv2.cvtColor(fr, cv2.COLOR_RGB2BGR), (w, h), interpolation=cv2.INTER_NEAREST)
                        img[BAR_H + 30:BAR_H + 30 + h, x0:x0 + w] = big
                        text(img, name, (x0 + 8, BAR_H + 22), 0.7)
                    text(img, lines[0], (12, 34), 0.8)
                    text(img, lines[1] + f"   frame {k + 1}/16", (12, 72), 0.65)
                    vid.write(img)
        vid.close()
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
