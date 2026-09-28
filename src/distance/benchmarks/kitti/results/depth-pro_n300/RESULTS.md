# KITTI distance benchmark: `depth-pro_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `depth-pro_median`, `depth-pro_p10`, `depth-pro_p25` |
| Depth model | `depth-pro`, given our focal length; inference 865.7 ms median, 5047.5 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:29:09+00:00 |

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
| depth-pro_median | 1187 | 100% | 1.88 | 3.56 | 13% | 52% | -8.7% |
| depth-pro_p10 | 1187 | 100% | 2.61 | 4.43 | 15% | 40% | -13.6% |
| depth-pro_p25 | 1187 | 100% | 2.28 | 3.97 | 14% | 47% | -11.6% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median | 1187 | 100% | 3.49 | 5.07 | 18% | 25% | -18.1% |
| depth-pro_p10 | 1187 | 100% | 4.45 | 6.16 | 22% | 15% | -22.3% |
| depth-pro_p25 | 1187 | 100% | 4.02 | 5.64 | 21% | 19% | -20.5% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / depth-pro_median | 206 | 100% | 1.75 | 3.20 | 9% | 67% | -6.2% |
| in path / depth-pro_p10 | 206 | 100% | 2.17 | 3.78 | 11% | 61% | -8.9% |
| in path / depth-pro_p25 | 206 | 100% | 1.92 | 3.49 | 10% | 65% | -7.7% |
| beside / depth-pro_median | 981 | 100% | 1.91 | 3.64 | 13% | 49% | -9.2% |
| beside / depth-pro_p10 | 981 | 100% | 2.75 | 4.56 | 16% | 36% | -14.6% |
| beside / depth-pro_p25 | 981 | 100% | 2.33 | 4.07 | 14% | 44% | -12.3% |

### `depth-pro_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.45 | 0.89 | 13% | 67% | -8.8% |
| 10-20 m | 44 | 100% | 0.76 | 0.93 | 6% | 77% | -0.8% |
| 20-30 m | 46 | 100% | 1.44 | 1.83 | 7% | 72% | -3.5% |
| 30-50 m | 76 | 100% | 3.27 | 4.61 | 11% | 63% | -9.0% |
| 50+ m | 25 | 100% | 5.64 | 6.82 | 11% | 56% | -10.4% |

### `depth-pro_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.66 | 0.94 | 13% | 53% | -12.1% |
| 10-20 m | 44 | 100% | 1.00 | 0.98 | 7% | 82% | -3.9% |
| 20-30 m | 46 | 100% | 1.78 | 2.14 | 9% | 65% | -6.1% |
| 30-50 m | 76 | 100% | 3.66 | 5.25 | 13% | 55% | -11.2% |
| 50+ m | 25 | 100% | 7.07 | 8.96 | 14% | 36% | -14.1% |

### `depth-pro_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.54 | 0.90 | 12% | 60% | -10.8% |
| 10-20 m | 44 | 100% | 0.96 | 0.96 | 7% | 86% | -2.8% |
| 20-30 m | 46 | 100% | 1.57 | 2.00 | 8% | 70% | -5.1% |
| 30-50 m | 76 | 100% | 3.66 | 4.91 | 12% | 57% | -10.1% |
| 50+ m | 25 | 100% | 6.61 | 7.91 | 12% | 48% | -12.4% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / depth-pro_median | 206 | 100% | 3.06 | 4.69 | 14% | 40% | -13.3% |
| in path / depth-pro_p10 | 206 | 100% | 3.85 | 5.50 | 16% | 25% | -15.8% |
| in path / depth-pro_p25 | 206 | 100% | 3.50 | 5.12 | 15% | 32% | -14.7% |
| beside / depth-pro_median | 981 | 100% | 3.56 | 5.15 | 19% | 22% | -19.1% |
| beside / depth-pro_p10 | 981 | 100% | 4.53 | 6.30 | 24% | 13% | -23.7% |
| beside / depth-pro_p25 | 981 | 100% | 4.07 | 5.74 | 22% | 16% | -21.7% |

### `depth-pro_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.60 | 1.82 | 25% | 27% | -24.6% |
| 10-20 m | 41 | 100% | 1.90 | 1.76 | 12% | 46% | -12.2% |
| 20-30 m | 49 | 100% | 2.31 | 2.53 | 10% | 49% | -9.3% |
| 30-50 m | 74 | 100% | 5.33 | 5.96 | 15% | 36% | -13.8% |
| 50+ m | 31 | 100% | 8.81 | 9.95 | 16% | 29% | -15.7% |

### `depth-pro_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.98 | 2.01 | 27% | 18% | -27.1% |
| 10-20 m | 41 | 100% | 2.15 | 2.11 | 15% | 32% | -14.6% |
| 20-30 m | 49 | 100% | 3.07 | 3.12 | 12% | 35% | -12.0% |
| 30-50 m | 74 | 100% | 5.60 | 6.76 | 17% | 22% | -15.9% |
| 50+ m | 31 | 100% | 10.46 | 12.00 | 19% | 10% | -18.9% |

### `depth-pro_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.83 | 1.94 | 26% | 18% | -26.1% |
| 10-20 m | 41 | 100% | 2.05 | 2.00 | 14% | 41% | -13.9% |
| 20-30 m | 49 | 100% | 2.78 | 2.87 | 11% | 41% | -10.9% |
| 30-50 m | 74 | 100% | 5.57 | 6.34 | 16% | 30% | -14.8% |
| 50+ m | 31 | 100% | 10.46 | 11.01 | 17% | 16% | -17.4% |

## `depth-pro_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.55 | 0.98 | 16% | 50% | -4.3% |
| 10-20 m | 297 | 100% | 1.03 | 1.43 | 9% | 63% | -6.0% |
| 20-30 m | 226 | 100% | 1.98 | 2.66 | 11% | 59% | -7.7% |
| 30-50 m | 319 | 100% | 4.12 | 5.07 | 13% | 48% | -11.6% |
| 50+ m | 135 | 100% | 9.67 | 10.24 | 17% | 29% | -16.5% |

## `depth-pro_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 1.91 | 3.59 | 12% | 52% | -8.1% |
| pedestrian | 126 | 100% | 1.33 | 1.84 | 15% | 54% | -13.9% |
| van | 84 | 100% | 2.50 | 5.58 | 16% | 45% | -10.3% |
| truck | 42 | 100% | 2.64 | 4.87 | 13% | 55% | -6.1% |
| cyclist | 20 | 100% | 1.09 | 2.12 | 9% | 80% | -1.8% |

## `depth-pro_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.64 | 1.06 | 15% | 46% | -12.2% |
| 10-20 m | 297 | 100% | 1.35 | 1.75 | 12% | 52% | -10.2% |
| 20-30 m | 226 | 100% | 2.89 | 3.43 | 14% | 42% | -12.4% |
| 30-50 m | 319 | 100% | 5.60 | 6.52 | 17% | 33% | -15.9% |
| 50+ m | 135 | 100% | 11.23 | 12.28 | 20% | 21% | -20.1% |

## `depth-pro_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.65 | 4.49 | 15% | 41% | -13.1% |
| pedestrian | 126 | 100% | 1.61 | 2.30 | 17% | 44% | -16.9% |
| van | 84 | 100% | 3.75 | 6.76 | 18% | 29% | -17.1% |
| truck | 42 | 100% | 3.39 | 5.78 | 15% | 36% | -10.4% |
| cyclist | 20 | 100% | 1.49 | 2.42 | 9% | 60% | -8.4% |

## `depth-pro_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 0.56 | 1.00 | 15% | 50% | -9.7% |
| 10-20 m | 297 | 100% | 1.28 | 1.60 | 11% | 60% | -8.7% |
| 20-30 m | 226 | 100% | 2.45 | 2.93 | 12% | 51% | -9.9% |
| 30-50 m | 319 | 100% | 4.63 | 5.76 | 15% | 41% | -13.7% |
| 50+ m | 135 | 100% | 10.94 | 11.33 | 19% | 24% | -18.5% |

## `depth-pro_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 2.31 | 4.02 | 13% | 47% | -11.1% |
| pedestrian | 126 | 100% | 1.30 | 2.03 | 16% | 49% | -15.4% |
| van | 84 | 100% | 3.35 | 6.05 | 16% | 37% | -14.1% |
| truck | 42 | 100% | 3.09 | 5.37 | 14% | 45% | -8.6% |
| cyclist | 20 | 100% | 1.04 | 2.13 | 8% | 75% | -5.5% |

## `depth-pro_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.03 | 2.21 | 30% | 6% | -29.7% |
| 10-20 m | 299 | 100% | 2.45 | 2.56 | 17% | 26% | -17.1% |
| 20-30 m | 246 | 100% | 3.37 | 3.64 | 14% | 34% | -14.1% |
| 30-50 m | 329 | 100% | 5.78 | 6.36 | 16% | 31% | -15.5% |
| 50+ m | 155 | 100% | 11.81 | 12.35 | 20% | 20% | -20.0% |

## `depth-pro_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 3.56 | 5.08 | 18% | 23% | -17.9% |
| pedestrian | 126 | 100% | 1.68 | 2.25 | 18% | 44% | -17.4% |
| van | 84 | 100% | 5.34 | 7.74 | 23% | 17% | -22.5% |
| truck | 42 | 100% | 8.04 | 9.23 | 22% | 14% | -21.7% |
| cyclist | 20 | 100% | 1.42 | 2.34 | 9% | 80% | -5.6% |

## `depth-pro_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.42 | 2.57 | 35% | 4% | -35.4% |
| 10-20 m | 299 | 100% | 2.83 | 3.08 | 21% | 16% | -20.9% |
| 20-30 m | 246 | 100% | 4.25 | 4.67 | 19% | 22% | -18.5% |
| 30-50 m | 329 | 100% | 7.44 | 7.94 | 20% | 16% | -19.8% |
| 50+ m | 155 | 100% | 13.82 | 14.35 | 24% | 9% | -23.3% |

## `depth-pro_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 4.56 | 6.22 | 22% | 13% | -22.2% |
| pedestrian | 126 | 100% | 2.15 | 2.77 | 20% | 33% | -20.3% |
| van | 84 | 100% | 6.33 | 9.20 | 28% | 5% | -27.6% |
| truck | 42 | 100% | 8.88 | 10.42 | 25% | 7% | -24.8% |
| cyclist | 20 | 100% | 2.27 | 3.14 | 12% | 45% | -12.0% |

## `depth-pro_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 2.27 | 2.45 | 34% | 4% | -33.5% |
| 10-20 m | 299 | 100% | 2.71 | 2.89 | 20% | 21% | -19.6% |
| 20-30 m | 246 | 100% | 3.81 | 4.14 | 16% | 26% | -16.3% |
| 30-50 m | 329 | 100% | 6.44 | 7.10 | 18% | 21% | -17.6% |
| 50+ m | 155 | 100% | 13.04 | 13.44 | 22% | 13% | -21.8% |

## `depth-pro_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 4.09 | 5.68 | 21% | 16% | -20.4% |
| pedestrian | 126 | 100% | 1.91 | 2.48 | 19% | 40% | -18.8% |
| van | 84 | 100% | 5.71 | 8.42 | 25% | 8% | -25.2% |
| truck | 42 | 100% | 8.24 | 9.90 | 24% | 12% | -23.5% |
| cyclist | 20 | 100% | 1.47 | 2.70 | 10% | 65% | -9.2% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| depth-pro_median | 868.815 |
| depth-pro_p10 | 2.673 |
| depth-pro_p25 | 2.537 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
