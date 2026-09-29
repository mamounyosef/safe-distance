# nuScenes distance benchmark: `unidepth-v2-small`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-small_median`, `unidepth-v2-small_p10`, `unidepth-v2-small_p25` |
| Depth model | `unidepth-v2-small`, given our focal length; inference 60.7 ms median, 63.4 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:50:36+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median | 321 | 100% | 1.84 | 2.81 | 11% | 49% | +10.6% |
| unidepth-v2-small_p10 | 321 | 100% | 1.30 | 2.18 | 9% | 63% | +6.1% |
| unidepth-v2-small_p25 | 321 | 100% | 1.44 | 2.32 | 9% | 61% | +7.7% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median / day | 227 | 100% | 1.66 | 3.05 | 11% | 52% | +10.1% |
| unidepth-v2-small_median / night | 94 | 100% | 2.03 | 2.23 | 13% | 41% | +11.9% |
| unidepth-v2-small_p10 / day | 227 | 100% | 1.22 | 2.39 | 8% | 66% | +5.4% |
| unidepth-v2-small_p10 / night | 94 | 100% | 1.40 | 1.68 | 10% | 55% | +7.7% |
| unidepth-v2-small_p25 / day | 227 | 100% | 1.37 | 2.53 | 9% | 63% | +7.1% |
| unidepth-v2-small_p25 / night | 94 | 100% | 1.55 | 1.80 | 10% | 55% | +9.0% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median | 1797 | 100% | 1.73 | 3.45 | 10% | 62% | +3.6% |
| unidepth-v2-small_p10 | 1797 | 100% | 1.55 | 3.57 | 10% | 66% | -2.1% |
| unidepth-v2-small_p25 | 1797 | 100% | 1.54 | 3.34 | 9% | 67% | +0.1% |

### `unidepth-v2-small_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 1.05 | 1.04 | 15% | 22% | +15.2% |
| 10-20 m | 97 | 100% | 1.44 | 1.73 | 11% | 56% | +9.4% |
| 20-30 m | 81 | 100% | 2.40 | 2.48 | 11% | 48% | +10.4% |
| 30-50 m | 31 | 100% | 3.52 | 5.26 | 13% | 55% | +12.7% |
| 50+ m | 53 | 100% | 4.18 | 5.83 | 9% | 64% | +6.9% |

### `unidepth-v2-small_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.57 | 3.37 | 9% | 67% | +3.0% |
| pedestrian | 327 | 100% | 1.47 | 2.55 | 12% | 50% | +6.5% |
| truck | 134 | 100% | 2.01 | 2.91 | 9% | 68% | +2.5% |
| bus | 110 | 100% | 3.99 | 7.75 | 16% | 46% | -0.7% |
| parked two-wheeler | 24 | 100% | 1.72 | 1.86 | 10% | 50% | +9.5% |
| cyclist | 15 | 100% | 3.53 | 5.35 | 18% | 27% | +17.8% |

### `unidepth-v2-small_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.78 | 0.71 | 10% | 37% | +10.4% |
| 10-20 m | 97 | 100% | 0.93 | 1.27 | 8% | 71% | +5.3% |
| 20-30 m | 81 | 100% | 1.75 | 2.19 | 9% | 65% | +5.8% |
| 30-50 m | 31 | 100% | 2.25 | 3.28 | 8% | 65% | +7.0% |
| 50+ m | 53 | 100% | 4.17 | 4.80 | 7% | 70% | +2.6% |

### `unidepth-v2-small_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.50 | 3.36 | 8% | 72% | -2.2% |
| pedestrian | 327 | 100% | 1.37 | 2.24 | 10% | 54% | +1.2% |
| truck | 134 | 100% | 1.86 | 3.37 | 9% | 62% | -4.3% |
| bus | 110 | 100% | 4.41 | 10.56 | 20% | 47% | -11.4% |
| parked two-wheeler | 24 | 100% | 1.12 | 1.28 | 7% | 79% | +4.5% |
| cyclist | 15 | 100% | 2.70 | 3.59 | 12% | 40% | +12.4% |

### `unidepth-v2-small_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.86 | 0.81 | 12% | 34% | +11.9% |
| 10-20 m | 97 | 100% | 1.07 | 1.36 | 8% | 71% | +6.7% |
| 20-30 m | 81 | 100% | 1.88 | 2.12 | 9% | 64% | +7.5% |
| 30-50 m | 31 | 100% | 2.71 | 4.06 | 10% | 61% | +9.3% |
| 50+ m | 53 | 100% | 4.22 | 5.03 | 8% | 68% | +4.0% |

### `unidepth-v2-small_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.44 | 3.21 | 8% | 73% | -0.3% |
| pedestrian | 327 | 100% | 1.38 | 2.23 | 10% | 53% | +3.5% |
| truck | 134 | 100% | 1.83 | 2.97 | 8% | 65% | -1.8% |
| bus | 110 | 100% | 3.22 | 8.70 | 17% | 53% | -6.8% |
| parked two-wheeler | 24 | 100% | 1.40 | 1.51 | 8% | 62% | +6.3% |
| cyclist | 15 | 100% | 3.16 | 4.43 | 15% | 27% | +15.0% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median | 321 | 100% | 1.24 | 2.29 | 9% | 69% | +0.4% |
| unidepth-v2-small_p10 | 321 | 100% | 1.47 | 2.30 | 9% | 65% | -3.7% |
| unidepth-v2-small_p25 | 321 | 100% | 1.42 | 2.23 | 9% | 67% | -2.2% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median / day | 227 | 100% | 1.43 | 2.72 | 9% | 69% | +1.4% |
| unidepth-v2-small_median / night | 94 | 100% | 0.94 | 1.24 | 7% | 71% | -2.0% |
| unidepth-v2-small_p10 / day | 227 | 100% | 1.69 | 2.65 | 9% | 64% | -2.9% |
| unidepth-v2-small_p10 / night | 94 | 100% | 1.17 | 1.45 | 8% | 68% | -5.6% |
| unidepth-v2-small_p25 / day | 227 | 100% | 1.58 | 2.61 | 9% | 66% | -1.3% |
| unidepth-v2-small_p25 / night | 94 | 100% | 1.04 | 1.31 | 7% | 70% | -4.5% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median | 1797 | 100% | 2.04 | 3.77 | 10% | 59% | -4.6% |
| unidepth-v2-small_p10 | 1797 | 100% | 2.66 | 4.62 | 13% | 48% | -9.8% |
| unidepth-v2-small_p25 | 1797 | 100% | 2.43 | 4.16 | 12% | 53% | -7.8% |

### `unidepth-v2-small_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.99 | 1.13 | 14% | 29% | -4.0% |
| 10-20 m | 82 | 100% | 1.03 | 1.37 | 8% | 76% | -1.0% |
| 20-30 m | 90 | 100% | 0.92 | 1.29 | 5% | 86% | +0.3% |
| 30-50 m | 44 | 100% | 2.30 | 3.86 | 10% | 68% | +5.0% |
| 50+ m | 53 | 100% | 4.15 | 5.23 | 8% | 74% | +3.3% |

### `unidepth-v2-small_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.02 | 3.60 | 10% | 61% | -6.1% |
| pedestrian | 327 | 100% | 1.52 | 2.43 | 10% | 57% | +3.5% |
| truck | 134 | 100% | 2.68 | 3.64 | 10% | 53% | -8.2% |
| bus | 110 | 100% | 4.92 | 10.16 | 18% | 39% | -13.3% |
| parked two-wheeler | 24 | 100% | 1.03 | 1.23 | 6% | 88% | +4.4% |
| cyclist | 15 | 100% | 3.26 | 4.74 | 15% | 27% | +15.2% |

### `unidepth-v2-small_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.82 | 1.15 | 14% | 48% | -7.4% |
| 10-20 m | 82 | 100% | 1.36 | 1.59 | 10% | 57% | -5.2% |
| 20-30 m | 90 | 100% | 1.12 | 1.61 | 7% | 78% | -3.2% |
| 30-50 m | 44 | 100% | 2.46 | 3.41 | 9% | 66% | -0.9% |
| 50+ m | 53 | 100% | 4.05 | 4.74 | 7% | 74% | -0.9% |

### `unidepth-v2-small_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.73 | 4.38 | 12% | 48% | -10.8% |
| pedestrian | 327 | 100% | 1.43 | 2.23 | 10% | 61% | -1.6% |
| truck | 134 | 100% | 4.01 | 5.20 | 15% | 37% | -14.1% |
| bus | 110 | 100% | 8.61 | 14.64 | 25% | 18% | -22.6% |
| parked two-wheeler | 24 | 100% | 0.65 | 1.00 | 5% | 88% | -0.4% |
| cyclist | 15 | 100% | 2.10 | 2.98 | 10% | 60% | +10.0% |

### `unidepth-v2-small_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.90 | 1.15 | 14% | 44% | -6.2% |
| 10-20 m | 82 | 100% | 1.27 | 1.47 | 9% | 61% | -3.7% |
| 20-30 m | 90 | 100% | 1.04 | 1.52 | 6% | 80% | -2.2% |
| 30-50 m | 44 | 100% | 2.33 | 3.36 | 9% | 68% | +2.1% |
| 50+ m | 53 | 100% | 3.57 | 4.72 | 7% | 77% | +0.5% |

### `unidepth-v2-small_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.47 | 3.98 | 11% | 55% | -9.1% |
| pedestrian | 327 | 100% | 1.37 | 2.19 | 10% | 61% | +0.6% |
| truck | 134 | 100% | 3.50 | 4.44 | 13% | 42% | -11.9% |
| bus | 110 | 100% | 7.20 | 12.31 | 22% | 24% | -18.5% |
| parked two-wheeler | 24 | 100% | 0.77 | 1.07 | 5% | 88% | +1.3% |
| cyclist | 15 | 100% | 2.43 | 3.82 | 12% | 33% | +12.5% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
