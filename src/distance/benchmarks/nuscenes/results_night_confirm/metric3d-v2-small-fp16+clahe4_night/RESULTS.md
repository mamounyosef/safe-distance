# nuScenes distance benchmark: `metric3d-v2-small-fp16+clahe4_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16+clahe4_median`, `metric3d-v2-small-fp16+clahe4_p10`, `metric3d-v2-small-fp16+clahe4_p25` |
| Depth model | `metric3d-v2-small-fp16+clahe4`, given our focal length; inference 112.3 ms median, 127.8 ms p95 per frame |
| Dataset | [nuScenes v1.0-night](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 3299 (2152 at night) |
| Objects | 5232 matched to a detection of 12298 labelled (visibility at least v40-60); 1680 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `83793d9` (with uncommitted changes) |
| Created (UTC) | 2026-09-30T19:40:05+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 1680 | 100% | 0.96 | 2.17 | 10% | 62% | +5.5% |
| metric3d-v2-small-fp16+clahe4_p10 | 1680 | 100% | 0.80 | 2.26 | 9% | 68% | +0.8% |
| metric3d-v2-small-fp16+clahe4_p25 | 1680 | 100% | 0.83 | 2.10 | 9% | 67% | +2.8% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_median / night | 1680 | 100% | 0.96 | 2.17 | 10% | 62% | +5.5% |
| metric3d-v2-small-fp16+clahe4_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p10 / night | 1680 | 100% | 0.80 | 2.26 | 9% | 68% | +0.8% |
| metric3d-v2-small-fp16+clahe4_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p25 / night | 1680 | 100% | 0.83 | 2.10 | 9% | 67% | +2.8% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 5232 | 100% | 1.61 | 4.10 | 13% | 54% | -1.9% |
| metric3d-v2-small-fp16+clahe4_p10 | 5232 | 100% | 1.77 | 4.95 | 14% | 51% | -8.4% |
| metric3d-v2-small-fp16+clahe4_p25 | 5232 | 100% | 1.60 | 4.37 | 13% | 54% | -5.5% |

### `metric3d-v2-small-fp16+clahe4_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 594 | 100% | 0.51 | 0.63 | 11% | 58% | +10.6% |
| 10-20 m | 503 | 100% | 0.97 | 1.46 | 10% | 65% | +8.0% |
| 20-30 m | 291 | 100% | 1.58 | 2.10 | 9% | 71% | +2.0% |
| 30-50 m | 196 | 100% | 2.56 | 3.74 | 10% | 66% | -2.1% |
| 50+ m | 96 | 100% | 7.71 | 12.37 | 17% | 43% | -12.0% |

### `metric3d-v2-small-fp16+clahe4_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 1.46 | 3.72 | 12% | 56% | -1.4% |
| pedestrian | 345 | 100% | 2.06 | 3.15 | 15% | 46% | +1.3% |
| bus | 238 | 100% | 13.10 | 12.94 | 24% | 20% | -14.4% |
| truck | 143 | 100% | 1.94 | 3.50 | 11% | 55% | -5.3% |
| cyclist | 39 | 100% | 2.54 | 4.43 | 14% | 46% | -0.9% |
| parked two-wheeler | 7 | 100% | 0.73 | 0.94 | 7% | 71% | +5.7% |

### `metric3d-v2-small-fp16+clahe4_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 594 | 100% | 0.36 | 0.46 | 8% | 68% | +6.5% |
| 10-20 m | 503 | 100% | 0.72 | 1.00 | 7% | 79% | +3.3% |
| 20-30 m | 291 | 100% | 1.58 | 2.15 | 9% | 71% | -2.6% |
| 30-50 m | 196 | 100% | 3.60 | 4.88 | 13% | 53% | -8.3% |
| 50+ m | 96 | 100% | 11.41 | 15.07 | 21% | 34% | -18.7% |

### `metric3d-v2-small-fp16+clahe4_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 1.60 | 4.60 | 13% | 53% | -7.8% |
| pedestrian | 345 | 100% | 1.81 | 3.14 | 13% | 49% | -5.8% |
| bus | 238 | 100% | 14.53 | 14.14 | 26% | 19% | -22.4% |
| truck | 143 | 100% | 2.59 | 5.38 | 15% | 52% | -12.5% |
| cyclist | 39 | 100% | 1.60 | 3.79 | 12% | 56% | -6.2% |
| parked two-wheeler | 7 | 100% | 0.50 | 1.10 | 6% | 86% | -0.4% |

### `metric3d-v2-small-fp16+clahe4_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 594 | 100% | 0.40 | 0.51 | 9% | 64% | +7.9% |
| 10-20 m | 503 | 100% | 0.79 | 1.15 | 8% | 75% | +5.0% |
| 20-30 m | 291 | 100% | 1.51 | 1.96 | 8% | 74% | -0.3% |
| 30-50 m | 196 | 100% | 3.00 | 4.07 | 10% | 62% | -5.0% |
| 50+ m | 96 | 100% | 8.98 | 13.30 | 18% | 39% | -15.0% |

### `metric3d-v2-small-fp16+clahe4_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 1.47 | 4.01 | 12% | 56% | -4.9% |
| pedestrian | 345 | 100% | 1.81 | 3.02 | 13% | 48% | -3.0% |
| bus | 238 | 100% | 14.20 | 13.50 | 24% | 21% | -19.3% |
| truck | 143 | 100% | 1.93 | 4.06 | 12% | 56% | -8.2% |
| cyclist | 39 | 100% | 2.37 | 3.91 | 13% | 49% | -3.7% |
| parked two-wheeler | 7 | 100% | 0.43 | 0.92 | 5% | 86% | +1.5% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 1680 | 100% | 1.80 | 2.94 | 15% | 36% | -11.7% |
| metric3d-v2-small-fp16+clahe4_p10 | 1680 | 100% | 2.02 | 3.48 | 17% | 28% | -15.8% |
| metric3d-v2-small-fp16+clahe4_p25 | 1680 | 100% | 1.93 | 3.16 | 16% | 32% | -14.0% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_median / night | 1680 | 100% | 1.80 | 2.94 | 15% | 36% | -11.7% |
| metric3d-v2-small-fp16+clahe4_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p10 / night | 1680 | 100% | 2.02 | 3.48 | 17% | 28% | -15.8% |
| metric3d-v2-small-fp16+clahe4_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+clahe4_p25 / night | 1680 | 100% | 1.93 | 3.16 | 16% | 32% | -14.0% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+clahe4_median | 5232 | 100% | 2.79 | 5.41 | 17% | 30% | -14.2% |
| metric3d-v2-small-fp16+clahe4_p10 | 5232 | 100% | 3.43 | 6.67 | 21% | 20% | -19.8% |
| metric3d-v2-small-fp16+clahe4_p25 | 5232 | 100% | 3.14 | 5.96 | 19% | 24% | -17.2% |

### `metric3d-v2-small-fp16+clahe4_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 469 | 100% | 1.66 | 1.60 | 22% | 5% | -21.4% |
| 10-20 m | 560 | 100% | 1.46 | 1.61 | 11% | 50% | -8.0% |
| 20-30 m | 317 | 100% | 2.31 | 2.58 | 10% | 53% | -5.9% |
| 30-50 m | 230 | 100% | 4.26 | 4.69 | 12% | 43% | -7.8% |
| 50+ m | 104 | 100% | 9.76 | 13.32 | 18% | 35% | -14.2% |

### `metric3d-v2-small-fp16+clahe4_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 2.69 | 4.95 | 16% | 29% | -14.5% |
| pedestrian | 345 | 100% | 1.93 | 3.18 | 14% | 48% | -1.1% |
| bus | 238 | 100% | 19.06 | 17.42 | 30% | 10% | -27.9% |
| truck | 143 | 100% | 3.82 | 5.49 | 16% | 29% | -15.6% |
| cyclist | 39 | 100% | 2.61 | 4.41 | 13% | 49% | -4.7% |
| parked two-wheeler | 7 | 100% | 0.57 | 0.85 | 5% | 86% | -0.0% |

### `metric3d-v2-small-fp16+clahe4_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 469 | 100% | 1.84 | 1.78 | 25% | 3% | -24.4% |
| 10-20 m | 560 | 100% | 1.71 | 1.75 | 12% | 38% | -11.8% |
| 20-30 m | 317 | 100% | 2.66 | 2.93 | 12% | 45% | -9.8% |
| 30-50 m | 230 | 100% | 4.99 | 6.23 | 16% | 33% | -13.8% |
| 50+ m | 104 | 100% | 12.81 | 16.07 | 22% | 27% | -20.6% |

### `metric3d-v2-small-fp16+clahe4_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 3.31 | 6.24 | 21% | 19% | -20.0% |
| pedestrian | 345 | 100% | 2.00 | 3.30 | 13% | 44% | -8.0% |
| bus | 238 | 100% | 21.06 | 19.52 | 34% | 5% | -34.4% |
| truck | 143 | 100% | 5.06 | 7.76 | 22% | 13% | -22.0% |
| cyclist | 39 | 100% | 2.03 | 4.15 | 13% | 56% | -9.8% |
| parked two-wheeler | 7 | 100% | 1.09 | 1.38 | 8% | 71% | -5.8% |

### `metric3d-v2-small-fp16+clahe4_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 469 | 100% | 1.78 | 1.71 | 24% | 4% | -23.4% |
| 10-20 m | 560 | 100% | 1.63 | 1.69 | 12% | 42% | -10.4% |
| 20-30 m | 317 | 100% | 2.51 | 2.71 | 11% | 50% | -8.0% |
| 30-50 m | 230 | 100% | 4.52 | 5.29 | 13% | 40% | -10.5% |
| 50+ m | 104 | 100% | 10.27 | 14.30 | 20% | 30% | -17.1% |

### `metric3d-v2-small-fp16+clahe4_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 3.05 | 5.52 | 18% | 23% | -17.5% |
| pedestrian | 345 | 100% | 1.85 | 3.14 | 13% | 49% | -5.3% |
| bus | 238 | 100% | 20.57 | 18.58 | 32% | 8% | -31.8% |
| truck | 143 | 100% | 4.12 | 6.29 | 18% | 20% | -18.1% |
| cyclist | 39 | 100% | 2.10 | 4.09 | 13% | 62% | -7.5% |
| parked two-wheeler | 7 | 100% | 0.85 | 1.17 | 7% | 86% | -3.9% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
