# nuScenes distance benchmark: `metric3d-v2-small-fp16+clahe2_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16+clahe2_median`, `metric3d-v2-small-fp16+clahe2_p10`, `metric3d-v2-small-fp16+clahe2_p25` |
| Depth model | `metric3d-v2-small-fp16+clahe2`, given our focal length; inference 107.0 ms median, 116.4 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 121 (116 at night) |
| Objects | 347 matched to a detection of 782 labelled (visibility at least v40-60); 94 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `12e710c` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T18:30:44+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe2_median | 94 | 100% | 1.07 | 1.57 | 9% | 66% | +5.7% |
| metric3d-v2-small-fp16+clahe2_p10 | 94 | 100% | 1.04 | 1.52 | 8% | 76% | +1.8% |
| metric3d-v2-small-fp16+clahe2_p25 | 94 | 100% | 1.01 | 1.46 | 8% | 70% | +3.3% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe2_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe2_median / night | 94 | 100% | 1.07 | 1.57 | 9% | 66% | +5.7% |
| metric3d-v2-small-fp16+clahe2_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe2_p10 / night | 94 | 100% | 1.04 | 1.52 | 8% | 76% | +1.8% |
| metric3d-v2-small-fp16+clahe2_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe2_p25 / night | 94 | 100% | 1.01 | 1.46 | 8% | 70% | +3.3% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe2_median | 347 | 100% | 3.07 | 7.19 | 16% | 41% | -10.2% |
| metric3d-v2-small-fp16+clahe2_p10 | 347 | 100% | 4.07 | 8.52 | 19% | 37% | -15.5% |
| metric3d-v2-small-fp16+clahe2_p25 | 347 | 100% | 3.34 | 7.79 | 17% | 37% | -13.1% |

### `metric3d-v2-small-fp16+clahe2_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.75 | 1.10 | 16% | 31% | +16.4% |
| 10-20 m | 30 | 100% | 1.23 | 1.48 | 9% | 70% | +4.0% |
| 20-30 m | 48 | 100% | 1.02 | 1.35 | 6% | 75% | +5.3% |
| 30-50 m | 2 | 100% | 7.16 | 7.16 | 19% | 50% | -19.0% |
| 50+ m | 1 | 100% | 9.38 | 9.38 | 17% | 0% | -17.0% |

### `metric3d-v2-small-fp16+clahe2_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.26 | 6.72 | 15% | 48% | -7.6% |
| pedestrian | 57 | 100% | 4.83 | 4.88 | 18% | 21% | -15.6% |
| bus | 25 | 100% | 19.51 | 19.49 | 29% | 4% | -28.4% |
| cyclist | 8 | 100% | 0.50 | 0.77 | 4% | 88% | +3.2% |
| parked two-wheeler | 1 | 100% | 3.72 | 3.72 | 15% | 0% | -14.8% |

### `metric3d-v2-small-fp16+clahe2_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.51 | 0.54 | 8% | 62% | +8.3% |
| 10-20 m | 30 | 100% | 0.86 | 1.42 | 8% | 80% | -0.5% |
| 20-30 m | 48 | 100% | 1.14 | 1.35 | 6% | 79% | +3.1% |
| 30-50 m | 2 | 100% | 8.13 | 8.13 | 22% | 50% | -21.6% |
| 50+ m | 1 | 100% | 11.92 | 11.92 | 22% | 0% | -21.6% |

### `metric3d-v2-small-fp16+clahe2_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.73 | 7.84 | 17% | 44% | -13.1% |
| pedestrian | 57 | 100% | 5.40 | 5.52 | 21% | 16% | -19.3% |
| bus | 25 | 100% | 25.55 | 24.99 | 37% | 4% | -36.9% |
| cyclist | 8 | 100% | 0.59 | 0.68 | 4% | 88% | +1.1% |
| parked two-wheeler | 1 | 100% | 4.20 | 4.20 | 17% | 0% | -16.8% |

### `metric3d-v2-small-fp16+clahe2_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.57 | 0.69 | 11% | 46% | +10.6% |
| 10-20 m | 30 | 100% | 0.94 | 1.37 | 8% | 73% | +1.3% |
| 20-30 m | 48 | 100% | 1.15 | 1.29 | 6% | 77% | +4.0% |
| 30-50 m | 2 | 100% | 7.81 | 7.81 | 21% | 50% | -20.8% |
| 50+ m | 1 | 100% | 10.00 | 10.00 | 18% | 0% | -18.1% |

### `metric3d-v2-small-fp16+clahe2_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.35 | 7.19 | 15% | 45% | -10.7% |
| pedestrian | 57 | 100% | 5.24 | 5.24 | 20% | 12% | -17.9% |
| bus | 25 | 100% | 23.15 | 22.15 | 33% | 4% | -32.5% |
| cyclist | 8 | 100% | 0.51 | 0.72 | 4% | 88% | +2.0% |
| parked two-wheeler | 1 | 100% | 3.92 | 3.92 | 16% | 0% | -15.6% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe2_median | 94 | 100% | 1.63 | 1.87 | 9% | 63% | -7.5% |
| metric3d-v2-small-fp16+clahe2_p10 | 94 | 100% | 1.81 | 2.31 | 12% | 52% | -10.8% |
| metric3d-v2-small-fp16+clahe2_p25 | 94 | 100% | 1.74 | 2.10 | 10% | 57% | -9.6% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe2_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe2_median / night | 94 | 100% | 1.63 | 1.87 | 9% | 63% | -7.5% |
| metric3d-v2-small-fp16+clahe2_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe2_p10 / night | 94 | 100% | 1.81 | 2.31 | 12% | 52% | -10.8% |
| metric3d-v2-small-fp16+clahe2_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe2_p25 / night | 94 | 100% | 1.74 | 2.10 | 10% | 57% | -9.6% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe2_median | 347 | 100% | 4.33 | 8.66 | 19% | 30% | -17.8% |
| metric3d-v2-small-fp16+clahe2_p10 | 347 | 100% | 5.62 | 10.29 | 23% | 21% | -22.7% |
| metric3d-v2-small-fp16+clahe2_p25 | 347 | 100% | 5.16 | 9.49 | 21% | 25% | -20.5% |

### `metric3d-v2-small-fp16+clahe2_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.63 | 1.59 | 20% | 0% | -20.0% |
| 10-20 m | 20 | 100% | 2.12 | 1.87 | 11% | 45% | -6.9% |
| 20-30 m | 56 | 100% | 1.25 | 1.40 | 6% | 86% | -4.4% |
| 30-50 m | 6 | 100% | 3.19 | 5.13 | 14% | 33% | -14.3% |
| 50+ m | 1 | 100% | 11.96 | 11.96 | 21% | 0% | -20.7% |

### `metric3d-v2-small-fp16+clahe2_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.46 | 8.05 | 18% | 34% | -16.8% |
| pedestrian | 57 | 100% | 5.27 | 5.20 | 19% | 16% | -17.4% |
| bus | 25 | 100% | 25.59 | 25.54 | 35% | 0% | -34.9% |
| cyclist | 8 | 100% | 0.60 | 0.74 | 4% | 88% | +1.7% |
| parked two-wheeler | 1 | 100% | 4.07 | 4.07 | 16% | 0% | -16.0% |

### `metric3d-v2-small-fp16+clahe2_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.84 | 1.90 | 24% | 0% | -23.9% |
| 10-20 m | 20 | 100% | 1.76 | 2.51 | 15% | 40% | -13.4% |
| 20-30 m | 56 | 100% | 1.47 | 1.73 | 7% | 71% | -6.5% |
| 30-50 m | 6 | 100% | 3.61 | 5.76 | 16% | 17% | -16.1% |
| 50+ m | 1 | 100% | 14.50 | 14.50 | 25% | 0% | -25.1% |

### `metric3d-v2-small-fp16+clahe2_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 5.03 | 9.57 | 22% | 23% | -21.8% |
| pedestrian | 57 | 100% | 5.83 | 5.88 | 22% | 12% | -21.0% |
| bus | 25 | 100% | 31.63 | 31.08 | 43% | 0% | -42.7% |
| cyclist | 8 | 100% | 0.65 | 0.70 | 4% | 100% | -0.4% |
| parked two-wheeler | 1 | 100% | 4.55 | 4.55 | 18% | 0% | -17.9% |

### `metric3d-v2-small-fp16+clahe2_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.72 | 1.80 | 23% | 0% | -22.7% |
| 10-20 m | 20 | 100% | 1.68 | 2.16 | 13% | 55% | -10.9% |
| 20-30 m | 56 | 100% | 1.55 | 1.58 | 7% | 73% | -5.7% |
| 30-50 m | 6 | 100% | 3.42 | 5.52 | 15% | 33% | -15.4% |
| 50+ m | 1 | 100% | 12.58 | 12.58 | 22% | 0% | -21.8% |

### `metric3d-v2-small-fp16+clahe2_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.19 | 8.82 | 20% | 27% | -19.6% |
| pedestrian | 57 | 100% | 5.60 | 5.60 | 21% | 16% | -19.6% |
| bus | 25 | 100% | 29.23 | 28.24 | 39% | 0% | -38.7% |
| cyclist | 8 | 100% | 0.58 | 0.72 | 4% | 88% | +0.5% |
| parked two-wheeler | 1 | 100% | 4.27 | 4.27 | 17% | 0% | -16.8% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
