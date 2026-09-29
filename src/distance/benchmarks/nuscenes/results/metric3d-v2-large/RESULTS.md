# nuScenes distance benchmark: `metric3d-v2-large`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-large_median`, `metric3d-v2-large_p10`, `metric3d-v2-large_p25` |
| Depth model | `metric3d-v2-large`, given our focal length; inference 886.8 ms median, 892.5 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:49:40+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 321 | 100% | 1.18 | 1.90 | 9% | 61% | +7.4% |
| metric3d-v2-large_p10 | 321 | 100% | 1.07 | 1.73 | 8% | 69% | +4.3% |
| metric3d-v2-large_p25 | 321 | 100% | 1.04 | 1.73 | 8% | 68% | +5.6% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median / day | 227 | 100% | 0.93 | 1.65 | 7% | 73% | +4.9% |
| metric3d-v2-large_median / night | 94 | 100% | 2.40 | 2.52 | 14% | 32% | +13.5% |
| metric3d-v2-large_p10 / day | 227 | 100% | 0.89 | 1.51 | 6% | 82% | +1.9% |
| metric3d-v2-large_p10 / night | 94 | 100% | 2.08 | 2.27 | 12% | 38% | +10.3% |
| metric3d-v2-large_p25 / day | 227 | 100% | 0.87 | 1.48 | 6% | 81% | +3.2% |
| metric3d-v2-large_p25 / night | 94 | 100% | 2.15 | 2.34 | 12% | 38% | +11.4% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 1797 | 100% | 1.29 | 2.61 | 8% | 74% | -0.3% |
| metric3d-v2-large_p10 | 1797 | 100% | 1.57 | 3.76 | 10% | 64% | -5.5% |
| metric3d-v2-large_p25 | 1797 | 100% | 1.40 | 2.99 | 8% | 71% | -2.9% |

### `metric3d-v2-large_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.84 | 0.95 | 14% | 17% | +14.0% |
| 10-20 m | 97 | 100% | 0.81 | 1.13 | 7% | 71% | +5.5% |
| 20-30 m | 81 | 100% | 2.58 | 2.54 | 11% | 46% | +10.0% |
| 30-50 m | 31 | 100% | 1.40 | 1.88 | 5% | 90% | +2.5% |
| 50+ m | 53 | 100% | 3.35 | 3.41 | 5% | 96% | +2.6% |

### `metric3d-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.33 | 2.69 | 7% | 74% | +0.2% |
| pedestrian | 327 | 100% | 0.95 | 1.39 | 7% | 73% | -0.2% |
| truck | 134 | 100% | 1.48 | 2.26 | 6% | 83% | -1.2% |
| bus | 110 | 100% | 2.52 | 5.92 | 11% | 64% | -6.2% |
| parked two-wheeler | 24 | 100% | 1.81 | 2.18 | 12% | 50% | +8.3% |
| cyclist | 15 | 100% | 0.83 | 1.72 | 5% | 87% | -0.6% |

### `metric3d-v2-large_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.69 | 0.70 | 10% | 36% | +10.4% |
| 10-20 m | 97 | 100% | 0.55 | 1.01 | 6% | 81% | +2.0% |
| 20-30 m | 81 | 100% | 2.07 | 2.51 | 11% | 54% | +7.0% |
| 30-50 m | 31 | 100% | 1.30 | 1.63 | 4% | 94% | -0.8% |
| 50+ m | 53 | 100% | 2.50 | 3.09 | 5% | 92% | +0.8% |

### `metric3d-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.65 | 3.98 | 10% | 64% | -5.4% |
| pedestrian | 327 | 100% | 1.16 | 1.83 | 9% | 68% | -3.3% |
| truck | 134 | 100% | 2.03 | 3.44 | 9% | 64% | -7.2% |
| bus | 110 | 100% | 3.24 | 8.15 | 15% | 54% | -12.7% |
| parked two-wheeler | 24 | 100% | 1.87 | 2.13 | 11% | 54% | +2.6% |
| cyclist | 15 | 100% | 0.75 | 1.88 | 5% | 80% | -2.0% |

### `metric3d-v2-large_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.75 | 0.77 | 11% | 27% | +11.5% |
| 10-20 m | 97 | 100% | 0.61 | 1.01 | 6% | 82% | +3.5% |
| 20-30 m | 81 | 100% | 2.16 | 2.41 | 11% | 54% | +8.5% |
| 30-50 m | 31 | 100% | 1.48 | 1.64 | 4% | 94% | +0.8% |
| 50+ m | 53 | 100% | 2.99 | 3.16 | 5% | 94% | +1.6% |

### `metric3d-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.45 | 3.12 | 8% | 72% | -2.6% |
| pedestrian | 327 | 100% | 1.09 | 1.53 | 8% | 71% | -1.6% |
| truck | 134 | 100% | 1.73 | 2.76 | 7% | 75% | -4.8% |
| bus | 110 | 100% | 2.83 | 6.50 | 12% | 62% | -9.2% |
| parked two-wheeler | 24 | 100% | 2.00 | 2.10 | 11% | 50% | +5.7% |
| cyclist | 15 | 100% | 0.86 | 1.78 | 5% | 87% | -1.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 321 | 100% | 1.39 | 1.68 | 7% | 75% | -2.7% |
| metric3d-v2-large_p10 | 321 | 100% | 1.61 | 2.00 | 9% | 67% | -5.4% |
| metric3d-v2-large_p25 | 321 | 100% | 1.53 | 1.82 | 8% | 70% | -4.3% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median / day | 227 | 100% | 1.39 | 1.79 | 7% | 77% | -3.6% |
| metric3d-v2-large_median / night | 94 | 100% | 1.40 | 1.43 | 8% | 72% | -0.5% |
| metric3d-v2-large_p10 / day | 227 | 100% | 1.65 | 2.15 | 9% | 67% | -6.3% |
| metric3d-v2-large_p10 / night | 94 | 100% | 1.59 | 1.64 | 9% | 67% | -3.2% |
| metric3d-v2-large_p25 / day | 227 | 100% | 1.61 | 1.94 | 8% | 71% | -5.1% |
| metric3d-v2-large_p25 / night | 94 | 100% | 1.51 | 1.53 | 8% | 68% | -2.2% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 1797 | 100% | 2.37 | 3.64 | 10% | 55% | -8.2% |
| metric3d-v2-large_p10 | 1797 | 100% | 3.03 | 5.19 | 14% | 40% | -13.0% |
| metric3d-v2-large_p25 | 1797 | 100% | 2.74 | 4.29 | 12% | 46% | -10.6% |

### `metric3d-v2-large_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.58 | 0.94 | 12% | 56% | -5.2% |
| 10-20 m | 82 | 100% | 1.08 | 1.17 | 7% | 71% | -5.4% |
| 20-30 m | 90 | 100% | 1.59 | 1.75 | 7% | 78% | +0.3% |
| 30-50 m | 44 | 100% | 2.24 | 2.46 | 7% | 82% | -2.9% |
| 50+ m | 53 | 100% | 2.14 | 2.44 | 4% | 92% | -0.9% |

### `metric3d-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.48 | 3.62 | 11% | 52% | -8.7% |
| pedestrian | 327 | 100% | 1.22 | 1.51 | 7% | 77% | -3.0% |
| truck | 134 | 100% | 3.30 | 4.17 | 12% | 41% | -11.6% |
| bus | 110 | 100% | 7.03 | 10.22 | 18% | 24% | -17.9% |
| parked two-wheeler | 24 | 100% | 1.86 | 1.74 | 9% | 62% | +3.1% |
| cyclist | 15 | 100% | 0.76 | 2.00 | 6% | 87% | -2.7% |

### `metric3d-v2-large_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.52 | 0.99 | 12% | 54% | -7.5% |
| 10-20 m | 82 | 100% | 1.58 | 1.66 | 10% | 54% | -8.9% |
| 20-30 m | 90 | 100% | 1.74 | 2.01 | 8% | 69% | -2.0% |
| 30-50 m | 44 | 100% | 2.51 | 2.98 | 8% | 82% | -6.9% |
| 50+ m | 53 | 100% | 1.58 | 2.67 | 4% | 85% | -2.6% |

### `metric3d-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.20 | 5.35 | 15% | 37% | -13.8% |
| pedestrian | 327 | 100% | 1.40 | 2.00 | 9% | 66% | -6.1% |
| truck | 134 | 100% | 4.93 | 6.02 | 17% | 20% | -16.7% |
| bus | 110 | 100% | 8.31 | 12.94 | 23% | 17% | -23.5% |
| parked two-wheeler | 24 | 100% | 2.01 | 2.11 | 10% | 50% | -2.4% |
| cyclist | 15 | 100% | 0.94 | 2.24 | 6% | 73% | -4.1% |

### `metric3d-v2-large_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.52 | 0.98 | 12% | 54% | -6.7% |
| 10-20 m | 82 | 100% | 1.44 | 1.46 | 9% | 57% | -7.6% |
| 20-30 m | 90 | 100% | 1.65 | 1.90 | 8% | 73% | -1.1% |
| 30-50 m | 44 | 100% | 2.38 | 2.55 | 7% | 86% | -4.5% |
| 50+ m | 53 | 100% | 1.93 | 2.46 | 4% | 87% | -1.8% |

### `metric3d-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.88 | 4.34 | 13% | 43% | -11.2% |
| pedestrian | 327 | 100% | 1.35 | 1.68 | 8% | 72% | -4.3% |
| truck | 134 | 100% | 4.03 | 5.20 | 15% | 28% | -14.6% |
| bus | 110 | 100% | 7.77 | 11.17 | 20% | 18% | -20.4% |
| parked two-wheeler | 24 | 100% | 1.79 | 1.82 | 9% | 62% | +0.5% |
| cyclist | 15 | 100% | 0.86 | 2.10 | 6% | 73% | -3.5% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
