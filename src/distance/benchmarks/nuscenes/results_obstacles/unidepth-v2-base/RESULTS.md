# nuScenes distance benchmark: `unidepth-v2-base`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 110.3 ms median, 112.2 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (17 at night) |
| Objects | 838 matched to a detection of 838 labelled (visibility at least v40-60); 104 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:05:05+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 104 | 100% | 3.62 | 4.66 | 20% | 36% | +18.8% |
| unidepth-v2-base_p10 | 104 | 100% | 0.62 | 2.40 | 8% | 80% | -2.1% |
| unidepth-v2-base_p25 | 104 | 100% | 1.01 | 2.66 | 10% | 74% | +1.9% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median / day | 104 | 100% | 3.62 | 4.66 | 20% | 36% | +18.8% |
| unidepth-v2-base_median / night | 0 | - | - | - | - | - | - |
| unidepth-v2-base_p10 / day | 104 | 100% | 0.62 | 2.40 | 8% | 80% | -2.1% |
| unidepth-v2-base_p10 / night | 0 | - | - | - | - | - | - |
| unidepth-v2-base_p25 / day | 104 | 100% | 1.01 | 2.66 | 10% | 74% | +1.9% |
| unidepth-v2-base_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 838 | 100% | 4.14 | 7.06 | 20% | 40% | +5.7% |
| unidepth-v2-base_p10 | 838 | 100% | 1.88 | 6.39 | 15% | 64% | -12.1% |
| unidepth-v2-base_p25 | 838 | 100% | 1.69 | 5.80 | 14% | 65% | -7.5% |

### `unidepth-v2-base_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 2.15 | 2.00 | 25% | 31% | +24.8% |
| 10-20 m | 32 | 100% | 2.93 | 2.59 | 19% | 47% | +18.2% |
| 20-30 m | 25 | 100% | 4.43 | 5.15 | 21% | 40% | +20.8% |
| 30-50 m | 30 | 100% | 5.57 | 6.50 | 18% | 23% | +18.2% |
| 50+ m | 4 | 100% | 11.18 | 12.95 | 23% | 25% | -3.4% |

### `unidepth-v2-base_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.73 | 5.46 | 22% | 23% | +18.8% |
| barrier | 369 | 100% | 2.90 | 9.10 | 18% | 61% | -11.0% |

### `unidepth-v2-base_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.12 | 0.18 | 2% | 100% | +1.7% |
| 10-20 m | 32 | 100% | 0.36 | 1.39 | 8% | 88% | -5.3% |
| 20-30 m | 25 | 100% | 0.99 | 2.25 | 9% | 76% | -2.4% |
| 30-50 m | 30 | 100% | 2.34 | 2.90 | 8% | 70% | +2.8% |
| 50+ m | 4 | 100% | 5.53 | 14.90 | 27% | 50% | -23.7% |

### `unidepth-v2-base_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.13 | 2.59 | 9% | 79% | -5.5% |
| barrier | 369 | 100% | 4.85 | 11.22 | 22% | 44% | -20.4% |

### `unidepth-v2-base_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.31 | 0.40 | 5% | 85% | +5.0% |
| 10-20 m | 32 | 100% | 0.52 | 1.59 | 10% | 84% | -2.4% |
| 20-30 m | 25 | 100% | 1.71 | 2.69 | 11% | 68% | +2.8% |
| 30-50 m | 30 | 100% | 1.63 | 3.03 | 8% | 67% | +7.1% |
| 50+ m | 4 | 100% | 6.04 | 15.69 | 28% | 50% | -18.8% |

### `unidepth-v2-base_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.21 | 2.41 | 9% | 72% | -0.2% |
| barrier | 369 | 100% | 3.72 | 10.12 | 20% | 57% | -16.7% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 104 | 100% | 3.33 | 4.32 | 18% | 35% | +16.1% |
| unidepth-v2-base_p10 | 104 | 100% | 0.78 | 2.48 | 9% | 78% | -4.5% |
| unidepth-v2-base_p25 | 104 | 100% | 0.67 | 2.51 | 9% | 79% | -0.5% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median / day | 104 | 100% | 3.33 | 4.32 | 18% | 35% | +16.1% |
| unidepth-v2-base_median / night | 0 | - | - | - | - | - | - |
| unidepth-v2-base_p10 / day | 104 | 100% | 0.78 | 2.48 | 9% | 78% | -4.5% |
| unidepth-v2-base_p10 / night | 0 | - | - | - | - | - | - |
| unidepth-v2-base_p25 / day | 104 | 100% | 0.67 | 2.51 | 9% | 79% | -0.5% |
| unidepth-v2-base_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 838 | 100% | 4.08 | 7.11 | 20% | 40% | +3.4% |
| unidepth-v2-base_p10 | 838 | 100% | 2.15 | 6.84 | 16% | 58% | -14.0% |
| unidepth-v2-base_p25 | 838 | 100% | 1.88 | 6.09 | 14% | 62% | -9.5% |

### `unidepth-v2-base_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 2.02 | 1.80 | 22% | 20% | +21.2% |
| 10-20 m | 34 | 100% | 2.58 | 2.16 | 15% | 44% | +14.4% |
| 20-30 m | 26 | 100% | 3.95 | 4.70 | 19% | 42% | +18.1% |
| 30-50 m | 30 | 100% | 5.30 | 6.14 | 17% | 23% | +17.0% |
| 50+ m | 4 | 100% | 10.88 | 12.81 | 22% | 25% | -3.9% |

### `unidepth-v2-base_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.46 | 5.26 | 21% | 25% | +17.1% |
| barrier | 369 | 100% | 3.09 | 9.46 | 18% | 59% | -14.0% |

### `unidepth-v2-base_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.17 | 0.27 | 3% | 90% | -2.9% |
| 10-20 m | 34 | 100% | 0.33 | 1.04 | 7% | 91% | -6.6% |
| 20-30 m | 26 | 100% | 1.23 | 2.70 | 11% | 77% | -6.4% |
| 30-50 m | 30 | 100% | 2.40 | 2.97 | 8% | 63% | +1.8% |
| 50+ m | 4 | 100% | 5.51 | 15.03 | 27% | 50% | -24.1% |

### `unidepth-v2-base_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.30 | 2.72 | 9% | 77% | -6.9% |
| barrier | 369 | 100% | 5.93 | 12.08 | 24% | 34% | -23.2% |

### `unidepth-v2-base_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.28 | 0.31 | 4% | 100% | +0.3% |
| 10-20 m | 34 | 100% | 0.39 | 1.01 | 7% | 88% | -3.8% |
| 20-30 m | 26 | 100% | 1.72 | 2.93 | 12% | 77% | -1.4% |
| 30-50 m | 30 | 100% | 1.41 | 2.84 | 8% | 67% | +6.0% |
| 50+ m | 4 | 100% | 6.02 | 15.68 | 28% | 50% | -19.2% |

### `unidepth-v2-base_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.15 | 2.37 | 9% | 75% | -1.6% |
| barrier | 369 | 100% | 4.34 | 10.82 | 21% | 45% | -19.6% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
