# KITTI distance benchmark: `da2-metric-base_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da2-metric-base_median`, `da2-metric-base_p10`, `da2-metric-base_p25` |
| Depth model | `da2-metric-base`, not given our focal length; inference 99.4 ms median, 108.3 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:05:54+00:00 |

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
| da2-metric-base_median | 1187 | 100% | 2.75 | 4.12 | 18% | 38% | +11.0% |
| da2-metric-base_p10 | 1187 | 100% | 1.94 | 3.43 | 13% | 51% | +0.7% |
| da2-metric-base_p25 | 1187 | 100% | 2.18 | 3.53 | 14% | 46% | +4.4% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median | 1187 | 100% | 2.51 | 3.90 | 15% | 44% | -0.3% |
| da2-metric-base_p10 | 1187 | 100% | 2.32 | 3.98 | 15% | 42% | -9.6% |
| da2-metric-base_p25 | 1187 | 100% | 2.36 | 3.77 | 14% | 44% | -6.2% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da2-metric-base_median | 206 | 100% | 3.85 | 5.30 | 19% | 34% | +18.6% |
| in path / da2-metric-base_p10 | 206 | 100% | 2.08 | 3.19 | 10% | 60% | +8.3% |
| in path / da2-metric-base_p25 | 206 | 100% | 2.61 | 3.87 | 13% | 51% | +11.6% |
| beside / da2-metric-base_median | 981 | 100% | 2.51 | 3.87 | 18% | 39% | +9.4% |
| beside / da2-metric-base_p10 | 981 | 100% | 1.93 | 3.48 | 14% | 49% | -0.9% |
| beside / da2-metric-base_p25 | 981 | 100% | 2.08 | 3.46 | 15% | 45% | +2.9% |

### `da2-metric-base_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 3.22 | 3.50 | 47% | 13% | +47.2% |
| 10-20 m | 44 | 100% | 2.22 | 2.77 | 19% | 30% | +19.0% |
| 20-30 m | 46 | 100% | 2.96 | 4.40 | 18% | 37% | +17.6% |
| 30-50 m | 76 | 100% | 7.21 | 7.28 | 18% | 30% | +16.6% |
| 50+ m | 25 | 100% | 5.54 | 6.46 | 11% | 60% | +8.4% |

### `da2-metric-base_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.25 | 1.30 | 18% | 27% | +17.7% |
| 10-20 m | 44 | 100% | 0.83 | 1.08 | 8% | 70% | +7.0% |
| 20-30 m | 46 | 100% | 1.50 | 2.24 | 9% | 70% | +8.0% |
| 30-50 m | 76 | 100% | 3.58 | 4.73 | 11% | 51% | +8.8% |
| 50+ m | 25 | 100% | 4.43 | 5.14 | 8% | 72% | +3.9% |

### `da2-metric-base_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.69 | 1.92 | 26% | 27% | +25.9% |
| 10-20 m | 44 | 100% | 1.17 | 1.47 | 11% | 59% | +10.0% |
| 20-30 m | 46 | 100% | 2.07 | 2.87 | 12% | 59% | +11.0% |
| 30-50 m | 76 | 100% | 5.06 | 5.66 | 14% | 42% | +11.8% |
| 50+ m | 25 | 100% | 4.87 | 5.67 | 9% | 64% | +5.8% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da2-metric-base_median | 206 | 100% | 2.43 | 3.89 | 14% | 58% | +9.8% |
| in path / da2-metric-base_p10 | 206 | 100% | 1.51 | 2.58 | 8% | 64% | +0.3% |
| in path / da2-metric-base_p25 | 206 | 100% | 1.70 | 2.87 | 9% | 64% | +3.3% |
| beside / da2-metric-base_median | 981 | 100% | 2.51 | 3.90 | 15% | 41% | -2.5% |
| beside / da2-metric-base_p10 | 981 | 100% | 2.71 | 4.27 | 16% | 37% | -11.7% |
| beside / da2-metric-base_p25 | 981 | 100% | 2.55 | 3.97 | 15% | 40% | -8.2% |

### `da2-metric-base_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 3.24 | 3.35 | 43% | 9% | +33.3% |
| 10-20 m | 41 | 100% | 1.33 | 1.76 | 13% | 56% | +6.3% |
| 20-30 m | 49 | 100% | 1.35 | 3.29 | 13% | 71% | +11.2% |
| 30-50 m | 74 | 100% | 3.70 | 4.94 | 12% | 53% | +9.5% |
| 50+ m | 31 | 100% | 3.90 | 5.34 | 9% | 68% | +5.0% |

### `da2-metric-base_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.28 | 1.28 | 17% | 9% | +2.4% |
| 10-20 m | 41 | 100% | 1.46 | 1.40 | 10% | 51% | -3.4% |
| 20-30 m | 49 | 100% | 1.27 | 1.79 | 7% | 78% | +0.5% |
| 30-50 m | 74 | 100% | 1.87 | 3.37 | 8% | 65% | +2.0% |
| 50+ m | 31 | 100% | 2.19 | 3.98 | 7% | 74% | -0.0% |

### `da2-metric-base_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.69 | 1.75 | 23% | 9% | +10.1% |
| 10-20 m | 41 | 100% | 1.27 | 1.44 | 10% | 51% | -0.6% |
| 20-30 m | 49 | 100% | 1.19 | 1.96 | 8% | 78% | +3.5% |
| 30-50 m | 74 | 100% | 2.14 | 3.74 | 9% | 66% | +4.9% |
| 50+ m | 31 | 100% | 2.75 | 4.50 | 8% | 74% | +2.1% |

## `da2-metric-base_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 1.24 | 1.65 | 29% | 23% | +25.6% |
| 10-20 m | 297 | 100% | 2.08 | 2.55 | 17% | 37% | +12.5% |
| 20-30 m | 226 | 100% | 3.04 | 4.27 | 17% | 38% | +10.0% |
| 30-50 m | 319 | 100% | 4.99 | 5.88 | 15% | 40% | +5.9% |
| 50+ m | 135 | 100% | 5.16 | 6.96 | 12% | 56% | -1.5% |

## `da2-metric-base_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.40 | 3.73 | 15% | 42% | +7.0% |
| pedestrian | 126 | 100% | 3.92 | 4.74 | 35% | 10% | +33.9% |
| van | 84 | 100% | 3.38 | 4.93 | 19% | 42% | +10.0% |
| truck | 42 | 100% | 5.62 | 6.31 | 23% | 26% | +16.8% |
| cyclist | 20 | 100% | 8.55 | 9.65 | 43% | 5% | +40.9% |

## `da2-metric-base_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.76 | 0.92 | 17% | 44% | +10.7% |
| 10-20 m | 297 | 100% | 1.29 | 1.60 | 11% | 56% | +1.0% |
| 20-30 m | 226 | 100% | 2.31 | 3.13 | 13% | 53% | -0.2% |
| 30-50 m | 319 | 100% | 4.18 | 5.14 | 13% | 48% | -2.2% |
| 50+ m | 135 | 100% | 5.04 | 7.86 | 13% | 56% | -7.3% |

## `da2-metric-base_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.90 | 3.39 | 12% | 55% | -1.6% |
| pedestrian | 126 | 100% | 1.71 | 2.44 | 16% | 31% | +13.1% |
| van | 84 | 100% | 2.58 | 4.57 | 16% | 48% | -0.5% |
| truck | 42 | 100% | 3.55 | 4.20 | 15% | 50% | +7.8% |
| cyclist | 20 | 100% | 4.73 | 5.20 | 21% | 35% | +16.8% |

## `da2-metric-base_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.92 | 1.13 | 21% | 36% | +15.4% |
| 10-20 m | 297 | 100% | 1.48 | 1.86 | 13% | 50% | +4.7% |
| 20-30 m | 226 | 100% | 2.45 | 3.36 | 14% | 46% | +3.8% |
| 30-50 m | 319 | 100% | 4.38 | 5.20 | 13% | 45% | +1.1% |
| 50+ m | 135 | 100% | 4.73 | 7.24 | 12% | 59% | -4.6% |

## `da2-metric-base_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.96 | 3.36 | 13% | 50% | +1.5% |
| pedestrian | 126 | 100% | 2.51 | 3.15 | 22% | 20% | +20.3% |
| van | 84 | 100% | 2.45 | 4.37 | 16% | 54% | +4.1% |
| truck | 42 | 100% | 4.44 | 4.85 | 17% | 45% | +10.8% |
| cyclist | 20 | 100% | 5.82 | 7.05 | 30% | 15% | +26.6% |

## `da2-metric-base_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.31 | 1.70 | 22% | 15% | -2.0% |
| 10-20 m | 299 | 100% | 1.59 | 2.09 | 14% | 45% | -0.7% |
| 20-30 m | 246 | 100% | 2.52 | 3.68 | 15% | 50% | +2.9% |
| 30-50 m | 329 | 100% | 4.17 | 5.19 | 13% | 46% | +0.4% |
| 50+ m | 155 | 100% | 5.07 | 7.24 | 12% | 59% | -4.6% |

## `da2-metric-base_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.08 | 3.61 | 12% | 49% | -4.5% |
| pedestrian | 126 | 100% | 3.48 | 4.28 | 30% | 14% | +28.2% |
| van | 84 | 100% | 3.15 | 4.86 | 14% | 42% | -5.1% |
| truck | 42 | 100% | 2.90 | 4.71 | 13% | 64% | -2.9% |
| cyclist | 20 | 100% | 7.57 | 8.87 | 38% | 5% | +35.2% |

## `da2-metric-base_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.43 | 1.51 | 21% | 15% | -14.6% |
| 10-20 m | 299 | 100% | 1.75 | 2.22 | 15% | 37% | -10.8% |
| 20-30 m | 246 | 100% | 2.33 | 3.24 | 13% | 52% | -7.1% |
| 30-50 m | 329 | 100% | 3.83 | 5.16 | 13% | 48% | -7.3% |
| 50+ m | 155 | 100% | 6.11 | 8.53 | 14% | 49% | -10.7% |

## `da2-metric-base_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.45 | 4.07 | 15% | 41% | -12.1% |
| pedestrian | 126 | 100% | 1.33 | 2.12 | 13% | 49% | +8.4% |
| van | 84 | 100% | 3.19 | 5.43 | 17% | 35% | -14.1% |
| truck | 42 | 100% | 2.73 | 4.34 | 12% | 57% | -10.4% |
| cyclist | 20 | 100% | 3.72 | 4.67 | 18% | 35% | +12.2% |

## `da2-metric-base_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.47 | 1.56 | 21% | 11% | -10.6% |
| 10-20 m | 299 | 100% | 1.76 | 2.13 | 15% | 39% | -7.5% |
| 20-30 m | 246 | 100% | 2.20 | 3.14 | 13% | 56% | -3.6% |
| 30-50 m | 329 | 100% | 3.77 | 4.94 | 12% | 50% | -4.1% |
| 50+ m | 155 | 100% | 5.26 | 7.75 | 13% | 55% | -8.0% |

## `da2-metric-base_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.37 | 3.75 | 14% | 46% | -9.4% |
| pedestrian | 126 | 100% | 1.94 | 2.74 | 18% | 29% | +15.3% |
| van | 84 | 100% | 3.15 | 4.92 | 15% | 38% | -10.1% |
| truck | 42 | 100% | 2.03 | 3.95 | 11% | 64% | -7.9% |
| cyclist | 20 | 100% | 4.85 | 6.28 | 25% | 15% | +21.5% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| da2-metric-base_median | 103.173 |
| da2-metric-base_p10 | 2.891 |
| da2-metric-base_p25 | 2.721 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
