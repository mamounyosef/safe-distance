# nuScenes distance benchmark: `unidepth-v2-large`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 212.6 ms median, 214.6 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (17 at night) |
| Objects | 838 matched to a detection of 838 labelled (visibility at least v40-60); 104 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:05:44+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 104 | 100% | 3.23 | 5.12 | 20% | 38% | +17.9% |
| unidepth-v2-large_p10 | 104 | 100% | 0.48 | 2.27 | 8% | 82% | -3.7% |
| unidepth-v2-large_p25 | 104 | 100% | 0.99 | 2.65 | 9% | 76% | +0.2% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median / day | 104 | 100% | 3.23 | 5.12 | 20% | 38% | +17.9% |
| unidepth-v2-large_median / night | 0 | - | - | - | - | - | - |
| unidepth-v2-large_p10 / day | 104 | 100% | 0.48 | 2.27 | 8% | 82% | -3.7% |
| unidepth-v2-large_p10 / night | 0 | - | - | - | - | - | - |
| unidepth-v2-large_p25 / day | 104 | 100% | 0.99 | 2.65 | 9% | 76% | +0.2% |
| unidepth-v2-large_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 838 | 100% | 3.49 | 6.94 | 20% | 44% | +5.8% |
| unidepth-v2-large_p10 | 838 | 100% | 1.86 | 6.35 | 15% | 62% | -13.3% |
| unidepth-v2-large_p25 | 838 | 100% | 1.76 | 5.64 | 13% | 68% | -8.5% |

### `unidepth-v2-large_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 1.68 | 1.62 | 20% | 31% | +20.1% |
| 10-20 m | 32 | 100% | 2.42 | 2.27 | 16% | 44% | +15.2% |
| 20-30 m | 25 | 100% | 4.42 | 5.25 | 21% | 44% | +20.6% |
| 30-50 m | 30 | 100% | 4.89 | 7.34 | 20% | 37% | +20.0% |
| 50+ m | 4 | 100% | 19.31 | 22.01 | 39% | 0% | +0.2% |

### `unidepth-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.57 | 5.96 | 23% | 28% | +19.3% |
| barrier | 369 | 100% | 2.14 | 8.18 | 16% | 65% | -11.4% |

### `unidepth-v2-large_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.16 | 0.17 | 2% | 100% | -1.2% |
| 10-20 m | 32 | 100% | 0.21 | 1.35 | 8% | 88% | -7.6% |
| 20-30 m | 25 | 100% | 0.91 | 2.32 | 9% | 76% | -3.6% |
| 30-50 m | 30 | 100% | 1.85 | 2.38 | 7% | 77% | +1.2% |
| 50+ m | 4 | 100% | 6.04 | 15.40 | 28% | 50% | -19.1% |

### `unidepth-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.19 | 2.46 | 9% | 80% | -6.6% |
| barrier | 369 | 100% | 5.17 | 11.28 | 22% | 40% | -21.8% |

### `unidepth-v2-large_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.05 | 0.15 | 2% | 100% | +1.2% |
| 10-20 m | 32 | 100% | 0.28 | 1.37 | 8% | 84% | -5.2% |
| 20-30 m | 25 | 100% | 1.96 | 2.92 | 11% | 68% | +2.0% |
| 30-50 m | 30 | 100% | 2.02 | 2.89 | 8% | 70% | +5.6% |
| 50+ m | 4 | 100% | 10.76 | 17.48 | 31% | 25% | -12.5% |

### `unidepth-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.14 | 2.29 | 8% | 78% | -1.0% |
| barrier | 369 | 100% | 3.36 | 9.89 | 19% | 56% | -17.9% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 104 | 100% | 2.96 | 4.92 | 18% | 40% | +15.2% |
| unidepth-v2-large_p10 | 104 | 100% | 0.89 | 2.51 | 9% | 76% | -6.0% |
| unidepth-v2-large_p25 | 104 | 100% | 1.01 | 2.70 | 10% | 75% | -2.2% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median / day | 104 | 100% | 2.96 | 4.92 | 18% | 40% | +15.2% |
| unidepth-v2-large_median / night | 0 | - | - | - | - | - | - |
| unidepth-v2-large_p10 / day | 104 | 100% | 0.89 | 2.51 | 9% | 76% | -6.0% |
| unidepth-v2-large_p10 / night | 0 | - | - | - | - | - | - |
| unidepth-v2-large_p25 / day | 104 | 100% | 1.01 | 2.70 | 10% | 75% | -2.2% |
| unidepth-v2-large_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 838 | 100% | 3.72 | 7.06 | 20% | 42% | +3.5% |
| unidepth-v2-large_p10 | 838 | 100% | 2.22 | 6.91 | 16% | 54% | -15.2% |
| unidepth-v2-large_p25 | 838 | 100% | 1.89 | 6.02 | 14% | 63% | -10.5% |

### `unidepth-v2-large_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 1.53 | 1.49 | 18% | 20% | +16.1% |
| 10-20 m | 34 | 100% | 2.16 | 2.06 | 15% | 44% | +11.6% |
| 20-30 m | 26 | 100% | 3.71 | 4.84 | 19% | 46% | +17.9% |
| 30-50 m | 30 | 100% | 4.62 | 7.11 | 19% | 43% | +18.9% |
| 50+ m | 4 | 100% | 19.02 | 21.87 | 38% | 0% | -0.2% |

### `unidepth-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.35 | 5.78 | 22% | 28% | +17.6% |
| barrier | 369 | 100% | 2.55 | 8.70 | 17% | 59% | -14.4% |

### `unidepth-v2-large_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.41 | 0.48 | 6% | 80% | -5.9% |
| 10-20 m | 34 | 100% | 0.73 | 1.30 | 9% | 85% | -8.8% |
| 20-30 m | 26 | 100% | 0.99 | 2.85 | 11% | 69% | -7.5% |
| 30-50 m | 30 | 100% | 2.19 | 2.56 | 7% | 73% | +0.2% |
| 50+ m | 4 | 100% | 6.02 | 15.40 | 27% | 50% | -19.5% |

### `unidepth-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.33 | 2.63 | 10% | 76% | -7.9% |
| barrier | 369 | 100% | 6.28 | 12.35 | 25% | 27% | -24.4% |

### `unidepth-v2-large_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.31 | 0.37 | 5% | 90% | -3.6% |
| 10-20 m | 34 | 100% | 0.57 | 1.14 | 8% | 91% | -6.5% |
| 20-30 m | 26 | 100% | 1.67 | 3.22 | 13% | 62% | -2.2% |
| 30-50 m | 30 | 100% | 1.84 | 2.85 | 8% | 70% | +4.6% |
| 50+ m | 4 | 100% | 10.46 | 17.33 | 31% | 25% | -13.0% |

### `unidepth-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.14 | 2.28 | 8% | 79% | -2.4% |
| barrier | 369 | 100% | 4.40 | 10.77 | 21% | 43% | -20.7% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
