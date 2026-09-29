# nuScenes distance benchmark: `metric3d-v2-small-fp16_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 87.0 ms median, 99.3 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 121 (116 at night) |
| Objects | 347 matched to a detection of 782 labelled (visibility at least v40-60); 94 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `12e710c` |
| Created (UTC) | 2026-09-29T18:30:19+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 94 | 100% | 1.74 | 2.07 | 12% | 44% | +9.7% |
| metric3d-v2-small-fp16_p10 | 94 | 100% | 1.16 | 1.86 | 10% | 55% | +5.9% |
| metric3d-v2-small-fp16_p25 | 94 | 100% | 1.35 | 1.86 | 10% | 56% | +7.2% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_median / night | 94 | 100% | 1.74 | 2.07 | 12% | 44% | +9.7% |
| metric3d-v2-small-fp16_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p10 / night | 94 | 100% | 1.16 | 1.86 | 10% | 55% | +5.9% |
| metric3d-v2-small-fp16_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p25 / night | 94 | 100% | 1.35 | 1.86 | 10% | 56% | +7.2% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 347 | 100% | 3.62 | 7.20 | 16% | 36% | -8.3% |
| metric3d-v2-small-fp16_p10 | 347 | 100% | 3.83 | 8.33 | 18% | 34% | -13.4% |
| metric3d-v2-small-fp16_p25 | 347 | 100% | 3.71 | 7.70 | 17% | 37% | -11.1% |

### `metric3d-v2-small-fp16_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.69 | 1.01 | 15% | 31% | +15.2% |
| 10-20 m | 30 | 100% | 1.57 | 1.73 | 10% | 50% | +6.3% |
| 20-30 m | 48 | 100% | 2.42 | 2.49 | 12% | 44% | +11.5% |
| 30-50 m | 2 | 100% | 2.25 | 2.25 | 6% | 50% | -6.0% |
| 50+ m | 1 | 100% | 5.71 | 5.71 | 10% | 0% | -10.3% |

### `metric3d-v2-small-fp16_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.93 | 6.78 | 15% | 41% | -5.0% |
| pedestrian | 57 | 100% | 4.21 | 4.15 | 16% | 21% | -13.7% |
| bus | 25 | 100% | 22.38 | 20.84 | 31% | 4% | -30.5% |
| cyclist | 8 | 100% | 0.59 | 0.63 | 4% | 100% | -2.4% |
| parked two-wheeler | 1 | 100% | 2.79 | 2.79 | 11% | 0% | -11.1% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.49 | 0.53 | 8% | 62% | +8.0% |
| 10-20 m | 30 | 100% | 0.89 | 1.53 | 9% | 73% | +1.8% |
| 20-30 m | 48 | 100% | 2.19 | 2.20 | 10% | 44% | +8.9% |
| 30-50 m | 2 | 100% | 3.72 | 3.72 | 10% | 50% | -10.1% |
| 50+ m | 1 | 100% | 8.65 | 8.65 | 16% | 0% | -15.7% |

### `metric3d-v2-small-fp16_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.39 | 7.74 | 17% | 38% | -10.6% |
| pedestrian | 57 | 100% | 4.60 | 4.69 | 18% | 19% | -16.6% |
| bus | 25 | 100% | 24.28 | 25.28 | 38% | 0% | -37.6% |
| cyclist | 8 | 100% | 0.64 | 0.79 | 4% | 100% | -3.6% |
| parked two-wheeler | 1 | 100% | 3.25 | 3.25 | 13% | 0% | -13.0% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.53 | 0.64 | 10% | 54% | +9.9% |
| 10-20 m | 30 | 100% | 0.89 | 1.53 | 9% | 77% | +3.4% |
| 20-30 m | 48 | 100% | 2.23 | 2.23 | 11% | 46% | +9.9% |
| 30-50 m | 2 | 100% | 3.43 | 3.43 | 9% | 50% | -9.3% |
| 50+ m | 1 | 100% | 6.84 | 6.84 | 12% | 0% | -12.4% |

### `metric3d-v2-small-fp16_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.10 | 7.17 | 16% | 42% | -8.2% |
| pedestrian | 57 | 100% | 4.36 | 4.45 | 17% | 21% | -15.4% |
| bus | 25 | 100% | 22.86 | 22.96 | 34% | 0% | -34.0% |
| cyclist | 8 | 100% | 0.66 | 0.73 | 4% | 100% | -3.2% |
| parked two-wheeler | 1 | 100% | 2.93 | 2.93 | 12% | 0% | -11.7% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 94 | 100% | 1.50 | 1.59 | 9% | 67% | -3.9% |
| metric3d-v2-small-fp16_p10 | 94 | 100% | 1.72 | 1.92 | 10% | 61% | -7.2% |
| metric3d-v2-small-fp16_p25 | 94 | 100% | 1.58 | 1.77 | 9% | 66% | -6.0% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_median / night | 94 | 100% | 1.50 | 1.59 | 9% | 67% | -3.9% |
| metric3d-v2-small-fp16_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p10 / night | 94 | 100% | 1.72 | 1.92 | 10% | 61% | -7.2% |
| metric3d-v2-small-fp16_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p25 / night | 94 | 100% | 1.58 | 1.77 | 9% | 66% | -6.0% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 347 | 100% | 3.98 | 8.40 | 18% | 33% | -16.0% |
| metric3d-v2-small-fp16_p10 | 347 | 100% | 4.88 | 9.85 | 22% | 26% | -20.7% |
| metric3d-v2-small-fp16_p25 | 347 | 100% | 4.54 | 9.11 | 20% | 29% | -18.6% |

### `metric3d-v2-small-fp16_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.71 | 1.64 | 21% | 0% | -20.6% |
| 10-20 m | 20 | 100% | 1.47 | 1.66 | 10% | 60% | -6.5% |
| 20-30 m | 56 | 100% | 1.35 | 1.36 | 6% | 82% | +0.8% |
| 30-50 m | 6 | 100% | 1.61 | 2.33 | 6% | 83% | -6.4% |
| 50+ m | 1 | 100% | 8.29 | 8.29 | 14% | 0% | -14.3% |

### `metric3d-v2-small-fp16_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.23 | 7.72 | 17% | 38% | -14.5% |
| pedestrian | 57 | 100% | 4.71 | 4.48 | 17% | 21% | -15.6% |
| bus | 25 | 100% | 28.46 | 26.93 | 37% | 0% | -36.9% |
| cyclist | 8 | 100% | 0.74 | 0.82 | 5% | 88% | -3.8% |
| parked two-wheeler | 1 | 100% | 3.14 | 3.14 | 12% | 0% | -12.3% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.84 | 1.92 | 24% | 0% | -24.1% |
| 10-20 m | 20 | 100% | 1.87 | 2.30 | 14% | 30% | -12.6% |
| 20-30 m | 56 | 100% | 1.33 | 1.47 | 6% | 82% | -1.5% |
| 30-50 m | 6 | 100% | 2.22 | 3.24 | 9% | 83% | -9.0% |
| 50+ m | 1 | 100% | 11.23 | 11.23 | 19% | 0% | -19.4% |

### `metric3d-v2-small-fp16_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.21 | 9.11 | 21% | 29% | -19.5% |
| pedestrian | 57 | 100% | 4.97 | 5.07 | 19% | 16% | -18.3% |
| bus | 25 | 100% | 30.36 | 31.37 | 43% | 0% | -43.3% |
| cyclist | 8 | 100% | 0.91 | 0.99 | 5% | 88% | -5.0% |
| parked two-wheeler | 1 | 100% | 3.60 | 3.60 | 14% | 0% | -14.2% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.80 | 1.84 | 23% | 0% | -23.1% |
| 10-20 m | 20 | 100% | 1.65 | 2.02 | 12% | 50% | -10.5% |
| 20-30 m | 56 | 100% | 1.37 | 1.40 | 6% | 84% | -0.7% |
| 30-50 m | 6 | 100% | 1.97 | 2.99 | 8% | 83% | -8.2% |
| 50+ m | 1 | 100% | 9.42 | 9.42 | 16% | 0% | -16.3% |

### `metric3d-v2-small-fp16_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.92 | 8.40 | 19% | 32% | -17.3% |
| pedestrian | 57 | 100% | 4.90 | 4.82 | 18% | 19% | -17.2% |
| bus | 25 | 100% | 28.94 | 29.05 | 40% | 0% | -39.9% |
| cyclist | 8 | 100% | 0.86 | 0.93 | 5% | 88% | -4.6% |
| parked two-wheeler | 1 | 100% | 3.28 | 3.28 | 13% | 0% | -12.9% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
