# nuScenes distance benchmark: `unidepth-v2-base`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 111.5 ms median, 113.6 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:51:52+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 321 | 100% | 1.17 | 2.00 | 8% | 70% | +7.2% |
| unidepth-v2-base_p10 | 321 | 100% | 0.85 | 1.56 | 6% | 83% | +3.3% |
| unidepth-v2-base_p25 | 321 | 100% | 0.90 | 1.60 | 6% | 79% | +4.7% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median / day | 227 | 100% | 1.25 | 2.19 | 8% | 75% | +7.0% |
| unidepth-v2-base_median / night | 94 | 100% | 1.12 | 1.53 | 9% | 59% | +7.9% |
| unidepth-v2-base_p10 / day | 227 | 100% | 0.88 | 1.69 | 6% | 87% | +2.8% |
| unidepth-v2-base_p10 / night | 94 | 100% | 0.79 | 1.24 | 7% | 71% | +4.7% |
| unidepth-v2-base_p25 / day | 227 | 100% | 0.98 | 1.73 | 6% | 84% | +4.2% |
| unidepth-v2-base_p25 / night | 94 | 100% | 0.87 | 1.27 | 7% | 67% | +5.8% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 1797 | 100% | 1.29 | 2.77 | 8% | 74% | +1.9% |
| unidepth-v2-base_p10 | 1797 | 100% | 1.26 | 3.01 | 8% | 74% | -3.2% |
| unidepth-v2-base_p25 | 1797 | 100% | 1.16 | 2.76 | 7% | 76% | -1.3% |

### `unidepth-v2-base_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.48 | 0.63 | 9% | 68% | +9.1% |
| 10-20 m | 97 | 100% | 1.04 | 1.17 | 7% | 70% | +6.2% |
| 20-30 m | 81 | 100% | 1.50 | 1.74 | 8% | 72% | +7.1% |
| 30-50 m | 31 | 100% | 2.32 | 4.30 | 11% | 65% | +10.6% |
| 50+ m | 53 | 100% | 3.36 | 4.08 | 6% | 75% | +5.3% |

### `unidepth-v2-base_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.30 | 2.72 | 7% | 75% | +2.2% |
| pedestrian | 327 | 100% | 0.96 | 1.79 | 8% | 75% | +2.8% |
| truck | 134 | 100% | 1.30 | 2.22 | 7% | 77% | +0.2% |
| bus | 110 | 100% | 2.68 | 6.70 | 12% | 58% | -6.2% |
| parked two-wheeler | 24 | 100% | 1.92 | 2.21 | 12% | 38% | +11.7% |
| cyclist | 15 | 100% | 1.77 | 4.82 | 14% | 53% | +14.1% |

### `unidepth-v2-base_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.28 | 0.36 | 5% | 83% | +5.1% |
| 10-20 m | 97 | 100% | 0.78 | 0.98 | 6% | 87% | +2.8% |
| 20-30 m | 81 | 100% | 1.18 | 1.61 | 7% | 75% | +3.5% |
| 30-50 m | 31 | 100% | 1.14 | 2.28 | 6% | 81% | +5.2% |
| 50+ m | 53 | 100% | 3.34 | 3.45 | 5% | 87% | +1.2% |

### `unidepth-v2-base_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.25 | 2.87 | 7% | 75% | -2.9% |
| pedestrian | 327 | 100% | 0.86 | 1.59 | 7% | 77% | -1.3% |
| truck | 134 | 100% | 1.86 | 3.02 | 8% | 72% | -5.7% |
| bus | 110 | 100% | 3.78 | 9.16 | 16% | 51% | -13.6% |
| parked two-wheeler | 24 | 100% | 1.33 | 1.62 | 8% | 71% | +6.3% |
| cyclist | 15 | 100% | 1.37 | 2.42 | 8% | 73% | +8.1% |

### `unidepth-v2-base_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.35 | 0.44 | 6% | 78% | +6.5% |
| 10-20 m | 97 | 100% | 0.86 | 0.99 | 6% | 81% | +4.1% |
| 20-30 m | 81 | 100% | 1.20 | 1.49 | 7% | 73% | +4.9% |
| 30-50 m | 31 | 100% | 1.52 | 2.80 | 7% | 74% | +6.7% |
| 50+ m | 53 | 100% | 3.19 | 3.46 | 5% | 87% | +2.5% |

### `unidepth-v2-base_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.14 | 2.65 | 7% | 78% | -1.1% |
| pedestrian | 327 | 100% | 0.87 | 1.55 | 7% | 78% | +0.4% |
| truck | 134 | 100% | 1.43 | 2.51 | 7% | 78% | -3.4% |
| bus | 110 | 100% | 2.87 | 7.94 | 14% | 56% | -10.4% |
| parked two-wheeler | 24 | 100% | 1.50 | 1.81 | 9% | 54% | +8.0% |
| cyclist | 15 | 100% | 1.48 | 3.81 | 11% | 67% | +11.2% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 321 | 100% | 1.40 | 1.92 | 7% | 76% | -2.7% |
| unidepth-v2-base_p10 | 321 | 100% | 1.72 | 2.13 | 9% | 69% | -6.2% |
| unidepth-v2-base_p25 | 321 | 100% | 1.58 | 1.99 | 8% | 72% | -4.9% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median / day | 227 | 100% | 1.30 | 2.11 | 7% | 79% | -1.5% |
| unidepth-v2-base_median / night | 94 | 100% | 1.43 | 1.47 | 8% | 68% | -5.5% |
| unidepth-v2-base_p10 / day | 227 | 100% | 1.73 | 2.29 | 8% | 72% | -5.4% |
| unidepth-v2-base_p10 / night | 94 | 100% | 1.71 | 1.74 | 10% | 61% | -8.1% |
| unidepth-v2-base_p25 / day | 227 | 100% | 1.60 | 2.14 | 8% | 75% | -4.0% |
| unidepth-v2-base_p25 / night | 94 | 100% | 1.58 | 1.63 | 9% | 64% | -7.2% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 1797 | 100% | 1.98 | 3.40 | 10% | 62% | -6.2% |
| unidepth-v2-base_p10 | 1797 | 100% | 2.60 | 4.34 | 12% | 49% | -10.8% |
| unidepth-v2-base_p25 | 1797 | 100% | 2.36 | 3.91 | 11% | 55% | -9.1% |

### `unidepth-v2-base_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.25 | 0.91 | 11% | 54% | -9.8% |
| 10-20 m | 82 | 100% | 1.00 | 1.17 | 7% | 78% | -3.9% |
| 20-30 m | 90 | 100% | 1.46 | 1.51 | 6% | 83% | -2.7% |
| 30-50 m | 44 | 100% | 2.00 | 3.36 | 9% | 73% | +2.8% |
| 50+ m | 53 | 100% | 2.81 | 3.60 | 5% | 85% | +1.8% |

### `unidepth-v2-base_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.99 | 3.17 | 9% | 64% | -6.8% |
| pedestrian | 327 | 100% | 0.96 | 1.74 | 7% | 73% | -0.1% |
| truck | 134 | 100% | 3.03 | 3.86 | 11% | 52% | -10.3% |
| bus | 110 | 100% | 5.83 | 10.60 | 18% | 24% | -17.9% |
| parked two-wheeler | 24 | 100% | 1.09 | 1.48 | 7% | 79% | +6.5% |
| cyclist | 15 | 100% | 1.53 | 4.26 | 12% | 60% | +11.6% |

### `unidepth-v2-base_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.37 | 1.07 | 13% | 52% | -12.5% |
| 10-20 m | 82 | 100% | 1.49 | 1.52 | 10% | 50% | -7.5% |
| 20-30 m | 90 | 100% | 1.68 | 1.86 | 8% | 73% | -5.4% |
| 30-50 m | 44 | 100% | 2.02 | 2.91 | 8% | 82% | -2.8% |
| 50+ m | 53 | 100% | 3.54 | 3.90 | 6% | 94% | -2.2% |

### `unidepth-v2-base_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.75 | 4.18 | 12% | 47% | -11.4% |
| pedestrian | 327 | 100% | 1.05 | 1.68 | 8% | 73% | -4.0% |
| truck | 134 | 100% | 4.34 | 5.44 | 16% | 28% | -15.3% |
| bus | 110 | 100% | 8.72 | 13.69 | 24% | 15% | -24.3% |
| parked two-wheeler | 24 | 100% | 0.89 | 1.36 | 7% | 83% | +1.4% |
| cyclist | 15 | 100% | 1.10 | 1.92 | 6% | 80% | +5.8% |

### `unidepth-v2-base_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.27 | 1.00 | 12% | 52% | -11.5% |
| 10-20 m | 82 | 100% | 1.31 | 1.36 | 8% | 61% | -6.1% |
| 20-30 m | 90 | 100% | 1.62 | 1.79 | 7% | 77% | -4.6% |
| 30-50 m | 44 | 100% | 1.94 | 2.69 | 7% | 77% | -0.4% |
| 50+ m | 53 | 100% | 3.14 | 3.67 | 5% | 96% | -1.0% |

### `unidepth-v2-base_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.48 | 3.74 | 11% | 54% | -9.8% |
| pedestrian | 327 | 100% | 1.03 | 1.58 | 7% | 74% | -2.3% |
| truck | 134 | 100% | 3.95 | 4.78 | 14% | 37% | -13.3% |
| bus | 110 | 100% | 7.48 | 12.26 | 22% | 17% | -21.5% |
| parked two-wheeler | 24 | 100% | 0.87 | 1.39 | 7% | 83% | +3.0% |
| cyclist | 15 | 100% | 1.24 | 3.29 | 9% | 67% | +8.8% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
