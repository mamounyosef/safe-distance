"""List the night scenes in a nuScenes metadata folder.

Run: python scripts/nuscenes_night_scenes.py
"""

import json
from collections import Counter
from pathlib import Path

# ---- CONFIG ----
META_DIR = Path(r"C:\safe-distance-data\nuscenes-trainval\v1.0-trainval")
# ----------------


def load(name):
    return json.loads((META_DIR / f"{name}.json").read_text(encoding="utf-8"))


def main():
    scenes = load("scene")
    logs = {log["token"]: log for log in load("log")}
    night = [s for s in scenes if "night" in s["description"].lower()]
    print(f"scenes: {len(scenes)}, night scenes: {len(night)}, "
          f"night keyframes: {sum(s['nbr_samples'] for s in night)}")
    places = Counter(logs[s["log_token"]]["location"] for s in night)
    print("night scenes per location:", dict(places))
    for s in night:
        log = logs[s["log_token"]]
        print(f"{s['name']}  {log['logfile']}  {s['nbr_samples']:3d} frames  {s['description']}")


if __name__ == "__main__":
    main()
