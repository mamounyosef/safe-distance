# nuScenes distance benchmark: `unidepth-v2-large`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 213.1 ms median, 215.2 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:53:50+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 321 | 100% | 0.99 | 2.03 | 8% | 72% | +6.6% |
| unidepth-v2-large_p10 | 321 | 100% | 0.70 | 1.53 | 6% | 85% | +2.8% |
| unidepth-v2-large_p25 | 321 | 100% | 0.78 | 1.57 | 6% | 82% | +4.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median / day | 227 | 100% | 0.97 | 2.31 | 7% | 74% | +6.4% |
| unidepth-v2-large_median / night | 94 | 100% | 1.02 | 1.37 | 8% | 68% | +7.2% |
| unidepth-v2-large_p10 / day | 227 | 100% | 0.71 | 1.74 | 6% | 86% | +2.4% |
| unidepth-v2-large_p10 / night | 94 | 100% | 0.67 | 1.03 | 6% | 81% | +3.7% |
| unidepth-v2-large_p25 / day | 227 | 100% | 0.79 | 1.78 | 6% | 84% | +3.8% |
| unidepth-v2-large_p25 / night | 94 | 100% | 0.73 | 1.08 | 6% | 77% | +4.9% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 1797 | 100% | 1.11 | 2.67 | 7% | 76% | +1.1% |
| unidepth-v2-large_p10 | 1797 | 100% | 1.21 | 2.87 | 8% | 74% | -3.8% |
| unidepth-v2-large_p25 | 1797 | 100% | 1.11 | 2.63 | 7% | 76% | -2.0% |

### `unidepth-v2-large_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.69 | 0.70 | 10% | 41% | +10.0% |
| 10-20 m | 97 | 100% | 0.80 | 0.94 | 6% | 85% | +4.6% |
| 20-30 m | 81 | 100% | 1.15 | 1.47 | 6% | 79% | +5.8% |
| 30-50 m | 31 | 100% | 2.16 | 3.84 | 10% | 77% | +9.0% |
| 50+ m | 53 | 100% | 3.66 | 5.30 | 8% | 70% | +6.6% |

### `unidepth-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.12 | 2.67 | 7% | 78% | +1.5% |
| pedestrian | 327 | 100% | 0.92 | 1.66 | 7% | 76% | +0.7% |
| truck | 134 | 100% | 1.36 | 2.47 | 6% | 78% | +1.9% |
| bus | 110 | 100% | 2.49 | 6.06 | 11% | 60% | -5.4% |
| parked two-wheeler | 24 | 100% | 0.88 | 1.19 | 7% | 79% | +6.2% |
| cyclist | 15 | 100% | 1.08 | 4.13 | 11% | 60% | +7.5% |

### `unidepth-v2-large_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.46 | 0.44 | 6% | 86% | +5.7% |
| 10-20 m | 97 | 100% | 0.58 | 0.75 | 5% | 92% | +1.2% |
| 20-30 m | 81 | 100% | 0.82 | 1.34 | 6% | 83% | +2.2% |
| 30-50 m | 31 | 100% | 1.06 | 2.14 | 5% | 84% | +3.5% |
| 50+ m | 53 | 100% | 3.06 | 4.12 | 6% | 74% | +3.0% |

### `unidepth-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.19 | 2.83 | 7% | 75% | -3.4% |
| pedestrian | 327 | 100% | 1.02 | 1.67 | 8% | 75% | -3.3% |
| truck | 134 | 100% | 1.78 | 2.58 | 8% | 74% | -4.2% |
| bus | 110 | 100% | 3.20 | 7.67 | 15% | 56% | -12.0% |
| parked two-wheeler | 24 | 100% | 0.58 | 0.90 | 5% | 92% | +1.0% |
| cyclist | 15 | 100% | 1.04 | 2.41 | 7% | 73% | +2.7% |

### `unidepth-v2-large_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.55 | 0.52 | 7% | 71% | +7.1% |
| 10-20 m | 97 | 100% | 0.59 | 0.76 | 5% | 93% | +2.5% |
| 20-30 m | 81 | 100% | 0.94 | 1.26 | 5% | 80% | +3.6% |
| 30-50 m | 31 | 100% | 1.23 | 2.40 | 6% | 84% | +4.8% |
| 50+ m | 53 | 100% | 3.09 | 4.24 | 7% | 74% | +4.2% |

### `unidepth-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.10 | 2.62 | 7% | 77% | -1.7% |
| pedestrian | 327 | 100% | 0.96 | 1.53 | 7% | 77% | -1.6% |
| truck | 134 | 100% | 1.35 | 2.30 | 6% | 82% | -1.7% |
| bus | 110 | 100% | 2.58 | 6.72 | 13% | 60% | -9.1% |
| parked two-wheeler | 24 | 100% | 0.54 | 0.96 | 5% | 88% | +2.6% |
| cyclist | 15 | 100% | 0.96 | 3.15 | 9% | 60% | +4.7% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 321 | 100% | 1.34 | 2.00 | 8% | 76% | -3.2% |
| unidepth-v2-large_p10 | 321 | 100% | 1.78 | 2.18 | 9% | 68% | -6.7% |
| unidepth-v2-large_p25 | 321 | 100% | 1.68 | 2.03 | 8% | 69% | -5.5% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median / day | 227 | 100% | 1.32 | 2.26 | 8% | 78% | -2.0% |
| unidepth-v2-large_median / night | 94 | 100% | 1.41 | 1.39 | 8% | 71% | -6.1% |
| unidepth-v2-large_p10 / day | 227 | 100% | 1.82 | 2.38 | 9% | 70% | -5.7% |
| unidepth-v2-large_p10 / night | 94 | 100% | 1.73 | 1.72 | 10% | 63% | -9.0% |
| unidepth-v2-large_p25 / day | 227 | 100% | 1.70 | 2.22 | 8% | 72% | -4.4% |
| unidepth-v2-large_p25 / night | 94 | 100% | 1.63 | 1.59 | 9% | 64% | -8.0% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 1797 | 100% | 2.06 | 3.38 | 10% | 61% | -6.9% |
| unidepth-v2-large_p10 | 1797 | 100% | 2.77 | 4.22 | 13% | 47% | -11.3% |
| unidepth-v2-large_p25 | 1797 | 100% | 2.55 | 3.81 | 11% | 53% | -9.7% |

### `unidepth-v2-large_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.56 | 1.08 | 13% | 54% | -8.6% |
| 10-20 m | 82 | 100% | 1.15 | 1.14 | 7% | 79% | -5.6% |
| 20-30 m | 90 | 100% | 1.31 | 1.44 | 6% | 83% | -3.8% |
| 30-50 m | 44 | 100% | 1.80 | 3.21 | 8% | 80% | +1.6% |
| 50+ m | 53 | 100% | 3.05 | 4.21 | 6% | 79% | +3.0% |

### `unidepth-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.11 | 3.28 | 10% | 60% | -7.4% |
| pedestrian | 327 | 100% | 1.14 | 1.72 | 7% | 75% | -2.1% |
| truck | 134 | 100% | 3.00 | 3.44 | 11% | 53% | -8.6% |
| bus | 110 | 100% | 5.78 | 9.69 | 17% | 31% | -17.1% |
| parked two-wheeler | 24 | 100% | 0.58 | 0.93 | 5% | 96% | +1.3% |
| cyclist | 15 | 100% | 1.09 | 3.79 | 10% | 60% | +5.1% |

### `unidepth-v2-large_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.43 | 1.15 | 14% | 52% | -11.4% |
| 10-20 m | 82 | 100% | 1.58 | 1.58 | 10% | 52% | -9.2% |
| 20-30 m | 90 | 100% | 1.82 | 1.88 | 8% | 74% | -6.5% |
| 30-50 m | 44 | 100% | 2.15 | 3.08 | 9% | 77% | -4.0% |
| 50+ m | 53 | 100% | 3.86 | 3.89 | 6% | 91% | -0.5% |

### `unidepth-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.98 | 4.21 | 13% | 45% | -11.8% |
| pedestrian | 327 | 100% | 1.27 | 1.83 | 8% | 67% | -6.0% |
| truck | 134 | 100% | 3.95 | 4.41 | 15% | 34% | -13.9% |
| bus | 110 | 100% | 8.03 | 12.10 | 23% | 17% | -22.7% |
| parked two-wheeler | 24 | 100% | 0.82 | 1.15 | 6% | 79% | -3.7% |
| cyclist | 15 | 100% | 1.16 | 2.12 | 7% | 87% | +0.5% |

### `unidepth-v2-large_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.47 | 1.14 | 14% | 52% | -10.4% |
| 10-20 m | 82 | 100% | 1.44 | 1.39 | 9% | 56% | -7.9% |
| 20-30 m | 90 | 100% | 1.71 | 1.77 | 7% | 76% | -5.8% |
| 30-50 m | 44 | 100% | 2.10 | 2.74 | 7% | 80% | -1.7% |
| 50+ m | 53 | 100% | 3.38 | 3.75 | 6% | 89% | +0.6% |

### `unidepth-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.68 | 3.81 | 12% | 51% | -10.2% |
| pedestrian | 327 | 100% | 1.23 | 1.65 | 8% | 70% | -4.3% |
| truck | 134 | 100% | 3.50 | 3.89 | 13% | 44% | -11.6% |
| bus | 110 | 100% | 7.39 | 10.91 | 20% | 22% | -20.2% |
| parked two-wheeler | 24 | 100% | 0.66 | 1.08 | 6% | 88% | -2.1% |
| cyclist | 15 | 100% | 1.23 | 2.85 | 8% | 67% | +2.4% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
