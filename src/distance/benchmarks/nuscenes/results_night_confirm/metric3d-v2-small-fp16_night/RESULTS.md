# nuScenes distance benchmark: `metric3d-v2-small-fp16_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 88.4 ms median, 99.7 ms p95 per frame |
| Dataset | [nuScenes v1.0-night](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 3299 (2152 at night) |
| Objects | 5232 matched to a detection of 12298 labelled (visibility at least v40-60); 1680 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `83793d9` |
| Created (UTC) | 2026-09-30T19:32:48+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 1680 | 100% | 1.46 | 2.82 | 14% | 38% | +10.9% |
| metric3d-v2-small-fp16_p10 | 1680 | 100% | 1.19 | 2.75 | 12% | 51% | +6.3% |
| metric3d-v2-small-fp16_p25 | 1680 | 100% | 1.25 | 2.63 | 13% | 47% | +8.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_median / night | 1680 | 100% | 1.46 | 2.82 | 14% | 38% | +10.9% |
| metric3d-v2-small-fp16_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p10 / night | 1680 | 100% | 1.19 | 2.75 | 12% | 51% | +6.3% |
| metric3d-v2-small-fp16_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p25 / night | 1680 | 100% | 1.25 | 2.63 | 13% | 47% | +8.1% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 5232 | 100% | 1.79 | 4.29 | 14% | 46% | +0.8% |
| metric3d-v2-small-fp16_p10 | 5232 | 100% | 1.73 | 5.12 | 15% | 49% | -5.2% |
| metric3d-v2-small-fp16_p25 | 5232 | 100% | 1.66 | 4.54 | 14% | 50% | -2.5% |

### `metric3d-v2-small-fp16_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 594 | 100% | 0.88 | 0.94 | 16% | 28% | +16.2% |
| 10-20 m | 503 | 100% | 1.85 | 2.10 | 14% | 28% | +13.9% |
| 20-30 m | 291 | 100% | 2.13 | 2.91 | 12% | 56% | +10.8% |
| 30-50 m | 196 | 100% | 1.99 | 3.33 | 9% | 70% | +0.1% |
| 50+ m | 96 | 100% | 13.77 | 17.03 | 23% | 30% | -15.1% |

### `metric3d-v2-small-fp16_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 1.67 | 3.97 | 14% | 47% | +1.7% |
| pedestrian | 345 | 100% | 2.00 | 3.05 | 14% | 45% | +1.8% |
| bus | 238 | 100% | 13.02 | 12.70 | 24% | 19% | -14.8% |
| truck | 143 | 100% | 1.84 | 3.56 | 11% | 55% | -3.6% |
| cyclist | 39 | 100% | 2.69 | 3.73 | 12% | 38% | +0.4% |
| parked two-wheeler | 7 | 100% | 1.86 | 2.56 | 21% | 14% | +20.4% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 594 | 100% | 0.68 | 0.73 | 13% | 47% | +12.4% |
| 10-20 m | 503 | 100% | 1.50 | 1.66 | 11% | 46% | +10.5% |
| 20-30 m | 291 | 100% | 1.61 | 2.26 | 9% | 66% | +5.6% |
| 30-50 m | 196 | 100% | 2.51 | 4.39 | 11% | 66% | -6.0% |
| 50+ m | 96 | 100% | 17.37 | 19.05 | 27% | 22% | -25.7% |

### `metric3d-v2-small-fp16_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 1.57 | 4.78 | 14% | 51% | -4.4% |
| pedestrian | 345 | 100% | 2.15 | 3.16 | 14% | 43% | -2.8% |
| bus | 238 | 100% | 15.68 | 14.16 | 25% | 22% | -21.1% |
| truck | 143 | 100% | 2.40 | 5.64 | 16% | 50% | -11.4% |
| cyclist | 39 | 100% | 2.36 | 4.01 | 12% | 38% | -3.5% |
| parked two-wheeler | 7 | 100% | 1.51 | 1.78 | 14% | 43% | +11.7% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 594 | 100% | 0.74 | 0.80 | 14% | 42% | +13.6% |
| 10-20 m | 503 | 100% | 1.61 | 1.79 | 12% | 40% | +11.6% |
| 20-30 m | 291 | 100% | 1.75 | 2.32 | 9% | 64% | +7.5% |
| 30-50 m | 196 | 100% | 2.25 | 3.73 | 10% | 70% | -2.5% |
| 50+ m | 96 | 100% | 15.61 | 17.11 | 24% | 29% | -21.3% |

### `metric3d-v2-small-fp16_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 1.55 | 4.21 | 13% | 52% | -1.6% |
| pedestrian | 345 | 100% | 2.00 | 3.07 | 14% | 46% | -0.8% |
| bus | 238 | 100% | 14.38 | 13.42 | 24% | 21% | -18.6% |
| truck | 143 | 100% | 1.56 | 4.21 | 12% | 57% | -6.5% |
| cyclist | 39 | 100% | 2.33 | 3.74 | 12% | 41% | -1.5% |
| parked two-wheeler | 7 | 100% | 1.62 | 2.00 | 16% | 43% | +14.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 1680 | 100% | 1.35 | 2.71 | 12% | 57% | -7.3% |
| metric3d-v2-small-fp16_p10 | 1680 | 100% | 1.51 | 3.12 | 13% | 48% | -11.2% |
| metric3d-v2-small-fp16_p25 | 1680 | 100% | 1.44 | 2.81 | 13% | 51% | -9.7% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_median / night | 1680 | 100% | 1.35 | 2.71 | 12% | 57% | -7.3% |
| metric3d-v2-small-fp16_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p10 / night | 1680 | 100% | 1.51 | 3.12 | 13% | 48% | -11.2% |
| metric3d-v2-small-fp16_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16_p25 / night | 1680 | 100% | 1.44 | 2.81 | 13% | 51% | -9.7% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 5232 | 100% | 2.20 | 5.16 | 15% | 41% | -11.9% |
| metric3d-v2-small-fp16_p10 | 5232 | 100% | 2.80 | 6.45 | 19% | 31% | -17.2% |
| metric3d-v2-small-fp16_p25 | 5232 | 100% | 2.54 | 5.71 | 17% | 35% | -14.7% |

### `metric3d-v2-small-fp16_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 469 | 100% | 1.43 | 1.35 | 19% | 15% | -17.8% |
| 10-20 m | 560 | 100% | 0.81 | 0.99 | 7% | 79% | -2.9% |
| 20-30 m | 317 | 100% | 1.38 | 2.10 | 8% | 78% | +2.1% |
| 30-50 m | 230 | 100% | 2.68 | 3.71 | 9% | 69% | -4.8% |
| 50+ m | 104 | 100% | 13.90 | 17.79 | 24% | 28% | -17.2% |

### `metric3d-v2-small-fp16_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 2.06 | 4.69 | 14% | 42% | -12.0% |
| pedestrian | 345 | 100% | 2.05 | 3.09 | 14% | 46% | -0.6% |
| bus | 238 | 100% | 19.22 | 17.31 | 29% | 11% | -28.4% |
| truck | 143 | 100% | 3.07 | 5.27 | 14% | 46% | -14.1% |
| cyclist | 39 | 100% | 2.80 | 3.64 | 11% | 46% | -3.5% |
| parked two-wheeler | 7 | 100% | 1.19 | 2.09 | 15% | 43% | +13.8% |

### `metric3d-v2-small-fp16_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 469 | 100% | 1.60 | 1.52 | 21% | 6% | -20.5% |
| 10-20 m | 560 | 100% | 1.00 | 1.12 | 8% | 72% | -5.7% |
| 20-30 m | 317 | 100% | 1.44 | 1.83 | 7% | 74% | -2.2% |
| 30-50 m | 230 | 100% | 3.82 | 5.39 | 14% | 54% | -10.8% |
| 50+ m | 104 | 100% | 16.49 | 20.06 | 27% | 17% | -26.9% |

### `metric3d-v2-small-fp16_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 2.67 | 5.98 | 18% | 31% | -17.2% |
| pedestrian | 345 | 100% | 2.15 | 3.26 | 14% | 43% | -5.1% |
| bus | 238 | 100% | 21.48 | 19.47 | 34% | 6% | -33.5% |
| truck | 143 | 100% | 4.75 | 7.80 | 21% | 22% | -21.1% |
| cyclist | 39 | 100% | 2.63 | 4.11 | 12% | 56% | -7.2% |
| parked two-wheeler | 7 | 100% | 0.89 | 1.31 | 8% | 86% | +5.5% |

### `metric3d-v2-small-fp16_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 469 | 100% | 1.54 | 1.47 | 20% | 8% | -19.7% |
| 10-20 m | 560 | 100% | 0.94 | 1.08 | 7% | 74% | -4.8% |
| 20-30 m | 317 | 100% | 1.41 | 1.75 | 7% | 76% | -0.8% |
| 30-50 m | 230 | 100% | 3.04 | 4.34 | 11% | 63% | -7.2% |
| 50+ m | 104 | 100% | 15.61 | 18.08 | 25% | 22% | -22.9% |

### `metric3d-v2-small-fp16_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 4460 | 100% | 2.40 | 5.24 | 16% | 36% | -14.8% |
| pedestrian | 345 | 100% | 2.12 | 3.14 | 13% | 43% | -3.1% |
| bus | 238 | 100% | 20.65 | 18.53 | 32% | 7% | -31.4% |
| truck | 143 | 100% | 3.38 | 6.21 | 17% | 36% | -16.7% |
| cyclist | 39 | 100% | 2.48 | 3.80 | 11% | 56% | -5.3% |
| parked two-wheeler | 7 | 100% | 0.98 | 1.54 | 10% | 86% | +8.1% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
