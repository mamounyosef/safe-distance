# KITTI distance benchmark: `unidepth-v2-small_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-small_median`, `unidepth-v2-small_p10`, `unidepth-v2-small_p25` |
| Depth model | `unidepth-v2-small`, given our focal length; inference 60.1 ms median, 71.1 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:15:26+00:00 |

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
| unidepth-v2-small_median | 1187 | 100% | 1.31 | 2.45 | 9% | 64% | -3.1% |
| unidepth-v2-small_p10 | 1187 | 100% | 1.73 | 2.98 | 12% | 53% | -9.4% |
| unidepth-v2-small_p25 | 1187 | 100% | 1.53 | 2.63 | 10% | 58% | -7.2% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median | 1187 | 100% | 2.75 | 3.58 | 15% | 37% | -12.7% |
| unidepth-v2-small_p10 | 1187 | 100% | 3.40 | 4.51 | 19% | 26% | -18.2% |
| unidepth-v2-small_p25 | 1187 | 100% | 3.15 | 4.06 | 17% | 31% | -16.2% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-small_median | 206 | 100% | 1.23 | 2.36 | 7% | 84% | +2.1% |
| in path / unidepth-v2-small_p10 | 206 | 100% | 1.25 | 1.86 | 6% | 85% | -2.7% |
| in path / unidepth-v2-small_p25 | 206 | 100% | 1.17 | 1.89 | 6% | 85% | -1.2% |
| beside / unidepth-v2-small_median | 981 | 100% | 1.37 | 2.47 | 10% | 60% | -4.2% |
| beside / unidepth-v2-small_p10 | 981 | 100% | 1.92 | 3.21 | 13% | 46% | -10.8% |
| beside / unidepth-v2-small_p25 | 981 | 100% | 1.64 | 2.79 | 11% | 53% | -8.4% |

### `unidepth-v2-small_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.23 | 0.24 | 4% | 100% | -2.0% |
| 10-20 m | 44 | 100% | 0.61 | 0.76 | 5% | 86% | -2.5% |
| 20-30 m | 46 | 100% | 0.90 | 1.73 | 7% | 89% | +3.1% |
| 30-50 m | 76 | 100% | 2.14 | 3.16 | 8% | 79% | +3.9% |
| 50+ m | 25 | 100% | 3.80 | 5.13 | 8% | 76% | +4.9% |

### `unidepth-v2-small_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.36 | 0.43 | 6% | 87% | -6.3% |
| 10-20 m | 44 | 100% | 0.93 | 1.03 | 7% | 80% | -6.5% |
| 20-30 m | 46 | 100% | 0.99 | 1.18 | 5% | 96% | -2.1% |
| 30-50 m | 76 | 100% | 1.93 | 2.52 | 6% | 82% | -1.0% |
| 50+ m | 25 | 100% | 2.60 | 3.43 | 6% | 88% | +0.1% |

### `unidepth-v2-small_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.32 | 0.34 | 5% | 87% | -4.8% |
| 10-20 m | 44 | 100% | 0.86 | 0.94 | 6% | 80% | -5.2% |
| 20-30 m | 46 | 100% | 1.00 | 1.19 | 5% | 96% | -0.8% |
| 30-50 m | 76 | 100% | 1.94 | 2.54 | 6% | 83% | +0.6% |
| 50+ m | 25 | 100% | 2.94 | 3.82 | 6% | 80% | +1.8% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-small_median | 206 | 100% | 2.36 | 2.98 | 10% | 58% | -5.4% |
| in path / unidepth-v2-small_p10 | 206 | 100% | 2.66 | 3.06 | 11% | 49% | -9.8% |
| in path / unidepth-v2-small_p25 | 206 | 100% | 2.58 | 2.89 | 10% | 53% | -8.4% |
| beside / unidepth-v2-small_median | 981 | 100% | 2.83 | 3.71 | 16% | 32% | -14.2% |
| beside / unidepth-v2-small_p10 | 981 | 100% | 3.57 | 4.81 | 21% | 21% | -20.0% |
| beside / unidepth-v2-small_p25 | 981 | 100% | 3.27 | 4.30 | 19% | 26% | -17.8% |

### `unidepth-v2-small_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.85 | 1.26 | 17% | 27% | -16.9% |
| 10-20 m | 41 | 100% | 2.03 | 2.03 | 14% | 29% | -13.4% |
| 20-30 m | 49 | 100% | 2.12 | 2.33 | 9% | 61% | -4.1% |
| 30-50 m | 74 | 100% | 2.52 | 3.19 | 8% | 70% | -2.4% |
| 50+ m | 31 | 100% | 4.33 | 5.38 | 9% | 71% | -0.0% |

### `unidepth-v2-small_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.95 | 1.51 | 20% | 18% | -20.2% |
| 10-20 m | 41 | 100% | 2.54 | 2.46 | 17% | 12% | -16.7% |
| 20-30 m | 49 | 100% | 2.55 | 2.44 | 10% | 49% | -8.8% |
| 30-50 m | 74 | 100% | 3.05 | 3.41 | 8% | 59% | -7.0% |
| 50+ m | 31 | 100% | 3.87 | 4.54 | 7% | 81% | -5.1% |

### `unidepth-v2-small_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.92 | 1.41 | 19% | 18% | -18.9% |
| 10-20 m | 41 | 100% | 2.38 | 2.32 | 16% | 20% | -15.7% |
| 20-30 m | 49 | 100% | 2.34 | 2.21 | 9% | 55% | -7.6% |
| 30-50 m | 74 | 100% | 2.88 | 3.13 | 8% | 66% | -5.5% |
| 50+ m | 31 | 100% | 4.12 | 4.66 | 8% | 77% | -3.3% |

## `unidepth-v2-small_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.52 | 0.70 | 12% | 56% | -3.0% |
| 10-20 m | 297 | 100% | 0.85 | 1.27 | 8% | 70% | -5.9% |
| 20-30 m | 226 | 100% | 1.38 | 2.16 | 9% | 67% | -2.6% |
| 30-50 m | 319 | 100% | 2.67 | 3.54 | 9% | 64% | -1.8% |
| 50+ m | 135 | 100% | 4.29 | 5.70 | 10% | 59% | -1.6% |

## `unidepth-v2-small_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.34 | 2.44 | 9% | 65% | -3.5% |
| pedestrian | 126 | 100% | 0.86 | 1.45 | 10% | 62% | -5.1% |
| van | 84 | 100% | 1.89 | 2.87 | 11% | 54% | -4.5% |
| truck | 42 | 100% | 1.82 | 3.33 | 11% | 76% | +2.2% |
| cyclist | 20 | 100% | 3.44 | 5.57 | 22% | 45% | +17.7% |

## `unidepth-v2-small_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.86 | 0.98 | 15% | 31% | -11.6% |
| 10-20 m | 297 | 100% | 1.39 | 1.73 | 12% | 52% | -11.4% |
| 20-30 m | 226 | 100% | 2.01 | 2.62 | 10% | 60% | -8.3% |
| 30-50 m | 319 | 100% | 2.86 | 4.11 | 11% | 61% | -7.7% |
| 50+ m | 135 | 100% | 5.37 | 6.75 | 11% | 56% | -7.3% |

## `unidepth-v2-small_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.83 | 3.06 | 12% | 52% | -9.7% |
| pedestrian | 126 | 100% | 1.12 | 1.57 | 11% | 56% | -9.0% |
| van | 84 | 100% | 2.47 | 3.89 | 13% | 49% | -11.8% |
| truck | 42 | 100% | 1.91 | 3.55 | 12% | 69% | -3.5% |
| cyclist | 20 | 100% | 2.01 | 3.03 | 12% | 60% | -2.2% |

## `unidepth-v2-small_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.74 | 0.88 | 14% | 40% | -8.9% |
| 10-20 m | 297 | 100% | 1.19 | 1.51 | 10% | 59% | -9.5% |
| 20-30 m | 226 | 100% | 1.65 | 2.29 | 9% | 66% | -6.1% |
| 30-50 m | 319 | 100% | 2.71 | 3.60 | 9% | 64% | -5.5% |
| 50+ m | 135 | 100% | 4.90 | 6.13 | 10% | 59% | -5.1% |

## `unidepth-v2-small_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.63 | 2.69 | 10% | 58% | -7.5% |
| pedestrian | 126 | 100% | 0.91 | 1.48 | 10% | 60% | -7.4% |
| van | 84 | 100% | 2.15 | 3.30 | 11% | 51% | -9.0% |
| truck | 42 | 100% | 1.75 | 3.36 | 11% | 71% | -1.6% |
| cyclist | 20 | 100% | 1.55 | 2.90 | 10% | 60% | +5.1% |

## `unidepth-v2-small_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.98 | 1.98 | 27% | 5% | -27.1% |
| 10-20 m | 299 | 100% | 2.52 | 2.67 | 18% | 18% | -17.8% |
| 20-30 m | 246 | 100% | 2.83 | 3.23 | 13% | 41% | -9.3% |
| 30-50 m | 329 | 100% | 3.23 | 4.09 | 10% | 57% | -7.0% |
| 50+ m | 155 | 100% | 5.34 | 6.46 | 11% | 55% | -5.7% |

## `unidepth-v2-small_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.81 | 3.58 | 15% | 36% | -13.4% |
| pedestrian | 126 | 100% | 1.23 | 1.76 | 12% | 44% | -8.9% |
| van | 84 | 100% | 4.00 | 4.69 | 17% | 32% | -16.8% |
| truck | 42 | 100% | 4.73 | 6.02 | 16% | 31% | -14.3% |
| cyclist | 20 | 100% | 2.59 | 5.25 | 20% | 45% | +13.1% |

## `unidepth-v2-small_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.50 | 2.37 | 33% | 3% | -33.2% |
| 10-20 m | 299 | 100% | 3.17 | 3.29 | 22% | 7% | -22.5% |
| 20-30 m | 246 | 100% | 3.59 | 4.02 | 16% | 25% | -15.1% |
| 30-50 m | 329 | 100% | 4.44 | 5.32 | 14% | 45% | -12.7% |
| 50+ m | 155 | 100% | 6.54 | 8.06 | 13% | 46% | -11.2% |

## `unidepth-v2-small_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.47 | 4.60 | 19% | 25% | -18.8% |
| pedestrian | 126 | 100% | 1.62 | 1.98 | 14% | 31% | -12.7% |
| van | 84 | 100% | 4.88 | 6.29 | 22% | 19% | -22.5% |
| truck | 42 | 100% | 5.79 | 7.11 | 19% | 21% | -18.7% |
| cyclist | 20 | 100% | 2.26 | 3.19 | 13% | 50% | -5.8% |

## `unidepth-v2-small_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.33 | 2.25 | 31% | 4% | -31.2% |
| 10-20 m | 299 | 100% | 2.94 | 3.07 | 21% | 12% | -20.8% |
| 20-30 m | 246 | 100% | 3.32 | 3.59 | 14% | 33% | -13.1% |
| 30-50 m | 329 | 100% | 3.89 | 4.65 | 12% | 51% | -10.5% |
| 50+ m | 155 | 100% | 5.96 | 7.30 | 12% | 49% | -9.0% |

## `unidepth-v2-small_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.22 | 4.14 | 18% | 30% | -16.9% |
| pedestrian | 126 | 100% | 1.44 | 1.85 | 13% | 38% | -11.2% |
| van | 84 | 100% | 4.59 | 5.51 | 20% | 23% | -20.3% |
| truck | 42 | 100% | 5.37 | 6.66 | 18% | 29% | -17.2% |
| cyclist | 20 | 100% | 1.76 | 2.74 | 10% | 65% | +1.0% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-small_median | 62.923 |
| unidepth-v2-small_p10 | 2.616 |
| unidepth-v2-small_p25 | 2.388 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
