# nuScenes distance benchmark: `combinations`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `min(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `min(metric3d-v2-small_p10,unidepth-v2-base_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` |
| Depth model | `combination of saved runs: metric3d-v2-small, metric3d-v2-large, unidepth-v2-base, unidepth-v2-large`, given our focal length; inference sum of members ms median, sum of members ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:42:16+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 321 | 100% | 0.74 | 1.62 | 6% | 85% | -1.1% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 321 | 100% | 0.68 | 1.54 | 6% | 86% | +1.8% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 321 | 100% | 0.67 | 1.24 | 5% | 90% | +1.4% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 321 | 100% | 0.84 | 1.52 | 6% | 77% | +4.2% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 321 | 100% | 0.81 | 1.66 | 6% | 84% | -0.9% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 321 | 100% | 0.78 | 1.47 | 6% | 85% | +2.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 227 | 100% | 0.78 | 1.80 | 5% | 87% | -2.2% |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 94 | 100% | 0.65 | 1.17 | 6% | 81% | +1.7% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 227 | 100% | 0.64 | 1.63 | 5% | 90% | +0.5% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 94 | 100% | 0.86 | 1.32 | 7% | 76% | +4.9% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 227 | 100% | 0.68 | 1.33 | 5% | 94% | +0.6% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 94 | 100% | 0.66 | 1.03 | 6% | 81% | +3.3% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 227 | 100% | 0.76 | 1.50 | 5% | 86% | +2.8% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 94 | 100% | 1.38 | 1.56 | 8% | 55% | +7.6% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 227 | 100% | 0.79 | 1.81 | 6% | 87% | -2.3% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 94 | 100% | 0.81 | 1.30 | 7% | 76% | +2.4% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 227 | 100% | 0.78 | 1.51 | 5% | 92% | +0.7% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 94 | 100% | 0.79 | 1.37 | 8% | 68% | +5.4% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1797 | 100% | 1.83 | 4.62 | 12% | 57% | -10.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1797 | 100% | 1.44 | 3.46 | 9% | 68% | -6.5% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1797 | 100% | 1.32 | 3.15 | 8% | 72% | -6.1% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1797 | 100% | 1.20 | 2.72 | 7% | 75% | -3.3% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1797 | 100% | 1.83 | 4.63 | 12% | 58% | -10.0% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1797 | 100% | 1.40 | 3.58 | 9% | 68% | -6.2% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.26 | 0.30 | 4% | 98% | +3.1% |
| 10-20 m | 97 | 100% | 0.61 | 0.83 | 5% | 90% | -2.1% |
| 20-30 m | 81 | 100% | 1.00 | 1.56 | 7% | 79% | -0.9% |
| 30-50 m | 31 | 100% | 1.67 | 2.64 | 7% | 81% | -5.6% |
| 50+ m | 53 | 100% | 3.03 | 4.02 | 6% | 74% | -1.8% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.79 | 4.53 | 11% | 60% | -9.4% |
| pedestrian | 327 | 100% | 1.53 | 2.63 | 11% | 54% | -9.5% |
| truck | 134 | 100% | 2.84 | 4.58 | 12% | 52% | -11.3% |
| bus | 110 | 100% | 7.96 | 12.39 | 22% | 32% | -20.1% |
| parked two-wheeler | 24 | 100% | 0.68 | 2.54 | 12% | 67% | -11.7% |
| cyclist | 15 | 100% | 0.88 | 1.56 | 5% | 87% | -3.7% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.36 | 0.38 | 6% | 95% | +5.2% |
| 10-20 m | 97 | 100% | 0.49 | 0.76 | 5% | 92% | +0.6% |
| 20-30 m | 81 | 100% | 1.01 | 1.61 | 7% | 75% | +2.4% |
| 30-50 m | 31 | 100% | 1.05 | 1.94 | 5% | 84% | -1.0% |
| 50+ m | 53 | 100% | 3.25 | 3.88 | 6% | 83% | +1.0% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.43 | 3.42 | 9% | 70% | -5.8% |
| pedestrian | 327 | 100% | 1.22 | 1.93 | 9% | 68% | -5.8% |
| truck | 134 | 100% | 1.76 | 3.06 | 9% | 62% | -7.5% |
| bus | 110 | 100% | 5.35 | 9.75 | 17% | 45% | -15.7% |
| parked two-wheeler | 24 | 100% | 0.53 | 1.34 | 6% | 79% | -5.2% |
| cyclist | 15 | 100% | 0.72 | 1.06 | 4% | 93% | -0.1% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.46 | 0.44 | 6% | 86% | +5.7% |
| 10-20 m | 97 | 100% | 0.47 | 0.65 | 4% | 94% | +0.1% |
| 20-30 m | 81 | 100% | 0.83 | 1.33 | 6% | 85% | +1.3% |
| 30-50 m | 31 | 100% | 1.32 | 1.59 | 4% | 94% | -0.1% |
| 50+ m | 53 | 100% | 2.47 | 2.86 | 4% | 92% | -0.1% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.30 | 3.16 | 8% | 73% | -5.6% |
| pedestrian | 327 | 100% | 1.16 | 1.70 | 8% | 74% | -5.3% |
| truck | 134 | 100% | 2.04 | 3.13 | 8% | 69% | -7.2% |
| bus | 110 | 100% | 3.37 | 7.89 | 15% | 55% | -13.1% |
| parked two-wheeler | 24 | 100% | 0.74 | 1.13 | 6% | 88% | -2.5% |
| cyclist | 15 | 100% | 1.04 | 2.01 | 6% | 87% | -4.2% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.61 | 0.59 | 9% | 59% | +8.6% |
| 10-20 m | 97 | 100% | 0.67 | 0.83 | 5% | 87% | +2.3% |
| 20-30 m | 81 | 100% | 1.62 | 1.78 | 8% | 64% | +5.3% |
| 30-50 m | 31 | 100% | 1.16 | 1.74 | 4% | 87% | +2.1% |
| 50+ m | 53 | 100% | 2.66 | 3.28 | 5% | 94% | +2.3% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.22 | 2.78 | 7% | 76% | -3.0% |
| pedestrian | 327 | 100% | 0.95 | 1.47 | 7% | 76% | -2.4% |
| truck | 134 | 100% | 1.45 | 2.29 | 7% | 80% | -4.5% |
| bus | 110 | 100% | 2.73 | 6.99 | 13% | 57% | -10.6% |
| parked two-wheeler | 24 | 100% | 1.16 | 1.27 | 7% | 79% | +3.3% |
| cyclist | 15 | 100% | 0.42 | 0.66 | 3% | 93% | +0.7% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.21 | 0.29 | 4% | 95% | +3.4% |
| 10-20 m | 97 | 100% | 0.70 | 0.89 | 5% | 90% | -1.3% |
| 20-30 m | 81 | 100% | 1.28 | 1.65 | 7% | 74% | -0.3% |
| 30-50 m | 31 | 100% | 1.73 | 2.64 | 7% | 81% | -5.5% |
| 50+ m | 53 | 100% | 3.40 | 4.05 | 6% | 77% | -3.4% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.81 | 4.55 | 11% | 61% | -9.2% |
| pedestrian | 327 | 100% | 1.48 | 2.55 | 11% | 55% | -8.9% |
| truck | 134 | 100% | 2.93 | 4.72 | 12% | 51% | -11.3% |
| bus | 110 | 100% | 7.96 | 12.40 | 21% | 32% | -20.0% |
| parked two-wheeler | 24 | 100% | 0.66 | 2.52 | 12% | 67% | -11.4% |
| cyclist | 15 | 100% | 0.71 | 1.48 | 5% | 87% | -2.8% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.30 | 0.35 | 5% | 90% | +4.9% |
| 10-20 m | 97 | 100% | 0.69 | 0.90 | 5% | 89% | +1.4% |
| 20-30 m | 81 | 100% | 1.06 | 1.71 | 7% | 72% | +3.0% |
| 30-50 m | 31 | 100% | 1.15 | 1.76 | 4% | 87% | -0.1% |
| 50+ m | 53 | 100% | 2.55 | 3.21 | 5% | 91% | +0.2% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.37 | 3.49 | 9% | 70% | -5.6% |
| pedestrian | 327 | 100% | 1.19 | 1.82 | 8% | 73% | -4.8% |
| truck | 134 | 100% | 2.22 | 3.64 | 9% | 58% | -8.2% |
| bus | 110 | 100% | 6.05 | 10.59 | 18% | 41% | -16.5% |
| parked two-wheeler | 24 | 100% | 0.62 | 1.13 | 6% | 79% | -2.6% |
| cyclist | 15 | 100% | 0.31 | 0.80 | 3% | 93% | +2.6% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 321 | 100% | 2.19 | 2.73 | 11% | 53% | -10.3% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 321 | 100% | 1.86 | 2.26 | 9% | 64% | -7.6% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 321 | 100% | 1.77 | 2.10 | 9% | 67% | -8.0% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 321 | 100% | 1.60 | 1.83 | 8% | 71% | -5.5% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 321 | 100% | 2.11 | 2.75 | 11% | 52% | -10.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 321 | 100% | 1.77 | 2.16 | 9% | 64% | -7.4% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 227 | 100% | 2.39 | 2.97 | 11% | 52% | -10.1% |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 94 | 100% | 1.87 | 2.15 | 11% | 55% | -10.9% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 227 | 100% | 2.05 | 2.51 | 9% | 66% | -7.5% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 94 | 100% | 1.55 | 1.68 | 9% | 62% | -8.0% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 227 | 100% | 1.79 | 2.23 | 9% | 69% | -7.4% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 94 | 100% | 1.73 | 1.79 | 10% | 61% | -9.4% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 227 | 100% | 1.72 | 2.07 | 8% | 72% | -5.4% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 94 | 100% | 1.20 | 1.26 | 8% | 70% | -5.6% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 227 | 100% | 2.32 | 3.04 | 11% | 51% | -10.1% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 94 | 100% | 1.81 | 2.07 | 11% | 55% | -10.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 227 | 100% | 1.90 | 2.37 | 9% | 65% | -7.3% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 94 | 100% | 1.61 | 1.66 | 9% | 63% | -7.6% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1797 | 100% | 3.73 | 6.42 | 18% | 28% | -17.4% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1797 | 100% | 3.14 | 5.05 | 14% | 38% | -13.9% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1797 | 100% | 3.11 | 4.80 | 14% | 39% | -13.5% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1797 | 100% | 2.67 | 4.08 | 12% | 49% | -10.9% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1797 | 100% | 3.72 | 6.42 | 17% | 29% | -17.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1797 | 100% | 3.00 | 5.16 | 14% | 40% | -13.6% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.63 | 1.19 | 14% | 50% | -14.1% |
| 10-20 m | 82 | 100% | 1.83 | 1.99 | 12% | 33% | -11.7% |
| 20-30 m | 90 | 100% | 2.26 | 2.45 | 10% | 56% | -9.4% |
| 30-50 m | 44 | 100% | 3.61 | 4.19 | 12% | 55% | -11.3% |
| 50+ m | 53 | 100% | 3.58 | 4.64 | 7% | 79% | -5.2% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.75 | 6.38 | 18% | 26% | -17.5% |
| pedestrian | 327 | 100% | 1.90 | 2.94 | 13% | 45% | -12.0% |
| truck | 134 | 100% | 5.80 | 7.33 | 21% | 10% | -20.4% |
| bus | 110 | 100% | 13.19 | 17.35 | 30% | 8% | -30.1% |
| parked two-wheeler | 24 | 100% | 1.54 | 3.33 | 16% | 54% | -16.0% |
| cyclist | 15 | 100% | 1.31 | 2.03 | 7% | 87% | -5.7% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.36 | 1.09 | 13% | 52% | -12.3% |
| 10-20 m | 82 | 100% | 1.66 | 1.68 | 10% | 43% | -9.6% |
| 20-30 m | 90 | 100% | 1.55 | 1.91 | 8% | 73% | -6.2% |
| 30-50 m | 44 | 100% | 2.71 | 3.39 | 10% | 75% | -7.6% |
| 50+ m | 53 | 100% | 3.38 | 3.98 | 6% | 87% | -2.4% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.19 | 5.01 | 15% | 36% | -14.1% |
| pedestrian | 327 | 100% | 1.59 | 2.17 | 10% | 58% | -8.4% |
| truck | 134 | 100% | 4.72 | 5.64 | 17% | 22% | -16.9% |
| bus | 110 | 100% | 10.79 | 14.60 | 26% | 12% | -26.1% |
| parked two-wheeler | 24 | 100% | 1.17 | 1.99 | 10% | 71% | -9.7% |
| cyclist | 15 | 100% | 0.96 | 1.04 | 5% | 87% | -2.2% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.43 | 1.15 | 14% | 52% | -11.4% |
| 10-20 m | 82 | 100% | 1.57 | 1.63 | 10% | 50% | -10.1% |
| 20-30 m | 90 | 100% | 1.80 | 1.95 | 8% | 71% | -7.4% |
| 30-50 m | 44 | 100% | 2.62 | 3.10 | 9% | 84% | -6.7% |
| 50+ m | 53 | 100% | 2.30 | 3.18 | 5% | 85% | -3.5% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.23 | 4.84 | 14% | 35% | -13.9% |
| pedestrian | 327 | 100% | 1.52 | 1.95 | 9% | 65% | -8.0% |
| truck | 134 | 100% | 4.63 | 5.73 | 17% | 22% | -16.6% |
| bus | 110 | 100% | 8.28 | 12.77 | 24% | 15% | -23.7% |
| parked two-wheeler | 24 | 100% | 1.16 | 1.56 | 8% | 67% | -7.1% |
| cyclist | 15 | 100% | 1.77 | 2.47 | 8% | 73% | -6.3% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.47 | 1.06 | 13% | 52% | -9.1% |
| 10-20 m | 82 | 100% | 1.48 | 1.50 | 9% | 56% | -8.4% |
| 20-30 m | 90 | 100% | 1.02 | 1.50 | 6% | 81% | -3.8% |
| 30-50 m | 44 | 100% | 2.41 | 2.80 | 8% | 82% | -4.3% |
| 50+ m | 53 | 100% | 2.62 | 2.86 | 4% | 89% | -1.2% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.83 | 4.10 | 12% | 45% | -11.5% |
| pedestrian | 327 | 100% | 1.15 | 1.62 | 8% | 72% | -5.1% |
| truck | 134 | 100% | 4.04 | 4.64 | 14% | 33% | -14.2% |
| bus | 110 | 100% | 7.94 | 11.62 | 22% | 18% | -21.6% |
| parked two-wheeler | 24 | 100% | 0.89 | 1.10 | 5% | 88% | -1.6% |
| cyclist | 15 | 100% | 0.70 | 0.78 | 3% | 93% | -1.5% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.63 | 1.17 | 14% | 50% | -14.0% |
| 10-20 m | 82 | 100% | 1.78 | 1.92 | 12% | 30% | -10.9% |
| 20-30 m | 90 | 100% | 1.96 | 2.35 | 9% | 59% | -8.7% |
| 30-50 m | 44 | 100% | 3.61 | 4.18 | 12% | 55% | -11.3% |
| 50+ m | 53 | 100% | 4.20 | 5.10 | 8% | 75% | -6.7% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.73 | 6.39 | 18% | 26% | -17.3% |
| pedestrian | 327 | 100% | 1.85 | 2.84 | 12% | 47% | -11.5% |
| truck | 134 | 100% | 5.98 | 7.48 | 21% | 9% | -20.5% |
| bus | 110 | 100% | 13.19 | 17.36 | 30% | 8% | -30.0% |
| parked two-wheeler | 24 | 100% | 1.52 | 3.30 | 16% | 58% | -15.7% |
| cyclist | 15 | 100% | 1.31 | 1.91 | 6% | 87% | -4.9% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.47 | 1.08 | 13% | 52% | -12.8% |
| 10-20 m | 82 | 100% | 1.60 | 1.62 | 10% | 41% | -8.7% |
| 20-30 m | 90 | 100% | 1.55 | 1.90 | 8% | 73% | -5.7% |
| 30-50 m | 44 | 100% | 2.67 | 3.25 | 9% | 75% | -7.0% |
| 50+ m | 53 | 100% | 3.27 | 3.59 | 5% | 89% | -3.2% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.08 | 5.06 | 14% | 38% | -13.9% |
| pedestrian | 327 | 100% | 1.49 | 2.03 | 9% | 61% | -7.4% |
| truck | 134 | 100% | 5.08 | 6.32 | 18% | 19% | -17.6% |
| bus | 110 | 100% | 11.46 | 15.41 | 27% | 12% | -26.9% |
| parked two-wheeler | 24 | 100% | 0.70 | 1.47 | 7% | 79% | -7.2% |
| cyclist | 15 | 100% | 0.45 | 0.67 | 3% | 93% | +0.4% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
