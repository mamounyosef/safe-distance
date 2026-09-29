# Distance stability benchmark (KITTI tracking): `metric3d-v2-small-fp16_f150`

Generated automatically from `results.json` by `benchmark_distance_stability.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, precision fp16 (autocast), given our focal length |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (public labels) |
| Frames | 3023: first 150 of each of 21 sequences, 10 fps |
| Objects | 14444 observations of 422 tracked objects |
| Ground truth | laser-measured 3D boxes, distance to the nearest surface of the footprint |
| Association | each labelled object followed by its labelled track ID; detections matched per frame |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `b7b5097` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:39:11+00:00 |

## Metrics

- **Jitter**: |change in estimate - true change| between consecutive frames, as a percentage
  of the distance (and in metres). 0 means the estimate moves exactly like the real object.
- **Speed error**: |speed from estimates - true speed| in m/s, from distances 1 frame (0.1 s)
  or 5 frames (0.5 s) apart. This is the error the Time To Collision stage would inherit.
- **Within 10%**: per-frame accuracy on this dataset, as a cross-check.

## In path

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 2754 | 2564 | 1.4% | 4.5% | 0.28 | 2.80 | 0.85 | 89% |
| metric3d-v2-small-fp16_p10 | 2754 | 2564 | 1.4% | 4.5% | 0.27 | 2.73 | 0.80 | 85% |
| metric3d-v2-small-fp16_p25 | 2754 | 2564 | 1.4% | 4.3% | 0.28 | 2.77 | 0.82 | 88% |

## All objects

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 14444 | 13419 | 1.7% | 5.7% | 0.32 | 3.18 | 1.13 | 71% |
| metric3d-v2-small-fp16_p10 | 14444 | 13419 | 1.6% | 6.4% | 0.32 | 3.18 | 1.14 | 60% |
| metric3d-v2-small-fp16_p25 | 14444 | 13419 | 1.6% | 5.6% | 0.31 | 3.13 | 1.09 | 66% |

## `metric3d-v2-small-fp16_median` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.7% | 4.5% | 0.12 | 1.21 | 0.32 | 94% |
| 10-20 m | 770 | 698 | 1.4% | 3.9% | 0.19 | 1.94 | 0.54 | 94% |
| 20-30 m | 611 | 567 | 1.1% | 3.4% | 0.28 | 2.79 | 0.85 | 96% |
| 30-50 m | 722 | 669 | 1.6% | 4.5% | 0.58 | 5.77 | 1.77 | 87% |
| 50+ m | 261 | 237 | 2.0% | 8.9% | 1.25 | 12.52 | 3.86 | 61% |

## `metric3d-v2-small-fp16_median` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.6% | 5.6% | 0.35 | 3.54 | 1.31 | 74% |
| pedestrian | 3340 | 2982 | 1.7% | 5.1% | 0.21 | 2.10 | 0.66 | 66% |
| van | 1079 | 1014 | 2.1% | 7.3% | 0.44 | 4.41 | 1.69 | 64% |
| cyclist | 323 | 241 | 1.8% | 6.1% | 0.29 | 2.86 | 0.89 | 69% |
| truck | 153 | 142 | 2.2% | 7.6% | 0.53 | 5.34 | 2.19 | 58% |
| tram | 51 | 50 | 4.3% | 14.7% | 2.25 | 22.53 | 12.55 | 37% |

## `metric3d-v2-small-fp16_p10` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.8% | 4.5% | 0.12 | 1.18 | 0.34 | 86% |
| 10-20 m | 770 | 698 | 1.4% | 4.2% | 0.20 | 1.97 | 0.51 | 93% |
| 20-30 m | 611 | 567 | 1.1% | 3.6% | 0.26 | 2.56 | 0.80 | 95% |
| 30-50 m | 722 | 669 | 1.5% | 4.3% | 0.54 | 5.43 | 1.70 | 77% |
| 50+ m | 261 | 237 | 2.1% | 8.1% | 1.22 | 12.21 | 3.86 | 54% |

## `metric3d-v2-small-fp16_p10` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.6% | 6.5% | 0.36 | 3.63 | 1.37 | 64% |
| pedestrian | 3340 | 2982 | 1.7% | 4.9% | 0.21 | 2.11 | 0.64 | 53% |
| van | 1079 | 1014 | 2.2% | 9.1% | 0.47 | 4.67 | 1.82 | 51% |
| cyclist | 323 | 241 | 1.7% | 5.0% | 0.24 | 2.44 | 0.75 | 63% |
| truck | 153 | 142 | 2.5% | 8.2% | 0.56 | 5.58 | 2.38 | 55% |
| tram | 51 | 50 | 4.7% | 21.4% | 2.04 | 20.39 | 14.93 | 25% |

## `metric3d-v2-small-fp16_p25` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.8% | 4.8% | 0.12 | 1.20 | 0.32 | 92% |
| 10-20 m | 770 | 698 | 1.4% | 3.6% | 0.20 | 1.96 | 0.52 | 95% |
| 20-30 m | 611 | 567 | 1.1% | 3.4% | 0.26 | 2.57 | 0.82 | 96% |
| 30-50 m | 722 | 669 | 1.5% | 4.2% | 0.55 | 5.54 | 1.70 | 82% |
| 50+ m | 261 | 237 | 2.1% | 9.6% | 1.28 | 12.83 | 4.24 | 57% |

## `metric3d-v2-small-fp16_p25` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.5% | 5.6% | 0.35 | 3.51 | 1.30 | 70% |
| pedestrian | 3340 | 2982 | 1.6% | 4.8% | 0.21 | 2.06 | 0.64 | 58% |
| van | 1079 | 1014 | 2.0% | 7.2% | 0.45 | 4.48 | 1.64 | 60% |
| cyclist | 323 | 241 | 1.8% | 4.8% | 0.25 | 2.51 | 0.72 | 66% |
| truck | 153 | 142 | 2.4% | 7.8% | 0.56 | 5.59 | 2.38 | 56% |
| tram | 51 | 50 | 4.9% | 13.9% | 2.09 | 20.89 | 12.88 | 33% |

## Known limitations

- The labels themselves are not perfectly steady frame to frame (each box is fitted to the laser
  scan separately), so part of every method's measured jitter is label noise, a floor none can beat.
- Objects are followed by their labelled ID; a real tracker's ID switches would add error on top.
- First 150 frames of each sequence only.
