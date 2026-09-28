# KITTI distance benchmark: `unidepth-v2-base_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 110.1 ms median, 120.6 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:16:16+00:00 |

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
| unidepth-v2-base_median | 1187 | 100% | 1.10 | 2.09 | 8% | 70% | -4.4% |
| unidepth-v2-base_p10 | 1187 | 100% | 1.67 | 2.92 | 11% | 56% | -10.1% |
| unidepth-v2-base_p25 | 1187 | 100% | 1.45 | 2.50 | 10% | 61% | -8.1% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 1187 | 100% | 2.70 | 3.57 | 15% | 35% | -14.0% |
| unidepth-v2-base_p10 | 1187 | 100% | 3.48 | 4.70 | 19% | 22% | -18.9% |
| unidepth-v2-base_p25 | 1187 | 100% | 3.21 | 4.21 | 17% | 27% | -17.1% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-base_median | 206 | 100% | 0.74 | 1.53 | 5% | 91% | -0.7% |
| in path / unidepth-v2-base_p10 | 206 | 100% | 1.02 | 1.72 | 5% | 90% | -4.5% |
| in path / unidepth-v2-base_p25 | 206 | 100% | 0.94 | 1.56 | 5% | 91% | -3.3% |
| beside / unidepth-v2-base_median | 981 | 100% | 1.19 | 2.21 | 9% | 65% | -5.2% |
| beside / unidepth-v2-base_p10 | 981 | 100% | 1.87 | 3.17 | 12% | 49% | -11.3% |
| beside / unidepth-v2-base_p25 | 981 | 100% | 1.61 | 2.69 | 11% | 55% | -9.1% |

### `unidepth-v2-base_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.36 | 0.31 | 5% | 100% | -0.8% |
| 10-20 m | 44 | 100% | 0.50 | 0.70 | 5% | 93% | -0.4% |
| 20-30 m | 46 | 100% | 0.74 | 1.40 | 6% | 91% | +2.0% |
| 30-50 m | 76 | 100% | 1.08 | 1.56 | 4% | 93% | -1.7% |
| 50+ m | 25 | 100% | 2.22 | 3.92 | 6% | 76% | -2.8% |

### `unidepth-v2-base_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.39 | 0.40 | 6% | 93% | -5.1% |
| 10-20 m | 44 | 100% | 0.67 | 0.71 | 5% | 93% | -4.7% |
| 20-30 m | 46 | 100% | 0.94 | 0.94 | 4% | 98% | -2.7% |
| 30-50 m | 76 | 100% | 1.38 | 2.08 | 5% | 89% | -4.8% |
| 50+ m | 25 | 100% | 3.30 | 4.61 | 7% | 72% | -6.0% |

### `unidepth-v2-base_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.35 | 0.34 | 5% | 93% | -3.5% |
| 10-20 m | 44 | 100% | 0.61 | 0.66 | 5% | 98% | -3.5% |
| 20-30 m | 46 | 100% | 0.86 | 0.98 | 4% | 93% | -1.6% |
| 30-50 m | 76 | 100% | 1.18 | 1.77 | 4% | 92% | -3.7% |
| 50+ m | 25 | 100% | 2.85 | 4.27 | 7% | 72% | -5.0% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-base_median | 206 | 100% | 2.23 | 2.98 | 10% | 54% | -8.0% |
| in path / unidepth-v2-base_p10 | 206 | 100% | 2.90 | 3.62 | 12% | 42% | -11.5% |
| in path / unidepth-v2-base_p25 | 206 | 100% | 2.69 | 3.32 | 11% | 49% | -10.5% |
| beside / unidepth-v2-base_median | 981 | 100% | 2.78 | 3.70 | 16% | 31% | -15.3% |
| beside / unidepth-v2-base_p10 | 981 | 100% | 3.67 | 4.93 | 21% | 18% | -20.5% |
| beside / unidepth-v2-base_p25 | 981 | 100% | 3.39 | 4.39 | 19% | 23% | -18.5% |

### `unidepth-v2-base_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.88 | 1.15 | 16% | 18% | -15.6% |
| 10-20 m | 41 | 100% | 1.81 | 1.83 | 12% | 27% | -11.7% |
| 20-30 m | 49 | 100% | 2.11 | 2.34 | 9% | 65% | -4.7% |
| 30-50 m | 74 | 100% | 2.89 | 3.29 | 8% | 62% | -7.3% |
| 50+ m | 31 | 100% | 4.46 | 5.40 | 8% | 65% | -7.5% |

### `unidepth-v2-base_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.00 | 1.39 | 19% | 18% | -18.8% |
| 10-20 m | 41 | 100% | 2.31 | 2.19 | 15% | 12% | -14.9% |
| 20-30 m | 49 | 100% | 2.64 | 2.43 | 10% | 47% | -9.5% |
| 30-50 m | 74 | 100% | 3.62 | 4.19 | 10% | 53% | -10.2% |
| 50+ m | 31 | 100% | 5.73 | 6.81 | 11% | 58% | -10.7% |

### `unidepth-v2-base_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 0.96 | 1.29 | 18% | 18% | -17.5% |
| 10-20 m | 41 | 100% | 2.22 | 2.07 | 14% | 15% | -14.0% |
| 20-30 m | 49 | 100% | 2.41 | 2.25 | 9% | 59% | -8.3% |
| 30-50 m | 74 | 100% | 3.41 | 3.80 | 9% | 58% | -9.2% |
| 50+ m | 31 | 100% | 5.47 | 6.20 | 10% | 65% | -9.7% |

## `unidepth-v2-base_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.53 | 0.67 | 12% | 55% | -1.9% |
| 10-20 m | 297 | 100% | 0.75 | 1.09 | 7% | 73% | -5.7% |
| 20-30 m | 226 | 100% | 1.20 | 1.85 | 7% | 77% | -3.4% |
| 30-50 m | 319 | 100% | 2.21 | 2.82 | 7% | 73% | -4.8% |
| 50+ m | 135 | 100% | 4.48 | 5.18 | 9% | 64% | -6.5% |

## `unidepth-v2-base_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.09 | 2.05 | 8% | 71% | -4.5% |
| pedestrian | 126 | 100% | 0.91 | 1.19 | 9% | 63% | -5.8% |
| van | 84 | 100% | 1.61 | 3.09 | 11% | 60% | -5.2% |
| truck | 42 | 100% | 2.38 | 3.50 | 11% | 74% | -2.2% |
| cyclist | 20 | 100% | 1.56 | 2.44 | 9% | 60% | +3.9% |

## `unidepth-v2-base_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.76 | 0.92 | 14% | 37% | -10.8% |
| 10-20 m | 297 | 100% | 1.21 | 1.59 | 11% | 60% | -10.6% |
| 20-30 m | 226 | 100% | 1.73 | 2.43 | 10% | 65% | -9.0% |
| 30-50 m | 319 | 100% | 3.17 | 4.05 | 10% | 60% | -9.8% |
| 50+ m | 135 | 100% | 5.96 | 7.09 | 12% | 50% | -10.8% |

## `unidepth-v2-base_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.71 | 2.94 | 11% | 56% | -10.3% |
| pedestrian | 126 | 100% | 1.11 | 1.46 | 10% | 58% | -9.7% |
| van | 84 | 100% | 2.77 | 4.36 | 14% | 43% | -12.1% |
| truck | 42 | 100% | 3.27 | 4.17 | 13% | 57% | -6.5% |
| cyclist | 20 | 100% | 1.48 | 2.58 | 10% | 65% | -6.0% |

## `unidepth-v2-base_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.69 | 0.83 | 13% | 42% | -8.1% |
| 10-20 m | 297 | 100% | 1.06 | 1.39 | 9% | 64% | -8.9% |
| 20-30 m | 226 | 100% | 1.46 | 2.05 | 8% | 71% | -6.8% |
| 30-50 m | 319 | 100% | 2.78 | 3.40 | 9% | 65% | -7.8% |
| 50+ m | 135 | 100% | 5.37 | 6.13 | 10% | 56% | -9.0% |

## `unidepth-v2-base_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.47 | 2.50 | 9% | 62% | -8.2% |
| pedestrian | 126 | 100% | 0.98 | 1.25 | 9% | 61% | -8.2% |
| van | 84 | 100% | 2.18 | 3.74 | 12% | 46% | -9.5% |
| truck | 42 | 100% | 2.71 | 3.85 | 12% | 62% | -5.1% |
| cyclist | 20 | 100% | 1.33 | 2.10 | 7% | 70% | -0.9% |

## `unidepth-v2-base_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.93 | 1.92 | 26% | 4% | -26.4% |
| 10-20 m | 299 | 100% | 2.45 | 2.54 | 17% | 18% | -17.1% |
| 20-30 m | 246 | 100% | 2.68 | 3.02 | 12% | 44% | -10.2% |
| 30-50 m | 329 | 100% | 3.79 | 4.20 | 11% | 50% | -9.8% |
| 50+ m | 155 | 100% | 5.71 | 6.80 | 11% | 50% | -10.4% |

## `unidepth-v2-base_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.76 | 3.55 | 15% | 34% | -14.4% |
| pedestrian | 126 | 100% | 1.29 | 1.54 | 12% | 48% | -9.6% |
| van | 84 | 100% | 4.22 | 5.22 | 18% | 23% | -17.6% |
| truck | 42 | 100% | 6.02 | 7.46 | 19% | 12% | -18.6% |
| cyclist | 20 | 100% | 1.26 | 2.40 | 9% | 65% | -0.1% |

## `unidepth-v2-base_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.41 | 2.33 | 33% | 3% | -32.7% |
| 10-20 m | 299 | 100% | 2.98 | 3.16 | 22% | 8% | -21.5% |
| 20-30 m | 246 | 100% | 3.38 | 3.90 | 16% | 26% | -15.5% |
| 30-50 m | 329 | 100% | 5.14 | 5.78 | 15% | 36% | -14.6% |
| 50+ m | 155 | 100% | 7.90 | 9.06 | 15% | 32% | -14.6% |

## `unidepth-v2-base_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.61 | 4.76 | 19% | 21% | -19.4% |
| pedestrian | 126 | 100% | 1.59 | 1.90 | 14% | 33% | -13.4% |
| van | 84 | 100% | 5.14 | 6.74 | 23% | 13% | -22.9% |
| truck | 42 | 100% | 7.43 | 8.58 | 22% | 5% | -21.7% |
| cyclist | 20 | 100% | 1.69 | 3.07 | 12% | 65% | -9.6% |

## `unidepth-v2-base_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.25 | 2.20 | 31% | 3% | -30.7% |
| 10-20 m | 299 | 100% | 2.83 | 2.95 | 20% | 12% | -20.1% |
| 20-30 m | 246 | 100% | 3.21 | 3.48 | 14% | 34% | -13.6% |
| 30-50 m | 329 | 100% | 4.48 | 5.05 | 13% | 41% | -12.6% |
| 50+ m | 155 | 100% | 7.07 | 8.04 | 13% | 41% | -12.9% |

## `unidepth-v2-base_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.30 | 4.24 | 18% | 26% | -17.6% |
| pedestrian | 126 | 100% | 1.50 | 1.66 | 12% | 40% | -12.0% |
| van | 84 | 100% | 4.80 | 6.07 | 21% | 18% | -20.8% |
| truck | 42 | 100% | 7.30 | 8.19 | 21% | 7% | -20.6% |
| cyclist | 20 | 100% | 1.31 | 2.39 | 8% | 75% | -4.7% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-base_median | 113.168 |
| unidepth-v2-base_p10 | 2.563 |
| unidepth-v2-base_p25 | 2.505 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
