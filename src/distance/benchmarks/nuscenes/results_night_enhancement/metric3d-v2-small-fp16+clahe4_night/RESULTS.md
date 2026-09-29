# nuScenes distance benchmark: `metric3d-v2-small-fp16+clahe4_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16+clahe4_median`, `metric3d-v2-small-fp16+clahe4_p10`, `metric3d-v2-small-fp16+clahe4_p25` |
| Depth model | `metric3d-v2-small-fp16+clahe4`, given our focal length; inference 106.2 ms median, 112.8 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 121 (116 at night) |
| Objects | 347 matched to a detection of 782 labelled (visibility at least v40-60); 94 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `12e710c` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T18:31:05+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 94 | 100% | 0.97 | 1.45 | 8% | 73% | +2.9% |
| metric3d-v2-small-fp16+clahe4_p10 | 94 | 100% | 0.82 | 1.50 | 7% | 82% | -0.8% |
| metric3d-v2-small-fp16+clahe4_p25 | 94 | 100% | 0.83 | 1.43 | 7% | 79% | +0.7% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_median / night | 94 | 100% | 0.97 | 1.45 | 8% | 73% | +2.9% |
| metric3d-v2-small-fp16+clahe4_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p10 / night | 94 | 100% | 0.82 | 1.50 | 7% | 82% | -0.8% |
| metric3d-v2-small-fp16+clahe4_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p25 / night | 94 | 100% | 0.83 | 1.43 | 7% | 79% | +0.7% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 347 | 100% | 3.17 | 7.68 | 17% | 41% | -12.4% |
| metric3d-v2-small-fp16+clahe4_p10 | 347 | 100% | 4.37 | 9.02 | 20% | 35% | -17.8% |
| metric3d-v2-small-fp16+clahe4_p25 | 347 | 100% | 3.71 | 8.34 | 18% | 38% | -15.4% |

### `metric3d-v2-small-fp16+clahe4_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.89 | 1.16 | 18% | 0% | +17.9% |
| 10-20 m | 30 | 100% | 0.84 | 1.12 | 6% | 83% | +0.3% |
| 20-30 m | 48 | 100% | 1.04 | 1.14 | 5% | 92% | +2.2% |
| 30-50 m | 2 | 100% | 9.78 | 9.78 | 26% | 0% | -25.9% |
| 50+ m | 1 | 100% | 13.71 | 13.71 | 25% | 0% | -24.8% |

### `metric3d-v2-small-fp16+clahe4_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.13 | 6.97 | 15% | 48% | -9.9% |
| pedestrian | 57 | 100% | 4.79 | 4.96 | 19% | 18% | -16.1% |
| bus | 25 | 100% | 25.18 | 23.57 | 34% | 4% | -33.7% |
| cyclist | 8 | 100% | 0.71 | 0.91 | 5% | 88% | +2.2% |
| parked two-wheeler | 1 | 100% | 2.32 | 2.32 | 9% | 100% | -9.2% |

### `metric3d-v2-small-fp16+clahe4_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.70 | 0.60 | 10% | 62% | +9.7% |
| 10-20 m | 30 | 100% | 0.76 | 1.33 | 8% | 80% | -4.1% |
| 20-30 m | 48 | 100% | 1.06 | 1.16 | 5% | 94% | +0.2% |
| 30-50 m | 2 | 100% | 10.85 | 10.85 | 29% | 0% | -28.8% |
| 50+ m | 1 | 100% | 16.43 | 16.43 | 30% | 0% | -29.8% |

### `metric3d-v2-small-fp16+clahe4_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.91 | 8.14 | 18% | 41% | -15.5% |
| pedestrian | 57 | 100% | 5.25 | 5.60 | 21% | 14% | -20.1% |
| bus | 25 | 100% | 29.84 | 28.81 | 42% | 4% | -42.2% |
| cyclist | 8 | 100% | 0.76 | 0.71 | 4% | 100% | -0.9% |
| parked two-wheeler | 1 | 100% | 2.79 | 2.79 | 11% | 0% | -11.1% |

### `metric3d-v2-small-fp16+clahe4_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.78 | 0.77 | 12% | 38% | +12.2% |
| 10-20 m | 30 | 100% | 0.75 | 1.18 | 7% | 80% | -2.1% |
| 20-30 m | 48 | 100% | 0.95 | 1.10 | 5% | 94% | +1.1% |
| 30-50 m | 2 | 100% | 10.70 | 10.70 | 28% | 0% | -28.4% |
| 50+ m | 1 | 100% | 14.49 | 14.49 | 26% | 0% | -26.2% |

### `metric3d-v2-small-fp16+clahe4_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.51 | 7.53 | 17% | 46% | -13.0% |
| pedestrian | 57 | 100% | 5.12 | 5.33 | 20% | 14% | -18.5% |
| bus | 25 | 100% | 26.39 | 26.10 | 38% | 4% | -37.9% |
| cyclist | 8 | 100% | 0.83 | 0.83 | 5% | 88% | +0.5% |
| parked two-wheeler | 1 | 100% | 2.53 | 2.53 | 10% | 0% | -10.1% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 94 | 100% | 1.68 | 2.29 | 11% | 46% | -10.1% |
| metric3d-v2-small-fp16+clahe4_p10 | 94 | 100% | 2.15 | 2.79 | 13% | 37% | -13.2% |
| metric3d-v2-small-fp16+clahe4_p25 | 94 | 100% | 1.96 | 2.55 | 12% | 43% | -11.9% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_median / night | 94 | 100% | 1.68 | 2.29 | 11% | 46% | -10.1% |
| metric3d-v2-small-fp16+clahe4_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p10 / night | 94 | 100% | 2.15 | 2.79 | 13% | 37% | -13.2% |
| metric3d-v2-small-fp16+clahe4_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p25 / night | 94 | 100% | 1.96 | 2.55 | 12% | 43% | -11.9% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 347 | 100% | 4.52 | 9.34 | 21% | 23% | -19.9% |
| metric3d-v2-small-fp16+clahe4_p10 | 347 | 100% | 5.83 | 10.93 | 25% | 17% | -24.8% |
| metric3d-v2-small-fp16+clahe4_p25 | 347 | 100% | 5.34 | 10.17 | 23% | 19% | -22.6% |

### `metric3d-v2-small-fp16+clahe4_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.49 | 1.42 | 18% | 0% | -17.9% |
| 10-20 m | 20 | 100% | 2.09 | 2.09 | 12% | 35% | -10.1% |
| 20-30 m | 56 | 100% | 1.63 | 1.81 | 8% | 64% | -7.3% |
| 30-50 m | 6 | 100% | 3.96 | 6.63 | 19% | 0% | -18.5% |
| 50+ m | 1 | 100% | 16.29 | 16.29 | 28% | 0% | -28.2% |

### `metric3d-v2-small-fp16+clahe4_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.86 | 8.55 | 19% | 25% | -19.0% |
| pedestrian | 57 | 100% | 5.23 | 5.30 | 19% | 14% | -17.9% |
| bus | 25 | 100% | 31.26 | 29.58 | 40% | 0% | -39.9% |
| cyclist | 8 | 100% | 0.87 | 0.88 | 5% | 88% | +0.7% |
| parked two-wheeler | 1 | 100% | 2.67 | 2.67 | 10% | 0% | -10.5% |

### `metric3d-v2-small-fp16+clahe4_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.81 | 1.76 | 22% | 0% | -22.2% |
| 10-20 m | 20 | 100% | 2.79 | 2.79 | 17% | 15% | -16.2% |
| 20-30 m | 56 | 100% | 2.00 | 2.23 | 9% | 57% | -9.3% |
| 30-50 m | 6 | 100% | 4.30 | 7.25 | 20% | 0% | -20.3% |
| 50+ m | 1 | 100% | 19.01 | 19.01 | 33% | 0% | -32.9% |

### `metric3d-v2-small-fp16+clahe4_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 5.29 | 10.05 | 24% | 17% | -24.0% |
| pedestrian | 57 | 100% | 5.67 | 5.97 | 22% | 16% | -21.9% |
| bus | 25 | 100% | 35.92 | 34.90 | 48% | 0% | -47.6% |
| cyclist | 8 | 100% | 0.80 | 0.77 | 4% | 100% | -2.3% |
| parked two-wheeler | 1 | 100% | 3.14 | 3.14 | 12% | 0% | -12.3% |

### `metric3d-v2-small-fp16+clahe4_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.76 | 1.67 | 21% | 0% | -21.0% |
| 10-20 m | 20 | 100% | 2.56 | 2.40 | 14% | 30% | -13.5% |
| 20-30 m | 56 | 100% | 1.82 | 2.03 | 9% | 61% | -8.4% |
| 30-50 m | 6 | 100% | 4.13 | 7.07 | 20% | 0% | -19.8% |
| 50+ m | 1 | 100% | 17.07 | 17.07 | 30% | 0% | -29.5% |

### `metric3d-v2-small-fp16+clahe4_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.61 | 9.34 | 22% | 19% | -21.8% |
| pedestrian | 57 | 100% | 5.54 | 5.69 | 21% | 18% | -20.2% |
| bus | 25 | 100% | 32.47 | 32.20 | 44% | 0% | -43.6% |
| cyclist | 8 | 100% | 0.87 | 0.88 | 5% | 88% | -1.0% |
| parked two-wheeler | 1 | 100% | 2.88 | 2.88 | 11% | 0% | -11.3% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
