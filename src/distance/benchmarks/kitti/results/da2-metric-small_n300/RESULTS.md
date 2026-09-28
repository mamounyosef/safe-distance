# KITTI distance benchmark: `da2-metric-small_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da2-metric-small_median`, `da2-metric-small_p10`, `da2-metric-small_p25` |
| Depth model | `da2-metric-small`, not given our focal length; inference 49.1 ms median, 54.5 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:05:08+00:00 |

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
| da2-metric-small_median | 1187 | 100% | 2.39 | 4.00 | 17% | 41% | +7.6% |
| da2-metric-small_p10 | 1187 | 100% | 1.69 | 3.67 | 13% | 53% | -3.7% |
| da2-metric-small_p25 | 1187 | 100% | 1.79 | 3.57 | 14% | 51% | +0.5% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median | 1187 | 100% | 2.46 | 4.10 | 15% | 44% | -3.7% |
| da2-metric-small_p10 | 1187 | 100% | 2.72 | 4.74 | 17% | 37% | -13.7% |
| da2-metric-small_p25 | 1187 | 100% | 2.38 | 4.26 | 15% | 40% | -9.9% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da2-metric-small_median | 206 | 100% | 2.87 | 4.34 | 15% | 45% | +13.1% |
| in path / da2-metric-small_p10 | 206 | 100% | 1.46 | 2.74 | 8% | 69% | +2.9% |
| in path / da2-metric-small_p25 | 206 | 100% | 1.82 | 3.14 | 10% | 61% | +6.4% |
| beside / da2-metric-small_median | 981 | 100% | 2.27 | 3.93 | 17% | 41% | +6.4% |
| beside / da2-metric-small_p10 | 981 | 100% | 1.73 | 3.87 | 14% | 50% | -5.1% |
| beside / da2-metric-small_p25 | 981 | 100% | 1.78 | 3.65 | 14% | 48% | -0.8% |

### `da2-metric-small_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 2.45 | 2.35 | 32% | 27% | +32.1% |
| 10-20 m | 44 | 100% | 1.85 | 2.39 | 17% | 43% | +16.3% |
| 20-30 m | 46 | 100% | 2.31 | 3.47 | 14% | 48% | +13.3% |
| 30-50 m | 76 | 100% | 4.45 | 5.77 | 14% | 43% | +10.7% |
| 50+ m | 25 | 100% | 5.06 | 6.24 | 10% | 60% | +3.1% |

### `da2-metric-small_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.25 | 1.07 | 15% | 33% | +14.6% |
| 10-20 m | 44 | 100% | 0.65 | 0.91 | 6% | 75% | +3.6% |
| 20-30 m | 46 | 100% | 1.29 | 1.89 | 8% | 74% | +3.3% |
| 30-50 m | 76 | 100% | 2.50 | 3.40 | 8% | 72% | +1.9% |
| 50+ m | 25 | 100% | 4.79 | 6.57 | 11% | 64% | -2.9% |

### `da2-metric-small_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.53 | 1.49 | 20% | 27% | +20.4% |
| 10-20 m | 44 | 100% | 0.89 | 1.26 | 9% | 66% | +7.3% |
| 20-30 m | 46 | 100% | 1.56 | 2.39 | 10% | 67% | +6.9% |
| 30-50 m | 76 | 100% | 2.90 | 3.97 | 10% | 63% | +5.0% |
| 50+ m | 25 | 100% | 5.62 | 6.32 | 10% | 56% | +0.0% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da2-metric-small_median | 206 | 100% | 2.00 | 3.56 | 12% | 63% | +4.8% |
| in path / da2-metric-small_p10 | 206 | 100% | 1.91 | 3.20 | 10% | 61% | -4.7% |
| in path / da2-metric-small_p25 | 206 | 100% | 1.91 | 3.08 | 10% | 60% | -1.5% |
| beside / da2-metric-small_median | 981 | 100% | 2.51 | 4.21 | 15% | 40% | -5.4% |
| beside / da2-metric-small_p10 | 981 | 100% | 3.01 | 5.07 | 18% | 32% | -15.6% |
| beside / da2-metric-small_p25 | 981 | 100% | 2.56 | 4.51 | 16% | 36% | -11.7% |

### `da2-metric-small_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 2.15 | 2.26 | 29% | 18% | +18.4% |
| 10-20 m | 41 | 100% | 1.23 | 1.61 | 12% | 61% | +4.0% |
| 20-30 m | 49 | 100% | 1.31 | 2.55 | 10% | 71% | +7.2% |
| 30-50 m | 74 | 100% | 3.17 | 4.62 | 11% | 65% | +3.5% |
| 50+ m | 31 | 100% | 4.86 | 5.66 | 10% | 65% | +0.1% |

### `da2-metric-small_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.07 | 1.17 | 15% | 27% | +0.2% |
| 10-20 m | 41 | 100% | 1.63 | 1.48 | 10% | 44% | -6.0% |
| 20-30 m | 49 | 100% | 1.71 | 2.18 | 9% | 76% | -3.6% |
| 30-50 m | 74 | 100% | 2.88 | 3.86 | 9% | 65% | -4.8% |
| 50+ m | 31 | 100% | 4.63 | 6.26 | 10% | 61% | -6.4% |

### `da2-metric-small_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.44 | 1.54 | 20% | 0% | +6.4% |
| 10-20 m | 41 | 100% | 1.47 | 1.39 | 10% | 44% | -3.4% |
| 20-30 m | 49 | 100% | 1.43 | 2.12 | 9% | 73% | +0.2% |
| 30-50 m | 74 | 100% | 2.79 | 3.83 | 9% | 69% | -1.9% |
| 50+ m | 31 | 100% | 3.73 | 5.57 | 9% | 61% | -3.5% |

## `da2-metric-small_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 1.10 | 1.38 | 27% | 26% | +23.4% |
| 10-20 m | 297 | 100% | 1.69 | 2.35 | 16% | 42% | +9.6% |
| 20-30 m | 226 | 100% | 2.88 | 4.10 | 16% | 41% | +8.1% |
| 30-50 m | 319 | 100% | 4.11 | 5.49 | 14% | 47% | +0.6% |
| 50+ m | 135 | 100% | 6.41 | 8.06 | 14% | 50% | -5.9% |

## `da2-metric-small_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.11 | 3.71 | 15% | 45% | +4.0% |
| pedestrian | 126 | 100% | 2.89 | 3.74 | 26% | 17% | +24.4% |
| van | 84 | 100% | 3.66 | 5.32 | 20% | 37% | +8.2% |
| truck | 42 | 100% | 4.05 | 5.48 | 23% | 50% | +15.1% |
| cyclist | 20 | 100% | 9.95 | 10.69 | 48% | 10% | +45.4% |

## `da2-metric-small_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.70 | 0.83 | 16% | 48% | +8.5% |
| 10-20 m | 297 | 100% | 0.96 | 1.50 | 10% | 61% | -2.9% |
| 20-30 m | 226 | 100% | 1.97 | 2.96 | 12% | 58% | -4.1% |
| 30-50 m | 319 | 100% | 3.53 | 5.45 | 14% | 51% | -8.4% |
| 50+ m | 135 | 100% | 7.33 | 9.88 | 17% | 39% | -13.0% |

## `da2-metric-small_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.69 | 3.74 | 13% | 55% | -5.8% |
| pedestrian | 126 | 100% | 1.27 | 1.74 | 12% | 44% | +7.3% |
| van | 84 | 100% | 2.31 | 5.04 | 17% | 48% | -5.3% |
| truck | 42 | 100% | 2.77 | 4.52 | 16% | 62% | +2.8% |
| cyclist | 20 | 100% | 4.92 | 5.37 | 22% | 30% | +16.4% |

## `da2-metric-small_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.84 | 0.99 | 19% | 40% | +13.5% |
| 10-20 m | 297 | 100% | 1.24 | 1.68 | 11% | 57% | +1.5% |
| 20-30 m | 226 | 100% | 2.24 | 3.13 | 13% | 55% | +0.5% |
| 30-50 m | 319 | 100% | 3.64 | 5.09 | 13% | 51% | -4.7% |
| 50+ m | 135 | 100% | 7.02 | 8.84 | 15% | 45% | -9.9% |

## `da2-metric-small_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.70 | 3.50 | 13% | 54% | -2.1% |
| pedestrian | 126 | 100% | 1.67 | 2.32 | 16% | 31% | +13.5% |
| van | 84 | 100% | 2.20 | 4.62 | 17% | 46% | -0.1% |
| truck | 42 | 100% | 2.84 | 4.72 | 17% | 60% | +6.4% |
| cyclist | 20 | 100% | 6.86 | 7.70 | 32% | 15% | +28.1% |

## `da2-metric-small_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.29 | 1.46 | 19% | 22% | -4.9% |
| 10-20 m | 299 | 100% | 1.51 | 2.04 | 14% | 48% | -3.6% |
| 20-30 m | 246 | 100% | 2.59 | 3.59 | 14% | 48% | +1.2% |
| 30-50 m | 329 | 100% | 3.96 | 5.46 | 14% | 49% | -4.1% |
| 50+ m | 155 | 100% | 7.03 | 8.70 | 15% | 45% | -9.3% |

## `da2-metric-small_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.14 | 3.84 | 13% | 49% | -7.3% |
| pedestrian | 126 | 100% | 2.42 | 3.32 | 21% | 25% | +19.2% |
| van | 84 | 100% | 3.30 | 5.62 | 17% | 30% | -7.2% |
| truck | 42 | 100% | 5.53 | 6.31 | 17% | 45% | -6.2% |
| cyclist | 20 | 100% | 9.08 | 9.90 | 42% | 10% | +39.4% |

## `da2-metric-small_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.39 | 1.49 | 20% | 18% | -16.5% |
| 10-20 m | 299 | 100% | 2.01 | 2.48 | 17% | 33% | -14.1% |
| 20-30 m | 246 | 100% | 2.59 | 3.58 | 14% | 46% | -10.8% |
| 30-50 m | 329 | 100% | 4.43 | 6.27 | 16% | 44% | -13.0% |
| 50+ m | 155 | 100% | 8.70 | 11.03 | 18% | 35% | -16.3% |

## `da2-metric-small_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.93 | 4.92 | 17% | 35% | -16.0% |
| pedestrian | 126 | 100% | 0.93 | 1.50 | 9% | 63% | +2.9% |
| van | 84 | 100% | 4.23 | 6.64 | 20% | 27% | -18.5% |
| truck | 42 | 100% | 5.79 | 6.78 | 17% | 33% | -15.1% |
| cyclist | 20 | 100% | 4.06 | 4.81 | 18% | 35% | +11.8% |

## `da2-metric-small_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.38 | 1.46 | 19% | 13% | -12.4% |
| 10-20 m | 299 | 100% | 1.77 | 2.25 | 15% | 35% | -10.3% |
| 20-30 m | 246 | 100% | 2.29 | 3.26 | 13% | 52% | -6.4% |
| 30-50 m | 329 | 100% | 3.86 | 5.59 | 14% | 49% | -9.4% |
| 50+ m | 155 | 100% | 7.39 | 9.74 | 16% | 41% | -13.3% |

## `da2-metric-small_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.40 | 4.29 | 15% | 41% | -12.7% |
| pedestrian | 126 | 100% | 1.29 | 1.98 | 13% | 40% | +8.8% |
| van | 84 | 100% | 3.44 | 5.75 | 17% | 38% | -14.0% |
| truck | 42 | 100% | 5.89 | 6.24 | 16% | 36% | -12.4% |
| cyclist | 20 | 100% | 5.87 | 6.92 | 27% | 15% | +23.0% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| da2-metric-small_median | 52.208 |
| da2-metric-small_p10 | 2.781 |
| da2-metric-small_p25 | 2.684 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
