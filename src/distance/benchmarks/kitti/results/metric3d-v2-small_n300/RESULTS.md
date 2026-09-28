# KITTI distance benchmark: `metric3d-v2-small_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small_median`, `metric3d-v2-small_p10`, `metric3d-v2-small_p25` |
| Depth model | `metric3d-v2-small`, given our focal length; inference 149.2 ms median, 152.6 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:09:41+00:00 |

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
| metric3d-v2-small_median | 1187 | 100% | 1.10 | 2.19 | 8% | 72% | -1.7% |
| metric3d-v2-small_p10 | 1187 | 100% | 1.40 | 3.01 | 10% | 63% | -8.2% |
| metric3d-v2-small_p25 | 1187 | 100% | 1.19 | 2.47 | 9% | 69% | -5.6% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small_median | 1187 | 100% | 2.21 | 3.23 | 13% | 45% | -11.7% |
| metric3d-v2-small_p10 | 1187 | 100% | 3.04 | 4.57 | 18% | 29% | -17.4% |
| metric3d-v2-small_p25 | 1187 | 100% | 2.75 | 3.89 | 16% | 36% | -15.0% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-small_median | 206 | 100% | 0.92 | 1.50 | 5% | 91% | +1.3% |
| in path / metric3d-v2-small_p10 | 206 | 100% | 0.91 | 1.84 | 5% | 88% | -2.5% |
| in path / metric3d-v2-small_p25 | 206 | 100% | 0.86 | 1.61 | 5% | 92% | -1.1% |
| beside / metric3d-v2-small_median | 981 | 100% | 1.15 | 2.34 | 9% | 68% | -2.3% |
| beside / metric3d-v2-small_p10 | 981 | 100% | 1.53 | 3.25 | 12% | 57% | -9.4% |
| beside / metric3d-v2-small_p25 | 981 | 100% | 1.30 | 2.65 | 10% | 64% | -6.5% |

### `metric3d-v2-small_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.27 | 0.35 | 5% | 80% | +3.7% |
| 10-20 m | 44 | 100% | 0.47 | 0.74 | 5% | 89% | +2.1% |
| 20-30 m | 46 | 100% | 0.87 | 1.05 | 4% | 96% | +1.8% |
| 30-50 m | 76 | 100% | 1.40 | 1.75 | 4% | 95% | +0.9% |
| 50+ m | 25 | 100% | 2.85 | 3.60 | 6% | 84% | -1.0% |

### `metric3d-v2-small_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.20 | 0.27 | 4% | 93% | -0.8% |
| 10-20 m | 44 | 100% | 0.45 | 0.68 | 4% | 91% | -1.4% |
| 20-30 m | 46 | 100% | 0.82 | 1.05 | 4% | 93% | -1.7% |
| 30-50 m | 76 | 100% | 1.38 | 1.98 | 5% | 88% | -2.4% |
| 50+ m | 25 | 100% | 4.00 | 5.87 | 9% | 72% | -7.5% |

### `metric3d-v2-small_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.23 | 0.26 | 4% | 93% | +0.7% |
| 10-20 m | 44 | 100% | 0.41 | 0.65 | 4% | 93% | -0.2% |
| 20-30 m | 46 | 100% | 0.84 | 0.94 | 4% | 96% | +0.0% |
| 30-50 m | 76 | 100% | 1.27 | 1.80 | 5% | 92% | -1.2% |
| 50+ m | 25 | 100% | 3.43 | 4.81 | 8% | 80% | -5.4% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-small_median | 206 | 100% | 1.75 | 2.37 | 7% | 70% | -6.2% |
| in path / metric3d-v2-small_p10 | 206 | 100% | 2.35 | 3.35 | 10% | 60% | -9.8% |
| in path / metric3d-v2-small_p25 | 206 | 100% | 2.09 | 2.92 | 9% | 62% | -8.4% |
| beside / metric3d-v2-small_median | 981 | 100% | 2.29 | 3.41 | 14% | 39% | -12.8% |
| beside / metric3d-v2-small_p10 | 981 | 100% | 3.22 | 4.83 | 19% | 23% | -19.0% |
| beside / metric3d-v2-small_p25 | 981 | 100% | 2.85 | 4.09 | 17% | 30% | -16.4% |

### `metric3d-v2-small_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.62 | 0.93 | 12% | 55% | -12.4% |
| 10-20 m | 41 | 100% | 1.30 | 1.36 | 9% | 56% | -9.2% |
| 20-30 m | 49 | 100% | 1.39 | 1.46 | 6% | 76% | -4.8% |
| 30-50 m | 74 | 100% | 2.27 | 2.64 | 7% | 77% | -5.0% |
| 50+ m | 31 | 100% | 4.66 | 4.99 | 8% | 71% | -5.4% |

### `metric3d-v2-small_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.86 | 1.20 | 16% | 45% | -16.0% |
| 10-20 m | 41 | 100% | 1.80 | 1.77 | 12% | 39% | -12.0% |
| 20-30 m | 49 | 100% | 1.94 | 2.05 | 8% | 73% | -7.7% |
| 30-50 m | 74 | 100% | 3.19 | 3.53 | 9% | 68% | -8.4% |
| 50+ m | 31 | 100% | 6.27 | 7.81 | 12% | 52% | -11.7% |

### `metric3d-v2-small_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.78 | 1.11 | 15% | 45% | -14.7% |
| 10-20 m | 41 | 100% | 1.69 | 1.64 | 11% | 41% | -11.1% |
| 20-30 m | 49 | 100% | 1.73 | 1.83 | 7% | 73% | -6.6% |
| 30-50 m | 74 | 100% | 2.82 | 3.07 | 8% | 72% | -6.8% |
| 50+ m | 31 | 100% | 6.04 | 6.59 | 10% | 55% | -9.5% |

## `metric3d-v2-small_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.45 | 0.61 | 12% | 63% | +3.6% |
| 10-20 m | 297 | 100% | 0.75 | 1.00 | 7% | 78% | -2.6% |
| 20-30 m | 226 | 100% | 1.29 | 1.80 | 7% | 79% | -1.8% |
| 30-50 m | 319 | 100% | 2.29 | 3.03 | 8% | 72% | -3.0% |
| 50+ m | 135 | 100% | 4.27 | 5.99 | 10% | 62% | -4.6% |

## `metric3d-v2-small_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.12 | 2.21 | 8% | 73% | -1.4% |
| pedestrian | 126 | 100% | 0.75 | 1.24 | 8% | 73% | -6.2% |
| van | 84 | 100% | 1.48 | 3.15 | 11% | 67% | -1.4% |
| truck | 42 | 100% | 1.34 | 2.46 | 9% | 76% | +2.5% |
| cyclist | 20 | 100% | 1.58 | 2.79 | 10% | 55% | +2.4% |

## `metric3d-v2-small_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.52 | 0.68 | 11% | 58% | -6.2% |
| 10-20 m | 297 | 100% | 0.89 | 1.30 | 9% | 70% | -7.5% |
| 20-30 m | 226 | 100% | 1.51 | 2.32 | 9% | 69% | -7.3% |
| 30-50 m | 319 | 100% | 2.64 | 4.34 | 11% | 60% | -9.3% |
| 50+ m | 135 | 100% | 5.36 | 8.38 | 14% | 51% | -12.1% |

## `metric3d-v2-small_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.41 | 3.11 | 10% | 64% | -8.2% |
| pedestrian | 126 | 100% | 0.98 | 1.61 | 10% | 60% | -9.9% |
| van | 84 | 100% | 2.21 | 4.01 | 12% | 52% | -9.2% |
| truck | 42 | 100% | 1.70 | 3.03 | 10% | 74% | -2.9% |
| cyclist | 20 | 100% | 1.87 | 2.87 | 11% | 55% | -5.8% |

## `metric3d-v2-small_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.44 | 0.61 | 11% | 63% | -3.0% |
| 10-20 m | 297 | 100% | 0.73 | 1.13 | 8% | 74% | -5.9% |
| 20-30 m | 226 | 100% | 1.28 | 1.91 | 8% | 74% | -4.6% |
| 30-50 m | 319 | 100% | 2.37 | 3.52 | 9% | 67% | -6.3% |
| 50+ m | 135 | 100% | 4.82 | 6.76 | 11% | 60% | -8.7% |

## `metric3d-v2-small_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.20 | 2.52 | 9% | 70% | -5.4% |
| pedestrian | 126 | 100% | 0.91 | 1.37 | 9% | 65% | -8.2% |
| van | 84 | 100% | 1.58 | 3.30 | 10% | 61% | -6.0% |
| truck | 42 | 100% | 2.00 | 2.80 | 9% | 74% | -1.0% |
| cyclist | 20 | 100% | 1.53 | 2.77 | 11% | 50% | -4.2% |

## `metric3d-v2-small_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.63 | 1.66 | 23% | 9% | -22.4% |
| 10-20 m | 299 | 100% | 1.87 | 2.09 | 14% | 32% | -14.1% |
| 20-30 m | 246 | 100% | 2.04 | 2.44 | 10% | 59% | -8.8% |
| 30-50 m | 329 | 100% | 2.93 | 3.90 | 10% | 58% | -7.9% |
| 50+ m | 155 | 100% | 5.57 | 6.88 | 11% | 54% | -8.7% |

## `metric3d-v2-small_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.25 | 3.21 | 13% | 45% | -11.8% |
| pedestrian | 126 | 100% | 1.24 | 1.62 | 11% | 50% | -10.1% |
| van | 84 | 100% | 3.35 | 4.64 | 16% | 35% | -14.3% |
| truck | 42 | 100% | 4.98 | 5.86 | 15% | 36% | -14.4% |
| cyclist | 20 | 100% | 1.48 | 2.75 | 10% | 55% | -1.6% |

## `metric3d-v2-small_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.17 | 2.10 | 30% | 6% | -29.5% |
| 10-20 m | 299 | 100% | 2.40 | 2.73 | 19% | 16% | -18.6% |
| 20-30 m | 246 | 100% | 2.99 | 3.49 | 14% | 39% | -13.6% |
| 30-50 m | 329 | 100% | 4.55 | 5.71 | 15% | 41% | -14.1% |
| 50+ m | 155 | 100% | 8.31 | 9.93 | 16% | 38% | -15.6% |

## `metric3d-v2-small_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.13 | 4.69 | 18% | 29% | -17.7% |
| pedestrian | 126 | 100% | 1.46 | 2.07 | 14% | 38% | -13.6% |
| van | 84 | 100% | 4.36 | 6.09 | 21% | 21% | -20.5% |
| truck | 42 | 100% | 5.98 | 7.13 | 18% | 21% | -18.4% |
| cyclist | 20 | 100% | 2.14 | 3.17 | 13% | 50% | -9.3% |

## `metric3d-v2-small_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.02 | 1.96 | 27% | 9% | -27.1% |
| 10-20 m | 299 | 100% | 2.23 | 2.52 | 17% | 21% | -17.2% |
| 20-30 m | 246 | 100% | 2.55 | 2.98 | 12% | 47% | -11.4% |
| 30-50 m | 329 | 100% | 3.85 | 4.71 | 12% | 49% | -11.1% |
| 50+ m | 155 | 100% | 6.42 | 8.20 | 14% | 45% | -12.4% |

## `metric3d-v2-small_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.80 | 3.95 | 16% | 36% | -15.2% |
| pedestrian | 126 | 100% | 1.35 | 1.81 | 13% | 43% | -12.0% |
| van | 84 | 100% | 3.81 | 5.22 | 18% | 24% | -17.8% |
| truck | 42 | 100% | 5.78 | 6.63 | 17% | 24% | -17.0% |
| cyclist | 20 | 100% | 1.81 | 2.98 | 12% | 55% | -7.8% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| metric3d-v2-small_median | 151.935 |
| metric3d-v2-small_p10 | 2.514 |
| metric3d-v2-small_p25 | 2.339 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
