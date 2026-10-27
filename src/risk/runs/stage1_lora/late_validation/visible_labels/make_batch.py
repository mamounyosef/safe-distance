"""Add one more labelling batch to set.json under the one-window-per-clip policy (last frame only).

Batch 3: random last-frame crash windows of kinds A (clip stops 0.5 s before the crash), B (1.0 s) and C (1.5 s),
plus decoys (Nexar Public normal clips, last frame), shuffled, with new anonymous names (w208, ...). Windows already
in set.json are never picked again (C windows of batch 2 that are not yet labelled can be). Frames and clips are cut
exactly like make_set.py (the 16 frames the model saw, 960 x 540; the page clip at 8 fps).

RUN IT (from the repo root):
    python src\\risk\\runs\\stage1_lora\\late_validation\\visible_labels\\make_batch.py [--batch 3] [--a 12] [--b 12] [--c 16] [--decoys 10] [--seed 43]
"""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import make_set as M                                    # same folder: the cut, paths and settings

GROUP_OF = {"a": 0, "b": 1, "c": 2}                     # kind -> Nexar test group


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=3)
    ap.add_argument("--a", type=int, default=12)
    ap.add_argument("--b", type=int, default=12)
    ap.add_argument("--c", type=int, default=16)
    ap.add_argument("--decoys", type=int, default=10)
    ap.add_argument("--seed", type=int, default=43)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    items = json.loads((M.DATA / "set.json").read_text())
    if any(it["batch"] == a.batch for it in items):
        raise SystemExit(f"batch {a.batch} already exists in set.json")
    labelled = set(json.loads((M.DATA / "human_labels.json").read_text())) if (M.DATA / "human_labels.json").exists() else set()
    taken = {(it["clip"], it["end_back"]) for it in items if it["batch"] != 2 or it["name"] in labelled}
    used_clips = {it["clip"] for it in items if it["batch"] != 2 or it["name"] in labelled}

    wins = json.loads((M.LV / "windows.json").read_text())
    new = []
    for kind, n in (("a", a.a), ("b", a.b), ("c", a.c)):
        g = GROUP_OF[kind]
        pool = sorted({w["clip"] for w in wins if w["group"] == "nexar_crash" and w["nexar_group"] == g
                       and (w["clip"], 0) not in taken})
        for k in rng.choice(len(pool), size=n, replace=False):
            new.append({"kind": "crash", "clip": pool[k], "folder": "positive", "nexar_group": g, "end_back": 0,
                        "before_crash_s": M.GROUP_S[g]})
    pool = sorted({w["clip"] for w in wins if w["group"] == "nexar_normal" and w["clip"] not in used_clips})
    for k in rng.choice(len(pool), size=a.decoys, replace=False):
        c = pool[k]
        g = next(w["nexar_group"] for w in wins if w["clip"] == c)
        new.append({"kind": "decoy", "clip": c, "folder": "negative", "nexar_group": g, "end_back": 0,
                    "before_crash_s": None})
    new = [new[k] for k in rng.permutation(len(new))]                # crashes and decoys mixed
    start = len(items) + 1
    for k, it in enumerate(new):
        it.update(batch=a.batch, name=f"w{start + k:03d}", policy="last_frame")

    M.download(new)
    with ProcessPoolExecutor(M.WORKERS) as pool_ex:
        new = list(pool_ex.map(M.cut, new))
    items += new
    (M.DATA / "set.json").write_text(json.dumps(items, indent=1))
    summary = json.loads((M.HERE / "results" / "set_summary.json").read_text())
    summary[f"batch{a.batch}"] = {"windows": len(new), "a": a.a, "b": a.b, "c": a.c, "decoys": a.decoys,
                                  "seed": a.seed, "policy": "one window per clip, last frame"}
    (M.HERE / "results" / "set_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"batch {a.batch}: {len(new)} windows ({new[0]['name']} to {new[-1]['name']}) added to set.json")


if __name__ == "__main__":
    main()
