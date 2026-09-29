# Distance stability benchmark (KITTI tracking): `unidepth-v2-base_f150`

Generated automatically from `results.json` by `benchmark_distance_stability.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, precision fp16 (library autocast), given our focal length |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (public labels) |
| Frames | 3023: first 150 of each of 21 sequences, 10 fps |
| Objects | 14444 observations of 422 tracked objects |
| Ground truth | laser-measured 3D boxes, distance to the nearest surface of the footprint |
| Association | each labelled object followed by its labelled track ID; detections matched per frame |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `b7b5097` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:06:53+00:00 |

## Metrics

- **Jitter**: |change in estimate - true change| between consecutive frames, as a percentage
  of the distance (and in metres). 0 means the estimate moves exactly like the real object.
- **Speed error**: |speed from estimates - true speed| in m/s, from distances 1 frame (0.1 s)
  or 5 frames (0.5 s) apart. This is the error the Time To Collision stage would inherit.
- **Within 10%**: per-frame accuracy on this dataset, as a cross-check.

## In path

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 2754 | 2564 | 1.1% | 3.3% | 0.22 | 2.21 | 0.72 | 93% |
| unidepth-v2-base_p10 | 2754 | 2564 | 1.1% | 3.0% | 0.21 | 2.08 | 0.65 | 90% |
| unidepth-v2-base_p25 | 2754 | 2564 | 1.1% | 3.1% | 0.21 | 2.10 | 0.68 | 92% |

## All objects

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 14444 | 13419 | 1.2% | 4.3% | 0.25 | 2.50 | 0.97 | 72% |
| unidepth-v2-base_p10 | 14444 | 13419 | 1.2% | 4.2% | 0.23 | 2.35 | 0.90 | 58% |
| unidepth-v2-base_p25 | 14444 | 13419 | 1.2% | 4.0% | 0.24 | 2.36 | 0.90 | 63% |

## `unidepth-v2-base_median` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.3% | 2.8% | 0.08 | 0.84 | 0.30 | 89% |
| 10-20 m | 770 | 698 | 0.9% | 3.3% | 0.13 | 1.28 | 0.47 | 95% |
| 20-30 m | 611 | 567 | 0.9% | 2.6% | 0.22 | 2.18 | 0.74 | 98% |
| 30-50 m | 722 | 669 | 1.4% | 3.5% | 0.52 | 5.24 | 1.72 | 91% |
| 50+ m | 261 | 237 | 1.5% | 4.1% | 0.94 | 9.40 | 3.84 | 90% |

## `unidepth-v2-base_median` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.2% | 4.1% | 0.28 | 2.78 | 1.10 | 75% |
| pedestrian | 3340 | 2982 | 1.3% | 4.6% | 0.16 | 1.62 | 0.58 | 71% |
| van | 1079 | 1014 | 1.4% | 4.7% | 0.32 | 3.23 | 1.43 | 60% |
| cyclist | 323 | 241 | 2.1% | 6.7% | 0.34 | 3.43 | 1.23 | 81% |
| truck | 153 | 142 | 2.3% | 7.3% | 0.52 | 5.17 | 2.68 | 54% |
| tram | 51 | 50 | 2.4% | 10.4% | 1.42 | 14.20 | 5.83 | 12% |

## `unidepth-v2-base_p10` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.1% | 2.7% | 0.08 | 0.81 | 0.28 | 92% |
| 10-20 m | 770 | 698 | 0.9% | 2.8% | 0.13 | 1.28 | 0.43 | 95% |
| 20-30 m | 611 | 567 | 0.9% | 2.5% | 0.23 | 2.29 | 0.66 | 97% |
| 30-50 m | 722 | 669 | 1.3% | 3.4% | 0.48 | 4.80 | 1.60 | 82% |
| 50+ m | 261 | 237 | 1.4% | 3.9% | 0.94 | 9.39 | 3.31 | 82% |

## `unidepth-v2-base_p10` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.1% | 4.3% | 0.27 | 2.71 | 1.11 | 58% |
| pedestrian | 3340 | 2982 | 1.2% | 3.5% | 0.15 | 1.49 | 0.52 | 61% |
| van | 1079 | 1014 | 1.3% | 4.9% | 0.29 | 2.94 | 1.34 | 43% |
| cyclist | 323 | 241 | 1.4% | 4.3% | 0.22 | 2.18 | 0.82 | 74% |
| truck | 153 | 142 | 2.3% | 7.9% | 0.50 | 4.97 | 2.06 | 50% |
| tram | 51 | 50 | 2.1% | 7.1% | 0.91 | 9.08 | 6.95 | 10% |

## `unidepth-v2-base_p25` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 344 | 1.2% | 2.8% | 0.09 | 0.85 | 0.28 | 92% |
| 10-20 m | 770 | 698 | 1.0% | 2.9% | 0.13 | 1.28 | 0.45 | 97% |
| 20-30 m | 611 | 567 | 0.9% | 2.4% | 0.22 | 2.24 | 0.66 | 98% |
| 30-50 m | 722 | 669 | 1.3% | 3.3% | 0.48 | 4.81 | 1.58 | 84% |
| 50+ m | 261 | 237 | 1.4% | 3.8% | 0.94 | 9.42 | 3.71 | 85% |

## `unidepth-v2-base_p25` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8990 | 1.1% | 3.9% | 0.27 | 2.66 | 1.07 | 64% |
| pedestrian | 3340 | 2982 | 1.2% | 3.8% | 0.16 | 1.57 | 0.55 | 66% |
| van | 1079 | 1014 | 1.3% | 4.7% | 0.31 | 3.06 | 1.35 | 50% |
| cyclist | 323 | 241 | 1.6% | 4.7% | 0.25 | 2.46 | 0.87 | 80% |
| truck | 153 | 142 | 2.0% | 7.5% | 0.43 | 4.33 | 1.90 | 54% |
| tram | 51 | 50 | 2.1% | 7.4% | 1.16 | 11.57 | 6.50 | 12% |

## Known limitations

- The labels themselves are not perfectly steady frame to frame (each box is fitted to the laser
  scan separately), so part of every method's measured jitter is label noise, a floor none can beat.
- Objects are followed by their labelled ID; a real tracker's ID switches would add error on top.
- First 150 frames of each sequence only.
