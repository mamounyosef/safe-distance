# nuScenes distance benchmark: `da3-metric-large`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da3-metric-large_median`, `da3-metric-large_p10`, `da3-metric-large_p25` |
| Depth model | `da3-metric-large`, given our focal length; inference 80.7 ms median, 84.6 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:55:01+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median | 321 | 100% | 1.40 | 2.31 | 10% | 60% | +4.1% |
| da3-metric-large_p10 | 321 | 100% | 1.40 | 2.72 | 9% | 61% | +0.3% |
| da3-metric-large_p25 | 321 | 100% | 1.28 | 2.50 | 9% | 61% | +1.8% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median / day | 227 | 100% | 1.24 | 2.52 | 9% | 65% | +2.2% |
| da3-metric-large_median / night | 94 | 100% | 1.69 | 1.80 | 11% | 48% | +8.6% |
| da3-metric-large_p10 / day | 227 | 100% | 1.25 | 3.18 | 9% | 63% | -1.8% |
| da3-metric-large_p10 / night | 94 | 100% | 1.49 | 1.61 | 9% | 57% | +5.4% |
| da3-metric-large_p25 / day | 227 | 100% | 1.23 | 2.86 | 9% | 63% | -0.2% |
| da3-metric-large_p25 / night | 94 | 100% | 1.49 | 1.64 | 10% | 55% | +6.5% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median | 1797 | 100% | 1.52 | 4.01 | 10% | 64% | -3.0% |
| da3-metric-large_p10 | 1797 | 100% | 1.78 | 4.76 | 11% | 60% | -7.4% |
| da3-metric-large_p25 | 1797 | 100% | 1.56 | 4.33 | 11% | 62% | -5.6% |

### `da3-metric-large_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 1.11 | 1.11 | 16% | 19% | +16.3% |
| 10-20 m | 97 | 100% | 0.92 | 1.24 | 8% | 71% | +5.2% |
| 20-30 m | 81 | 100% | 1.80 | 1.87 | 8% | 67% | +3.7% |
| 30-50 m | 31 | 100% | 1.80 | 2.70 | 7% | 81% | -1.5% |
| 50+ m | 53 | 100% | 4.83 | 6.07 | 9% | 64% | -7.6% |

### `da3-metric-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.62 | 4.02 | 10% | 64% | -3.9% |
| pedestrian | 327 | 100% | 1.09 | 1.82 | 9% | 66% | +3.6% |
| truck | 134 | 100% | 1.89 | 3.44 | 9% | 69% | -3.7% |
| bus | 110 | 100% | 6.53 | 12.02 | 20% | 40% | -14.4% |
| parked two-wheeler | 24 | 100% | 0.96 | 1.10 | 6% | 75% | +3.7% |
| cyclist | 15 | 100% | 0.74 | 1.97 | 6% | 80% | +2.9% |

### `da3-metric-large_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.84 | 0.79 | 12% | 37% | +11.6% |
| 10-20 m | 97 | 100% | 0.88 | 1.10 | 7% | 76% | +2.2% |
| 20-30 m | 81 | 100% | 1.83 | 2.17 | 9% | 64% | +0.3% |
| 30-50 m | 31 | 100% | 2.06 | 3.04 | 8% | 74% | -6.6% |
| 50+ m | 53 | 100% | 7.44 | 8.47 | 12% | 47% | -11.7% |

### `da3-metric-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.03 | 4.82 | 11% | 59% | -8.1% |
| pedestrian | 327 | 100% | 1.00 | 1.92 | 9% | 69% | -0.5% |
| truck | 134 | 100% | 2.05 | 4.50 | 11% | 55% | -9.2% |
| bus | 110 | 100% | 10.22 | 14.09 | 24% | 35% | -20.4% |
| parked two-wheeler | 24 | 100% | 1.08 | 1.38 | 7% | 75% | -1.2% |
| cyclist | 15 | 100% | 0.81 | 1.21 | 4% | 93% | +0.5% |

### `da3-metric-large_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.91 | 0.89 | 13% | 32% | +13.2% |
| 10-20 m | 97 | 100% | 0.83 | 1.13 | 7% | 76% | +3.4% |
| 20-30 m | 81 | 100% | 1.75 | 1.98 | 9% | 63% | +1.7% |
| 30-50 m | 31 | 100% | 1.55 | 2.74 | 7% | 74% | -4.4% |
| 50+ m | 53 | 100% | 6.61 | 7.47 | 11% | 53% | -10.1% |

### `da3-metric-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.70 | 4.37 | 10% | 62% | -6.4% |
| pedestrian | 327 | 100% | 1.05 | 1.78 | 8% | 68% | +1.3% |
| truck | 134 | 100% | 1.89 | 3.95 | 9% | 62% | -7.2% |
| bus | 110 | 100% | 9.12 | 12.99 | 22% | 35% | -17.8% |
| parked two-wheeler | 24 | 100% | 0.88 | 1.11 | 6% | 75% | +1.0% |
| cyclist | 15 | 100% | 0.78 | 1.46 | 5% | 87% | +1.5% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median | 321 | 100% | 1.79 | 2.91 | 10% | 57% | -5.8% |
| da3-metric-large_p10 | 321 | 100% | 2.06 | 3.66 | 12% | 48% | -9.2% |
| da3-metric-large_p25 | 321 | 100% | 1.93 | 3.34 | 11% | 51% | -7.9% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median / day | 227 | 100% | 2.05 | 3.50 | 11% | 52% | -6.1% |
| da3-metric-large_median / night | 94 | 100% | 1.07 | 1.49 | 7% | 69% | -5.1% |
| da3-metric-large_p10 / day | 227 | 100% | 2.41 | 4.45 | 13% | 42% | -9.8% |
| da3-metric-large_p10 / night | 94 | 100% | 1.21 | 1.75 | 9% | 62% | -7.8% |
| da3-metric-large_p25 / day | 227 | 100% | 2.25 | 4.04 | 12% | 45% | -8.3% |
| da3-metric-large_p25 / night | 94 | 100% | 1.19 | 1.63 | 8% | 65% | -6.9% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median | 1797 | 100% | 2.64 | 5.31 | 13% | 47% | -10.8% |
| da3-metric-large_p10 | 1797 | 100% | 3.50 | 6.45 | 16% | 34% | -14.9% |
| da3-metric-large_p25 | 1797 | 100% | 3.13 | 5.90 | 15% | 39% | -13.2% |

### `da3-metric-large_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.94 | 1.08 | 13% | 35% | -3.2% |
| 10-20 m | 82 | 100% | 1.07 | 1.28 | 8% | 72% | -4.6% |
| 20-30 m | 90 | 100% | 1.39 | 1.93 | 8% | 64% | -4.5% |
| 30-50 m | 44 | 100% | 3.35 | 3.90 | 11% | 52% | -7.7% |
| 50+ m | 53 | 100% | 7.09 | 8.09 | 12% | 49% | -10.8% |

### `da3-metric-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.86 | 5.34 | 13% | 45% | -12.6% |
| pedestrian | 327 | 100% | 0.95 | 1.77 | 8% | 73% | +0.7% |
| truck | 134 | 100% | 3.98 | 5.65 | 14% | 22% | -13.9% |
| bus | 110 | 100% | 9.90 | 16.48 | 26% | 11% | -25.6% |
| parked two-wheeler | 24 | 100% | 0.88 | 1.08 | 5% | 83% | -1.2% |
| cyclist | 15 | 100% | 0.99 | 1.73 | 6% | 80% | +0.7% |

### `da3-metric-large_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.65 | 1.09 | 13% | 50% | -6.8% |
| 10-20 m | 82 | 100% | 1.36 | 1.61 | 10% | 50% | -7.6% |
| 20-30 m | 90 | 100% | 1.64 | 2.29 | 9% | 62% | -7.1% |
| 30-50 m | 44 | 100% | 4.20 | 4.85 | 13% | 34% | -12.8% |
| 50+ m | 53 | 100% | 9.77 | 10.68 | 15% | 28% | -14.8% |

### `da3-metric-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.94 | 6.60 | 17% | 26% | -16.5% |
| pedestrian | 327 | 100% | 1.11 | 1.99 | 8% | 72% | -3.3% |
| truck | 134 | 100% | 4.76 | 7.23 | 19% | 14% | -18.7% |
| bus | 110 | 100% | 16.04 | 18.83 | 31% | 5% | -30.7% |
| parked two-wheeler | 24 | 100% | 1.29 | 1.63 | 8% | 75% | -5.9% |
| cyclist | 15 | 100% | 1.08 | 1.15 | 4% | 100% | -1.7% |

### `da3-metric-large_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.74 | 1.09 | 13% | 42% | -5.6% |
| 10-20 m | 82 | 100% | 1.29 | 1.47 | 9% | 61% | -6.4% |
| 20-30 m | 90 | 100% | 1.57 | 2.20 | 9% | 63% | -6.3% |
| 30-50 m | 44 | 100% | 3.72 | 4.23 | 12% | 41% | -10.2% |
| 50+ m | 53 | 100% | 9.06 | 9.62 | 14% | 32% | -13.2% |

### `da3-metric-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.47 | 6.02 | 15% | 33% | -14.9% |
| pedestrian | 327 | 100% | 0.96 | 1.81 | 8% | 74% | -1.6% |
| truck | 134 | 100% | 4.60 | 6.53 | 17% | 16% | -17.0% |
| bus | 110 | 100% | 13.51 | 17.66 | 29% | 9% | -28.4% |
| parked two-wheeler | 24 | 100% | 1.20 | 1.32 | 6% | 83% | -3.8% |
| cyclist | 15 | 100% | 0.99 | 1.31 | 5% | 93% | -0.7% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
