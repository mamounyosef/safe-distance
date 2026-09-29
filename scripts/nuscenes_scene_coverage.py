"""Count which nuScenes scenes (night and day) have front-camera keyframes on disk.

Uses only the small tables (scene, log, sample): each image file name holds its log
name and timestamp, so it is matched to the scene whose time range contains it.

Run: python scripts/nuscenes_scene_coverage.py
"""

import json
from collections import defaultdict
from pathlib import Path

# ---- CONFIG ----
ROOT = Path(r"C:\safe-distance-data\nuscenes-trainval")
META_DIR = ROOT / "v1.0-trainval"
IMAGE_DIR = ROOT / "samples" / "CAM_FRONT"
MARGIN_US = 500_000   # half a second either side of a scene's first/last keyframe
# ----------------


def load(name):
    return json.loads((META_DIR / f"{name}.json").read_text(encoding="utf-8"))


def main():
    scenes = {s["token"]: s for s in load("scene")}
    logs = {log["token"]: log["logfile"] for log in load("log")}
    times = defaultdict(list)
    for sample in load("sample"):
        times[sample["scene_token"]].append(sample["timestamp"])
    ranges = defaultdict(list)   # logfile -> [(start, end, scene)]
    for token, scene in scenes.items():
        ranges[logs[scene["log_token"]]].append(
            (min(times[token]) - MARGIN_US, max(times[token]) + MARGIN_US, scene))

    found = defaultdict(int)
    unmatched = 0
    for path in IMAGE_DIR.glob("*.jpg"):
        logfile, _, stamp = path.stem.split("__")
        stamp = int(stamp)
        hit = next((s for a, b, s in ranges.get(logfile, []) if a <= stamp <= b), None)
        if hit is None:
            unmatched += 1
        else:
            found[hit["name"]] += 1

    night = {n: c for n, c in found.items()
             if "night" in next(s for s in scenes.values() if s["name"] == n)["description"].lower()}
    print(f"images: {sum(found.values()) + unmatched}, unmatched: {unmatched}")
    print(f"scenes on disk: {len(found)}, of which night: {len(night)} "
          f"({sum(night.values())} night images)")
    for name in sorted(night):
        print(f"  {name}: {night[name]} images")
    # Hypothesis: the 10 download parts split scene.json in order, 85 scenes each.
    order = [s["name"] for s in load("scene")]
    first_85 = set(order[:85])
    print(f"on-disk scenes == first 85 of scene.json: {set(found) == first_85}")
    for part in range(10):
        chunk = [scenes_by_name for scenes_by_name in order[part * 85:(part + 1) * 85]]
        n_night = sum("night" in next(s for s in scenes.values() if s["name"] == n)["description"].lower()
                      for n in chunk)
        print(f"  part {part + 1:02d}: {chunk[0]} .. {chunk[-1]}, night scenes: {n_night}")
    names = sorted(found)
    print(f"scene names on disk: {names[0]} .. {names[-1]}")
    print("  " + " ".join(n.split("-")[1] for n in names))


if __name__ == "__main__":
    main()
