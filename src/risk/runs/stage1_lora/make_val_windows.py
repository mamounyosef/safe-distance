"""Build the FIXED validation windows that stage 1 scores after every epoch (this PC, free, seconds).

Every epoch the training script scores the same 2,202 windows (2 s of video each, 2 per clip), so epochs are
comparable:

    Nexar Public crash clips   334 x 2  windows ending at the clip's LAST frame (0.5 / 1.0 / 1.5 s before the
                                        crash: Nexar's own test moment, the "group") and 0.5 s earlier   label 1
    Nexar Public normal clips  333 x 2  the same two moments (last frame, 0.5 s earlier)                  label 0
    BDD100K val, cleaned       434 x 2  the 2 moments plain BADAS-Open found MOST risky in that clip, at least
                                        2 s apart ("hard moments": where false beeps come from)          label 0

Nexar's official mAP is computed on the last-frame windows only (window "rank" 1), like the baseline's 0.903.

Inputs:  C:/safe-distance-data/nexar/meta/solution.csv            (Nexar's test labels: id, target, Usage, group)
         src/risk/data/bdd100k_ids/val_clean.txt                  (the 434 clean val clips)
         src/risk/runs/baseline_badas_open/results/eval/series_bdd_val.json   (plain BADAS readings, every 0.5 s)
Output:  src/risk/runs/stage1_lora/val_windows.json  (NOT in git: it holds Nexar's test labels; it is shipped to
         Modal with the code)

RUN IT (from the repo root, before launching training):
    .venv\\Scripts\\python.exe src\\risk\\runs\\stage1_lora\\make_val_windows.py
"""

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RISK = HERE.parents[1]                                            # src/risk

# ---- CONFIG ----
SOLUTION = Path(r"C:\safe-distance-data\nexar\meta\solution.csv")
VAL_CLEAN = RISK / "data/bdd100k_ids/val_clean.txt"
BDD_SERIES = RISK / "runs/baseline_badas_open/results/eval/series_bdd_val.json"
OUT = HERE / "val_windows.json"
FPS = 8                                                           # cached frames per second
NEXAR_BACK_FRAMES = [0, 4]                                        # windows end at the last frame and 0.5 s earlier
BDD_MIN_GAP_S = 2.0                                               # the 2 BDD moments must not share video
# ----------------


def main() -> None:
    windows = []

    # 1) Nexar Public: windows ending at the last frame and 0.5 s earlier. "end_back" = frames before the last
    #    frame (the clip length is only known on Modal, where the frames are).
    for r in csv.DictReader(SOLUTION.open()):
        if r["Usage"] != "Public":
            continue                                              # Private stays untouched for the final score
        crash = r["target"] == "1"
        for rank, back in enumerate(NEXAR_BACK_FRAMES, 1):
            windows.append({"group": "nexar_crash" if crash else "nexar_normal",
                            "folder": f"nexar_test-public_{'positive' if crash else 'negative'}",
                            "clip": r["id"], "end": None, "end_back": back, "rank": rank,
                            "label": 1.0 if crash else 0.0,
                            "nexar_group": int(r["group"])})      # 0/1/2 = 0.5 / 1.0 / 1.5 s before the crash

    # 2) BDD100K val (cleaned): the 2 riskiest readings of plain BADAS, at least BDD_MIN_GAP_S apart
    series = json.loads(BDD_SERIES.read_text())
    for clip in VAL_CLEAN.read_text().split():
        by_risk = sorted(series[clip], key=lambda r: -r[1])        # readings are (window end time s, risk)
        picked = [by_risk[0][0]]
        picked += [next(t for t, _ in by_risk if abs(t - picked[0]) >= BDD_MIN_GAP_S)]
        for rank, t in enumerate(picked, 1):
            windows.append({"group": "bdd_hard", "folder": "bdd100k_videos_100k_val", "clip": clip,
                            "end": int(round(t * FPS)), "end_back": None, "rank": rank, "label": 0.0,
                            "nexar_group": None})

    OUT.write_text(json.dumps(windows, indent=1))
    print(f"saved {OUT}: {len(windows)} windows {dict(Counter(w['group'] for w in windows))}")


if __name__ == "__main__":
    main()
