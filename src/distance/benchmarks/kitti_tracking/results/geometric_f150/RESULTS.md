# Distance stability benchmark (KITTI tracking): `geometric_f150`

Generated automatically from `results.json` by `benchmark_distance_stability.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `ground_plane`, `known_size`, `combined` |
| Dataset | [KITTI Tracking](https://www.cvlibs.net/datasets/kitti/eval_tracking.php), training (public labels) |
| Frames | 3023: first 150 of each of 21 sequences, 10 fps |
| Objects | 14444 observations of 422 tracked objects |
| Ground truth | laser-measured 3D boxes, distance to the nearest surface of the footprint |
| Association | each labelled object followed by its labelled track ID; detections matched per frame |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `70d771f` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:32:33+00:00 |

## Metrics

- **Jitter**: |change in estimate - true change| between consecutive frames, as a percentage
  of the distance (and in metres). 0 means the estimate moves exactly like the real object.
- **Speed error**: |speed from estimates - true speed| in m/s, from distances 1 frame (0.1 s)
  or 5 frames (0.5 s) apart. This is the error the Time To Collision stage would inherit.
- **Within 10%**: per-frame accuracy on this dataset, as a cross-check.

## In path

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 2754 | 2479 | 1.6% | 8.5% | 0.30 | 3.02 | 2.18 | 33% |
| known_size | 2754 | 2515 | 1.1% | 4.3% | 0.22 | 2.20 | 0.61 | 81% |
| combined | 2754 | 2515 | 1.1% | 4.3% | 0.22 | 2.20 | 0.61 | 81% |

## All objects

| Estimator | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 14444 | 13004 | 1.8% | 10.0% | 0.36 | 3.63 | 2.07 | 30% |
| known_size | 14444 | 13315 | 1.4% | 7.7% | 0.30 | 2.96 | 0.93 | 67% |
| combined | 14444 | 13328 | 1.4% | 7.8% | 0.30 | 2.96 | 0.93 | 67% |

## `ground_plane` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 295 | 1.3% | 4.1% | 0.10 | 0.96 | 0.41 | 6% |
| 10-20 m | 770 | 698 | 1.4% | 6.0% | 0.19 | 1.86 | 1.20 | 34% |
| 20-30 m | 611 | 566 | 1.7% | 5.9% | 0.41 | 4.13 | 1.88 | 60% |
| 30-50 m | 722 | 658 | 2.5% | 13.9% | 0.89 | 8.91 | 6.94 | 21% |
| 50+ m | 261 | 214 | 3.0% | 14.9% | 2.06 | 20.65 | 8.21 | 33% |

## `ground_plane` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8721 | 1.8% | 10.2% | 0.42 | 4.19 | 2.56 | 34% |
| pedestrian | 3340 | 2891 | 1.6% | 7.1% | 0.20 | 2.03 | 0.94 | 19% |
| van | 1079 | 968 | 2.6% | 13.5% | 0.57 | 5.66 | 3.16 | 28% |
| cyclist | 323 | 240 | 3.2% | 17.1% | 0.56 | 5.62 | 2.27 | 21% |
| truck | 153 | 134 | 3.2% | 24.3% | 0.64 | 6.36 | 4.43 | 27% |
| tram | 51 | 50 | 4.7% | 16.0% | 2.42 | 24.16 | 16.47 | 14% |

## `known_size` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 295 | 1.0% | 3.3% | 0.08 | 0.78 | 0.27 | 82% |
| 10-20 m | 770 | 698 | 1.0% | 4.2% | 0.14 | 1.35 | 0.36 | 74% |
| 20-30 m | 611 | 567 | 0.9% | 3.0% | 0.21 | 2.13 | 0.60 | 91% |
| 30-50 m | 722 | 669 | 1.2% | 3.9% | 0.44 | 4.44 | 1.37 | 83% |
| 50+ m | 261 | 237 | 3.0% | 10.7% | 1.77 | 17.70 | 4.99 | 75% |

## `known_size` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8986 | 1.3% | 7.3% | 0.33 | 3.26 | 1.09 | 72% |
| pedestrian | 3340 | 2898 | 1.4% | 4.7% | 0.18 | 1.82 | 0.43 | 76% |
| van | 1079 | 1005 | 2.3% | 84.2% | 0.55 | 5.53 | 3.06 | 6% |
| cyclist | 323 | 241 | 3.5% | 12.7% | 0.53 | 5.28 | 1.28 | 57% |
| truck | 153 | 135 | 1.3% | 9.6% | 0.35 | 3.55 | 1.50 | 46% |
| tram | 51 | 50 | 2.5% | 13.4% | 1.72 | 17.22 | 7.89 | 16% |

## `combined` in path, by distance

| Distance | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 390 | 295 | 1.0% | 3.3% | 0.08 | 0.78 | 0.27 | 82% |
| 10-20 m | 770 | 698 | 1.0% | 4.2% | 0.14 | 1.35 | 0.36 | 74% |
| 20-30 m | 611 | 567 | 0.9% | 3.0% | 0.21 | 2.13 | 0.60 | 91% |
| 30-50 m | 722 | 669 | 1.2% | 3.9% | 0.44 | 4.44 | 1.37 | 83% |
| 50+ m | 261 | 237 | 3.0% | 10.7% | 1.77 | 17.70 | 4.99 | 75% |

## `combined` by class

| Class | Observations | Pairs | Jitter median | Jitter p90 | Jitter median (m) | Speed error, 1 frame (m/s) | Speed error, 5 frames (m/s) | Within 10% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car | 9498 | 8986 | 1.3% | 7.3% | 0.33 | 3.26 | 1.09 | 72% |
| pedestrian | 3340 | 2899 | 1.4% | 4.7% | 0.18 | 1.82 | 0.43 | 76% |
| van | 1079 | 1010 | 2.3% | 84.3% | 0.55 | 5.50 | 3.01 | 6% |
| cyclist | 323 | 241 | 3.5% | 12.7% | 0.53 | 5.28 | 1.28 | 57% |
| truck | 153 | 142 | 1.4% | 10.6% | 0.36 | 3.57 | 1.74 | 44% |
| tram | 51 | 50 | 2.5% | 13.4% | 1.72 | 17.22 | 7.89 | 16% |

## Known limitations

- The labels themselves are not perfectly steady frame to frame (each box is fitted to the laser
  scan separately), so part of every method's measured jitter is label noise, a floor none can beat.
- Objects are followed by their labelled ID; a real tracker's ID switches would add error on top.
- First 150 frames of each sequence only.
