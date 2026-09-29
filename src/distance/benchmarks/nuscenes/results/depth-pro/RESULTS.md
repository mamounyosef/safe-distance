# nuScenes distance benchmark: `depth-pro`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `depth-pro_median`, `depth-pro_p10`, `depth-pro_p25` |
| Depth model | `depth-pro`, given our focal length; inference 853.0 ms median, 856.5 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T12:01:21+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median | 321 | 100% | 2.62 | 4.96 | 14% | 42% | -10.2% |
| depth-pro_p10 | 321 | 100% | 2.81 | 5.50 | 16% | 40% | -13.1% |
| depth-pro_p25 | 321 | 100% | 2.73 | 5.27 | 15% | 41% | -12.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median / day | 227 | 100% | 3.31 | 6.20 | 15% | 34% | -14.8% |
| depth-pro_median / night | 94 | 100% | 1.39 | 1.96 | 10% | 63% | +0.7% |
| depth-pro_p10 / day | 227 | 100% | 3.74 | 6.93 | 18% | 30% | -17.6% |
| depth-pro_p10 / night | 94 | 100% | 1.21 | 2.03 | 10% | 63% | -2.2% |
| depth-pro_p25 / day | 227 | 100% | 3.59 | 6.63 | 17% | 31% | -16.5% |
| depth-pro_p25 / night | 94 | 100% | 1.31 | 1.98 | 10% | 66% | -1.3% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median | 1797 | 100% | 4.27 | 7.54 | 19% | 24% | -17.6% |
| depth-pro_p10 | 1797 | 100% | 5.08 | 8.51 | 22% | 18% | -21.2% |
| depth-pro_p25 | 1797 | 100% | 4.77 | 8.04 | 21% | 20% | -19.7% |

### `depth-pro_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.23 | 0.36 | 5% | 86% | -0.3% |
| 10-20 m | 97 | 100% | 1.78 | 2.18 | 13% | 42% | -11.6% |
| 20-30 m | 81 | 100% | 2.40 | 3.08 | 13% | 42% | -3.8% |
| 30-50 m | 31 | 100% | 7.19 | 7.03 | 19% | 16% | -18.0% |
| 50+ m | 53 | 100% | 14.14 | 16.81 | 24% | 9% | -24.3% |

### `depth-pro_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 4.72 | 7.93 | 20% | 24% | -18.0% |
| pedestrian | 327 | 100% | 2.90 | 3.61 | 15% | 30% | -13.9% |
| truck | 134 | 100% | 5.26 | 7.43 | 19% | 23% | -17.9% |
| bus | 110 | 100% | 10.20 | 16.58 | 28% | 17% | -24.9% |
| parked two-wheeler | 24 | 100% | 2.51 | 2.78 | 14% | 25% | -14.2% |
| cyclist | 15 | 100% | 3.96 | 4.84 | 17% | 20% | -17.3% |

### `depth-pro_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.25 | 0.38 | 5% | 83% | -3.7% |
| 10-20 m | 97 | 100% | 2.16 | 2.53 | 16% | 37% | -14.3% |
| 20-30 m | 81 | 100% | 2.74 | 3.49 | 14% | 44% | -6.7% |
| 30-50 m | 31 | 100% | 8.15 | 8.17 | 21% | 6% | -21.5% |
| 50+ m | 53 | 100% | 15.64 | 18.12 | 26% | 8% | -26.4% |

### `depth-pro_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.44 | 8.89 | 22% | 17% | -21.5% |
| pedestrian | 327 | 100% | 3.51 | 4.27 | 18% | 25% | -17.1% |
| truck | 134 | 100% | 6.04 | 8.55 | 22% | 15% | -22.1% |
| bus | 110 | 100% | 13.11 | 18.41 | 31% | 9% | -30.0% |
| parked two-wheeler | 24 | 100% | 3.24 | 3.58 | 19% | 12% | -18.6% |
| cyclist | 15 | 100% | 4.45 | 5.84 | 20% | 13% | -20.2% |

### `depth-pro_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.24 | 0.35 | 5% | 86% | -2.7% |
| 10-20 m | 97 | 100% | 2.02 | 2.38 | 15% | 39% | -13.2% |
| 20-30 m | 81 | 100% | 2.65 | 3.31 | 13% | 44% | -5.6% |
| 30-50 m | 31 | 100% | 8.12 | 7.70 | 20% | 10% | -20.2% |
| 50+ m | 53 | 100% | 14.73 | 17.59 | 26% | 8% | -25.5% |

### `depth-pro_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.10 | 8.43 | 21% | 19% | -20.1% |
| pedestrian | 327 | 100% | 3.15 | 3.93 | 16% | 27% | -15.6% |
| truck | 134 | 100% | 5.93 | 8.00 | 21% | 17% | -20.5% |
| bus | 110 | 100% | 12.29 | 17.57 | 30% | 12% | -27.9% |
| parked two-wheeler | 24 | 100% | 2.87 | 3.17 | 16% | 17% | -16.3% |
| cyclist | 15 | 100% | 4.20 | 5.40 | 19% | 13% | -19.0% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median | 321 | 100% | 3.54 | 6.29 | 19% | 31% | -18.8% |
| depth-pro_p10 | 321 | 100% | 4.15 | 6.94 | 22% | 27% | -21.4% |
| depth-pro_p25 | 321 | 100% | 3.82 | 6.68 | 21% | 28% | -20.4% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median / day | 227 | 100% | 4.85 | 7.93 | 22% | 20% | -21.8% |
| depth-pro_median / night | 94 | 100% | 1.70 | 2.35 | 13% | 59% | -11.7% |
| depth-pro_p10 / day | 227 | 100% | 5.61 | 8.69 | 24% | 16% | -24.4% |
| depth-pro_p10 / night | 94 | 100% | 1.89 | 2.72 | 15% | 54% | -14.2% |
| depth-pro_p25 / day | 227 | 100% | 5.34 | 8.38 | 23% | 18% | -23.4% |
| depth-pro_p25 / night | 94 | 100% | 1.87 | 2.59 | 14% | 54% | -13.4% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median | 1797 | 100% | 6.25 | 9.46 | 25% | 12% | -24.4% |
| depth-pro_p10 | 1797 | 100% | 7.12 | 10.50 | 28% | 8% | -27.6% |
| depth-pro_p25 | 1797 | 100% | 6.80 | 10.01 | 26% | 9% | -26.2% |

### `depth-pro_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.78 | 1.33 | 16% | 50% | -15.8% |
| 10-20 m | 82 | 100% | 3.37 | 3.49 | 22% | 18% | -21.4% |
| 20-30 m | 90 | 100% | 2.04 | 3.34 | 13% | 56% | -12.6% |
| 30-50 m | 44 | 100% | 7.51 | 7.96 | 21% | 16% | -20.6% |
| 50+ m | 53 | 100% | 16.54 | 19.13 | 27% | 6% | -26.9% |

### `depth-pro_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 6.72 | 9.94 | 26% | 10% | -25.6% |
| pedestrian | 327 | 100% | 3.30 | 3.98 | 17% | 25% | -16.4% |
| truck | 134 | 100% | 7.78 | 10.24 | 27% | 6% | -26.7% |
| bus | 110 | 100% | 14.57 | 21.44 | 35% | 1% | -34.8% |
| parked two-wheeler | 24 | 100% | 3.47 | 3.62 | 18% | 8% | -18.2% |
| cyclist | 15 | 100% | 4.30 | 5.44 | 19% | 7% | -19.1% |

### `depth-pro_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.91 | 1.49 | 18% | 46% | -18.0% |
| 10-20 m | 82 | 100% | 3.86 | 3.93 | 24% | 12% | -24.3% |
| 20-30 m | 90 | 100% | 2.41 | 3.84 | 15% | 52% | -14.8% |
| 30-50 m | 44 | 100% | 8.10 | 9.08 | 25% | 11% | -24.2% |
| 50+ m | 53 | 100% | 18.15 | 20.44 | 29% | 4% | -28.9% |

### `depth-pro_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 7.66 | 10.97 | 29% | 7% | -28.6% |
| pedestrian | 327 | 100% | 3.93 | 4.67 | 20% | 19% | -19.4% |
| truck | 134 | 100% | 8.54 | 11.50 | 30% | 2% | -30.3% |
| bus | 110 | 100% | 18.95 | 23.41 | 39% | 1% | -39.1% |
| parked two-wheeler | 24 | 100% | 4.07 | 4.42 | 22% | 4% | -22.4% |
| cyclist | 15 | 100% | 4.78 | 6.45 | 22% | 0% | -21.9% |

### `depth-pro_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.84 | 1.43 | 17% | 46% | -17.2% |
| 10-20 m | 82 | 100% | 3.73 | 3.76 | 23% | 16% | -23.3% |
| 20-30 m | 90 | 100% | 2.41 | 3.70 | 15% | 52% | -14.2% |
| 30-50 m | 44 | 100% | 7.89 | 8.51 | 23% | 11% | -22.4% |
| 50+ m | 53 | 100% | 17.38 | 19.91 | 28% | 4% | -28.1% |

### `depth-pro_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 7.29 | 10.49 | 27% | 8% | -27.4% |
| pedestrian | 327 | 100% | 3.65 | 4.33 | 18% | 21% | -18.0% |
| truck | 134 | 100% | 8.14 | 10.93 | 29% | 4% | -28.9% |
| bus | 110 | 100% | 16.63 | 22.53 | 37% | 1% | -37.2% |
| parked two-wheeler | 24 | 100% | 3.72 | 4.01 | 20% | 4% | -20.2% |
| cyclist | 15 | 100% | 4.62 | 6.00 | 21% | 0% | -20.7% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
