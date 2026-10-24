"""One review video of late-validation windows, to see by eye what the model gets wrong (this PC, no GPU).

Part A  FALSE ALARMS: every Nexar normal validation clip with a window above the threshold (no crash follows).
Part B  CRASHES 1.5 s BEFORE: crash windows ending 1.5 s before the crash, a seeded random sample of MISSED ones
        (risk below the threshold) and, for contrast, of CAUGHT ones (above it).

Each clip plays at real speed from its first to its last frame. A bar at the bottom shows the whole clip; the 2 s
window the model scored is drawn on it and outlined on the frame while it plays. Labels: the model's risk on that
window, the case, and (crash clips) when the crash happens after the clip ends.
Clips come from the Modal data volume (nexar/test-public) and are kept in C:/safe-distance-data/nexar/test-public
(a re-run downloads nothing twice). These are VALIDATION clips: for understanding only, never for training.

RUN IT (from the repo root; MODAL_CONFIG_PATH = a workspace whose data volume has Nexar):
    python scripts\\late_val_review_video.py [--step 1000] [--threshold 0.9] [--missed 10] [--caught 4]
Output: Downloads\\safe-distance-testing\\late_validation\\review_step<N>.mp4 and review_step<N>.json (the list)
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[1]
LV = REPO / "src/risk/runs/stage1_lora/late_validation"
LOCAL = Path(r"C:\safe-distance-data\nexar\test-public")
OUT_DIR = Path.home() / "Downloads" / "safe-distance-testing" / "late_validation"
FPS_CACHE = 8                                    # the cache (and the window ends) run at 8 frames per second
WINDOW_S = 2.0                                   # each window = 2 s of video
GROUP_S = {0: 0.5, 1: 1.0, 2: 1.5}               # Nexar test group -> clip stops this long before the crash
OUT_W, OUT_H = 960, 540                          # output frame size
SEED = 42


def pick(step: int, thr: float, n_missed: int, n_caught: int) -> list[dict]:
    """The clips to show, with the window(s) to mark and their risk."""
    windows = json.loads((LV / "windows.json").read_text())
    p = np.load(LV / f"results/predictions/step{step}.npz", allow_pickle=True)
    risk = 1.0 / (1.0 + np.exp(-p["logits"]))
    ids = [str(i) for i in p["ids"]]
    assert len(ids) == len(windows)
    rows = []
    for w, i, r in zip(windows, ids, risk):
        end = int(i.split("|")[2])                                    # the window's end frame (8 fps)
        rows.append({**{k: w[k] for k in ("group", "clip", "rank", "nexar_group")}, "end": end, "risk": float(r)})

    # A: every Nexar normal clip with a window above thr (all its windows shown, the risky ones in red)
    alarm_clips = sorted({r["clip"] for r in rows if r["group"] == "nexar_normal" and r["risk"] > thr})
    part_a = [{"part": "A", "clip": c, "folder": "negative", "crash_after_s": None,
               "windows": [r for r in rows if r["group"] == "nexar_normal" and r["clip"] == c]} for c in alarm_clips]
    part_a.sort(key=lambda x: -max(w["risk"] for w in x["windows"]))

    # B: crash windows that end 1.5 s before the crash (group 1 window 2, group 2 window 1)
    late = [r for r in rows if r["group"] == "nexar_crash"
            and GROUP_S[r["nexar_group"]] + (0.5 if r["rank"] == 2 else 0.0) == 1.5]
    rng = np.random.default_rng(SEED)
    missed = [r for r in late if r["risk"] <= thr]
    caught = [r for r in late if r["risk"] > thr]
    part_b = []
    for kind, pool, n in (("missed", missed, n_missed), ("caught", caught, n_caught)):
        for k in rng.choice(len(pool), size=min(n, len(pool)), replace=False):
            r = pool[k]
            part_b.append({"part": "B", "kind": kind, "clip": r["clip"], "folder": "positive",
                           "crash_after_s": GROUP_S[r["nexar_group"]], "windows": [r]})
    print(f"A: {len(part_a)} Nexar normal clips with a window above {thr}")
    print(f"B: 1.5 s crash windows: {len(missed)} missed, {len(caught)} caught; showing {n_missed} + {n_caught}")
    return part_a + part_b


def download(items: list[dict]) -> None:
    """Fetch the clips not yet on this PC from the Modal data volume."""
    need = [(it["folder"], it["clip"]) for it in items if not (LOCAL / it["folder"] / f"{it['clip']}.mp4").exists()]
    if not need:
        return
    import modal
    vol = modal.Volume.from_name("safe-distance-data")
    for folder, clip in dict.fromkeys(need):
        dst = LOCAL / folder / f"{clip}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in vol.read_file(f"nexar/test-public/{folder}/{clip}.mp4"):
                f.write(chunk)
        tmp.replace(dst)                                              # complete files only
        print(f"  downloaded {folder}/{clip}.mp4 ({dst.stat().st_size / 1e6:.1f} MB)")


def put(img, text, y, color=(255, 255, 255), scale=0.7):
    """Text with a dark outline (readable on any background)."""
    cv2.putText(img, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)


def render(items: list[dict], thr: float, out: Path) -> None:
    """Write all clips into one video."""
    writer = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), 30, (OUT_W, OUT_H))
    for n, it in enumerate(items, 1):
        cap = cv2.VideoCapture(str(LOCAL / it["folder"] / f"{it['clip']}.mp4"))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frames = []
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            frames.append(cv2.resize(fr, (OUT_W, OUT_H)))
        cap.release()
        dur = len(frames) / fps                                       # clip length in seconds
        if it["part"] == "A":
            head = f"A  FALSE ALARM?  Nexar NORMAL clip {it['clip']}  (no crash follows)"
        else:
            head = (f"B  {it['kind'].upper()}  Nexar CRASH clip {it['clip']}  (window ends 1.5 s before the crash)")

        # title card: 1.5 s
        card = np.zeros((OUT_H, OUT_W, 3), np.uint8)
        put(card, f"{n}/{len(items)}", 60, scale=1.0)
        put(card, head, 120, scale=0.65)
        for k, w in enumerate(it["windows"]):
            t1 = w["end"] / FPS_CACHE
            put(card, f"window {k + 1}: {t1 - WINDOW_S:.1f} s to {t1:.1f} s of the clip, risk {w['risk']:.3f}",
                170 + 35 * k, (80, 80, 255) if w["risk"] > thr else (120, 255, 120), 0.65)
        if it["crash_after_s"] is not None:
            put(card, f"the clip stops {it['crash_after_s']} s before the crash (the crash is NOT in the video)",
                170 + 35 * len(it["windows"]), (0, 200, 255), 0.6)
        for _ in range(45):
            writer.write(card)

        for i, fr in enumerate(frames):
            t = i / fps
            img = fr.copy()
            inside = [w for w in it["windows"] if w["end"] / FPS_CACHE - WINDOW_S <= t < w["end"] / FPS_CACHE]
            for w in inside:                                          # outline: this frame is inside a scored window
                col = (0, 0, 255) if w["risk"] > thr else (0, 220, 0)
                cv2.rectangle(img, (2, 2), (OUT_W - 3, OUT_H - 3), col, 6)
            put(img, head, 30, scale=0.55)
            put(img, f"t = {t:4.1f} s of {dur:.1f} s", 60, scale=0.6)
            if inside:
                put(img, f"IN THE WINDOW: risk {max(w['risk'] for w in inside):.3f}", 90,
                    (80, 80, 255) if max(w["risk"] for w in inside) > thr else (120, 255, 120))
            # timeline bar: the clip, its scored windows, the playhead
            y0, y1, x0, x1 = OUT_H - 34, OUT_H - 14, 14, OUT_W - 14
            cv2.rectangle(img, (x0, y0), (x1, y1), (60, 60, 60), -1)
            for w in it["windows"]:
                a = x0 + int((x1 - x0) * max(w["end"] / FPS_CACHE - WINDOW_S, 0) / dur)
                b = x0 + int((x1 - x0) * min(w["end"] / FPS_CACHE, dur) / dur)
                cv2.rectangle(img, (a, y0), (b, y1), (0, 0, 255) if w["risk"] > thr else (0, 200, 0), -1)
            px = x0 + int((x1 - x0) * t / dur)
            cv2.line(img, (px, y0 - 6), (px, y1 + 6), (255, 255, 255), 2)
            writer.write(cv2.resize(img, (OUT_W, OUT_H)) if fps == 30 else img)
            if abs(fps - 30) > 1 and i + 1 < len(frames):            # keep real speed for non-30 fps clips
                for _ in range(int(round(30 / fps)) - 1):
                    writer.write(img)
    writer.release()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=1000)
    ap.add_argument("--threshold", type=float, default=0.9)
    ap.add_argument("--missed", type=int, default=10)
    ap.add_argument("--caught", type=int, default=4)
    a = ap.parse_args()
    items = pick(a.step, a.threshold, a.missed, a.caught)
    download(items)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"review_step{a.step}.mp4"
    render(items, a.threshold, out)
    (OUT_DIR / f"review_step{a.step}.json").write_text(json.dumps(items, indent=1))
    print(f"saved {out} ({len(items)} clips)")


if __name__ == "__main__":
    main()
