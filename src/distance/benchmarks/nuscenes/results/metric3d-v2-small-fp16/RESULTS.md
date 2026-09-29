# nuScenes distance benchmark: `metric3d-v2-small-fp16`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 85.6 ms median, 91.0 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T13:57:28+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 321 | 100% | 1.17 | 2.05 | 8% | 71% | +5.1% |
| metric3d-v2-small-fp16_p10 | 321 | 100% | 0.97 | 1.87 | 7% | 76% | +0.8% |
| metric3d-v2-small-fp16_p25 | 321 | 100% | 0.94 | 1.84 | 7% | 76% | +2.6% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 227 | 100% | 0.95 | 2.04 | 6% | 82% | +3.1% |
| metric3d-v2-small-fp16_median / night | 94 | 100% | 1.74 | 2.07 | 12% | 44% | +9.7% |
| metric3d-v2-small-fp16_p10 / day | 227 | 100% | 0.83 | 1.88 | 6% | 85% | -1.3% |
| metric3d-v2-small-fp16_p10 / night | 94 | 100% | 1.16 | 1.86 | 10% | 55% | +5.9% |
| metric3d-v2-small-fp16_p25 / day | 227 | 100% | 0.86 | 1.83 | 6% | 85% | +0.7% |
| metric3d-v2-small-fp16_p25 / night | 94 | 100% | 1.35 | 1.86 | 10% | 56% | +7.2% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 1797 | 100% | 1.54 | 3.55 | 9% | 67% | -3.6% |
| metric3d-v2-small-fp16_p10 | 1797 | 100% | 1.87 | 4.62 | 12% | 57% | -9.2% |
| metric3d-v2-small-fp16_p25 | 1797 | 100% | 1.66 | 3.98 | 10% | 63% | -6.6% |

### `metric3d-v2-small-fp16_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.40 | 0.60 | 8% | 73% | +8.5% |
| 10-20 m | 97 | 100% | 0.87 | 1.16 | 7% | 73% | +3.7% |
| 20-30 m | 81 | 100% | 1.52 | 2.02 | 9% | 60% | +6.4% |
| 30-50 m | 31 | 100% | 1.65 | 2.30 | 6% | 81% | +0.2% |
| 50+ m | 53 | 100% | 5.10 | 5.20 | 8% | 74% | +4.4% |

### `metric3d-v2-small-fp16_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.44 | 3.54 | 9% | 70% | -2.5% |
| pedestrian | 327 | 100% | 1.40 | 2.06 | 9% | 67% | -4.5% |
| truck | 134 | 100% | 1.77 | 2.79 | 8% | 65% | -4.6% |
| bus | 110 | 100% | 5.84 | 9.79 | 17% | 41% | -12.7% |
| parked two-wheeler | 24 | 100% | 0.55 | 1.17 | 6% | 75% | -4.2% |
| cyclist | 15 | 100% | 0.64 | 1.10 | 4% | 93% | +0.0% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.29 | 0.37 | 5% | 88% | +4.7% |
| 10-20 m | 97 | 100% | 0.73 | 1.00 | 6% | 86% | -0.2% |
| 20-30 m | 81 | 100% | 1.84 | 2.19 | 10% | 58% | +2.5% |
| 30-50 m | 31 | 100% | 1.73 | 2.65 | 7% | 81% | -5.4% |
| 50+ m | 53 | 100% | 3.30 | 4.22 | 7% | 72% | -0.9% |

### `metric3d-v2-small-fp16_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.84 | 4.58 | 11% | 59% | -8.3% |
| pedestrian | 327 | 100% | 1.49 | 2.52 | 11% | 56% | -8.3% |
| truck | 134 | 100% | 2.85 | 4.51 | 12% | 53% | -10.8% |
| bus | 110 | 100% | 7.96 | 12.29 | 21% | 32% | -19.5% |
| parked two-wheeler | 24 | 100% | 0.66 | 2.52 | 12% | 67% | -11.5% |
| cyclist | 15 | 100% | 0.71 | 1.48 | 5% | 87% | -2.8% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.30 | 0.43 | 6% | 85% | +5.8% |
| 10-20 m | 97 | 100% | 0.73 | 1.03 | 6% | 84% | +1.5% |
| 20-30 m | 81 | 100% | 1.60 | 2.01 | 9% | 62% | +4.2% |
| 30-50 m | 31 | 100% | 1.66 | 2.34 | 6% | 81% | -2.9% |
| 50+ m | 53 | 100% | 4.31 | 4.35 | 7% | 74% | +1.5% |

### `metric3d-v2-small-fp16_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.61 | 3.91 | 9% | 66% | -5.6% |
| pedestrian | 327 | 100% | 1.42 | 2.24 | 10% | 61% | -6.5% |
| truck | 134 | 100% | 2.48 | 3.75 | 10% | 56% | -8.4% |
| bus | 110 | 100% | 6.35 | 11.02 | 19% | 37% | -16.4% |
| parked two-wheeler | 24 | 100% | 0.50 | 1.65 | 8% | 71% | -7.1% |
| cyclist | 15 | 100% | 0.66 | 1.12 | 4% | 93% | -1.6% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 321 | 100% | 1.67 | 2.19 | 9% | 68% | -4.8% |
| metric3d-v2-small-fp16_p10 | 321 | 100% | 1.94 | 2.60 | 10% | 55% | -8.6% |
| metric3d-v2-small-fp16_p25 | 321 | 100% | 1.80 | 2.33 | 9% | 60% | -7.0% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 227 | 100% | 1.91 | 2.45 | 9% | 68% | -5.1% |
| metric3d-v2-small-fp16_median / night | 94 | 100% | 1.50 | 1.59 | 9% | 67% | -3.9% |
| metric3d-v2-small-fp16_p10 / day | 227 | 100% | 2.14 | 2.88 | 10% | 52% | -9.2% |
| metric3d-v2-small-fp16_p10 / night | 94 | 100% | 1.72 | 1.92 | 10% | 61% | -7.2% |
| metric3d-v2-small-fp16_p25 / day | 227 | 100% | 2.03 | 2.56 | 9% | 57% | -7.4% |
| metric3d-v2-small-fp16_p25 / night | 94 | 100% | 1.58 | 1.77 | 9% | 66% | -6.0% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 1797 | 100% | 2.74 | 4.78 | 13% | 45% | -11.3% |
| metric3d-v2-small-fp16_p10 | 1797 | 100% | 3.57 | 6.27 | 17% | 30% | -16.4% |
| metric3d-v2-small-fp16_p25 | 1797 | 100% | 3.16 | 5.47 | 15% | 35% | -14.1% |

### `metric3d-v2-small-fp16_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.33 | 0.97 | 12% | 54% | -10.7% |
| 10-20 m | 82 | 100% | 1.34 | 1.45 | 9% | 66% | -6.5% |
| 20-30 m | 90 | 100% | 1.72 | 1.96 | 8% | 70% | -2.6% |
| 30-50 m | 44 | 100% | 3.18 | 3.17 | 9% | 70% | -5.6% |
| 50+ m | 53 | 100% | 3.34 | 4.15 | 6% | 79% | +0.9% |

### `metric3d-v2-small-fp16_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.73 | 4.66 | 13% | 45% | -11.2% |
| pedestrian | 327 | 100% | 1.65 | 2.24 | 10% | 57% | -7.2% |
| truck | 134 | 100% | 4.46 | 5.21 | 15% | 25% | -14.6% |
| bus | 110 | 100% | 10.45 | 14.27 | 24% | 14% | -23.7% |
| parked two-wheeler | 24 | 100% | 1.14 | 1.77 | 9% | 71% | -8.7% |
| cyclist | 15 | 100% | 0.87 | 1.23 | 5% | 87% | -2.1% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.63 | 1.12 | 13% | 50% | -13.1% |
| 10-20 m | 82 | 100% | 1.75 | 1.81 | 11% | 37% | -10.2% |
| 20-30 m | 90 | 100% | 1.79 | 2.28 | 9% | 61% | -5.9% |
| 30-50 m | 44 | 100% | 3.60 | 4.12 | 11% | 55% | -11.2% |
| 50+ m | 53 | 100% | 3.17 | 4.52 | 7% | 77% | -4.3% |

### `metric3d-v2-small-fp16_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.57 | 6.23 | 17% | 28% | -16.5% |
| pedestrian | 327 | 100% | 1.80 | 2.79 | 12% | 48% | -10.9% |
| truck | 134 | 100% | 5.80 | 7.23 | 20% | 12% | -20.0% |
| bus | 110 | 100% | 13.20 | 17.14 | 30% | 9% | -29.6% |
| parked two-wheeler | 24 | 100% | 1.52 | 3.30 | 16% | 58% | -15.7% |
| cyclist | 15 | 100% | 1.30 | 1.92 | 6% | 87% | -4.9% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.49 | 1.07 | 13% | 52% | -12.3% |
| 10-20 m | 82 | 100% | 1.61 | 1.66 | 10% | 48% | -8.7% |
| 20-30 m | 90 | 100% | 1.74 | 2.14 | 9% | 67% | -4.6% |
| 30-50 m | 44 | 100% | 3.19 | 3.44 | 9% | 59% | -8.2% |
| 50+ m | 53 | 100% | 2.74 | 4.00 | 6% | 75% | -2.0% |

### `metric3d-v2-small-fp16_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.16 | 5.36 | 15% | 33% | -14.0% |
| pedestrian | 327 | 100% | 1.71 | 2.47 | 11% | 53% | -9.1% |
| truck | 134 | 100% | 5.31 | 6.37 | 18% | 14% | -17.8% |
| bus | 110 | 100% | 11.66 | 15.72 | 27% | 12% | -26.9% |
| parked two-wheeler | 24 | 100% | 1.42 | 2.37 | 12% | 58% | -11.5% |
| cyclist | 15 | 100% | 1.07 | 1.42 | 5% | 93% | -3.7% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
