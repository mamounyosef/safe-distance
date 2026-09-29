# nuScenes distance benchmark: `combinations`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `min(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `min(metric3d-v2-small_p10,unidepth-v2-base_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` |
| Depth model | `combination of saved runs: metric3d-v2-small, metric3d-v2-large, unidepth-v2-base, unidepth-v2-large`, given our focal length; inference sum of members ms median, sum of members ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (17 at night) |
| Objects | 838 matched to a detection of 838 labelled (visibility at least v40-60); 104 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:01:10+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 104 | 100% | 1.32 | 3.50 | 11% | 62% | -10.9% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 104 | 100% | 1.15 | 2.68 | 9% | 79% | -6.9% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 104 | 100% | 1.19 | 2.56 | 9% | 83% | -6.9% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 104 | 100% | 1.03 | 2.34 | 8% | 82% | -4.4% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 104 | 100% | 1.32 | 3.49 | 11% | 62% | -10.4% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 104 | 100% | 1.20 | 2.76 | 9% | 78% | -6.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 104 | 100% | 1.32 | 3.50 | 11% | 62% | -10.9% |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 104 | 100% | 1.15 | 2.68 | 9% | 79% | -6.9% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 104 | 100% | 1.19 | 2.56 | 9% | 83% | -6.9% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 104 | 100% | 1.03 | 2.34 | 8% | 82% | -4.4% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 104 | 100% | 1.32 | 3.49 | 11% | 62% | -10.4% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 0 | - | - | - | - | - | - |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 104 | 100% | 1.20 | 2.76 | 9% | 78% | -6.1% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 0 | - | - | - | - | - | - |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 838 | 100% | 4.54 | 9.47 | 22% | 31% | -22.0% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 838 | 100% | 3.07 | 7.74 | 18% | 46% | -17.3% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 838 | 100% | 2.47 | 7.29 | 17% | 54% | -16.4% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 838 | 100% | 1.96 | 6.47 | 15% | 62% | -13.3% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 838 | 100% | 4.52 | 9.45 | 22% | 32% | -21.7% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 838 | 100% | 2.82 | 7.68 | 18% | 48% | -16.7% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.16 | 0.17 | 2% | 100% | -1.2% |
| 10-20 m | 32 | 100% | 0.40 | 1.61 | 10% | 84% | -9.4% |
| 20-30 m | 25 | 100% | 2.79 | 2.96 | 12% | 48% | -11.2% |
| 30-50 m | 30 | 100% | 4.34 | 4.89 | 13% | 40% | -12.8% |
| 50+ m | 4 | 100% | 15.36 | 22.45 | 40% | 0% | -39.7% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 3.74 | 4.69 | 16% | 37% | -15.8% |
| barrier | 369 | 100% | 11.12 | 15.55 | 30% | 23% | -30.0% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.13 | 0.16 | 2% | 100% | +0.9% |
| 10-20 m | 32 | 100% | 0.31 | 1.44 | 9% | 88% | -8.0% |
| 20-30 m | 25 | 100% | 1.49 | 2.54 | 10% | 72% | -7.4% |
| 30-50 m | 30 | 100% | 2.73 | 3.41 | 9% | 70% | -5.8% |
| 50+ m | 4 | 100% | 8.16 | 16.37 | 29% | 50% | -29.4% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.48 | 3.39 | 12% | 54% | -11.0% |
| barrier | 369 | 100% | 7.94 | 13.27 | 26% | 35% | -25.3% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.16 | 0.17 | 2% | 100% | -1.2% |
| 10-20 m | 32 | 100% | 0.25 | 1.40 | 9% | 88% | -8.1% |
| 20-30 m | 25 | 100% | 1.80 | 2.71 | 11% | 80% | -7.4% |
| 30-50 m | 30 | 100% | 2.52 | 2.81 | 8% | 77% | -4.7% |
| 50+ m | 4 | 100% | 8.20 | 16.72 | 30% | 50% | -29.9% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.88 | 3.27 | 11% | 67% | -10.5% |
| barrier | 369 | 100% | 5.84 | 12.40 | 24% | 37% | -24.0% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.10 | 0.21 | 3% | 100% | +2.1% |
| 10-20 m | 32 | 100% | 0.18 | 1.36 | 8% | 88% | -6.6% |
| 20-30 m | 25 | 100% | 1.56 | 2.51 | 10% | 80% | -5.3% |
| 30-50 m | 30 | 100% | 2.39 | 2.48 | 7% | 73% | -1.6% |
| 50+ m | 4 | 100% | 5.48 | 14.97 | 27% | 50% | -24.4% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.44 | 2.62 | 9% | 75% | -7.3% |
| barrier | 369 | 100% | 4.66 | 11.36 | 22% | 46% | -21.1% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.12 | 0.18 | 2% | 100% | +1.0% |
| 10-20 m | 32 | 100% | 0.31 | 1.57 | 9% | 84% | -8.4% |
| 20-30 m | 25 | 100% | 2.79 | 2.96 | 12% | 48% | -11.2% |
| 30-50 m | 30 | 100% | 4.23 | 4.88 | 13% | 40% | -12.8% |
| 50+ m | 4 | 100% | 15.36 | 22.45 | 40% | 0% | -39.7% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 3.74 | 4.67 | 16% | 37% | -15.5% |
| barrier | 369 | 100% | 11.12 | 15.52 | 30% | 25% | -29.6% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.15 | 0.21 | 3% | 100% | +2.4% |
| 10-20 m | 32 | 100% | 0.23 | 1.40 | 8% | 88% | -6.8% |
| 20-30 m | 25 | 100% | 1.51 | 2.47 | 10% | 80% | -6.8% |
| 30-50 m | 30 | 100% | 3.22 | 3.55 | 10% | 63% | -5.0% |
| 50+ m | 4 | 100% | 9.66 | 17.73 | 32% | 25% | -31.7% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.35 | 3.42 | 12% | 56% | -10.4% |
| barrier | 369 | 100% | 7.99 | 13.10 | 25% | 37% | -24.6% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 104 | 100% | 1.61 | 3.86 | 13% | 52% | -13.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 104 | 100% | 1.36 | 2.96 | 11% | 74% | -9.2% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 104 | 100% | 1.20 | 2.84 | 10% | 72% | -9.2% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 104 | 100% | 1.27 | 2.56 | 9% | 80% | -6.7% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 104 | 100% | 1.61 | 3.79 | 13% | 55% | -12.6% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 104 | 100% | 1.37 | 2.97 | 10% | 76% | -8.4% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 104 | 100% | 1.61 | 3.86 | 13% | 52% | -13.2% |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / day | 104 | 100% | 1.36 | 2.96 | 11% | 74% | -9.2% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 104 | 100% | 1.20 | 2.84 | 10% | 72% | -9.2% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / day | 104 | 100% | 1.27 | 2.56 | 9% | 80% | -6.7% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) / night | 0 | - | - | - | - | - | - |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 104 | 100% | 1.61 | 3.79 | 13% | 55% | -12.6% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 0 | - | - | - | - | - | - |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / day | 104 | 100% | 1.37 | 2.97 | 10% | 76% | -8.4% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) / night | 0 | - | - | - | - | - | - |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 838 | 100% | 4.93 | 10.12 | 24% | 23% | -23.8% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 838 | 100% | 3.47 | 8.36 | 20% | 37% | -19.1% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 838 | 100% | 3.09 | 7.90 | 19% | 45% | -18.3% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 838 | 100% | 2.43 | 6.99 | 16% | 55% | -15.3% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 838 | 100% | 4.89 | 10.08 | 24% | 24% | -23.5% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 838 | 100% | 3.28 | 8.27 | 19% | 40% | -18.6% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.41 | 0.48 | 6% | 80% | -6.0% |
| 10-20 m | 34 | 100% | 0.82 | 1.58 | 10% | 76% | -10.5% |
| 20-30 m | 26 | 100% | 3.08 | 3.68 | 15% | 42% | -14.8% |
| 30-50 m | 30 | 100% | 4.82 | 5.20 | 14% | 30% | -13.7% |
| 50+ m | 4 | 100% | 15.64 | 22.73 | 40% | 0% | -40.0% |

### `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.00 | 4.95 | 17% | 31% | -17.0% |
| barrier | 369 | 100% | 12.38 | 16.69 | 32% | 12% | -32.4% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.35 | 0.37 | 5% | 90% | -4.1% |
| 10-20 m | 34 | 100% | 0.71 | 1.35 | 9% | 88% | -9.0% |
| 20-30 m | 26 | 100% | 1.84 | 3.19 | 13% | 65% | -11.1% |
| 30-50 m | 30 | 100% | 3.22 | 3.62 | 10% | 63% | -6.7% |
| 50+ m | 4 | 100% | 8.43 | 16.66 | 30% | 50% | -29.7% |

### `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.75 | 3.63 | 13% | 49% | -12.3% |
| barrier | 369 | 100% | 9.19 | 14.38 | 28% | 22% | -27.9% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.41 | 0.48 | 6% | 80% | -5.9% |
| 10-20 m | 34 | 100% | 0.78 | 1.37 | 9% | 85% | -9.3% |
| 20-30 m | 26 | 100% | 2.16 | 3.25 | 13% | 62% | -11.2% |
| 30-50 m | 30 | 100% | 2.74 | 3.04 | 8% | 67% | -5.6% |
| 50+ m | 4 | 100% | 8.48 | 17.01 | 30% | 50% | -30.3% |

### `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.16 | 3.50 | 12% | 60% | -11.8% |
| barrier | 369 | 100% | 7.03 | 13.49 | 27% | 25% | -26.6% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.18 | 0.31 | 4% | 90% | -2.5% |
| 10-20 m | 34 | 100% | 0.66 | 1.26 | 8% | 91% | -7.8% |
| 20-30 m | 26 | 100% | 1.50 | 3.04 | 12% | 73% | -9.1% |
| 30-50 m | 30 | 100% | 2.65 | 2.69 | 7% | 73% | -2.5% |
| 50+ m | 4 | 100% | 5.46 | 15.10 | 27% | 50% | -24.8% |

### `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.65 | 2.79 | 10% | 72% | -8.6% |
| barrier | 369 | 100% | 5.79 | 12.32 | 24% | 33% | -23.8% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.29 | 0.33 | 4% | 90% | -3.9% |
| 10-20 m | 34 | 100% | 0.69 | 1.45 | 10% | 82% | -9.5% |
| 20-30 m | 26 | 100% | 3.08 | 3.66 | 15% | 42% | -14.7% |
| 30-50 m | 30 | 100% | 4.69 | 5.19 | 14% | 30% | -13.6% |
| 50+ m | 4 | 100% | 15.64 | 22.73 | 40% | 0% | -40.0% |

### `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.00 | 4.92 | 17% | 31% | -16.8% |
| barrier | 369 | 100% | 12.38 | 16.64 | 32% | 14% | -32.1% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.24 | 0.31 | 4% | 100% | -2.6% |
| 10-20 m | 34 | 100% | 0.51 | 1.21 | 8% | 88% | -7.9% |
| 20-30 m | 26 | 100% | 1.75 | 3.09 | 13% | 73% | -10.5% |
| 30-50 m | 30 | 100% | 3.27 | 3.76 | 10% | 63% | -5.9% |
| 50+ m | 4 | 100% | 9.94 | 18.02 | 32% | 25% | -32.0% |

### `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.61 | 3.64 | 13% | 51% | -11.7% |
| barrier | 369 | 100% | 9.33 | 14.15 | 27% | 27% | -27.2% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
