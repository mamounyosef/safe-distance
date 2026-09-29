# nuScenes distance benchmark: `metric3d-v2-small-fp16+gamma06_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16+gamma06_median`, `metric3d-v2-small-fp16+gamma06_p10`, `metric3d-v2-small-fp16+gamma06_p25` |
| Depth model | `metric3d-v2-small-fp16+gamma06`, given our focal length; inference 91.5 ms median, 113.3 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 121 (116 at night) |
| Objects | 347 matched to a detection of 782 labelled (visibility at least v40-60); 94 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `12e710c` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T18:31:24+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06_median | 94 | 100% | 1.54 | 2.00 | 11% | 47% | +8.6% |
| metric3d-v2-small-fp16+gamma06_p10 | 94 | 100% | 1.17 | 1.81 | 9% | 61% | +4.9% |
| metric3d-v2-small-fp16+gamma06_p25 | 94 | 100% | 1.28 | 1.81 | 9% | 61% | +6.2% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06_median / night | 94 | 100% | 1.54 | 2.00 | 11% | 47% | +8.6% |
| metric3d-v2-small-fp16+gamma06_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06_p10 / night | 94 | 100% | 1.17 | 1.81 | 9% | 61% | +4.9% |
| metric3d-v2-small-fp16+gamma06_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06_p25 / night | 94 | 100% | 1.28 | 1.81 | 9% | 61% | +6.2% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06_median | 347 | 100% | 3.24 | 6.82 | 15% | 38% | -8.1% |
| metric3d-v2-small-fp16+gamma06_p10 | 347 | 100% | 3.72 | 8.11 | 18% | 35% | -13.5% |
| metric3d-v2-small-fp16+gamma06_p25 | 347 | 100% | 3.44 | 7.41 | 17% | 37% | -11.1% |

### `metric3d-v2-small-fp16+gamma06_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.68 | 1.01 | 15% | 31% | +15.2% |
| 10-20 m | 30 | 100% | 1.35 | 1.63 | 10% | 53% | +5.8% |
| 20-30 m | 48 | 100% | 2.05 | 2.24 | 11% | 48% | +10.1% |
| 30-50 m | 2 | 100% | 5.89 | 5.89 | 16% | 50% | -16.1% |
| 50+ m | 1 | 100% | 6.77 | 6.77 | 12% | 0% | -12.3% |

### `metric3d-v2-small-fp16+gamma06_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.63 | 6.47 | 15% | 43% | -5.3% |
| pedestrian | 57 | 100% | 4.07 | 3.96 | 15% | 23% | -13.0% |
| bus | 25 | 100% | 20.17 | 19.20 | 28% | 4% | -28.3% |
| cyclist | 8 | 100% | 0.45 | 0.46 | 3% | 100% | -1.4% |
| parked two-wheeler | 1 | 100% | 2.78 | 2.78 | 11% | 0% | -11.1% |

### `metric3d-v2-small-fp16+gamma06_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.48 | 0.55 | 9% | 54% | +8.2% |
| 10-20 m | 30 | 100% | 0.75 | 1.43 | 8% | 80% | +1.4% |
| 20-30 m | 48 | 100% | 1.79 | 1.98 | 9% | 52% | +7.7% |
| 30-50 m | 2 | 100% | 7.29 | 7.29 | 20% | 50% | -19.9% |
| 50+ m | 1 | 100% | 10.54 | 10.54 | 19% | 0% | -19.1% |

### `metric3d-v2-small-fp16+gamma06_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.21 | 7.62 | 17% | 40% | -11.0% |
| pedestrian | 57 | 100% | 4.57 | 4.59 | 18% | 19% | -16.2% |
| bus | 25 | 100% | 23.70 | 23.71 | 35% | 0% | -35.5% |
| cyclist | 8 | 100% | 0.57 | 0.64 | 4% | 100% | -2.9% |
| parked two-wheeler | 1 | 100% | 3.19 | 3.19 | 13% | 0% | -12.7% |

### `metric3d-v2-small-fp16+gamma06_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.52 | 0.66 | 10% | 54% | +10.1% |
| 10-20 m | 30 | 100% | 0.87 | 1.43 | 8% | 77% | +3.0% |
| 20-30 m | 48 | 100% | 1.85 | 2.02 | 10% | 54% | +8.7% |
| 30-50 m | 2 | 100% | 6.93 | 6.93 | 19% | 50% | -18.9% |
| 50+ m | 1 | 100% | 8.22 | 8.22 | 15% | 0% | -14.9% |

### `metric3d-v2-small-fp16+gamma06_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.00 | 6.98 | 15% | 42% | -8.5% |
| pedestrian | 57 | 100% | 4.40 | 4.31 | 17% | 21% | -15.0% |
| bus | 25 | 100% | 20.72 | 21.29 | 32% | 0% | -31.7% |
| cyclist | 8 | 100% | 0.59 | 0.57 | 3% | 100% | -2.4% |
| parked two-wheeler | 1 | 100% | 2.91 | 2.91 | 12% | 0% | -11.6% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06_median | 94 | 100% | 1.44 | 1.70 | 9% | 68% | -4.9% |
| metric3d-v2-small-fp16+gamma06_p10 | 94 | 100% | 1.72 | 2.06 | 11% | 61% | -8.1% |
| metric3d-v2-small-fp16+gamma06_p25 | 94 | 100% | 1.59 | 1.90 | 10% | 66% | -6.9% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06_median / night | 94 | 100% | 1.44 | 1.70 | 9% | 68% | -4.9% |
| metric3d-v2-small-fp16+gamma06_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06_p10 / night | 94 | 100% | 1.72 | 2.06 | 11% | 61% | -8.1% |
| metric3d-v2-small-fp16+gamma06_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06_p25 / night | 94 | 100% | 1.59 | 1.90 | 10% | 66% | -6.9% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06_median | 347 | 100% | 3.82 | 8.11 | 18% | 33% | -15.9% |
| metric3d-v2-small-fp16+gamma06_p10 | 347 | 100% | 4.97 | 9.69 | 22% | 25% | -20.7% |
| metric3d-v2-small-fp16+gamma06_p25 | 347 | 100% | 4.53 | 8.91 | 20% | 29% | -18.6% |

### `metric3d-v2-small-fp16+gamma06_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.71 | 1.64 | 21% | 0% | -20.5% |
| 10-20 m | 20 | 100% | 1.47 | 1.64 | 10% | 65% | -6.3% |
| 20-30 m | 56 | 100% | 1.30 | 1.37 | 6% | 82% | -0.4% |
| 30-50 m | 6 | 100% | 2.10 | 3.90 | 11% | 83% | -10.7% |
| 50+ m | 1 | 100% | 9.35 | 9.35 | 16% | 0% | -16.2% |

### `metric3d-v2-small-fp16+gamma06_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.35 | 7.53 | 17% | 37% | -14.7% |
| pedestrian | 57 | 100% | 4.51 | 4.29 | 16% | 25% | -14.9% |
| bus | 25 | 100% | 26.25 | 25.29 | 35% | 0% | -34.8% |
| cyclist | 8 | 100% | 0.63 | 0.66 | 4% | 100% | -2.9% |
| parked two-wheeler | 1 | 100% | 3.13 | 3.13 | 12% | 0% | -12.3% |

### `metric3d-v2-small-fp16+gamma06_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.85 | 1.91 | 24% | 0% | -24.1% |
| 10-20 m | 20 | 100% | 1.69 | 2.29 | 14% | 40% | -12.2% |
| 20-30 m | 56 | 100% | 1.20 | 1.52 | 6% | 80% | -2.6% |
| 30-50 m | 6 | 100% | 2.63 | 4.75 | 13% | 67% | -13.1% |
| 50+ m | 1 | 100% | 13.12 | 13.12 | 23% | 0% | -22.7% |

### `metric3d-v2-small-fp16+gamma06_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.55 | 9.09 | 21% | 28% | -19.9% |
| pedestrian | 57 | 100% | 4.97 | 4.95 | 19% | 16% | -18.0% |
| bus | 25 | 100% | 29.78 | 29.80 | 41% | 0% | -41.2% |
| cyclist | 8 | 100% | 0.84 | 0.84 | 5% | 100% | -4.3% |
| parked two-wheeler | 1 | 100% | 3.54 | 3.54 | 14% | 0% | -13.9% |

### `metric3d-v2-small-fp16+gamma06_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.81 | 1.83 | 23% | 0% | -23.0% |
| 10-20 m | 20 | 100% | 1.44 | 2.00 | 12% | 55% | -10.2% |
| 20-30 m | 56 | 100% | 1.17 | 1.44 | 6% | 82% | -1.8% |
| 30-50 m | 6 | 100% | 2.38 | 4.47 | 12% | 83% | -12.3% |
| 50+ m | 1 | 100% | 10.80 | 10.80 | 19% | 0% | -18.7% |

### `metric3d-v2-small-fp16+gamma06_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.98 | 8.33 | 19% | 31% | -17.6% |
| pedestrian | 57 | 100% | 4.89 | 4.66 | 18% | 19% | -16.8% |
| bus | 25 | 100% | 26.80 | 27.38 | 38% | 0% | -37.8% |
| cyclist | 8 | 100% | 0.77 | 0.77 | 4% | 100% | -3.8% |
| parked two-wheeler | 1 | 100% | 3.26 | 3.26 | 13% | 0% | -12.8% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
