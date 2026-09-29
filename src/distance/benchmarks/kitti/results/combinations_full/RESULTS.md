# KITTI distance benchmark: `combinations_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `min(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `min(metric3d-v2-small_p10,unidepth-v2-base_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` |
| Depth model | `combination of saved runs: metric3d-v2-small_full, metric3d-v2-large_full, unidepth-v2-base_full, unidepth-v2-large_full`, given our focal length; inference sum of members ms median, sum of members ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `62bd9e8` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T20:49:18+00:00 |

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
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 6484 | 100% | 1.78 | 3.38 | 12% | 53% | -11.4% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 6484 | 100% | 1.41 | 2.69 | 10% | 63% | -8.5% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 6484 | 100% | 1.56 | 2.65 | 11% | 59% | -9.3% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 6484 | 100% | 1.06 | 2.04 | 8% | 70% | -5.9% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 6484 | 100% | 1.87 | 3.52 | 13% | 51% | -11.8% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 6484 | 100% | 1.47 | 2.83 | 10% | 61% | -8.9% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 6484 | 100% | 3.68 | 5.17 | 20% | 18% | -20.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 6484 | 100% | 3.20 | 4.36 | 18% | 27% | -17.5% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 6484 | 100% | 3.41 | 4.38 | 18% | 25% | -18.2% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 6484 | 100% | 2.74 | 3.56 | 16% | 37% | -15.2% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 6484 | 100% | 3.78 | 5.33 | 21% | 16% | -20.6% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 6484 | 100% | 3.28 | 4.53 | 18% | 25% | -18.0% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1020 | 100% | 1.24 | 2.05 | 6% | 85% | -5.8% |
| in path / mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1020 | 100% | 0.87 | 1.48 | 4% | 93% | -2.9% |
| in path / min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1020 | 100% | 1.11 | 1.53 | 5% | 90% | -4.1% |
| in path / mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1020 | 100% | 0.67 | 1.10 | 3% | 96% | -0.6% |
| in path / min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1020 | 100% | 1.15 | 2.14 | 6% | 84% | -5.8% |
| in path / mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1020 | 100% | 0.77 | 1.57 | 4% | 92% | -3.2% |
| beside / min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 5464 | 100% | 1.91 | 3.62 | 13% | 47% | -12.5% |
| beside / mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 5464 | 100% | 1.53 | 2.91 | 11% | 57% | -9.5% |
| beside / min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 5464 | 100% | 1.67 | 2.86 | 12% | 53% | -10.3% |
| beside / mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 5464 | 100% | 1.19 | 2.22 | 9% | 65% | -6.9% |
| beside / min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 5464 | 100% | 2.06 | 3.78 | 14% | 44% | -12.9% |
| beside / mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 5464 | 100% | 1.64 | 3.07 | 12% | 56% | -10.0% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.48 | 0.49 | 7% | 87% | -6.6% |
| 10-20 m | 183 | 100% | 0.81 | 0.94 | 6% | 85% | -5.9% |
| 20-30 m | 279 | 100% | 1.01 | 1.17 | 5% | 92% | -4.3% |
| 30-50 m | 335 | 100% | 2.28 | 2.63 | 7% | 83% | -6.2% |
| 50+ m | 125 | 100% | 3.85 | 5.29 | 8% | 69% | -7.0% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.30 | 0.35 | 5% | 92% | -4.3% |
| 10-20 m | 183 | 100% | 0.44 | 0.61 | 4% | 93% | -3.1% |
| 20-30 m | 279 | 100% | 0.71 | 0.84 | 3% | 97% | -1.9% |
| 30-50 m | 335 | 100% | 1.58 | 1.94 | 5% | 90% | -3.3% |
| 50+ m | 125 | 100% | 3.28 | 3.84 | 6% | 89% | -2.8% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.48 | 0.50 | 7% | 86% | -6.6% |
| 10-20 m | 183 | 100% | 0.77 | 0.85 | 6% | 88% | -4.9% |
| 20-30 m | 279 | 100% | 0.94 | 1.08 | 4% | 95% | -3.7% |
| 30-50 m | 335 | 100% | 1.83 | 2.04 | 5% | 89% | -4.1% |
| 50+ m | 125 | 100% | 2.24 | 2.91 | 5% | 91% | -1.7% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.27 | 0.31 | 4% | 97% | -3.8% |
| 10-20 m | 183 | 100% | 0.37 | 0.52 | 3% | 96% | -1.8% |
| 20-30 m | 279 | 100% | 0.58 | 0.71 | 3% | 100% | -0.5% |
| 30-50 m | 335 | 100% | 1.07 | 1.31 | 3% | 97% | -0.2% |
| 50+ m | 125 | 100% | 2.29 | 2.85 | 4% | 87% | +2.0% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.48 | 0.47 | 6% | 83% | -6.2% |
| 10-20 m | 183 | 100% | 0.70 | 0.82 | 5% | 92% | -5.1% |
| 20-30 m | 279 | 100% | 0.92 | 1.03 | 4% | 95% | -3.9% |
| 30-50 m | 335 | 100% | 2.14 | 2.73 | 7% | 82% | -6.6% |
| 50+ m | 125 | 100% | 5.02 | 6.25 | 10% | 56% | -9.0% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.29 | 0.35 | 5% | 94% | -4.0% |
| 10-20 m | 183 | 100% | 0.39 | 0.55 | 4% | 95% | -2.6% |
| 20-30 m | 279 | 100% | 0.60 | 0.76 | 3% | 98% | -1.7% |
| 30-50 m | 335 | 100% | 1.65 | 1.98 | 5% | 90% | -3.7% |
| 50+ m | 125 | 100% | 3.75 | 4.70 | 7% | 77% | -5.2% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1020 | 100% | 3.14 | 3.89 | 13% | 36% | -12.6% |
| in path / mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1020 | 100% | 2.60 | 3.05 | 10% | 52% | -9.9% |
| in path / min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1020 | 100% | 2.89 | 3.20 | 11% | 45% | -11.0% |
| in path / mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1020 | 100% | 2.11 | 2.34 | 9% | 67% | -7.8% |
| in path / min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1020 | 100% | 3.07 | 4.03 | 13% | 34% | -12.7% |
| in path / mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1020 | 100% | 2.51 | 3.20 | 10% | 53% | -10.2% |
| beside / min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 5464 | 100% | 3.80 | 5.41 | 22% | 15% | -21.6% |
| beside / mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 5464 | 100% | 3.33 | 4.61 | 19% | 23% | -19.0% |
| beside / min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 5464 | 100% | 3.51 | 4.60 | 20% | 21% | -19.6% |
| beside / mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 5464 | 100% | 2.90 | 3.78 | 17% | 32% | -16.6% |
| beside / min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 5464 | 100% | 3.99 | 5.58 | 22% | 13% | -22.1% |
| beside / mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 5464 | 100% | 3.45 | 4.78 | 20% | 20% | -19.4% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.06 | 1.49 | 18% | 22% | -18.2% |
| 10-20 m | 160 | 100% | 2.50 | 2.41 | 16% | 18% | -15.6% |
| 20-30 m | 278 | 100% | 2.90 | 2.84 | 11% | 37% | -11.4% |
| 30-50 m | 348 | 100% | 4.25 | 4.53 | 12% | 44% | -11.5% |
| 50+ m | 149 | 100% | 6.32 | 7.30 | 11% | 46% | -10.9% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.97 | 1.33 | 16% | 32% | -16.4% |
| 10-20 m | 160 | 100% | 2.17 | 2.02 | 13% | 26% | -13.1% |
| 20-30 m | 278 | 100% | 2.28 | 2.30 | 9% | 56% | -9.2% |
| 30-50 m | 348 | 100% | 3.35 | 3.51 | 9% | 62% | -8.7% |
| 50+ m | 149 | 100% | 4.67 | 5.45 | 8% | 64% | -7.1% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.07 | 1.48 | 18% | 21% | -18.1% |
| 10-20 m | 160 | 100% | 2.45 | 2.29 | 15% | 23% | -14.7% |
| 20-30 m | 278 | 100% | 2.85 | 2.72 | 11% | 39% | -10.9% |
| 30-50 m | 348 | 100% | 3.70 | 3.81 | 10% | 55% | -9.5% |
| 50+ m | 149 | 100% | 4.18 | 4.66 | 7% | 71% | -6.3% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.98 | 1.29 | 16% | 34% | -15.9% |
| 10-20 m | 160 | 100% | 2.04 | 1.88 | 12% | 29% | -12.0% |
| 20-30 m | 278 | 100% | 2.11 | 2.03 | 8% | 71% | -8.0% |
| 30-50 m | 348 | 100% | 2.36 | 2.48 | 6% | 80% | -5.9% |
| 50+ m | 149 | 100% | 3.05 | 3.71 | 6% | 85% | -2.7% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.24 | 1.47 | 18% | 16% | -18.0% |
| 10-20 m | 160 | 100% | 2.41 | 2.30 | 15% | 18% | -14.9% |
| 20-30 m | 278 | 100% | 2.69 | 2.70 | 11% | 40% | -10.9% |
| 30-50 m | 348 | 100% | 4.12 | 4.65 | 12% | 41% | -11.8% |
| 50+ m | 149 | 100% | 7.09 | 8.37 | 13% | 36% | -12.8% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.05 | 1.31 | 16% | 32% | -16.2% |
| 10-20 m | 160 | 100% | 2.10 | 1.94 | 13% | 28% | -12.6% |
| 20-30 m | 278 | 100% | 2.21 | 2.24 | 9% | 59% | -9.0% |
| 30-50 m | 348 | 100% | 3.33 | 3.61 | 9% | 64% | -9.0% |
| 50+ m | 149 | 100% | 5.54 | 6.45 | 10% | 52% | -9.3% |

## `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.76 | 0.87 | 13% | 38% | -10.5% |
| 10-20 m | 1589 | 100% | 1.31 | 1.69 | 12% | 55% | -11.4% |
| 20-30 m | 1382 | 100% | 1.90 | 2.71 | 11% | 62% | -10.5% |
| 30-50 m | 1705 | 100% | 3.41 | 4.94 | 13% | 56% | -12.2% |
| 50+ m | 691 | 100% | 6.32 | 8.76 | 14% | 47% | -13.0% |

## `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.85 | 3.44 | 12% | 53% | -11.6% |
| pedestrian | 590 | 100% | 1.18 | 1.74 | 12% | 51% | -11.2% |
| van | 432 | 100% | 2.54 | 4.39 | 14% | 45% | -13.0% |
| truck | 187 | 100% | 2.66 | 4.87 | 13% | 60% | -9.5% |
| cyclist | 152 | 100% | 1.09 | 2.82 | 9% | 68% | -5.6% |

## `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.61 | 0.74 | 12% | 49% | -7.5% |
| 10-20 m | 1589 | 100% | 0.98 | 1.36 | 9% | 65% | -8.9% |
| 20-30 m | 1382 | 100% | 1.48 | 2.23 | 9% | 69% | -7.9% |
| 30-50 m | 1705 | 100% | 2.61 | 3.95 | 10% | 64% | -9.1% |
| 50+ m | 691 | 100% | 4.61 | 6.68 | 11% | 62% | -8.5% |

## `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.46 | 2.72 | 10% | 63% | -8.5% |
| pedestrian | 590 | 100% | 0.99 | 1.46 | 10% | 59% | -8.9% |
| van | 432 | 100% | 2.13 | 3.52 | 11% | 56% | -10.0% |
| truck | 187 | 100% | 1.81 | 3.84 | 10% | 70% | -6.4% |
| cyclist | 152 | 100% | 0.88 | 2.46 | 8% | 73% | -2.4% |

## `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.76 | 0.86 | 13% | 38% | -10.0% |
| 10-20 m | 1589 | 100% | 1.21 | 1.56 | 11% | 58% | -10.4% |
| 20-30 m | 1382 | 100% | 1.75 | 2.38 | 10% | 66% | -9.0% |
| 30-50 m | 1705 | 100% | 2.70 | 3.75 | 10% | 66% | -8.9% |
| 50+ m | 691 | 100% | 4.08 | 5.92 | 10% | 66% | -7.7% |

## `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.62 | 2.68 | 11% | 59% | -9.5% |
| pedestrian | 590 | 100% | 1.03 | 1.45 | 10% | 55% | -9.4% |
| van | 432 | 100% | 2.17 | 3.44 | 12% | 53% | -10.0% |
| truck | 187 | 100% | 2.15 | 4.06 | 11% | 66% | -7.5% |
| cyclist | 152 | 100% | 0.96 | 2.43 | 8% | 76% | -3.8% |

## `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.57 | 0.69 | 11% | 52% | -6.5% |
| 10-20 m | 1589 | 100% | 0.77 | 1.16 | 8% | 70% | -7.4% |
| 20-30 m | 1382 | 100% | 1.09 | 1.81 | 7% | 76% | -5.8% |
| 30-50 m | 1705 | 100% | 1.80 | 2.89 | 8% | 75% | -5.4% |
| 50+ m | 691 | 100% | 3.01 | 4.62 | 8% | 74% | -3.3% |

## `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.08 | 2.05 | 8% | 70% | -5.9% |
| pedestrian | 590 | 100% | 0.87 | 1.26 | 9% | 64% | -7.4% |
| van | 432 | 100% | 1.52 | 2.71 | 9% | 66% | -6.7% |
| truck | 187 | 100% | 1.16 | 2.75 | 8% | 73% | -3.8% |
| cyclist | 152 | 100% | 0.89 | 2.16 | 7% | 81% | -1.1% |

## `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.74 | 0.88 | 14% | 38% | -10.2% |
| 10-20 m | 1589 | 100% | 1.32 | 1.71 | 12% | 55% | -11.5% |
| 20-30 m | 1382 | 100% | 1.89 | 2.72 | 11% | 61% | -10.6% |
| 30-50 m | 1705 | 100% | 3.80 | 5.16 | 13% | 52% | -12.9% |
| 50+ m | 691 | 100% | 7.42 | 9.47 | 16% | 38% | -14.8% |

## `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.94 | 3.59 | 13% | 51% | -11.9% |
| pedestrian | 590 | 100% | 1.23 | 1.77 | 12% | 50% | -11.4% |
| van | 432 | 100% | 2.83 | 4.67 | 15% | 40% | -13.7% |
| truck | 187 | 100% | 3.09 | 5.29 | 13% | 51% | -10.4% |
| cyclist | 152 | 100% | 1.10 | 2.49 | 9% | 67% | -5.3% |

## `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.61 | 0.74 | 12% | 51% | -7.4% |
| 10-20 m | 1589 | 100% | 0.99 | 1.39 | 10% | 64% | -9.1% |
| 20-30 m | 1382 | 100% | 1.48 | 2.26 | 9% | 69% | -8.1% |
| 30-50 m | 1705 | 100% | 2.87 | 4.18 | 11% | 62% | -9.8% |
| 50+ m | 691 | 100% | 5.43 | 7.32 | 12% | 56% | -10.3% |

## `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.53 | 2.87 | 10% | 62% | -9.0% |
| pedestrian | 590 | 100% | 1.01 | 1.47 | 10% | 59% | -9.1% |
| van | 432 | 100% | 2.30 | 3.87 | 12% | 53% | -10.8% |
| truck | 187 | 100% | 2.09 | 4.17 | 11% | 65% | -6.9% |
| cyclist | 152 | 100% | 0.91 | 2.33 | 8% | 71% | -2.6% |

## `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.42 | 2.32 | 32% | 3% | -32.4% |
| 10-20 m | 1594 | 100% | 3.10 | 3.29 | 22% | 7% | -22.5% |
| 20-30 m | 1422 | 100% | 3.69 | 4.26 | 17% | 19% | -17.1% |
| 30-50 m | 1838 | 100% | 5.35 | 6.50 | 17% | 29% | -16.7% |
| 50+ m | 782 | 100% | 8.38 | 10.63 | 17% | 32% | -16.4% |

## `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.72 | 5.26 | 21% | 17% | -20.8% |
| pedestrian | 590 | 100% | 1.62 | 2.19 | 15% | 31% | -14.8% |
| van | 432 | 100% | 5.15 | 6.83 | 23% | 9% | -23.2% |
| truck | 187 | 100% | 7.99 | 9.59 | 23% | 6% | -23.5% |
| cyclist | 152 | 100% | 1.66 | 3.39 | 12% | 55% | -9.8% |

## `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.28 | 2.16 | 30% | 5% | -30.2% |
| 10-20 m | 1594 | 100% | 2.76 | 2.97 | 20% | 11% | -20.3% |
| 20-30 m | 1422 | 100% | 3.22 | 3.71 | 15% | 30% | -14.8% |
| 30-50 m | 1838 | 100% | 4.39 | 5.41 | 14% | 42% | -13.7% |
| 50+ m | 782 | 100% | 6.53 | 8.33 | 14% | 46% | -12.2% |

## `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.26 | 4.43 | 18% | 26% | -18.1% |
| pedestrian | 590 | 100% | 1.45 | 1.88 | 13% | 40% | -12.6% |
| van | 432 | 100% | 4.44 | 5.82 | 21% | 16% | -20.5% |
| truck | 187 | 100% | 7.04 | 8.28 | 21% | 11% | -20.8% |
| cyclist | 152 | 100% | 1.22 | 2.80 | 10% | 66% | -6.8% |

## `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.38 | 2.29 | 32% | 3% | -32.0% |
| 10-20 m | 1594 | 100% | 3.02 | 3.17 | 22% | 8% | -21.7% |
| 20-30 m | 1422 | 100% | 3.50 | 3.95 | 16% | 23% | -15.8% |
| 30-50 m | 1838 | 100% | 4.52 | 5.35 | 14% | 40% | -13.7% |
| 50+ m | 782 | 100% | 6.00 | 7.61 | 12% | 49% | -11.4% |

## `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.47 | 4.44 | 19% | 23% | -18.8% |
| pedestrian | 590 | 100% | 1.50 | 1.87 | 14% | 37% | -13.1% |
| van | 432 | 100% | 4.60 | 5.74 | 21% | 17% | -20.5% |
| truck | 187 | 100% | 7.66 | 8.72 | 22% | 11% | -21.8% |
| cyclist | 152 | 100% | 1.51 | 2.88 | 10% | 66% | -8.0% |

## `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.18 | 2.10 | 29% | 5% | -29.4% |
| 10-20 m | 1594 | 100% | 2.61 | 2.78 | 19% | 13% | -19.1% |
| 20-30 m | 1422 | 100% | 2.78 | 3.27 | 13% | 40% | -13.0% |
| 30-50 m | 1838 | 100% | 3.30 | 4.17 | 11% | 58% | -10.4% |
| 50+ m | 782 | 100% | 4.62 | 5.80 | 9% | 66% | -7.2% |

## `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.78 | 3.58 | 16% | 36% | -15.6% |
| pedestrian | 590 | 100% | 1.31 | 1.65 | 12% | 45% | -11.1% |
| van | 432 | 100% | 3.92 | 4.77 | 18% | 28% | -17.5% |
| truck | 187 | 100% | 6.14 | 7.11 | 19% | 20% | -18.6% |
| cyclist | 152 | 100% | 1.11 | 2.43 | 9% | 72% | -5.5% |

## `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.38 | 2.31 | 32% | 3% | -32.1% |
| 10-20 m | 1594 | 100% | 3.09 | 3.30 | 23% | 7% | -22.6% |
| 20-30 m | 1422 | 100% | 3.68 | 4.27 | 17% | 19% | -17.2% |
| 30-50 m | 1838 | 100% | 5.66 | 6.73 | 17% | 25% | -17.2% |
| 50+ m | 782 | 100% | 9.44 | 11.41 | 19% | 24% | -18.2% |

## `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.86 | 5.44 | 21% | 15% | -21.2% |
| pedestrian | 590 | 100% | 1.69 | 2.22 | 15% | 29% | -15.0% |
| van | 432 | 100% | 5.43 | 7.11 | 24% | 7% | -23.8% |
| truck | 187 | 100% | 8.04 | 9.96 | 24% | 5% | -24.2% |
| cyclist | 152 | 100% | 1.65 | 3.03 | 11% | 53% | -9.6% |

## `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.23 | 2.15 | 30% | 6% | -30.0% |
| 10-20 m | 1594 | 100% | 2.79 | 2.98 | 20% | 11% | -20.4% |
| 20-30 m | 1422 | 100% | 3.21 | 3.73 | 15% | 30% | -15.0% |
| 30-50 m | 1838 | 100% | 4.76 | 5.65 | 15% | 37% | -14.3% |
| 50+ m | 782 | 100% | 7.51 | 9.09 | 15% | 35% | -13.9% |

## `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.35 | 4.60 | 19% | 23% | -18.5% |
| pedestrian | 590 | 100% | 1.47 | 1.90 | 13% | 41% | -12.8% |
| van | 432 | 100% | 4.82 | 6.22 | 21% | 12% | -21.3% |
| truck | 187 | 100% | 7.11 | 8.52 | 21% | 10% | -21.3% |
| cyclist | 152 | 100% | 1.26 | 2.65 | 9% | 63% | -7.0% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| metric3d-v2-small_median | 155.444 |
| metric3d-v2-small_p10 | 2.944 |
| metric3d-v2-small_p25 | 2.834 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
