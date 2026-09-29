# nuScenes distance benchmark: `metric3d-v2-small-fp16`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 83.4 ms median, 93.0 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (17 at night) |
| Objects | 838 matched to a detection of 838 labelled (visibility at least v40-60); 104 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:01:28+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 104 | 100% | 1.40 | 2.59 | 10% | 63% | +0.5% |
| metric3d-v2-small-fp16_p10 | 104 | 100% | 1.33 | 3.50 | 12% | 61% | -10.1% |
| metric3d-v2-small-fp16_p25 | 104 | 100% | 1.14 | 3.04 | 10% | 71% | -7.2% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 104 | 100% | 1.40 | 2.59 | 10% | 63% | +0.5% |
| metric3d-v2-small-fp16_median / night | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p10 / day | 104 | 100% | 1.33 | 3.50 | 12% | 61% | -10.1% |
| metric3d-v2-small-fp16_p10 / night | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p25 / day | 104 | 100% | 1.14 | 3.04 | 10% | 71% | -7.2% |
| metric3d-v2-small-fp16_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 838 | 100% | 2.41 | 7.13 | 17% | 51% | -12.0% |
| metric3d-v2-small-fp16_p10 | 838 | 100% | 4.49 | 9.40 | 22% | 33% | -21.3% |
| metric3d-v2-small-fp16_p25 | 838 | 100% | 3.57 | 8.44 | 20% | 42% | -18.1% |

### `metric3d-v2-small-fp16_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 1.28 | 1.40 | 17% | 8% | +17.4% |
| 10-20 m | 32 | 100% | 0.97 | 1.08 | 8% | 69% | +5.9% |
| 20-30 m | 25 | 100% | 1.14 | 1.66 | 7% | 88% | -2.9% |
| 30-50 m | 30 | 100% | 2.78 | 3.24 | 9% | 70% | -4.9% |
| 50+ m | 4 | 100% | 11.50 | 19.43 | 35% | 0% | -34.5% |

### `metric3d-v2-small-fp16_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 1.95 | 2.98 | 11% | 58% | -5.4% |
| barrier | 369 | 100% | 5.80 | 12.39 | 23% | 43% | -20.5% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.24 | 0.30 | 4% | 92% | +3.0% |
| 10-20 m | 32 | 100% | 0.35 | 1.56 | 9% | 84% | -8.3% |
| 20-30 m | 25 | 100% | 2.79 | 2.95 | 12% | 48% | -11.2% |
| 30-50 m | 30 | 100% | 4.23 | 4.88 | 13% | 40% | -12.8% |
| 50+ m | 4 | 100% | 15.37 | 22.43 | 40% | 0% | -39.7% |

### `metric3d-v2-small-fp16_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 3.73 | 4.66 | 16% | 37% | -15.4% |
| barrier | 369 | 100% | 10.95 | 15.42 | 30% | 28% | -28.7% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.41 | 0.46 | 6% | 85% | +5.5% |
| 10-20 m | 32 | 100% | 0.43 | 1.43 | 9% | 88% | -5.6% |
| 20-30 m | 25 | 100% | 2.21 | 2.63 | 10% | 60% | -8.9% |
| 30-50 m | 30 | 100% | 2.92 | 3.79 | 10% | 67% | -9.0% |
| 50+ m | 4 | 100% | 13.79 | 21.16 | 37% | 0% | -37.5% |

### `metric3d-v2-small-fp16_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.78 | 4.01 | 14% | 48% | -12.7% |
| barrier | 369 | 100% | 8.38 | 14.07 | 27% | 35% | -25.1% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 104 | 100% | 1.35 | 2.53 | 9% | 67% | -2.0% |
| metric3d-v2-small-fp16_p10 | 104 | 100% | 1.61 | 3.78 | 13% | 56% | -12.3% |
| metric3d-v2-small-fp16_p25 | 104 | 100% | 1.32 | 3.19 | 11% | 67% | -9.6% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 104 | 100% | 1.35 | 2.53 | 9% | 67% | -2.0% |
| metric3d-v2-small-fp16_median / night | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p10 / day | 104 | 100% | 1.61 | 3.78 | 13% | 56% | -12.3% |
| metric3d-v2-small-fp16_p10 / night | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p25 / day | 104 | 100% | 1.32 | 3.19 | 11% | 67% | -9.6% |
| metric3d-v2-small-fp16_p25 / night | 0 | - | - | - | - | - | - |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 838 | 100% | 2.73 | 7.57 | 17% | 47% | -14.1% |
| metric3d-v2-small-fp16_p10 | 838 | 100% | 4.88 | 10.01 | 23% | 26% | -23.1% |
| metric3d-v2-small-fp16_p25 | 838 | 100% | 4.06 | 9.01 | 21% | 37% | -20.1% |

### `metric3d-v2-small-fp16_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.90 | 1.00 | 12% | 50% | +12.3% |
| 10-20 m | 34 | 100% | 0.64 | 0.75 | 6% | 76% | +3.1% |
| 20-30 m | 26 | 100% | 1.22 | 1.78 | 7% | 73% | -4.6% |
| 30-50 m | 30 | 100% | 2.66 | 3.41 | 9% | 67% | -5.9% |
| 50+ m | 4 | 100% | 11.79 | 19.72 | 35% | 0% | -34.9% |

### `metric3d-v2-small-fp16_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 2.02 | 3.10 | 11% | 54% | -6.8% |
| barrier | 369 | 100% | 7.15 | 13.26 | 24% | 37% | -23.3% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.37 | 0.34 | 4% | 100% | -2.3% |
| 10-20 m | 34 | 100% | 0.67 | 1.42 | 9% | 82% | -9.1% |
| 20-30 m | 26 | 100% | 3.08 | 3.65 | 15% | 42% | -14.6% |
| 30-50 m | 30 | 100% | 4.69 | 5.19 | 14% | 30% | -13.6% |
| 50+ m | 4 | 100% | 15.64 | 22.72 | 40% | 0% | -40.0% |

### `metric3d-v2-small-fp16_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 4.01 | 4.91 | 17% | 31% | -16.6% |
| barrier | 369 | 100% | 12.05 | 16.50 | 32% | 19% | -31.3% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.32 | 0.31 | 4% | 100% | +0.0% |
| 10-20 m | 34 | 100% | 0.41 | 1.06 | 7% | 88% | -6.5% |
| 20-30 m | 26 | 100% | 2.61 | 3.28 | 13% | 46% | -12.5% |
| 30-50 m | 30 | 100% | 3.50 | 4.04 | 11% | 60% | -10.0% |
| 50+ m | 4 | 100% | 14.06 | 21.44 | 38% | 0% | -37.8% |

### `metric3d-v2-small-fp16_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 100% | 3.04 | 4.23 | 15% | 44% | -13.9% |
| barrier | 369 | 100% | 9.45 | 15.09 | 28% | 28% | -27.8% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
