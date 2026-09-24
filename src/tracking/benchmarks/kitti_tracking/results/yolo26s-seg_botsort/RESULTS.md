# KITTI tracking benchmark: `yolo26s-seg_botsort`

Generated automatically from `results.json` by `benchmark_kitti_tracking.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.05 |
| Tracker | botsort (track_high_thresh=0.25, track_low_thresh=0.05, new_track_thresh=0.25, track_buffer=30, match_thresh=0.8) |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (the only split with public labels) |
| Sequences / frames | 21 / 8008 at 10 fps |
| Match rule | IoU >= 0.5; objects and boxes under 25 px ignored |
| Ignored labels | Car: Van; Pedestrian: Cyclist, Person |
| Scoring | py-motmetrics 1.4.0 |
| Hardware | NVIDIA GeForce RTX 4060, FP16 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `4a31b54` (with uncommitted changes) |
| Created (UTC) | 2026-09-24T12:45:13+00:00 |

## Metrics

- **IDF1**: how consistently each real object keeps one ID over its whole life. Best single number.
- **MOTA**: 1 minus (misses + false alarms + ID switches) / real objects. Can be negative.
- **ID switches**: times a tracked object's ID wrongly changed. Lower is better.
- **Mostly tracked / lost**: share of real objects followed for at least 80% / at most 20% of their life.
- **Latency**: detection plus tracking per frame; p95 is the slowest 5%.

## Overall

| Class | IDF1 | MOTA | ID switches | Recall | Precision | Mostly tracked | Mostly lost | Unique objects | Object-frames |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Car | 79.5% | 72.0% | 228 | 82.0% | 90.1% | 62% | 5% | 561 | 22707 |
| Pedestrian | 66.3% | 50.8% | 188 | 71.5% | 78.9% | 44% | 8% | 167 | 11430 |

## Per sequence: Car

| Sequence | Frames | IDF1 | MOTA | ID switches | Unique objects |
| --- | --- | --- | --- | --- | --- |
| 0000 | 154 | 70.2% | 37.5% | 1 | 9 |
| 0001 | 447 | 81.2% | 68.9% | 22 | 88 |
| 0002 | 233 | 80.3% | 76.8% | 6 | 11 |
| 0003 | 144 | 92.7% | 90.2% | 3 | 8 |
| 0004 | 314 | 92.0% | 87.2% | 7 | 25 |
| 0005 | 297 | 89.4% | 82.4% | 8 | 33 |
| 0006 | 270 | 77.9% | 72.2% | 7 | 11 |
| 0007 | 800 | 87.5% | 81.2% | 34 | 53 |
| 0008 | 390 | 84.7% | 90.5% | 10 | 20 |
| 0009 | 803 | 77.8% | 63.1% | 25 | 76 |
| 0010 | 294 | 95.7% | 92.5% | 2 | 13 |
| 0011 | 373 | 74.1% | 63.9% | 26 | 50 |
| 0012 | 78 | 90.6% | 82.9% | 0 | 2 |
| 0013 | 340 | 44.4% | 15.4% | 1 | 2 |
| 0014 | 106 | 83.7% | 73.4% | 3 | 12 |
| 0015 | 376 | 89.1% | 86.8% | 6 | 9 |
| 0016 | 209 | 24.8% | 22.4% | 18 | 4 |
| 0017 | 145 | - | - | 0 | 0 |
| 0018 | 339 | 91.6% | 88.6% | 9 | 18 |
| 0019 | 1059 | 65.0% | 65.8% | 6 | 7 |
| 0020 | 837 | 79.6% | 73.8% | 34 | 110 |

## Per sequence: Pedestrian

| Sequence | Frames | IDF1 | MOTA | ID switches | Unique objects |
| --- | --- | --- | --- | --- | --- |
| 0000 | 154 | 28.0% | -63.6% | 0 | 2 |
| 0001 | 447 | 61.0% | 38.4% | 0 | 3 |
| 0002 | 233 | 89.6% | 79.6% | 0 | 1 |
| 0003 | 144 | - | - | 0 | 0 |
| 0004 | 314 | 23.2% | 12.3% | 10 | 5 |
| 0005 | 297 | 0.0% | -inf% | 0 | 0 |
| 0006 | 270 | - | - | 0 | 0 |
| 0007 | 800 | 77.1% | 52.2% | 0 | 2 |
| 0008 | 390 | 0.0% | -inf% | 0 | 0 |
| 0009 | 803 | 0.0% | -44.8% | 0 | 1 |
| 0010 | 294 | 54.5% | 33.3% | 0 | 2 |
| 0011 | 373 | 61.0% | 43.3% | 3 | 5 |
| 0012 | 78 | 0.0% | 0.0% | 0 | 1 |
| 0013 | 340 | 80.3% | 69.3% | 36 | 42 |
| 0014 | 106 | 38.5% | 4.1% | 5 | 2 |
| 0015 | 376 | 59.4% | 41.8% | 15 | 11 |
| 0016 | 209 | 73.5% | 59.6% | 34 | 19 |
| 0017 | 145 | 71.6% | 74.6% | 11 | 9 |
| 0018 | 339 | 0.0% | -inf% | 0 | 0 |
| 0019 | 1059 | 64.3% | 49.7% | 74 | 62 |
| 0020 | 837 | 0.0% | -inf% | 0 | 0 |

## Latency

| Median (ms) | p95 (ms) |
| --- | --- |
| 29.7 | 39.0 |

## Known limitations

- Not the official KITTI devkit: same classes, IoU and height rules, scored with py-motmetrics.
- Pedestrian also ignores Cyclist labels (see Setup), which is more lenient than the official rules.
- The detector was not trained on KITTI; tracking quality is bounded by detection quality.
- Daytime only, Karlsruhe, 2011.
