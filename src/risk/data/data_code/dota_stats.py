"""What DoTA's labels contain, counted over all 4,677 annotation files (this PC, free).

DoTA (Detection of Traffic Anomaly, Yao et al.): 4,677 dashcam clips from YouTube,
labelled at 10 frames per second. Per clip: whether our own camera car is involved
(ego_involve), the crash type, the frames where the anomaly starts and ends, and per
frame the boxes of the road users involved.

RUN IT (from the repo root, after downloading DoTA_annotations.zip to DOTA_META):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\dota_stats.py

Writes src/risk/data/dota_stats.json and prints a summary.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

DOTA_META = Path(r"C:\safe-distance-data\dota\meta")
OUT = Path(__file__).resolve().parents[1] / "dota_stats.json"
FPS = 10                                    # DoTA labels are at 10 frames per second


def main() -> None:
    files = sorted((DOTA_META / "annotations" / "annotations").glob("*.json"))
    meta = {**json.loads((DOTA_META / "metadata_train.json").read_text()),
            **json.loads((DOTA_META / "metadata_val.json").read_text())}
    s = {"clips": len(files), "in_metadata_train_or_val": 0, "ignored": 0, "ego": Counter(), "night": Counter(),
         "type_ego": Counter(), "type_other": Counter(), "object_categories": Counter(),
         "first_box_vs_anomaly_start_frames": Counter(), "clips_with_boxes": 0,
         "seconds_before_anomaly": [], "anomaly_seconds": [], "clip_seconds": []}
    example = None
    for f in files:
        a = json.loads(f.read_text())
        s["in_metadata_train_or_val"] += a["video_name"] in meta
        s["ignored"] += bool(a["ignore"])
        ego = "ego" if a["ego_involve"] else "other"
        s["ego"][ego] += 1
        s["night"][str(a["night"])] += 1
        s[f"type_{ego}"][a["accident_name"]] += 1
        s["seconds_before_anomaly"].append(a["anomaly_start"] / FPS)
        s["anomaly_seconds"].append((a["anomaly_end"] - a["anomaly_start"]) / FPS)
        s["clip_seconds"].append(a["num_frames"] / FPS)
        boxed = [fr for fr in a["labels"] if fr["objects"]]
        if boxed:
            s["clips_with_boxes"] += 1
            # Where do boxes begin, relative to the labelled anomaly start? (frames at 10 per second)
            s["first_box_vs_anomaly_start_frames"][boxed[0]["frame_id"] - a["anomaly_start"]] += 1
            for o in boxed[0]["objects"]:
                s["object_categories"][o.get("category", "?")] += 1
            if example is None:
                example = boxed[0]
    res = {k: (dict(v.most_common()) if isinstance(v, Counter) else v) for k, v in s.items()
           if not isinstance(v, list)}
    for k in ("seconds_before_anomaly", "anomaly_seconds", "clip_seconds"):
        v = sorted(s[k])
        res[k] = {"median": v[len(v) // 2], "p10": v[len(v) // 10], "p90": v[9 * len(v) // 10]}
    res["first_box_vs_anomaly_start_frames"] = dict(sorted(s["first_box_vs_anomaly_start_frames"].items())[:15])
    res["example_frame_with_boxes"] = example
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1)[:4000])


if __name__ == "__main__":
    main()
