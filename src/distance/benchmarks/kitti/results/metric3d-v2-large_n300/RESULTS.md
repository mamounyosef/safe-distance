# KITTI distance benchmark: `metric3d-v2-large_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-large_median`, `metric3d-v2-large_p10`, `metric3d-v2-large_p25` |
| Depth model | `metric3d-v2-large`, given our focal length; inference 914.4 ms median, 974.7 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:14:50+00:00 |

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
| metric3d-v2-large_median | 1187 | 100% | 0.98 | 1.73 | 7% | 77% | +0.6% |
| metric3d-v2-large_p10 | 1187 | 100% | 1.09 | 2.43 | 9% | 69% | -5.7% |
| metric3d-v2-large_p25 | 1187 | 100% | 0.99 | 1.86 | 7% | 75% | -3.0% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 1187 | 100% | 1.89 | 2.47 | 11% | 57% | -9.5% |
| metric3d-v2-large_p10 | 1187 | 100% | 2.51 | 3.71 | 16% | 41% | -14.9% |
| metric3d-v2-large_p25 | 1187 | 100% | 2.31 | 2.99 | 13% | 49% | -12.5% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-large_median | 206 | 100% | 1.08 | 1.61 | 5% | 87% | +3.7% |
| in path / metric3d-v2-large_p10 | 206 | 100% | 0.74 | 1.49 | 4% | 93% | +0.3% |
| in path / metric3d-v2-large_p25 | 206 | 100% | 0.83 | 1.28 | 4% | 95% | +1.9% |
| beside / metric3d-v2-large_median | 981 | 100% | 0.96 | 1.76 | 8% | 75% | -0.1% |
| beside / metric3d-v2-large_p10 | 981 | 100% | 1.17 | 2.62 | 10% | 64% | -6.9% |
| beside / metric3d-v2-large_p25 | 981 | 100% | 1.05 | 1.98 | 8% | 71% | -4.0% |

### `metric3d-v2-large_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.34 | 0.32 | 5% | 87% | +1.5% |
| 10-20 m | 44 | 100% | 0.41 | 0.72 | 5% | 84% | +2.6% |
| 20-30 m | 46 | 100% | 0.81 | 1.15 | 5% | 87% | +3.6% |
| 30-50 m | 76 | 100% | 1.78 | 2.05 | 5% | 89% | +4.3% |
| 50+ m | 25 | 100% | 2.22 | 3.49 | 6% | 84% | +5.4% |

### `metric3d-v2-large_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.14 | 0.24 | 4% | 93% | -2.2% |
| 10-20 m | 44 | 100% | 0.51 | 0.48 | 3% | 98% | -0.5% |
| 20-30 m | 46 | 100% | 0.56 | 0.96 | 4% | 93% | +0.3% |
| 30-50 m | 76 | 100% | 1.42 | 1.68 | 4% | 93% | +1.5% |
| 50+ m | 25 | 100% | 1.85 | 4.44 | 7% | 84% | -0.6% |

### `metric3d-v2-large_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.14 | 0.24 | 4% | 93% | -0.8% |
| 10-20 m | 44 | 100% | 0.42 | 0.49 | 3% | 98% | +0.4% |
| 20-30 m | 46 | 100% | 0.63 | 0.88 | 3% | 96% | +2.1% |
| 30-50 m | 76 | 100% | 1.48 | 1.65 | 4% | 97% | +2.8% |
| 50+ m | 25 | 100% | 1.96 | 2.91 | 5% | 84% | +2.9% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-large_median | 206 | 100% | 1.36 | 1.73 | 6% | 83% | -4.0% |
| in path / metric3d-v2-large_p10 | 206 | 100% | 1.69 | 2.30 | 8% | 71% | -7.1% |
| in path / metric3d-v2-large_p25 | 206 | 100% | 1.50 | 1.85 | 7% | 80% | -5.6% |
| beside / metric3d-v2-large_median | 981 | 100% | 2.02 | 2.62 | 12% | 51% | -10.7% |
| beside / metric3d-v2-large_p10 | 981 | 100% | 2.69 | 4.00 | 17% | 35% | -16.5% |
| beside / metric3d-v2-large_p25 | 981 | 100% | 2.46 | 3.23 | 15% | 42% | -14.0% |

### `metric3d-v2-large_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.73 | 1.08 | 15% | 55% | -14.5% |
| 10-20 m | 41 | 100% | 1.55 | 1.35 | 9% | 51% | -9.1% |
| 20-30 m | 49 | 100% | 0.82 | 1.07 | 4% | 96% | -3.0% |
| 30-50 m | 74 | 100% | 1.53 | 1.76 | 4% | 95% | -1.8% |
| 50+ m | 31 | 100% | 2.93 | 3.47 | 6% | 87% | -0.0% |

### `metric3d-v2-large_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.90 | 1.29 | 17% | 27% | -17.3% |
| 10-20 m | 41 | 100% | 1.80 | 1.69 | 12% | 37% | -11.6% |
| 20-30 m | 49 | 100% | 1.35 | 1.44 | 6% | 86% | -5.5% |
| 30-50 m | 74 | 100% | 1.77 | 2.28 | 6% | 81% | -4.9% |
| 50+ m | 31 | 100% | 2.53 | 4.89 | 8% | 87% | -5.3% |

### `metric3d-v2-large_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.81 | 1.20 | 16% | 36% | -16.1% |
| 10-20 m | 41 | 100% | 1.72 | 1.59 | 11% | 46% | -10.8% |
| 20-30 m | 49 | 100% | 1.16 | 1.28 | 5% | 94% | -4.7% |
| 30-50 m | 74 | 100% | 1.46 | 1.86 | 5% | 93% | -3.2% |
| 50+ m | 31 | 100% | 2.56 | 3.33 | 5% | 84% | -2.3% |

## `metric3d-v2-large_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.42 | 0.55 | 11% | 62% | +2.5% |
| 10-20 m | 297 | 100% | 0.69 | 0.92 | 6% | 83% | -1.3% |
| 20-30 m | 226 | 100% | 1.15 | 1.54 | 6% | 81% | -0.1% |
| 30-50 m | 319 | 100% | 1.85 | 2.30 | 6% | 81% | +0.8% |
| 50+ m | 135 | 100% | 3.28 | 4.33 | 7% | 73% | +2.5% |

## `metric3d-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.07 | 1.81 | 7% | 77% | +1.2% |
| pedestrian | 126 | 100% | 0.66 | 0.89 | 6% | 78% | -4.8% |
| van | 84 | 100% | 0.90 | 2.03 | 8% | 75% | +0.2% |
| truck | 42 | 100% | 1.24 | 1.85 | 8% | 86% | +4.0% |
| cyclist | 20 | 100% | 1.13 | 1.85 | 7% | 80% | +1.5% |

## `metric3d-v2-large_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.47 | 0.65 | 11% | 57% | -6.8% |
| 10-20 m | 297 | 100% | 0.66 | 1.08 | 7% | 74% | -6.0% |
| 20-30 m | 226 | 100% | 1.00 | 1.96 | 8% | 75% | -5.3% |
| 30-50 m | 319 | 100% | 2.20 | 3.46 | 9% | 69% | -5.1% |
| 50+ m | 135 | 100% | 3.80 | 6.52 | 11% | 65% | -5.3% |

## `metric3d-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.16 | 2.56 | 9% | 69% | -5.6% |
| pedestrian | 126 | 100% | 0.82 | 1.23 | 8% | 69% | -7.5% |
| van | 84 | 100% | 1.37 | 2.89 | 9% | 56% | -7.0% |
| truck | 42 | 100% | 1.24 | 2.38 | 9% | 81% | -0.7% |
| cyclist | 20 | 100% | 0.98 | 1.96 | 8% | 80% | -3.6% |

## `metric3d-v2-large_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.40 | 0.58 | 10% | 61% | -3.9% |
| 10-20 m | 297 | 100% | 0.61 | 0.95 | 6% | 77% | -4.5% |
| 20-30 m | 226 | 100% | 0.99 | 1.56 | 6% | 81% | -2.6% |
| 30-50 m | 319 | 100% | 2.04 | 2.69 | 7% | 78% | -2.2% |
| 50+ m | 135 | 100% | 3.39 | 4.37 | 7% | 73% | -1.0% |

## `metric3d-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.06 | 1.94 | 7% | 76% | -2.7% |
| pedestrian | 126 | 100% | 0.75 | 1.01 | 7% | 71% | -6.1% |
| van | 84 | 100% | 1.15 | 2.14 | 7% | 68% | -3.9% |
| truck | 42 | 100% | 1.39 | 1.93 | 8% | 83% | +1.4% |
| cyclist | 20 | 100% | 1.02 | 1.92 | 8% | 80% | -2.6% |

## `metric3d-v2-large_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.73 | 1.70 | 23% | 13% | -23.4% |
| 10-20 m | 299 | 100% | 1.76 | 1.95 | 13% | 36% | -13.3% |
| 20-30 m | 246 | 100% | 1.52 | 1.99 | 8% | 72% | -7.2% |
| 30-50 m | 329 | 100% | 2.15 | 2.78 | 7% | 76% | -4.7% |
| 50+ m | 155 | 100% | 3.79 | 4.35 | 7% | 77% | -1.8% |

## `metric3d-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.90 | 2.44 | 11% | 57% | -9.3% |
| pedestrian | 126 | 100% | 1.04 | 1.24 | 10% | 62% | -8.7% |
| van | 84 | 100% | 2.91 | 3.61 | 14% | 44% | -12.6% |
| truck | 42 | 100% | 4.19 | 4.85 | 13% | 43% | -13.2% |
| cyclist | 20 | 100% | 0.78 | 1.66 | 6% | 85% | -2.5% |

## `metric3d-v2-large_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.22 | 2.12 | 30% | 7% | -30.0% |
| 10-20 m | 299 | 100% | 2.33 | 2.55 | 17% | 20% | -17.5% |
| 20-30 m | 246 | 100% | 2.33 | 3.03 | 12% | 52% | -11.8% |
| 30-50 m | 329 | 100% | 3.25 | 4.48 | 12% | 59% | -10.5% |
| 50+ m | 155 | 100% | 4.87 | 7.00 | 11% | 61% | -8.8% |

## `metric3d-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.53 | 3.79 | 16% | 41% | -15.2% |
| pedestrian | 126 | 100% | 1.26 | 1.65 | 12% | 46% | -11.3% |
| van | 84 | 100% | 3.63 | 5.06 | 19% | 30% | -18.1% |
| truck | 42 | 100% | 4.59 | 6.04 | 17% | 33% | -16.6% |
| cyclist | 20 | 100% | 0.68 | 2.08 | 8% | 75% | -7.3% |

## `metric3d-v2-large_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.09 | 1.98 | 28% | 9% | -27.8% |
| 10-20 m | 299 | 100% | 2.20 | 2.35 | 16% | 26% | -16.2% |
| 20-30 m | 246 | 100% | 1.97 | 2.50 | 10% | 62% | -9.7% |
| 30-50 m | 329 | 100% | 2.80 | 3.50 | 9% | 69% | -7.6% |
| 50+ m | 155 | 100% | 4.35 | 4.93 | 8% | 71% | -5.0% |

## `metric3d-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.34 | 3.02 | 14% | 49% | -12.6% |
| pedestrian | 126 | 100% | 1.14 | 1.41 | 11% | 54% | -9.9% |
| van | 84 | 100% | 3.29 | 4.14 | 16% | 42% | -15.6% |
| truck | 42 | 100% | 4.44 | 5.36 | 15% | 38% | -15.0% |
| cyclist | 20 | 100% | 0.62 | 1.96 | 8% | 85% | -6.3% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| metric3d-v2-large_median | 916.897 |
| metric3d-v2-large_p10 | 2.556 |
| metric3d-v2-large_p25 | 2.39 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
