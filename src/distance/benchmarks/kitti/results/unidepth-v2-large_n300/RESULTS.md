# KITTI distance benchmark: `unidepth-v2-large_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 215.1 ms median, 237.0 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:17:43+00:00 |

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
| unidepth-v2-large_median | 1187 | 100% | 1.12 | 1.85 | 8% | 74% | -3.6% |
| unidepth-v2-large_p10 | 1187 | 100% | 1.62 | 2.58 | 10% | 60% | -9.2% |
| unidepth-v2-large_p25 | 1187 | 100% | 1.38 | 2.19 | 9% | 66% | -7.2% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 1187 | 100% | 2.54 | 3.18 | 14% | 40% | -13.2% |
| unidepth-v2-large_p10 | 1187 | 100% | 3.38 | 4.29 | 18% | 25% | -18.0% |
| unidepth-v2-large_p25 | 1187 | 100% | 3.08 | 3.82 | 17% | 30% | -16.3% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-large_median | 206 | 100% | 0.96 | 1.55 | 5% | 94% | -0.4% |
| in path / unidepth-v2-large_p10 | 206 | 100% | 1.09 | 1.62 | 5% | 92% | -4.1% |
| in path / unidepth-v2-large_p25 | 206 | 100% | 1.00 | 1.53 | 5% | 94% | -2.9% |
| beside / unidepth-v2-large_median | 981 | 100% | 1.15 | 1.91 | 8% | 69% | -4.2% |
| beside / unidepth-v2-large_p10 | 981 | 100% | 1.71 | 2.78 | 12% | 53% | -10.2% |
| beside / unidepth-v2-large_p25 | 981 | 100% | 1.47 | 2.33 | 10% | 60% | -8.1% |

### `unidepth-v2-large_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.15 | 0.16 | 2% | 100% | -1.1% |
| 10-20 m | 44 | 100% | 0.61 | 0.81 | 6% | 86% | -1.2% |
| 20-30 m | 46 | 100% | 1.27 | 1.57 | 6% | 96% | +0.6% |
| 30-50 m | 76 | 100% | 1.43 | 1.65 | 4% | 96% | -0.7% |
| 50+ m | 25 | 100% | 2.82 | 3.33 | 5% | 96% | +0.6% |

### `unidepth-v2-large_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.32 | 0.33 | 5% | 93% | -4.9% |
| 10-20 m | 44 | 100% | 0.77 | 0.81 | 6% | 86% | -5.2% |
| 20-30 m | 46 | 100% | 1.04 | 1.15 | 5% | 98% | -3.5% |
| 30-50 m | 76 | 100% | 1.79 | 2.10 | 5% | 91% | -3.9% |
| 50+ m | 25 | 100% | 2.72 | 3.21 | 5% | 92% | -3.5% |

### `unidepth-v2-large_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.28 | 0.25 | 4% | 93% | -3.7% |
| 10-20 m | 44 | 100% | 0.73 | 0.76 | 5% | 91% | -4.1% |
| 20-30 m | 46 | 100% | 1.05 | 1.39 | 6% | 98% | -1.8% |
| 30-50 m | 76 | 100% | 1.54 | 1.81 | 5% | 93% | -2.8% |
| 50+ m | 25 | 100% | 2.40 | 3.04 | 5% | 96% | -2.2% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-large_median | 206 | 100% | 2.22 | 2.79 | 9% | 57% | -7.7% |
| in path / unidepth-v2-large_p10 | 206 | 100% | 2.93 | 3.38 | 11% | 43% | -11.2% |
| in path / unidepth-v2-large_p25 | 206 | 100% | 2.68 | 3.14 | 11% | 46% | -10.0% |
| beside / unidepth-v2-large_median | 981 | 100% | 2.58 | 3.27 | 15% | 37% | -14.3% |
| beside / unidepth-v2-large_p10 | 981 | 100% | 3.48 | 4.48 | 20% | 21% | -19.5% |
| beside / unidepth-v2-large_p25 | 981 | 100% | 3.16 | 3.96 | 18% | 26% | -17.6% |

### `unidepth-v2-large_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.75 | 1.18 | 16% | 64% | -15.8% |
| 10-20 m | 41 | 100% | 1.99 | 1.98 | 13% | 22% | -12.5% |
| 20-30 m | 49 | 100% | 1.88 | 2.34 | 9% | 65% | -5.8% |
| 30-50 m | 74 | 100% | 2.96 | 3.01 | 7% | 66% | -6.5% |
| 50+ m | 31 | 100% | 3.72 | 4.64 | 7% | 65% | -4.6% |

### `unidepth-v2-large_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.86 | 1.39 | 19% | 36% | -18.6% |
| 10-20 m | 41 | 100% | 2.36 | 2.30 | 16% | 17% | -15.6% |
| 20-30 m | 49 | 100% | 2.73 | 2.53 | 10% | 47% | -10.0% |
| 30-50 m | 74 | 100% | 4.04 | 3.94 | 10% | 50% | -9.6% |
| 50+ m | 31 | 100% | 4.26 | 5.53 | 9% | 55% | -8.3% |

### `unidepth-v2-large_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.83 | 1.32 | 18% | 36% | -17.7% |
| 10-20 m | 41 | 100% | 2.25 | 2.19 | 15% | 17% | -14.7% |
| 20-30 m | 49 | 100% | 2.59 | 2.60 | 10% | 47% | -8.4% |
| 30-50 m | 74 | 100% | 3.41 | 3.55 | 9% | 55% | -8.5% |
| 50+ m | 31 | 100% | 3.67 | 4.93 | 8% | 61% | -7.2% |

## `unidepth-v2-large_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.54 | 0.66 | 12% | 59% | -1.9% |
| 10-20 m | 297 | 100% | 0.79 | 1.11 | 7% | 73% | -5.8% |
| 20-30 m | 226 | 100% | 1.28 | 1.77 | 7% | 76% | -3.5% |
| 30-50 m | 319 | 100% | 1.86 | 2.50 | 6% | 80% | -3.1% |
| 50+ m | 135 | 100% | 3.10 | 3.93 | 7% | 78% | -2.5% |

## `unidepth-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.15 | 1.86 | 8% | 75% | -3.4% |
| pedestrian | 126 | 100% | 0.87 | 1.13 | 8% | 67% | -6.4% |
| van | 84 | 100% | 1.48 | 2.51 | 10% | 64% | -3.4% |
| truck | 42 | 100% | 1.60 | 2.66 | 10% | 81% | +0.0% |
| cyclist | 20 | 100% | 0.66 | 1.48 | 6% | 80% | -1.0% |

## `unidepth-v2-large_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.78 | 0.89 | 14% | 35% | -10.5% |
| 10-20 m | 297 | 100% | 1.19 | 1.58 | 11% | 57% | -10.5% |
| 20-30 m | 226 | 100% | 1.81 | 2.40 | 10% | 67% | -8.8% |
| 30-50 m | 319 | 100% | 2.65 | 3.53 | 9% | 69% | -7.9% |
| 50+ m | 135 | 100% | 3.84 | 5.44 | 9% | 70% | -7.7% |

## `unidepth-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.66 | 2.61 | 10% | 60% | -9.3% |
| pedestrian | 126 | 100% | 1.05 | 1.36 | 10% | 52% | -9.3% |
| van | 84 | 100% | 2.23 | 3.60 | 12% | 55% | -10.4% |
| truck | 42 | 100% | 2.42 | 3.41 | 12% | 71% | -4.7% |
| cyclist | 20 | 100% | 1.49 | 2.38 | 9% | 75% | -8.2% |

## `unidepth-v2-large_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.69 | 0.80 | 13% | 42% | -7.8% |
| 10-20 m | 297 | 100% | 1.10 | 1.39 | 9% | 64% | -9.0% |
| 20-30 m | 226 | 100% | 1.54 | 2.04 | 8% | 73% | -6.6% |
| 30-50 m | 319 | 100% | 2.20 | 3.00 | 8% | 73% | -6.1% |
| 50+ m | 135 | 100% | 3.46 | 4.50 | 8% | 74% | -5.6% |

## `unidepth-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.42 | 2.21 | 9% | 66% | -7.2% |
| pedestrian | 126 | 100% | 0.99 | 1.26 | 9% | 60% | -8.1% |
| van | 84 | 100% | 1.96 | 3.03 | 10% | 57% | -7.7% |
| truck | 42 | 100% | 2.36 | 3.14 | 11% | 76% | -3.2% |
| cyclist | 20 | 100% | 1.04 | 2.01 | 8% | 85% | -5.6% |

## `unidepth-v2-large_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.88 | 1.91 | 26% | 9% | -26.3% |
| 10-20 m | 299 | 100% | 2.39 | 2.57 | 18% | 16% | -17.4% |
| 20-30 m | 246 | 100% | 2.54 | 2.88 | 12% | 48% | -10.2% |
| 30-50 m | 329 | 100% | 3.19 | 3.67 | 9% | 61% | -8.4% |
| 50+ m | 155 | 100% | 3.91 | 5.12 | 8% | 65% | -6.6% |

## `unidepth-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.62 | 3.17 | 14% | 40% | -13.4% |
| pedestrian | 126 | 100% | 1.31 | 1.52 | 11% | 47% | -10.2% |
| van | 84 | 100% | 3.70 | 4.37 | 16% | 33% | -15.9% |
| truck | 42 | 100% | 6.68 | 6.73 | 17% | 19% | -16.8% |
| cyclist | 20 | 100% | 1.17 | 1.88 | 8% | 75% | -4.8% |

## `unidepth-v2-large_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.38 | 2.31 | 32% | 4% | -32.5% |
| 10-20 m | 299 | 100% | 2.94 | 3.16 | 22% | 8% | -21.5% |
| 20-30 m | 246 | 100% | 3.47 | 3.80 | 15% | 26% | -15.2% |
| 30-50 m | 329 | 100% | 4.40 | 5.20 | 13% | 40% | -13.1% |
| 50+ m | 155 | 100% | 5.89 | 7.32 | 12% | 46% | -11.6% |

## `unidepth-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.47 | 4.34 | 19% | 24% | -18.4% |
| pedestrian | 126 | 100% | 1.59 | 1.80 | 13% | 33% | -13.0% |
| van | 84 | 100% | 4.78 | 5.97 | 21% | 17% | -21.3% |
| truck | 42 | 100% | 7.73 | 7.91 | 20% | 10% | -20.3% |
| cyclist | 20 | 100% | 1.99 | 3.08 | 12% | 70% | -11.7% |

## `unidepth-v2-large_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.24 | 2.19 | 30% | 4% | -30.4% |
| 10-20 m | 299 | 100% | 2.82 | 2.96 | 20% | 8% | -20.2% |
| 20-30 m | 246 | 100% | 3.13 | 3.44 | 14% | 31% | -13.3% |
| 30-50 m | 329 | 100% | 3.93 | 4.54 | 12% | 48% | -11.2% |
| 50+ m | 155 | 100% | 5.27 | 6.18 | 10% | 55% | -9.6% |

## `unidepth-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.15 | 3.84 | 17% | 29% | -16.6% |
| pedestrian | 126 | 100% | 1.48 | 1.68 | 13% | 33% | -11.9% |
| van | 84 | 100% | 4.32 | 5.21 | 19% | 23% | -19.1% |
| truck | 42 | 100% | 7.46 | 7.51 | 19% | 17% | -19.2% |
| cyclist | 20 | 100% | 1.86 | 2.64 | 10% | 70% | -9.2% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-large_median | 218.296 |
| unidepth-v2-large_p10 | 2.555 |
| unidepth-v2-large_p25 | 2.498 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
