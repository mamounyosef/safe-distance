"""Cut the full nuScenes metadata down to a few scenes, as a small table folder.

The full tables are 2.5 GB (sample_data.json alone 1.3 GB), too big to load while
other work holds the RAM. They are read with a streaming parser (ijson), one record
at a time, and only the records of the chosen scenes are kept. The output folder has
the same layout as v1.0-mini, so the benchmark reads it unchanged.

Chosen scenes: night scenes whose front-camera keyframes are all on disk, minus the
ones already used in nuScenes mini (so the test is on never-seen scenes).

Run: python scripts/nuscenes_subset_tables.py
"""

import json
from pathlib import Path

import ijson

# ---- CONFIG ----
ROOT = Path(r"C:\safe-distance-data\nuscenes-trainval")
SOURCE = ROOT / "v1.0-trainval"
TARGET = ROOT / "v1.0-night"
CAMERA = "CAM_FRONT"
EXCLUDE_SCENES = {"scene-1077", "scene-1094", "scene-1100"}   # the nuScenes mini night scenes
SMALL_TABLES = ["attribute", "category", "sensor", "visibility", "calibrated_sensor", "log", "map"]
# ----------------


def load(name):
    return json.loads((SOURCE / f"{name}.json").read_text(encoding="utf-8"))


def stream(name):
    with open(SOURCE / f"{name}.json", "rb") as f:
        yield from ijson.items(f, "item", use_float=True)


def save(name, rows):
    (TARGET / f"{name}.json").write_text(json.dumps(rows), encoding="utf-8")
    print(f"  {name}: {len(rows)} records")


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    scenes = [s for s in load("scene")
              if "night" in s["description"].lower() and s["name"] not in EXCLUDE_SCENES]
    samples = load("sample")
    scene_tokens = {s["token"] for s in scenes}
    sample_tokens = {s["token"] for s in samples if s["scene_token"] in scene_tokens}

    print("streaming sample_data (1.3 GB)...", flush=True)
    frames = [d for d in stream("sample_data")
              if d["sample_token"] in sample_tokens and d["is_key_frame"]
              and d["filename"].startswith(f"samples/{CAMERA}/")]

    # Keep only scenes whose every keyframe image is on disk.
    missing_scenes = set()
    scene_of = {s["token"]: s["scene_token"] for s in samples if s["token"] in sample_tokens}
    for d in frames:
        if not (ROOT / d["filename"]).exists():
            missing_scenes.add(scene_of[d["sample_token"]])
    scenes = [s for s in scenes if s["token"] not in missing_scenes]
    scene_tokens = {s["token"] for s in scenes}
    sample_tokens = {t for t, sc in scene_of.items() if sc in scene_tokens}
    frames = [d for d in frames if d["sample_token"] in sample_tokens]
    print(f"night scenes kept: {len(scenes)} (dropped {len(missing_scenes)} with images missing), "
          f"frames: {len(frames)}", flush=True)

    print("streaming ego_pose (0.6 GB)...", flush=True)
    pose_tokens = {d["ego_pose_token"] for d in frames}
    poses = [p for p in stream("ego_pose") if p["token"] in pose_tokens]

    print("streaming sample_annotation (0.6 GB)...", flush=True)
    annotations = [a for a in stream("sample_annotation") if a["sample_token"] in sample_tokens]
    instance_tokens = {a["instance_token"] for a in annotations}
    instances = [i for i in load("instance") if i["token"] in instance_tokens]

    print(f"writing {TARGET}", flush=True)
    save("scene", scenes)
    save("sample", [s for s in samples if s["token"] in sample_tokens])
    save("sample_data", frames)
    save("ego_pose", poses)
    save("sample_annotation", annotations)
    save("instance", instances)
    for name in SMALL_TABLES:
        save(name, load(name))
    print("scenes:", " ".join(sorted(s["name"].split("-")[1] for s in scenes)))


if __name__ == "__main__":
    main()
