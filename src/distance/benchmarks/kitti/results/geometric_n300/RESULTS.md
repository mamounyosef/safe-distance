# KITTI distance benchmark: `geometric_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `ground_plane`, `known_size`, `combined` |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` |
| Created (UTC) | 2026-09-28T19:04:34+00:00 |

## Metrics

- **Nearest surface**: true distance to the closest point of the object's footprint on the road
  (e.g. the rear bumper of the car ahead). The gap that matters for braking.
- **Centre**: true distance to the middle of the object, as KITTI records it.
- **Coverage**: share of objects the estimator answered for, rather than returning unknown.
- **Median / mean error**: absolute distance error in metres (mean = MAE, Mean Absolute Error).
- **Relative error**: average absolute error as a percentage of the true distance.
- **Within 10%**: share of answers within 10% of the true distance.
- **Bias**: average signed error; negative = estimates too close, positive = too far.
  Bias is systematic and correctable; the spread around it is not.

## Overall, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 1187 | 99% | 2.66 | 5.62 | 24% | 39% | +13.0% |
| known_size | 1187 | 100% | 1.65 | 2.96 | 17% | 64% | +12.3% |
| combined | 1187 | 100% | 1.65 | 2.96 | 18% | 64% | +12.6% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 1187 | 99% | 2.75 | 5.85 | 19% | 37% | +0.2% |
| known_size | 1187 | 100% | 1.73 | 2.97 | 12% | 59% | -0.8% |
| combined | 1187 | 100% | 1.73 | 2.96 | 13% | 59% | -0.8% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / ground_plane | 206 | 99% | 2.43 | 6.84 | 20% | 48% | +13.1% |
| in path / known_size | 206 | 100% | 1.52 | 2.98 | 9% | 75% | +3.9% |
| in path / combined | 206 | 100% | 1.52 | 2.98 | 9% | 75% | +3.9% |
| beside / ground_plane | 981 | 99% | 2.75 | 5.36 | 25% | 37% | +13.0% |
| beside / known_size | 981 | 99% | 1.70 | 2.96 | 19% | 62% | +14.1% |
| beside / combined | 981 | 100% | 1.71 | 2.96 | 20% | 61% | +14.4% |

### `ground_plane` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.07 | 1.19 | 18% | 20% | +17.0% |
| 10-20 m | 44 | 100% | 1.09 | 1.58 | 11% | 59% | +8.8% |
| 20-30 m | 46 | 100% | 1.88 | 3.64 | 14% | 59% | +10.0% |
| 30-50 m | 76 | 100% | 5.26 | 11.49 | 29% | 42% | +20.0% |
| 50+ m | 25 | 88% | 8.08 | 11.88 | 21% | 41% | +1.8% |

### `known_size` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.62 | 0.84 | 15% | 60% | +12.7% |
| 10-20 m | 44 | 100% | 0.91 | 1.70 | 11% | 82% | +5.6% |
| 20-30 m | 46 | 100% | 1.52 | 1.54 | 6% | 85% | +0.2% |
| 30-50 m | 76 | 100% | 2.32 | 3.66 | 9% | 75% | +2.8% |
| 50+ m | 25 | 100% | 4.41 | 7.07 | 11% | 52% | +6.1% |

### `combined` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.62 | 0.84 | 15% | 60% | +12.7% |
| 10-20 m | 44 | 100% | 0.91 | 1.70 | 11% | 82% | +5.6% |
| 20-30 m | 46 | 100% | 1.52 | 1.54 | 6% | 85% | +0.2% |
| 30-50 m | 76 | 100% | 2.32 | 3.66 | 9% | 75% | +2.8% |
| 50+ m | 25 | 100% | 4.41 | 7.07 | 11% | 52% | +6.1% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / ground_plane | 206 | 99% | 2.70 | 6.82 | 18% | 45% | +4.7% |
| in path / known_size | 206 | 100% | 2.26 | 3.30 | 10% | 59% | -4.0% |
| in path / combined | 206 | 100% | 2.26 | 3.30 | 10% | 59% | -4.0% |
| beside / ground_plane | 981 | 99% | 2.77 | 5.64 | 20% | 35% | -0.8% |
| beside / known_size | 981 | 99% | 1.62 | 2.90 | 13% | 59% | -0.1% |
| beside / combined | 981 | 100% | 1.62 | 2.89 | 13% | 59% | -0.1% |

### `ground_plane` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.73 | 0.82 | 10% | 55% | +1.7% |
| 10-20 m | 41 | 100% | 1.32 | 1.46 | 10% | 51% | -2.4% |
| 20-30 m | 49 | 100% | 2.69 | 3.30 | 13% | 49% | +1.9% |
| 30-50 m | 74 | 100% | 5.75 | 10.83 | 26% | 41% | +13.7% |
| 50+ m | 31 | 90% | 7.41 | 12.59 | 21% | 36% | -2.3% |

### `known_size` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.74 | 0.94 | 13% | 64% | -1.8% |
| 10-20 m | 41 | 100% | 1.80 | 1.82 | 12% | 41% | -8.6% |
| 20-30 m | 49 | 100% | 2.22 | 2.53 | 10% | 57% | -4.1% |
| 30-50 m | 74 | 100% | 3.61 | 3.79 | 9% | 65% | -4.5% |
| 50+ m | 31 | 100% | 3.21 | 6.12 | 10% | 68% | +2.9% |

### `combined` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.74 | 0.94 | 13% | 64% | -1.8% |
| 10-20 m | 41 | 100% | 1.80 | 1.82 | 12% | 41% | -8.6% |
| 20-30 m | 49 | 100% | 2.22 | 2.53 | 10% | 57% | -4.1% |
| 30-50 m | 74 | 100% | 3.61 | 3.79 | 9% | 65% | -4.5% |
| 50+ m | 31 | 100% | 3.21 | 6.12 | 10% | 68% | +2.9% |

## `ground_plane` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 99% | 1.42 | 1.83 | 46% | 25% | +45.1% |
| 10-20 m | 297 | 100% | 1.47 | 2.56 | 16% | 51% | +10.9% |
| 20-30 m | 226 | 100% | 2.93 | 4.49 | 18% | 46% | +6.4% |
| 30-50 m | 319 | 99% | 5.51 | 9.09 | 24% | 35% | +5.9% |
| 50+ m | 135 | 96% | 9.24 | 12.19 | 21% | 30% | -4.5% |

## `ground_plane` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 99% | 2.64 | 5.40 | 23% | 42% | +10.5% |
| pedestrian | 126 | 98% | 1.81 | 5.46 | 30% | 22% | +28.8% |
| van | 84 | 98% | 4.00 | 7.37 | 30% | 32% | +13.3% |
| truck | 42 | 100% | 5.15 | 6.18 | 26% | 33% | +14.8% |
| cyclist | 20 | 100% | 4.84 | 8.31 | 29% | 25% | +24.2% |

## `known_size` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 98% | 1.01 | 1.96 | 52% | 40% | +50.2% |
| 10-20 m | 297 | 100% | 1.04 | 1.81 | 12% | 71% | +8.0% |
| 20-30 m | 226 | 100% | 1.62 | 2.34 | 9% | 70% | +3.2% |
| 30-50 m | 319 | 100% | 2.60 | 3.57 | 9% | 72% | +2.6% |
| 50+ m | 135 | 100% | 4.60 | 6.58 | 11% | 56% | +2.2% |

## `known_size` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.62 | 2.47 | 17% | 67% | +11.7% |
| pedestrian | 126 | 98% | 0.63 | 1.61 | 10% | 80% | +7.5% |
| van | 84 | 100% | 7.46 | 9.06 | 41% | 8% | +28.0% |
| truck | 42 | 95% | 3.70 | 6.06 | 15% | 52% | +10.2% |
| cyclist | 20 | 100% | 1.42 | 2.04 | 9% | 70% | +9.1% |

## `combined` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 99% | 1.03 | 1.99 | 53% | 39% | +51.5% |
| 10-20 m | 297 | 100% | 1.04 | 1.81 | 12% | 71% | +8.0% |
| 20-30 m | 226 | 100% | 1.62 | 2.34 | 9% | 70% | +3.2% |
| 30-50 m | 319 | 100% | 2.60 | 3.57 | 9% | 72% | +2.6% |
| 50+ m | 135 | 100% | 4.60 | 6.58 | 11% | 56% | +2.2% |

## `combined` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.62 | 2.47 | 17% | 67% | +11.7% |
| pedestrian | 126 | 98% | 0.64 | 1.61 | 10% | 80% | +7.6% |
| van | 84 | 100% | 7.46 | 9.06 | 41% | 8% | +28.0% |
| truck | 42 | 100% | 3.70 | 5.98 | 24% | 50% | +18.9% |
| cyclist | 20 | 100% | 1.42 | 2.04 | 9% | 70% | +9.1% |

## `ground_plane` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 99% | 0.99 | 1.15 | 19% | 39% | +12.4% |
| 10-20 m | 299 | 100% | 1.53 | 2.35 | 15% | 45% | -2.1% |
| 20-30 m | 246 | 100% | 3.15 | 4.34 | 17% | 39% | -0.8% |
| 30-50 m | 329 | 99% | 6.32 | 9.18 | 24% | 33% | +1.1% |
| 50+ m | 155 | 96% | 10.32 | 12.94 | 22% | 23% | -8.5% |

## `ground_plane` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 99% | 2.83 | 5.73 | 18% | 37% | -2.6% |
| pedestrian | 126 | 98% | 1.37 | 5.04 | 25% | 38% | +23.8% |
| van | 84 | 98% | 4.24 | 7.62 | 21% | 32% | -5.2% |
| truck | 42 | 100% | 4.41 | 6.45 | 14% | 45% | -7.8% |
| cyclist | 20 | 100% | 3.88 | 7.75 | 25% | 30% | +19.5% |

## `known_size` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 97% | 1.16 | 1.59 | 28% | 37% | +16.0% |
| 10-20 m | 299 | 100% | 1.24 | 1.62 | 11% | 53% | -5.6% |
| 20-30 m | 246 | 100% | 1.86 | 2.68 | 11% | 63% | -2.5% |
| 30-50 m | 329 | 100% | 2.40 | 3.51 | 9% | 70% | -2.6% |
| 50+ m | 155 | 100% | 4.12 | 6.21 | 10% | 64% | -1.6% |

## `known_size` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.69 | 2.59 | 12% | 60% | -2.1% |
| pedestrian | 126 | 98% | 0.64 | 1.50 | 9% | 81% | +3.2% |
| van | 84 | 100% | 5.78 | 8.14 | 27% | 19% | +7.3% |
| truck | 42 | 95% | 3.98 | 5.98 | 14% | 45% | -4.4% |
| cyclist | 20 | 100% | 1.20 | 1.52 | 6% | 80% | +4.8% |

## `combined` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 99% | 1.17 | 1.60 | 28% | 37% | +16.0% |
| 10-20 m | 299 | 100% | 1.24 | 1.62 | 11% | 53% | -5.6% |
| 20-30 m | 246 | 100% | 1.86 | 2.68 | 11% | 63% | -2.5% |
| 30-50 m | 329 | 100% | 2.40 | 3.51 | 9% | 70% | -2.6% |
| 50+ m | 155 | 100% | 4.12 | 6.21 | 10% | 64% | -1.6% |

## `combined` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.69 | 2.59 | 12% | 60% | -2.1% |
| pedestrian | 126 | 98% | 0.65 | 1.51 | 9% | 81% | +3.3% |
| van | 84 | 100% | 5.78 | 8.14 | 27% | 19% | +7.3% |
| truck | 42 | 100% | 3.89 | 5.79 | 15% | 43% | -3.3% |
| cyclist | 20 | 100% | 1.20 | 1.52 | 6% | 80% | +4.8% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| ground_plane | 0.24 |
| known_size | 0.007 |
| combined | 0.158 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
