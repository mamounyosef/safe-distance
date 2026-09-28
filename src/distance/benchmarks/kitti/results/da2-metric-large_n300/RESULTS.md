# KITTI distance benchmark: `da2-metric-large_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da2-metric-large_median`, `da2-metric-large_p10`, `da2-metric-large_p25` |
| Depth model | `da2-metric-large`, not given our focal length; inference 266.8 ms median, 556.2 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:07:57+00:00 |

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
| da2-metric-large_median | 1187 | 100% | 2.50 | 3.67 | 17% | 42% | +11.7% |
| da2-metric-large_p10 | 1187 | 100% | 1.71 | 3.10 | 12% | 54% | +1.6% |
| da2-metric-large_p25 | 1187 | 100% | 1.93 | 3.14 | 13% | 50% | +5.3% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median | 1187 | 100% | 2.25 | 3.46 | 14% | 49% | +0.2% |
| da2-metric-large_p10 | 1187 | 100% | 2.25 | 3.69 | 14% | 45% | -8.8% |
| da2-metric-large_p25 | 1187 | 100% | 2.23 | 3.43 | 13% | 46% | -5.4% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da2-metric-large_median | 206 | 100% | 3.22 | 4.17 | 16% | 42% | +15.3% |
| in path / da2-metric-large_p10 | 206 | 100% | 1.88 | 2.90 | 9% | 65% | +7.3% |
| in path / da2-metric-large_p25 | 206 | 100% | 2.42 | 3.23 | 11% | 53% | +10.1% |
| beside / da2-metric-large_median | 981 | 100% | 2.27 | 3.56 | 18% | 42% | +11.0% |
| beside / da2-metric-large_p10 | 981 | 100% | 1.67 | 3.15 | 13% | 52% | +0.4% |
| beside / da2-metric-large_p25 | 981 | 100% | 1.82 | 3.12 | 14% | 49% | +4.4% |

### `da2-metric-large_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 3.21 | 3.19 | 43% | 7% | +42.6% |
| 10-20 m | 44 | 100% | 2.08 | 2.59 | 18% | 32% | +18.4% |
| 20-30 m | 46 | 100% | 2.67 | 3.59 | 14% | 50% | +14.2% |
| 30-50 m | 76 | 100% | 4.33 | 4.85 | 12% | 45% | +11.1% |
| 50+ m | 25 | 100% | 5.98 | 6.57 | 11% | 56% | +7.9% |

### `da2-metric-large_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.51 | 1.42 | 19% | 27% | +19.4% |
| 10-20 m | 44 | 100% | 0.84 | 1.05 | 8% | 70% | +7.3% |
| 20-30 m | 46 | 100% | 1.48 | 1.86 | 8% | 72% | +6.5% |
| 30-50 m | 76 | 100% | 3.17 | 3.73 | 9% | 68% | +6.5% |
| 50+ m | 25 | 100% | 5.56 | 6.40 | 10% | 52% | +4.0% |

### `da2-metric-large_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 2.19 | 2.15 | 29% | 20% | +28.9% |
| 10-20 m | 44 | 100% | 1.35 | 1.46 | 11% | 52% | +10.4% |
| 20-30 m | 46 | 100% | 1.86 | 2.41 | 10% | 61% | +9.1% |
| 30-50 m | 76 | 100% | 3.48 | 4.01 | 10% | 54% | +8.2% |
| 50+ m | 25 | 100% | 5.17 | 6.13 | 10% | 56% | +6.0% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da2-metric-large_median | 206 | 100% | 2.11 | 2.97 | 11% | 66% | +6.7% |
| in path / da2-metric-large_p10 | 206 | 100% | 1.74 | 2.51 | 8% | 71% | -0.7% |
| in path / da2-metric-large_p25 | 206 | 100% | 1.80 | 2.53 | 9% | 68% | +1.9% |
| beside / da2-metric-large_median | 981 | 100% | 2.29 | 3.56 | 14% | 46% | -1.1% |
| beside / da2-metric-large_p10 | 981 | 100% | 2.45 | 3.93 | 15% | 40% | -10.5% |
| beside / da2-metric-large_p25 | 981 | 100% | 2.39 | 3.62 | 14% | 42% | -7.0% |

### `da2-metric-large_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 3.57 | 2.96 | 37% | 18% | +27.8% |
| 10-20 m | 41 | 100% | 1.17 | 1.81 | 14% | 59% | +6.5% |
| 20-30 m | 49 | 100% | 1.55 | 2.59 | 10% | 76% | +7.9% |
| 30-50 m | 74 | 100% | 2.77 | 3.22 | 8% | 68% | +4.6% |
| 50+ m | 31 | 100% | 2.87 | 4.53 | 8% | 71% | +2.8% |

### `da2-metric-large_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.47 | 1.41 | 18% | 0% | +4.3% |
| 10-20 m | 41 | 100% | 1.37 | 1.33 | 9% | 56% | -2.9% |
| 20-30 m | 49 | 100% | 1.34 | 1.56 | 6% | 84% | -0.7% |
| 30-50 m | 74 | 100% | 2.52 | 2.96 | 7% | 81% | +0.1% |
| 50+ m | 31 | 100% | 3.95 | 4.87 | 8% | 71% | -1.3% |

### `da2-metric-large_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.85 | 2.02 | 26% | 0% | +13.5% |
| 10-20 m | 41 | 100% | 1.44 | 1.45 | 11% | 56% | -0.1% |
| 20-30 m | 49 | 100% | 1.29 | 1.67 | 7% | 82% | +2.0% |
| 30-50 m | 74 | 100% | 2.52 | 2.95 | 7% | 74% | +1.8% |
| 50+ m | 31 | 100% | 3.42 | 4.45 | 7% | 71% | +0.6% |

## `da2-metric-large_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 1.26 | 1.75 | 31% | 21% | +28.4% |
| 10-20 m | 297 | 100% | 2.01 | 2.66 | 18% | 37% | +14.5% |
| 20-30 m | 226 | 100% | 2.69 | 3.72 | 15% | 48% | +10.0% |
| 30-50 m | 319 | 100% | 3.52 | 4.37 | 11% | 52% | +4.7% |
| 50+ m | 135 | 100% | 5.54 | 7.11 | 12% | 52% | -1.2% |

## `da2-metric-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.09 | 3.13 | 13% | 48% | +7.2% |
| pedestrian | 126 | 100% | 4.10 | 4.86 | 38% | 10% | +36.9% |
| van | 84 | 100% | 2.59 | 5.04 | 19% | 43% | +12.1% |
| truck | 42 | 100% | 4.81 | 6.29 | 24% | 29% | +20.2% |
| cyclist | 20 | 100% | 8.78 | 9.28 | 43% | 10% | +39.9% |

## `da2-metric-large_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.78 | 0.93 | 18% | 42% | +12.4% |
| 10-20 m | 297 | 100% | 1.28 | 1.53 | 10% | 57% | +2.8% |
| 20-30 m | 226 | 100% | 1.86 | 2.58 | 10% | 59% | +0.1% |
| 30-50 m | 319 | 100% | 3.62 | 4.25 | 11% | 57% | -2.0% |
| 50+ m | 135 | 100% | 5.91 | 8.11 | 14% | 50% | -7.1% |

## `da2-metric-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.62 | 3.03 | 11% | 58% | -0.7% |
| pedestrian | 126 | 100% | 1.68 | 2.20 | 16% | 31% | +13.6% |
| van | 84 | 100% | 1.89 | 4.29 | 14% | 55% | +1.1% |
| truck | 42 | 100% | 3.15 | 4.41 | 16% | 55% | +10.6% |
| cyclist | 20 | 100% | 4.22 | 4.65 | 19% | 30% | +14.3% |

## `da2-metric-large_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.99 | 1.19 | 22% | 35% | +17.9% |
| 10-20 m | 297 | 100% | 1.49 | 1.89 | 13% | 49% | +6.9% |
| 20-30 m | 226 | 100% | 2.02 | 2.76 | 11% | 55% | +3.8% |
| 30-50 m | 319 | 100% | 3.43 | 4.05 | 10% | 55% | +0.9% |
| 50+ m | 135 | 100% | 5.39 | 7.42 | 13% | 55% | -4.5% |

## `da2-metric-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.63 | 2.89 | 11% | 55% | +2.2% |
| pedestrian | 126 | 100% | 2.72 | 3.06 | 23% | 17% | +22.1% |
| van | 84 | 100% | 2.06 | 4.32 | 15% | 52% | +5.7% |
| truck | 42 | 100% | 3.58 | 4.80 | 18% | 45% | +13.8% |
| cyclist | 20 | 100% | 6.11 | 6.70 | 30% | 15% | +26.8% |

## `da2-metric-large_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.31 | 1.73 | 22% | 22% | +0.3% |
| 10-20 m | 299 | 100% | 1.66 | 2.15 | 15% | 45% | +1.2% |
| 20-30 m | 246 | 100% | 1.90 | 3.13 | 13% | 60% | +3.2% |
| 30-50 m | 329 | 100% | 3.36 | 4.03 | 10% | 57% | -0.6% |
| 50+ m | 155 | 100% | 5.87 | 7.05 | 12% | 53% | -4.8% |

## `da2-metric-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.84 | 3.05 | 11% | 56% | -4.4% |
| pedestrian | 126 | 100% | 3.60 | 4.39 | 32% | 13% | +31.0% |
| van | 84 | 100% | 2.59 | 4.86 | 14% | 38% | -3.2% |
| truck | 42 | 100% | 2.53 | 4.36 | 13% | 55% | -0.7% |
| cyclist | 20 | 100% | 7.80 | 8.50 | 37% | 10% | +34.1% |

## `da2-metric-large_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.39 | 1.48 | 20% | 13% | -13.4% |
| 10-20 m | 299 | 100% | 1.66 | 2.02 | 14% | 41% | -9.1% |
| 20-30 m | 246 | 100% | 2.00 | 2.76 | 11% | 58% | -6.8% |
| 30-50 m | 329 | 100% | 3.54 | 4.62 | 12% | 54% | -7.1% |
| 50+ m | 155 | 100% | 6.67 | 8.65 | 14% | 45% | -10.5% |

## `da2-metric-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.33 | 3.75 | 14% | 45% | -11.3% |
| pedestrian | 126 | 100% | 1.21 | 1.84 | 12% | 48% | +8.8% |
| van | 84 | 100% | 3.28 | 5.35 | 16% | 36% | -12.7% |
| truck | 42 | 100% | 2.92 | 4.33 | 12% | 64% | -8.5% |
| cyclist | 20 | 100% | 3.23 | 4.16 | 15% | 30% | +9.7% |

## `da2-metric-large_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.44 | 1.57 | 21% | 11% | -8.5% |
| 10-20 m | 299 | 100% | 1.75 | 2.07 | 14% | 42% | -5.4% |
| 20-30 m | 246 | 100% | 1.86 | 2.62 | 10% | 61% | -3.3% |
| 30-50 m | 329 | 100% | 3.36 | 4.16 | 11% | 56% | -4.3% |
| 50+ m | 155 | 100% | 5.72 | 7.68 | 13% | 50% | -8.1% |

## `da2-metric-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.16 | 3.33 | 12% | 50% | -8.8% |
| pedestrian | 126 | 100% | 2.19 | 2.63 | 19% | 26% | +16.9% |
| van | 84 | 100% | 2.93 | 4.87 | 14% | 33% | -8.7% |
| truck | 42 | 100% | 2.32 | 3.76 | 11% | 62% | -5.9% |
| cyclist | 20 | 100% | 5.18 | 6.04 | 25% | 20% | +21.6% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| da2-metric-large_median | 270.336 |
| da2-metric-large_p10 | 2.596 |
| da2-metric-large_p25 | 2.403 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
