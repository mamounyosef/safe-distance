# KITTI tracking benchmark: `yolo26s-seg_bytetrack`

Generated automatically from `results.json` by `benchmark_kitti_tracking.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.05 |
| Tracker | bytetrack (track_high_thresh=0.25, track_low_thresh=0.05, new_track_thresh=0.25, track_buffer=30, match_thresh=0.8) |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (the only split with public labels) |
| Sequences / frames | 21 / 8008 at 10 fps |
| Match rule | IoU >= 0.5; objects and boxes under 25 px ignored |
| Ignored labels | Car: Van; Pedestrian: Cyclist, Person |
| Scoring | py-motmetrics 1.4.0 |
| Hardware | NVIDIA GeForce RTX 4060, FP16 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `4a31b54` (with uncommitted changes) |
| Created (UTC) | 2026-09-24T12:39:42+00:00 |

## Metrics

- **IDF1**: how consistently each real object keeps one ID over its whole life. Best single number.
- **MOTA**: 1 minus (misses + false alarms + ID switches) / real objects. Can be negative.
- **ID switches**: times a tracked object's ID wrongly changed. Lower is better.
- **Mostly tracked / lost**: share of real objects followed for at least 80% / at most 20% of their life.
- **Latency**: detection plus tracking per frame; p95 is the slowest 5%.

## Overall

| Class | IDF1 | MOTA | ID switches | Recall | Precision | Mostly tracked | Mostly lost | Unique objects | Object-frames |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Car | 77.0% | 64.8% | 301 | 77.1% | 87.5% | 52% | 10% | 561 | 22707 |
| Pedestrian | 63.9% | 49.9% | 250 | 68.0% | 81.0% | 35% | 15% | 167 | 11430 |

## Per sequence: Car

| Sequence | Frames | IDF1 | MOTA | ID switches | Unique objects |
| --- | --- | --- | --- | --- | --- |
| 0000 | 154 | 56.3% | 30.9% | 9 | 9 |
| 0001 | 447 | 70.7% | 49.7% | 49 | 88 |
| 0002 | 233 | 82.3% | 74.8% | 5 | 11 |
| 0003 | 144 | 93.6% | 89.9% | 1 | 8 |
| 0004 | 314 | 84.1% | 78.6% | 33 | 25 |
| 0005 | 297 | 85.9% | 80.2% | 28 | 33 |
| 0006 | 270 | 74.2% | 60.1% | 3 | 11 |
| 0007 | 800 | 83.9% | 72.1% | 39 | 53 |
| 0008 | 390 | 90.0% | 86.9% | 15 | 20 |
| 0009 | 803 | 71.7% | 54.2% | 23 | 76 |
| 0010 | 294 | 94.0% | 90.7% | 7 | 13 |
| 0011 | 373 | 74.2% | 58.7% | 26 | 50 |
| 0012 | 78 | 90.6% | 82.9% | 0 | 2 |
| 0013 | 340 | 43.0% | 13.5% | 0 | 2 |
| 0014 | 106 | 72.0% | 53.2% | 4 | 12 |
| 0015 | 376 | 92.0% | 86.6% | 4 | 9 |
| 0016 | 209 | 29.2% | 13.3% | 14 | 4 |
| 0017 | 145 | - | - | 0 | 0 |
| 0018 | 339 | 90.2% | 85.3% | 10 | 18 |
| 0019 | 1059 | 64.0% | 63.6% | 6 | 7 |
| 0020 | 837 | 81.2% | 69.5% | 25 | 110 |

## Per sequence: Pedestrian

| Sequence | Frames | IDF1 | MOTA | ID switches | Unique objects |
| --- | --- | --- | --- | --- | --- |
| 0000 | 154 | 35.7% | 18.2% | 0 | 2 |
| 0001 | 447 | 35.6% | 21.4% | 5 | 3 |
| 0002 | 233 | 88.8% | 78.4% | 0 | 1 |
| 0003 | 144 | - | - | 0 | 0 |
| 0004 | 314 | 12.2% | 4.6% | 4 | 5 |
| 0005 | 297 | - | - | 0 | 0 |
| 0006 | 270 | - | - | 0 | 0 |
| 0007 | 800 | 46.4% | 19.4% | 4 | 2 |
| 0008 | 390 | 0.0% | -inf% | 0 | 0 |
| 0009 | 803 | 0.0% | -17.2% | 0 | 1 |
| 0010 | 294 | 0.0% | 0.0% | 0 | 2 |
| 0011 | 373 | 50.7% | 34.3% | 4 | 5 |
| 0012 | 78 | 0.0% | 0.0% | 0 | 1 |
| 0013 | 340 | 70.9% | 57.2% | 57 | 42 |
| 0014 | 106 | 11.7% | -11.5% | 3 | 2 |
| 0015 | 376 | 61.0% | 39.5% | 23 | 11 |
| 0016 | 209 | 76.3% | 59.4% | 24 | 19 |
| 0017 | 145 | 77.8% | 72.6% | 11 | 9 |
| 0018 | 339 | 0.0% | -inf% | 0 | 0 |
| 0019 | 1059 | 59.7% | 48.4% | 115 | 62 |
| 0020 | 837 | - | - | 0 | 0 |

## Latency

| Median (ms) | p95 (ms) |
| --- | --- |
| 23.3 | 32.9 |

## Known limitations

- Not the official KITTI devkit: same classes, IoU and height rules, scored with py-motmetrics.
- Pedestrian also ignores Cyclist labels (see Setup), which is more lenient than the official rules.
- The detector was not trained on KITTI; tracking quality is bounded by detection quality.
- Daytime only, Karlsruhe, 2011.
