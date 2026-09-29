# Distance stability benchmark (KITTI tracking): `unidepth-v2-large_f150`

Generated automatically from `results.json` by `benchmark_distance_stability.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, precision fp16 (library autocast), given our focal length |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (public labels) |
| Frames | 3023: first 150 of each of 21 sequences, 10 fps |
| Objects | 14444 observations of 422 tracked objects |
| Ground truth | laser-measured 3D boxes, distance to the nearest surface of the footprint |
| Association | each labelled object followed by its labelled track ID; detections matched per frame |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `b7b5097` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:19:32+00:00 |

## Metrics

- **Jitter**: |change in estimate - true change| between consecutive frames, as a percentage
  of the distance (and in metres). 0 means the estimate moves exactly like the real object.
- **Speed error**: |speed from estimates - true speed| in m/s, from distances 1 frame (0.1 s)
  or 5 frames (0.5 s) apart. This is the error the Time To Collision stage would inherit.
- **Within 10%**: per-frame accuracy on this dataset, as a cross-check.

## In path

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 2754 | 2564 | 1.1% | 3.2% | 0.20 | 2.02 | 0.63 | 95% |
| unidepth-v2-large_p10 | 2754 | 2564 | 1.0% | 3.0% | 0.19 | 1.91 | 0.60 | 91% |
| unidepth-v2-large_p25 | 2754 | 2564 | 1.0% | 3.0% | 0.19 | 1.88 | 0.61 | 94% |

## All objects

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 14444 | 13419 | 1.2% | 4.2% | 0.23 | 2.30 | 0.89 | 73% |
| unidepth-v2-large_p10 | 14444 | 13419 | 1.1% | 4.2% | 0.23 | 2.25 | 0.83 | 61% |
| unidepth-v2-large_p25 | 14444 | 13419 | 1.1% | 4.0% | 0.22 | 2.21 | 0.83 | 66% |

## `unidepth-v2-large_median` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.0% | 2.5% | 0.07 | 0.70 | 0.22 | 97% |
| 10-20 m | 770 | 698 | 0.9% | 2.7% | 0.12 | 1.24 | 0.38 | 97% |
| 20-30 m | 611 | 567 | 0.9% | 2.4% | 0.23 | 2.30 | 0.63 | 96% |
| 30-50 m | 722 | 669 | 1.2% | 3.6% | 0.45 | 4.49 | 1.40 | 95% |
| 50+ m | 261 | 237 | 2.0% | 5.6% | 1.21 | 12.13 | 4.50 | 84% |

## `unidepth-v2-large_median` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.1% | 4.0% | 0.26 | 2.61 | 1.03 | 77% |
| pedestrian | 3340 | 2982 | 1.1% | 3.8% | 0.14 | 1.42 | 0.50 | 65% |
| van | 1079 | 1014 | 1.4% | 4.8% | 0.31 | 3.10 | 1.28 | 69% |
| cyclist | 323 | 241 | 1.8% | 7.4% | 0.27 | 2.72 | 0.89 | 80% |
| truck | 153 | 142 | 1.8% | 7.3% | 0.42 | 4.20 | 1.87 | 66% |
| tram | 51 | 50 | 2.3% | 8.0% | 1.20 | 11.96 | 4.45 | 67% |

## `unidepth-v2-large_p10` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.0% | 2.6% | 0.07 | 0.70 | 0.21 | 96% |
| 10-20 m | 770 | 698 | 0.8% | 2.6% | 0.11 | 1.12 | 0.35 | 90% |
| 20-30 m | 611 | 567 | 0.9% | 2.4% | 0.22 | 2.20 | 0.63 | 92% |
| 30-50 m | 722 | 669 | 1.1% | 3.3% | 0.41 | 4.09 | 1.31 | 87% |
| 50+ m | 261 | 237 | 1.9% | 4.9% | 1.11 | 11.07 | 4.07 | 95% |

## `unidepth-v2-large_p10` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.1% | 4.5% | 0.26 | 2.60 | 1.00 | 64% |
| pedestrian | 3340 | 2982 | 1.1% | 3.3% | 0.13 | 1.34 | 0.47 | 53% |
| van | 1079 | 1014 | 1.4% | 4.6% | 0.31 | 3.07 | 1.36 | 55% |
| cyclist | 323 | 241 | 1.3% | 3.8% | 0.20 | 2.01 | 0.69 | 75% |
| truck | 153 | 142 | 1.8% | 6.8% | 0.38 | 3.75 | 1.90 | 57% |
| tram | 51 | 50 | 1.9% | 6.2% | 1.19 | 11.94 | 4.93 | 18% |

## `unidepth-v2-large_p25` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.0% | 2.4% | 0.07 | 0.69 | 0.22 | 97% |
| 10-20 m | 770 | 698 | 0.8% | 2.6% | 0.11 | 1.12 | 0.37 | 95% |
| 20-30 m | 611 | 567 | 0.9% | 2.4% | 0.21 | 2.11 | 0.62 | 95% |
| 30-50 m | 722 | 669 | 1.1% | 3.4% | 0.40 | 4.02 | 1.36 | 92% |
| 50+ m | 261 | 237 | 1.8% | 4.8% | 1.09 | 10.93 | 4.03 | 93% |

## `unidepth-v2-large_p25` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.1% | 4.0% | 0.25 | 2.53 | 0.99 | 70% |
| pedestrian | 3340 | 2982 | 1.1% | 3.3% | 0.13 | 1.34 | 0.49 | 58% |
| van | 1079 | 1014 | 1.4% | 4.7% | 0.30 | 3.03 | 1.33 | 60% |
| cyclist | 323 | 241 | 1.4% | 4.3% | 0.20 | 1.97 | 0.73 | 80% |
| truck | 153 | 142 | 1.7% | 8.6% | 0.39 | 3.85 | 1.82 | 61% |
| tram | 51 | 50 | 1.7% | 6.5% | 1.25 | 12.54 | 5.16 | 31% |

## Known limitations

- The labels themselves are not perfectly steady frame to frame (each box is fitted to the laser
  scan separately), so part of every method's measured jitter is label noise, a floor none can beat.
- Objects are followed by their labelled ID; a real tracker's ID switches would add error on top.
- First 150 frames of each sequence only.
