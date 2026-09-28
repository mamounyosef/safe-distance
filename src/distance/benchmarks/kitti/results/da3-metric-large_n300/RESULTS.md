# KITTI distance benchmark: `da3-metric-large_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da3-metric-large_median`, `da3-metric-large_p10`, `da3-metric-large_p25` |
| Depth model | `da3-metric-large`, given our focal length; inference 50.5 ms median, 52.9 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:08:40+00:00 |

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
| da3-metric-large_median | 1187 | 100% | 2.01 | 3.36 | 12% | 49% | -9.0% |
| da3-metric-large_p10 | 1187 | 100% | 2.75 | 4.50 | 16% | 31% | -15.2% |
| da3-metric-large_p25 | 1187 | 100% | 2.39 | 3.97 | 14% | 39% | -12.8% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median | 1187 | 100% | 3.66 | 4.96 | 19% | 20% | -18.1% |
| da3-metric-large_p10 | 1187 | 100% | 4.68 | 6.32 | 24% | 10% | -23.5% |
| da3-metric-large_p25 | 1187 | 100% | 4.25 | 5.73 | 22% | 12% | -21.5% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da3-metric-large_median | 206 | 100% | 1.92 | 3.00 | 9% | 67% | -4.2% |
| in path / da3-metric-large_p10 | 206 | 100% | 1.95 | 3.52 | 10% | 56% | -8.7% |
| in path / da3-metric-large_p25 | 206 | 100% | 1.91 | 3.29 | 9% | 62% | -7.2% |
| beside / da3-metric-large_median | 981 | 100% | 2.02 | 3.44 | 13% | 46% | -10.0% |
| beside / da3-metric-large_p10 | 981 | 100% | 2.87 | 4.71 | 17% | 25% | -16.5% |
| beside / da3-metric-large_p25 | 981 | 100% | 2.50 | 4.11 | 15% | 34% | -14.0% |

### `da3-metric-large_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.35 | 0.39 | 6% | 80% | -4.3% |
| 10-20 m | 44 | 100% | 0.79 | 0.95 | 6% | 84% | -3.7% |
| 20-30 m | 46 | 100% | 1.59 | 2.21 | 9% | 72% | -0.8% |
| 30-50 m | 76 | 100% | 3.29 | 3.81 | 10% | 61% | -5.1% |
| 50+ m | 25 | 100% | 5.95 | 7.18 | 11% | 40% | -8.1% |

### `da3-metric-large_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.46 | 0.56 | 8% | 67% | -8.2% |
| 10-20 m | 44 | 100% | 1.14 | 1.28 | 9% | 68% | -7.4% |
| 20-30 m | 46 | 100% | 1.87 | 2.13 | 8% | 63% | -6.2% |
| 30-50 m | 76 | 100% | 4.11 | 4.45 | 11% | 49% | -9.3% |
| 50+ m | 25 | 100% | 7.05 | 8.94 | 14% | 36% | -14.0% |

### `da3-metric-large_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.40 | 0.47 | 7% | 73% | -6.8% |
| 10-20 m | 44 | 100% | 1.06 | 1.18 | 8% | 80% | -6.2% |
| 20-30 m | 46 | 100% | 1.77 | 2.15 | 8% | 63% | -4.5% |
| 30-50 m | 76 | 100% | 3.81 | 4.10 | 10% | 55% | -7.9% |
| 50+ m | 25 | 100% | 6.80 | 8.33 | 13% | 40% | -12.0% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / da3-metric-large_median | 206 | 100% | 3.20 | 4.49 | 14% | 33% | -11.2% |
| in path / da3-metric-large_p10 | 206 | 100% | 3.80 | 5.31 | 16% | 22% | -15.5% |
| in path / da3-metric-large_p25 | 206 | 100% | 3.66 | 4.96 | 15% | 25% | -14.1% |
| beside / da3-metric-large_median | 981 | 100% | 3.73 | 5.06 | 20% | 18% | -19.6% |
| beside / da3-metric-large_p10 | 981 | 100% | 4.75 | 6.53 | 25% | 7% | -25.2% |
| beside / da3-metric-large_p25 | 981 | 100% | 4.33 | 5.89 | 23% | 10% | -23.0% |

### `da3-metric-large_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.07 | 1.46 | 19% | 9% | -19.5% |
| 10-20 m | 41 | 100% | 2.12 | 2.23 | 15% | 20% | -14.6% |
| 20-30 m | 49 | 100% | 2.67 | 2.82 | 11% | 39% | -7.8% |
| 30-50 m | 74 | 100% | 4.78 | 5.28 | 13% | 38% | -9.6% |
| 50+ m | 31 | 100% | 8.05 | 9.30 | 14% | 39% | -13.2% |

### `da3-metric-large_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.35 | 1.70 | 23% | 0% | -22.6% |
| 10-20 m | 41 | 100% | 2.35 | 2.53 | 17% | 5% | -17.2% |
| 20-30 m | 49 | 100% | 3.35 | 3.36 | 13% | 35% | -12.4% |
| 30-50 m | 74 | 100% | 5.77 | 5.94 | 15% | 28% | -14.1% |
| 50+ m | 31 | 100% | 10.25 | 11.80 | 19% | 19% | -18.7% |

### `da3-metric-large_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.23 | 1.61 | 21% | 0% | -21.4% |
| 10-20 m | 41 | 100% | 2.31 | 2.42 | 16% | 7% | -16.3% |
| 20-30 m | 49 | 100% | 3.16 | 3.23 | 13% | 33% | -11.1% |
| 30-50 m | 74 | 100% | 5.59 | 5.56 | 14% | 31% | -12.6% |
| 50+ m | 31 | 100% | 9.41 | 10.80 | 17% | 29% | -16.7% |

## `da3-metric-large_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.65 | 0.82 | 13% | 46% | -6.6% |
| 10-20 m | 297 | 100% | 1.34 | 1.62 | 11% | 55% | -9.4% |
| 20-30 m | 226 | 100% | 2.21 | 2.87 | 11% | 55% | -7.6% |
| 30-50 m | 319 | 100% | 4.14 | 4.85 | 12% | 47% | -10.1% |
| 50+ m | 135 | 100% | 7.47 | 8.45 | 14% | 38% | -11.8% |

## `da3-metric-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.08 | 3.33 | 12% | 52% | -9.1% |
| pedestrian | 126 | 100% | 1.39 | 1.88 | 13% | 40% | -10.2% |
| van | 84 | 100% | 2.64 | 4.55 | 15% | 38% | -10.2% |
| truck | 42 | 100% | 2.92 | 5.89 | 16% | 43% | -8.6% |
| cyclist | 20 | 100% | 2.57 | 3.78 | 15% | 50% | +4.8% |

## `da3-metric-large_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.94 | 1.10 | 17% | 21% | -14.6% |
| 10-20 m | 297 | 100% | 1.84 | 2.13 | 14% | 39% | -13.9% |
| 20-30 m | 226 | 100% | 3.20 | 3.67 | 15% | 37% | -13.8% |
| 30-50 m | 319 | 100% | 5.68 | 6.61 | 17% | 28% | -16.2% |
| 50+ m | 135 | 100% | 10.41 | 11.46 | 19% | 24% | -18.8% |

## `da3-metric-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.98 | 4.62 | 16% | 31% | -15.4% |
| pedestrian | 126 | 100% | 1.59 | 2.19 | 15% | 29% | -14.3% |
| van | 84 | 100% | 3.77 | 5.97 | 18% | 17% | -17.3% |
| truck | 42 | 100% | 4.42 | 6.51 | 18% | 33% | -12.0% |
| cyclist | 20 | 100% | 2.09 | 3.33 | 13% | 60% | -8.8% |

## `da3-metric-large_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.81 | 1.00 | 15% | 31% | -12.0% |
| 10-20 m | 297 | 100% | 1.62 | 1.91 | 13% | 47% | -12.2% |
| 20-30 m | 226 | 100% | 2.76 | 3.24 | 13% | 44% | -11.3% |
| 30-50 m | 319 | 100% | 5.10 | 5.75 | 15% | 36% | -13.7% |
| 50+ m | 135 | 100% | 9.58 | 10.11 | 17% | 33% | -16.1% |

## `da3-metric-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.57 | 4.03 | 14% | 41% | -13.0% |
| pedestrian | 126 | 100% | 1.48 | 2.08 | 14% | 33% | -12.8% |
| van | 84 | 100% | 3.09 | 5.20 | 16% | 27% | -14.6% |
| truck | 42 | 100% | 4.11 | 6.28 | 17% | 38% | -10.8% |
| cyclist | 20 | 100% | 1.85 | 2.89 | 10% | 60% | -3.0% |

## `da3-metric-large_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.19 | 2.20 | 30% | 2% | -30.2% |
| 10-20 m | 299 | 100% | 2.86 | 3.04 | 21% | 11% | -20.3% |
| 20-30 m | 246 | 100% | 3.64 | 4.00 | 16% | 26% | -14.3% |
| 30-50 m | 329 | 100% | 5.74 | 6.27 | 16% | 30% | -14.5% |
| 50+ m | 155 | 100% | 9.87 | 10.23 | 17% | 30% | -15.4% |

## `da3-metric-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.76 | 4.95 | 19% | 20% | -18.5% |
| pedestrian | 126 | 100% | 1.83 | 2.28 | 16% | 26% | -13.8% |
| van | 84 | 100% | 5.28 | 6.78 | 22% | 11% | -21.8% |
| truck | 42 | 100% | 9.05 | 10.27 | 24% | 17% | -23.9% |
| cyclist | 20 | 100% | 2.62 | 3.75 | 14% | 45% | +0.7% |

## `da3-metric-large_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.58 | 2.57 | 36% | 1% | -36.0% |
| 10-20 m | 299 | 100% | 3.36 | 3.58 | 24% | 4% | -24.2% |
| 20-30 m | 246 | 100% | 4.70 | 5.05 | 20% | 13% | -19.8% |
| 30-50 m | 329 | 100% | 7.53 | 8.13 | 21% | 16% | -20.4% |
| 50+ m | 155 | 100% | 12.79 | 13.57 | 22% | 12% | -22.1% |

## `da3-metric-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 4.80 | 6.46 | 24% | 9% | -24.1% |
| pedestrian | 126 | 100% | 2.10 | 2.66 | 19% | 15% | -17.8% |
| van | 84 | 100% | 6.77 | 8.50 | 27% | 4% | -27.5% |
| truck | 42 | 100% | 9.42 | 11.09 | 26% | 7% | -26.3% |
| cyclist | 20 | 100% | 2.47 | 3.70 | 14% | 45% | -12.3% |

## `da3-metric-large_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.49 | 2.45 | 34% | 1% | -34.1% |
| 10-20 m | 299 | 100% | 3.18 | 3.37 | 23% | 6% | -22.8% |
| 20-30 m | 246 | 100% | 4.19 | 4.60 | 18% | 15% | -17.6% |
| 30-50 m | 329 | 100% | 6.91 | 7.26 | 18% | 19% | -17.9% |
| 50+ m | 155 | 100% | 11.79 | 12.16 | 20% | 19% | -19.6% |

## `da3-metric-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 4.41 | 5.82 | 22% | 12% | -21.9% |
| pedestrian | 126 | 100% | 1.98 | 2.53 | 18% | 17% | -16.3% |
| van | 84 | 100% | 6.06 | 7.66 | 25% | 7% | -25.3% |
| truck | 42 | 100% | 9.28 | 10.79 | 25% | 7% | -25.4% |
| cyclist | 20 | 100% | 1.83 | 3.03 | 11% | 55% | -6.8% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| da3-metric-large_median | 53.734 |
| da3-metric-large_p10 | 2.928 |
| da3-metric-large_p25 | 2.798 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
