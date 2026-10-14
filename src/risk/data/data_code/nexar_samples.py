"""20 random Nexar TRAIN crash clips with their labels drawn on, as ONE video (this PC, free).

Nexar labels per crash clip: time_of_event (the collision or near-collision) and
time_of_alert (the earliest moment a person could see it coming). Shown:
    time relative to the event, an "ALERT" banner from time_of_alert, a red frame at the event,
    a 1.5 s freeze at the alert and at the event.
Only the last SHOW_BEFORE_S seconds before the event (+ 1 s after) are shown, to keep it short.
Videos come from the Modal Volume (modal volume get: a file copy, no container, no cost).

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\nexar_samples.py

Output: C:\\Users\\mamou\\Downloads\\nexar_samples.mp4 (+ nexar_samples.json).
"""

from __future__ import annotations

import csv
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample_video import Writer, card, text  # noqa: E402

# ---- CONFIG ----
VOLUME = "safe-distance-data"
CACHE = Path(r"C:\safe-distance-data\nexar\samples")
OUT = Path.home() / "Downloads" / "nexar_samples.mp4"
N, SEED = 20, 11
SHOW_BEFORE_S = 8.0
SIZE, FPS = (1280, 720), 30.0
FREEZE_S, TITLE_S = 1.5, 1.5
# ----------------


def volume_get(remote: str, local: Path) -> Path:
    """Copy one file from the Modal Volume (account from MODAL_CONFIG_PATH)."""
    if not local.exists():
        local.parent.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, "MODAL_CONFIG_PATH": str(Path.home() / ".modal_session22.toml")}
        subprocess.run([sys.executable, "-m", "modal", "volume", "get", "--force", VOLUME, remote, str(local)],
                       check=True, env=env, capture_output=True)
    return local


def main() -> None:
    global OUT
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--min-lead", type=float, default=0.0, help="only clips whose alert is at least this many s before the event")
    a = ap.parse_args()
    OUT = a.out
    OUT.parent.mkdir(parents=True, exist_ok=True)
    meta = list(csv.DictReader(volume_get("nexar/train/positive/metadata.csv", CACHE / "metadata.csv").open()))
    meta = [r for r in meta if float(r["time_of_event"]) - float(r["time_of_alert"]) >= a.min_lead]
    print(f"{len(meta)} crash clips with the alert at least {a.min_lead} s before the event")
    picks = random.Random(a.seed).sample(meta, min(N, len(meta)))
    wr, shown = Writer(OUT, SIZE, FPS), []
    for k, r in enumerate(picks, 1):
        event, alert = float(r["time_of_event"]), float(r["time_of_alert"])
        path = volume_get(f"nexar/train/positive/{r['file_name']}", CACHE / r["file_name"])
        cap = cv2.VideoCapture(str(path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        wr.write(card(SIZE, [f"Nexar clip {k}/{N}   ({r['file_name']})",
                             f"alert {alert - event:+.1f} s before the event   {r['light_conditions']}, "
                             f"{r['weather']}, {r['scene']}"]), TITLE_S)
        f, frozen = 0, set()
        while True:
            ok, img = cap.read()
            if not ok:
                break
            t = f / fps
            f += 1
            if t < event - SHOW_BEFORE_S or t > event + 1.0:
                continue
            img = cv2.resize(img, SIZE)
            text(img, f"{t - event:+.1f} s {'before' if t < event else 'after'} event", (15, 40), 1.0)
            if alert <= t < event:
                text(img, "ALERT (labelled: danger visible)", (15, 85), 0.9, (0, 200, 255))
            if t >= event:
                cv2.rectangle(img, (0, 0), (SIZE[0] - 1, SIZE[1] - 1), (0, 0, 255), 10)
                text(img, "EVENT (labelled collision)", (15, 85), 0.9, (0, 0, 255))
            wr.write(img)
            for name, at in (("alert", alert), ("event", event)):
                if name not in frozen and t >= at:              # hold the first frame at the alert / event
                    frozen.add(name)
                    wr.write(img, FREEZE_S)
        cap.release()
        shown.append({"n": k, "clip": r["file_name"], "event_s": event, "alert_s": alert,
                      "alert_before_event_s": round(event - alert, 2)})
        print(f"[{k}/{N}] {r['file_name']}: alert {event - alert:.2f} s before the event", flush=True)
    wr.close()
    OUT.with_suffix(".json").write_text(json.dumps(shown, indent=1))
    lead = sorted(s["alert_before_event_s"] for s in shown)
    print(f"saved {OUT}; alert before event: median {lead[len(lead) // 2]} s, min {lead[0]}, max {lead[-1]}")


if __name__ == "__main__":
    main()
