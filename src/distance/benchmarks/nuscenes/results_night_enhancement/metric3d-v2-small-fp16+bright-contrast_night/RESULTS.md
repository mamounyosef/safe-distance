# nuScenes distance benchmark: `metric3d-v2-small-fp16+bright-contrast_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16+bright-contrast_median`, `metric3d-v2-small-fp16+bright-contrast_p10`, `metric3d-v2-small-fp16+bright-contrast_p25` |
| Depth model | `metric3d-v2-small-fp16+bright-contrast`, given our focal length; inference 85.2 ms median, 88.6 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 121 (116 at night) |
| Objects | 347 matched to a detection of 782 labelled (visibility at least v40-60); 94 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `12e710c` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T18:32:04+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+bright-contrast_median | 94 | 100% | 1.62 | 2.01 | 11% | 48% | +8.4% |
| metric3d-v2-small-fp16+bright-contrast_p10 | 94 | 100% | 1.13 | 1.88 | 9% | 59% | +4.3% |
| metric3d-v2-small-fp16+bright-contrast_p25 | 94 | 100% | 1.14 | 1.84 | 10% | 56% | +5.8% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+bright-contrast_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+bright-contrast_median / night | 94 | 100% | 1.62 | 2.01 | 11% | 48% | +8.4% |
| metric3d-v2-small-fp16+bright-contrast_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+bright-contrast_p10 / night | 94 | 100% | 1.13 | 1.88 | 9% | 59% | +4.3% |
| metric3d-v2-small-fp16+bright-contrast_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+bright-contrast_p25 / night | 94 | 100% | 1.14 | 1.84 | 10% | 56% | +5.8% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+bright-contrast_median | 347 | 100% | 3.37 | 7.28 | 16% | 37% | -9.3% |
| metric3d-v2-small-fp16+bright-contrast_p10 | 347 | 100% | 3.77 | 8.52 | 19% | 34% | -14.5% |
| metric3d-v2-small-fp16+bright-contrast_p25 | 347 | 100% | 3.53 | 7.85 | 17% | 35% | -12.2% |

### `metric3d-v2-small-fp16+bright-contrast_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.70 | 1.07 | 16% | 23% | +15.8% |
| 10-20 m | 30 | 100% | 1.61 | 1.73 | 10% | 63% | +5.3% |
| 20-30 m | 48 | 100% | 2.26 | 2.14 | 10% | 46% | +9.7% |
| 30-50 m | 2 | 100% | 4.54 | 4.54 | 12% | 50% | -12.1% |
| 50+ m | 1 | 100% | 11.19 | 11.19 | 20% | 0% | -20.3% |

### `metric3d-v2-small-fp16+bright-contrast_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.90 | 6.89 | 15% | 40% | -6.3% |
| pedestrian | 57 | 100% | 4.18 | 4.38 | 16% | 28% | -14.5% |
| bus | 25 | 100% | 19.96 | 20.22 | 30% | 4% | -29.6% |
| cyclist | 8 | 100% | 0.50 | 0.57 | 3% | 100% | -1.5% |
| parked two-wheeler | 1 | 100% | 2.86 | 2.86 | 11% | 0% | -11.4% |

### `metric3d-v2-small-fp16+bright-contrast_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.50 | 0.50 | 8% | 62% | +7.5% |
| 10-20 m | 30 | 100% | 1.02 | 1.57 | 9% | 73% | +0.5% |
| 20-30 m | 48 | 100% | 2.09 | 2.02 | 10% | 50% | +7.3% |
| 30-50 m | 2 | 100% | 6.00 | 6.00 | 16% | 50% | -16.1% |
| 50+ m | 1 | 100% | 13.95 | 13.95 | 25% | 0% | -25.3% |

### `metric3d-v2-small-fp16+bright-contrast_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.26 | 7.93 | 18% | 39% | -11.8% |
| pedestrian | 57 | 100% | 4.82 | 5.08 | 19% | 18% | -18.0% |
| bus | 25 | 100% | 25.41 | 25.07 | 37% | 0% | -37.3% |
| cyclist | 8 | 100% | 0.82 | 0.75 | 4% | 100% | -2.9% |
| parked two-wheeler | 1 | 100% | 3.35 | 3.35 | 13% | 0% | -13.4% |

### `metric3d-v2-small-fp16+bright-contrast_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.57 | 0.64 | 10% | 54% | +9.8% |
| 10-20 m | 30 | 100% | 1.04 | 1.56 | 9% | 73% | +2.2% |
| 20-30 m | 48 | 100% | 2.10 | 1.98 | 9% | 48% | +8.3% |
| 30-50 m | 2 | 100% | 5.58 | 5.58 | 15% | 50% | -14.9% |
| 50+ m | 1 | 100% | 12.22 | 12.22 | 22% | 0% | -22.1% |

### `metric3d-v2-small-fp16+bright-contrast_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.14 | 7.34 | 16% | 39% | -9.5% |
| pedestrian | 57 | 100% | 4.74 | 4.77 | 18% | 19% | -16.5% |
| bus | 25 | 100% | 23.82 | 22.59 | 33% | 0% | -33.4% |
| cyclist | 8 | 100% | 0.73 | 0.68 | 4% | 100% | -2.4% |
| parked two-wheeler | 1 | 100% | 3.10 | 3.10 | 12% | 0% | -12.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+bright-contrast_median | 94 | 100% | 1.58 | 1.81 | 9% | 65% | -5.1% |
| metric3d-v2-small-fp16+bright-contrast_p10 | 94 | 100% | 1.85 | 2.17 | 11% | 59% | -8.6% |
| metric3d-v2-small-fp16+bright-contrast_p25 | 94 | 100% | 1.70 | 1.99 | 10% | 62% | -7.3% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+bright-contrast_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+bright-contrast_median / night | 94 | 100% | 1.58 | 1.81 | 9% | 65% | -5.1% |
| metric3d-v2-small-fp16+bright-contrast_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+bright-contrast_p10 / night | 94 | 100% | 1.85 | 2.17 | 11% | 59% | -8.6% |
| metric3d-v2-small-fp16+bright-contrast_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+bright-contrast_p25 / night | 94 | 100% | 1.70 | 1.99 | 10% | 62% | -7.3% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+bright-contrast_median | 347 | 100% | 4.18 | 8.62 | 19% | 31% | -17.0% |
| metric3d-v2-small-fp16+bright-contrast_p10 | 347 | 100% | 5.16 | 10.13 | 23% | 24% | -21.7% |
| metric3d-v2-small-fp16+bright-contrast_p25 | 347 | 100% | 4.84 | 9.39 | 21% | 27% | -19.6% |

### `metric3d-v2-small-fp16+bright-contrast_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.63 | 1.64 | 21% | 0% | -20.6% |
| 10-20 m | 20 | 100% | 1.57 | 1.74 | 10% | 50% | -6.8% |
| 20-30 m | 56 | 100% | 1.33 | 1.45 | 6% | 82% | -0.5% |
| 30-50 m | 6 | 100% | 2.41 | 3.78 | 11% | 83% | -10.6% |
| 50+ m | 1 | 100% | 13.77 | 13.77 | 24% | 0% | -23.8% |

### `metric3d-v2-small-fp16+bright-contrast_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.57 | 8.03 | 18% | 34% | -15.7% |
| pedestrian | 57 | 100% | 4.60 | 4.72 | 17% | 19% | -16.3% |
| bus | 25 | 100% | 26.04 | 26.31 | 36% | 0% | -36.0% |
| cyclist | 8 | 100% | 0.75 | 0.76 | 4% | 100% | -3.0% |
| parked two-wheeler | 1 | 100% | 3.21 | 3.21 | 13% | 0% | -12.6% |

### `metric3d-v2-small-fp16+bright-contrast_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.87 | 1.95 | 25% | 0% | -24.5% |
| 10-20 m | 20 | 100% | 1.90 | 2.43 | 14% | 40% | -13.4% |
| 20-30 m | 56 | 100% | 1.37 | 1.60 | 7% | 79% | -2.9% |
| 30-50 m | 6 | 100% | 2.93 | 4.61 | 13% | 50% | -12.9% |
| 50+ m | 1 | 100% | 16.53 | 16.53 | 29% | 0% | -28.6% |

### `metric3d-v2-small-fp16+bright-contrast_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.46 | 9.43 | 22% | 27% | -20.6% |
| pedestrian | 57 | 100% | 5.28 | 5.45 | 20% | 14% | -19.7% |
| bus | 25 | 100% | 31.49 | 31.16 | 43% | 0% | -43.0% |
| cyclist | 8 | 100% | 0.87 | 0.95 | 5% | 88% | -4.3% |
| parked two-wheeler | 1 | 100% | 3.70 | 3.70 | 15% | 0% | -14.6% |

### `metric3d-v2-small-fp16+bright-contrast_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.80 | 1.86 | 23% | 0% | -23.3% |
| 10-20 m | 20 | 100% | 1.58 | 2.12 | 12% | 45% | -11.2% |
| 20-30 m | 56 | 100% | 1.21 | 1.50 | 6% | 80% | -2.0% |
| 30-50 m | 6 | 100% | 2.68 | 4.33 | 12% | 67% | -12.1% |
| 50+ m | 1 | 100% | 14.80 | 14.80 | 26% | 0% | -25.6% |

### `metric3d-v2-small-fp16+bright-contrast_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.05 | 8.74 | 20% | 30% | -18.5% |
| pedestrian | 57 | 100% | 5.20 | 5.13 | 19% | 14% | -18.3% |
| bus | 25 | 100% | 29.91 | 28.68 | 39% | 0% | -39.5% |
| cyclist | 8 | 100% | 0.87 | 0.88 | 5% | 88% | -3.8% |
| parked two-wheeler | 1 | 100% | 3.45 | 3.45 | 14% | 0% | -13.6% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
