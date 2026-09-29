# Distance stability benchmark (KITTI tracking): `metric3d-v2-large-fp16_f150`

Generated automatically from `results.json` by `benchmark_distance_stability.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-large-fp16_median`, `metric3d-v2-large-fp16_p10`, `metric3d-v2-large-fp16_p25` |
| Depth model | `metric3d-v2-large-fp16`, precision fp16 (autocast), given our focal length |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (public labels) |
| Frames | 3023: first 150 of each of 21 sequences, 10 fps |
| Objects | 14444 observations of 422 tracked objects |
| Ground truth | laser-measured 3D boxes, distance to the nearest surface of the footprint |
| Association | each labelled object followed by its labelled track ID; detections matched per frame |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `b7b5097` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:59:29+00:00 |

## Metrics

- **Jitter**: |change in estimate - true change| between consecutive frames, as a percentage
  of the distance (and in metres). 0 means the estimate moves exactly like the real object.
- **Speed error**: |speed from estimates - true speed| in m/s, from distances 1 frame (0.1 s)
  or 5 frames (0.5 s) apart. This is the error the Time To Collision stage would inherit.
- **Within 10%**: per-frame accuracy on this dataset, as a cross-check.

## In path

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 2754 | 2564 | 1.1% | 3.0% | 0.20 | 2.03 | 0.61 | 91% |
| metric3d-v2-large-fp16_p10 | 2754 | 2564 | 1.1% | 3.5% | 0.21 | 2.14 | 0.63 | 93% |
| metric3d-v2-large-fp16_p25 | 2754 | 2564 | 1.1% | 3.1% | 0.20 | 2.00 | 0.60 | 94% |

## All objects

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 14444 | 13419 | 1.2% | 4.1% | 0.23 | 2.33 | 0.89 | 76% |
| metric3d-v2-large-fp16_p10 | 14444 | 13419 | 1.2% | 5.1% | 0.24 | 2.40 | 0.90 | 67% |
| metric3d-v2-large-fp16_p25 | 14444 | 13419 | 1.2% | 4.1% | 0.23 | 2.29 | 0.85 | 73% |

## `metric3d-v2-large-fp16_median` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.1% | 2.6% | 0.08 | 0.76 | 0.22 | 98% |
| 10-20 m | 770 | 698 | 1.0% | 2.6% | 0.14 | 1.36 | 0.39 | 96% |
| 20-30 m | 611 | 567 | 0.9% | 2.2% | 0.21 | 2.08 | 0.65 | 93% |
| 30-50 m | 722 | 669 | 1.2% | 3.4% | 0.45 | 4.46 | 1.48 | 90% |
| 50+ m | 261 | 237 | 2.0% | 5.5% | 1.25 | 12.54 | 3.82 | 66% |

## `metric3d-v2-large-fp16_median` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.2% | 4.2% | 0.27 | 2.69 | 1.06 | 78% |
| pedestrian | 3340 | 2982 | 1.2% | 3.3% | 0.15 | 1.54 | 0.51 | 72% |
| van | 1079 | 1014 | 1.4% | 5.4% | 0.30 | 3.04 | 1.20 | 74% |
| cyclist | 323 | 241 | 1.2% | 4.3% | 0.18 | 1.78 | 0.78 | 84% |
| truck | 153 | 142 | 1.8% | 6.8% | 0.37 | 3.65 | 1.76 | 76% |
| tram | 51 | 50 | 2.2% | 6.6% | 1.22 | 12.16 | 6.51 | 69% |

## `metric3d-v2-large-fp16_p10` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.2% | 2.7% | 0.08 | 0.81 | 0.22 | 96% |
| 10-20 m | 770 | 698 | 1.1% | 3.2% | 0.16 | 1.56 | 0.40 | 96% |
| 20-30 m | 611 | 567 | 0.9% | 2.3% | 0.22 | 2.16 | 0.63 | 95% |
| 30-50 m | 722 | 669 | 1.2% | 4.2% | 0.46 | 4.59 | 1.38 | 88% |
| 50+ m | 261 | 237 | 2.0% | 5.2% | 1.29 | 12.92 | 3.70 | 84% |

## `metric3d-v2-large-fp16_p10` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.2% | 5.5% | 0.28 | 2.82 | 1.09 | 69% |
| pedestrian | 3340 | 2982 | 1.2% | 3.3% | 0.16 | 1.60 | 0.51 | 64% |
| van | 1079 | 1014 | 1.6% | 8.6% | 0.35 | 3.48 | 1.44 | 60% |
| cyclist | 323 | 241 | 1.2% | 4.5% | 0.17 | 1.74 | 0.78 | 79% |
| truck | 153 | 142 | 1.6% | 6.3% | 0.41 | 4.12 | 1.64 | 67% |
| tram | 51 | 50 | 2.4% | 10.0% | 1.34 | 13.38 | 13.88 | 6% |

## `metric3d-v2-large-fp16_p25` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.0% | 2.7% | 0.07 | 0.70 | 0.22 | 98% |
| 10-20 m | 770 | 698 | 1.0% | 2.7% | 0.14 | 1.38 | 0.38 | 98% |
| 20-30 m | 611 | 567 | 0.9% | 2.1% | 0.21 | 2.07 | 0.62 | 97% |
| 30-50 m | 722 | 669 | 1.2% | 3.6% | 0.44 | 4.36 | 1.35 | 93% |
| 50+ m | 261 | 237 | 2.0% | 5.1% | 1.23 | 12.29 | 3.26 | 77% |

## `metric3d-v2-large-fp16_p25` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.2% | 4.3% | 0.26 | 2.61 | 1.03 | 75% |
| pedestrian | 3340 | 2982 | 1.2% | 3.2% | 0.15 | 1.53 | 0.49 | 69% |
| van | 1079 | 1014 | 1.4% | 5.3% | 0.31 | 3.11 | 1.25 | 70% |
| cyclist | 323 | 241 | 1.2% | 3.6% | 0.17 | 1.67 | 0.73 | 82% |
| truck | 153 | 142 | 1.8% | 7.2% | 0.39 | 3.85 | 1.69 | 69% |
| tram | 51 | 50 | 2.7% | 27.0% | 1.52 | 15.16 | 9.13 | 20% |

## Known limitations

- The labels themselves are not perfectly steady frame to frame (each box is fitted to the laser
  scan separately), so part of every method's measured jitter is label noise, a floor none can beat.
- Objects are followed by their labelled ID; a real tracker's ID switches would add error on top.
- First 150 frames of each sequence only.
