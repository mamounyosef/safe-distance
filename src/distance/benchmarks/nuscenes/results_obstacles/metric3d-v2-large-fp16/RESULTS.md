# nuScenes distance benchmark: `metric3d-v2-large-fp16`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-large-fp16_median`, `metric3d-v2-large-fp16_p10`, `metric3d-v2-large-fp16_p25` |
| Depth model | `metric3d-v2-large-fp16`, given our focal length; inference 355.1 ms median, 357.2 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (17 at night) |
| Objects | 838 matched to a detection of 838 labelled (visibility at least v40-60); 104 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:04:41+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 104 | 100% | 1.35 | 2.15 | 9% | 71% | +1.4% |
| metric3d-v2-large-fp16_p10 | 104 | 100% | 1.43 | 2.90 | 10% | 74% | -7.0% |
| metric3d-v2-large-fp16_p25 | 104 | 100% | 1.43 | 2.58 | 9% | 81% | -5.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median / day | 104 | 100% | 1.35 | 2.15 | 9% | 71% | +1.4% |
| metric3d-v2-large-fp16_median / night | 0 | - | - | - | - | - | - |
| metric3d-v2-large-fp16_p10 / day | 104 | 100% | 1.43 | 2.90 | 10% | 74% | -7.0% |
| metric3d-v2-large-fp16_p10 / night | 0 | - | - | - | - | - | - |
| metric3d-v2-large-fp16_p25 / day | 104 | 100% | 1.43 | 2.58 | 9% | 81% | -5.1% |
| metric3d-v2-large-fp16_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 838 | 100% | 1.92 | 5.53 | 14% | 62% | -6.9% |
| metric3d-v2-large-fp16_p10 | 838 | 100% | 2.93 | 8.37 | 19% | 48% | -17.5% |
| metric3d-v2-large-fp16_p25 | 838 | 100% | 2.35 | 6.90 | 16% | 57% | -13.4% |

### `metric3d-v2-large-fp16_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 1.27 | 1.16 | 15% | 31% | +14.6% |
| 10-20 m | 32 | 100% | 0.56 | 0.92 | 6% | 78% | +3.5% |
| 20-30 m | 25 | 100% | 1.76 | 1.87 | 8% | 80% | -0.0% |
| 30-50 m | 30 | 100% | 1.86 | 2.46 | 7% | 77% | -1.7% |
| 50+ m | 4 | 100% | 5.25 | 14.62 | 26% | 50% | -25.8% |

### `metric3d-v2-large-fp16_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.61 | 2.55 | 10% | 65% | -1.7% |
| barrier | 369 | 100% | 3.19 | 9.33 | 18% | 59% | -13.5% |

### `metric3d-v2-large-fp16_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.24 | 0.36 | 4% | 92% | +3.6% |
| 10-20 m | 32 | 100% | 0.33 | 1.60 | 10% | 81% | -7.2% |
| 20-30 m | 25 | 100% | 1.82 | 2.75 | 11% | 76% | -8.1% |
| 30-50 m | 30 | 100% | 2.79 | 3.48 | 10% | 63% | -7.1% |
| 50+ m | 4 | 100% | 10.23 | 18.21 | 32% | 25% | -32.5% |

### `metric3d-v2-large-fp16_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.09 | 3.65 | 13% | 59% | -10.2% |
| barrier | 369 | 100% | 7.35 | 14.36 | 28% | 33% | -26.8% |

### `metric3d-v2-large-fp16_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.39 | 0.43 | 5% | 92% | +5.4% |
| 10-20 m | 32 | 100% | 0.29 | 1.45 | 9% | 84% | -5.6% |
| 20-30 m | 25 | 100% | 1.80 | 2.70 | 11% | 80% | -7.0% |
| 30-50 m | 30 | 100% | 2.57 | 2.76 | 8% | 77% | -4.3% |
| 50+ m | 4 | 100% | 8.18 | 16.60 | 30% | 50% | -29.7% |

### `metric3d-v2-large-fp16_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.90 | 3.12 | 11% | 65% | -7.9% |
| barrier | 369 | 100% | 4.85 | 11.71 | 23% | 47% | -20.3% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 104 | 100% | 1.21 | 2.13 | 8% | 71% | -1.0% |
| metric3d-v2-large-fp16_p10 | 104 | 100% | 1.51 | 3.13 | 11% | 67% | -9.3% |
| metric3d-v2-large-fp16_p25 | 104 | 100% | 1.49 | 2.76 | 10% | 75% | -7.4% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median / day | 104 | 100% | 1.21 | 2.13 | 8% | 71% | -1.0% |
| metric3d-v2-large-fp16_median / night | 0 | - | - | - | - | - | - |
| metric3d-v2-large-fp16_p10 / day | 104 | 100% | 1.51 | 3.13 | 11% | 67% | -9.3% |
| metric3d-v2-large-fp16_p10 / night | 0 | - | - | - | - | - | - |
| metric3d-v2-large-fp16_p25 / day | 104 | 100% | 1.49 | 2.76 | 10% | 75% | -7.4% |
| metric3d-v2-large-fp16_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 838 | 100% | 2.04 | 5.83 | 14% | 61% | -9.0% |
| metric3d-v2-large-fp16_p10 | 838 | 100% | 3.38 | 8.94 | 20% | 41% | -19.4% |
| metric3d-v2-large-fp16_p25 | 838 | 100% | 2.61 | 7.37 | 17% | 51% | -15.3% |

### `metric3d-v2-large-fp16_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 1.02 | 0.99 | 12% | 30% | +10.5% |
| 10-20 m | 34 | 100% | 0.49 | 0.83 | 6% | 82% | +0.7% |
| 20-30 m | 26 | 100% | 1.56 | 1.85 | 7% | 69% | -2.0% |
| 30-50 m | 30 | 100% | 2.39 | 2.53 | 7% | 77% | -2.7% |
| 50+ m | 4 | 100% | 5.47 | 14.76 | 26% | 50% | -26.2% |

### `metric3d-v2-large-fp16_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.70 | 2.60 | 10% | 65% | -3.2% |
| barrier | 369 | 100% | 3.54 | 9.94 | 19% | 56% | -16.5% |

### `metric3d-v2-large-fp16_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.14 | 0.39 | 4% | 80% | -0.7% |
| 10-20 m | 34 | 100% | 0.91 | 1.47 | 10% | 82% | -8.3% |
| 20-30 m | 26 | 100% | 2.26 | 3.33 | 14% | 65% | -11.8% |
| 30-50 m | 30 | 100% | 3.29 | 3.72 | 10% | 53% | -8.0% |
| 50+ m | 4 | 100% | 10.50 | 18.50 | 33% | 25% | -32.8% |

### `metric3d-v2-large-fp16_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.26 | 3.83 | 13% | 56% | -11.5% |
| barrier | 369 | 100% | 8.66 | 15.43 | 30% | 21% | -29.3% |

### `metric3d-v2-large-fp16_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.25 | 0.42 | 5% | 80% | +1.1% |
| 10-20 m | 34 | 100% | 0.71 | 1.26 | 8% | 88% | -6.7% |
| 20-30 m | 26 | 100% | 2.02 | 3.22 | 13% | 65% | -10.6% |
| 30-50 m | 30 | 100% | 2.74 | 2.96 | 8% | 70% | -5.3% |
| 50+ m | 4 | 100% | 8.46 | 16.89 | 30% | 50% | -30.1% |

### `metric3d-v2-large-fp16_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.03 | 3.27 | 12% | 62% | -9.2% |
| barrier | 369 | 100% | 5.52 | 12.58 | 24% | 37% | -23.1% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
