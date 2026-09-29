# nuScenes distance benchmark: `da2-metric-base`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da2-metric-base_median`, `da2-metric-base_p10`, `da2-metric-base_p25` |
| Depth model | `da2-metric-base`, not given our focal length; inference 54.2 ms median, 58.1 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T12:03:00+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median | 321 | 100% | 6.47 | 7.59 | 42% | 10% | +40.7% |
| da2-metric-base_p10 | 321 | 100% | 5.31 | 6.40 | 34% | 14% | +31.9% |
| da2-metric-base_p25 | 321 | 100% | 5.80 | 6.82 | 36% | 13% | +35.2% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median / day | 227 | 100% | 6.23 | 7.76 | 42% | 13% | +41.1% |
| da2-metric-base_median / night | 94 | 100% | 7.03 | 7.21 | 41% | 1% | +39.9% |
| da2-metric-base_p10 / day | 227 | 100% | 5.08 | 6.46 | 33% | 18% | +31.1% |
| da2-metric-base_p10 / night | 94 | 100% | 6.19 | 6.25 | 35% | 3% | +34.0% |
| da2-metric-base_p25 / day | 227 | 100% | 5.37 | 6.91 | 36% | 17% | +34.9% |
| da2-metric-base_p25 / night | 94 | 100% | 6.42 | 6.59 | 37% | 2% | +36.0% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median | 1797 | 100% | 5.95 | 7.66 | 30% | 19% | +24.2% |
| da2-metric-base_p10 | 1797 | 100% | 4.95 | 6.91 | 25% | 23% | +17.0% |
| da2-metric-base_p25 | 1797 | 100% | 5.25 | 7.17 | 27% | 22% | +20.0% |

### `da2-metric-base_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 5.35 | 5.57 | 81% | 0% | +81.3% |
| 10-20 m | 97 | 100% | 5.93 | 7.16 | 44% | 0% | +44.1% |
| 20-30 m | 81 | 100% | 8.51 | 7.91 | 34% | 6% | +34.2% |
| 30-50 m | 31 | 100% | 8.52 | 8.99 | 24% | 13% | +21.4% |
| 50+ m | 53 | 100% | 7.12 | 9.34 | 15% | 42% | +10.7% |

### `da2-metric-base_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.62 | 7.28 | 26% | 20% | +20.3% |
| pedestrian | 327 | 100% | 7.17 | 7.92 | 50% | 13% | +47.4% |
| truck | 134 | 100% | 4.87 | 5.96 | 21% | 29% | +15.8% |
| bus | 110 | 100% | 7.55 | 12.77 | 26% | 24% | +0.1% |
| parked two-wheeler | 24 | 100% | 9.30 | 9.36 | 53% | 8% | +52.4% |
| cyclist | 15 | 100% | 5.38 | 6.46 | 30% | 13% | +29.6% |

### `da2-metric-base_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.03 | 4.09 | 60% | 0% | +60.0% |
| 10-20 m | 97 | 100% | 4.98 | 6.12 | 38% | 1% | +37.5% |
| 20-30 m | 81 | 100% | 7.24 | 6.72 | 29% | 12% | +28.0% |
| 30-50 m | 31 | 100% | 6.61 | 6.09 | 16% | 29% | +13.6% |
| 50+ m | 53 | 100% | 8.34 | 9.16 | 15% | 45% | +7.4% |

### `da2-metric-base_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 4.70 | 6.61 | 22% | 25% | +14.8% |
| pedestrian | 327 | 100% | 5.22 | 6.27 | 38% | 17% | +33.8% |
| truck | 134 | 100% | 4.43 | 5.69 | 18% | 26% | +9.7% |
| bus | 110 | 100% | 7.07 | 13.53 | 26% | 23% | -6.9% |
| parked two-wheeler | 24 | 100% | 7.74 | 7.42 | 42% | 8% | +41.2% |
| cyclist | 15 | 100% | 4.41 | 5.31 | 25% | 27% | +24.1% |

### `da2-metric-base_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.36 | 4.55 | 66% | 0% | +66.4% |
| 10-20 m | 97 | 100% | 5.28 | 6.58 | 40% | 0% | +40.4% |
| 20-30 m | 81 | 100% | 7.62 | 7.05 | 31% | 11% | +30.5% |
| 30-50 m | 31 | 100% | 7.16 | 7.33 | 19% | 26% | +17.0% |
| 50+ m | 53 | 100% | 7.98 | 9.14 | 15% | 45% | +8.9% |

### `da2-metric-base_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 4.96 | 6.85 | 23% | 23% | +17.1% |
| pedestrian | 327 | 100% | 5.97 | 6.94 | 43% | 17% | +39.5% |
| truck | 134 | 100% | 4.43 | 5.70 | 19% | 26% | +12.0% |
| bus | 110 | 100% | 7.24 | 12.99 | 25% | 24% | -4.1% |
| parked two-wheeler | 24 | 100% | 8.73 | 8.46 | 48% | 4% | +46.9% |
| cyclist | 15 | 100% | 5.17 | 6.00 | 28% | 27% | +27.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median | 321 | 100% | 5.42 | 6.07 | 29% | 17% | +27.4% |
| da2-metric-base_p10 | 321 | 100% | 3.95 | 5.00 | 22% | 28% | +19.4% |
| da2-metric-base_p25 | 321 | 100% | 4.30 | 5.36 | 24% | 23% | +22.4% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median / day | 227 | 100% | 5.43 | 6.46 | 31% | 22% | +29.6% |
| da2-metric-base_median / night | 94 | 100% | 5.15 | 5.14 | 23% | 6% | +22.1% |
| da2-metric-base_p10 / day | 227 | 100% | 3.90 | 5.32 | 24% | 33% | +20.3% |
| da2-metric-base_p10 / night | 94 | 100% | 4.01 | 4.25 | 19% | 16% | +17.1% |
| da2-metric-base_p25 / day | 227 | 100% | 4.29 | 5.70 | 26% | 27% | +23.9% |
| da2-metric-base_p25 / night | 94 | 100% | 4.43 | 4.52 | 20% | 13% | +18.8% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median | 1797 | 100% | 4.58 | 6.73 | 22% | 31% | +14.0% |
| da2-metric-base_p10 | 1797 | 100% | 3.83 | 6.28 | 19% | 39% | +7.4% |
| da2-metric-base_p25 | 1797 | 100% | 4.09 | 6.39 | 20% | 37% | +10.2% |

### `da2-metric-base_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 5.37 | 4.26 | 57% | 2% | +56.7% |
| 10-20 m | 82 | 100% | 3.60 | 5.40 | 32% | 4% | +32.2% |
| 20-30 m | 90 | 100% | 5.72 | 5.68 | 24% | 14% | +24.0% |
| 30-50 m | 44 | 100% | 6.00 | 7.03 | 19% | 34% | +15.6% |
| 50+ m | 53 | 100% | 7.86 | 8.74 | 13% | 45% | +6.9% |

### `da2-metric-base_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.88 | 5.98 | 16% | 34% | +9.1% |
| pedestrian | 327 | 100% | 6.87 | 7.59 | 46% | 14% | +42.8% |
| truck | 134 | 100% | 3.59 | 5.27 | 13% | 44% | +3.0% |
| bus | 110 | 100% | 5.28 | 13.76 | 20% | 45% | -13.4% |
| parked two-wheeler | 24 | 100% | 8.72 | 8.61 | 46% | 8% | +45.1% |
| cyclist | 15 | 100% | 5.11 | 5.98 | 27% | 20% | +26.8% |

### `da2-metric-base_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 3.46 | 2.71 | 36% | 33% | +36.0% |
| 10-20 m | 82 | 100% | 2.66 | 4.43 | 26% | 10% | +25.9% |
| 20-30 m | 90 | 100% | 4.44 | 4.67 | 20% | 24% | +18.7% |
| 30-50 m | 44 | 100% | 4.28 | 5.08 | 14% | 45% | +7.8% |
| 50+ m | 53 | 100% | 8.23 | 8.64 | 13% | 42% | +3.7% |

### `da2-metric-base_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.09 | 5.62 | 14% | 45% | +4.1% |
| pedestrian | 327 | 100% | 4.93 | 5.99 | 35% | 16% | +29.8% |
| truck | 134 | 100% | 3.13 | 5.42 | 12% | 46% | -2.2% |
| bus | 110 | 100% | 6.57 | 15.40 | 23% | 36% | -19.4% |
| parked two-wheeler | 24 | 100% | 6.98 | 6.67 | 36% | 12% | +34.4% |
| cyclist | 15 | 100% | 4.15 | 4.83 | 22% | 27% | +21.4% |

### `da2-metric-base_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 3.85 | 3.20 | 42% | 15% | +42.4% |
| 10-20 m | 82 | 100% | 3.07 | 4.82 | 29% | 6% | +28.5% |
| 20-30 m | 90 | 100% | 4.67 | 5.00 | 21% | 21% | +20.6% |
| 30-50 m | 44 | 100% | 4.88 | 5.76 | 16% | 41% | +11.7% |
| 50+ m | 53 | 100% | 8.20 | 8.57 | 13% | 45% | +5.2% |

### `da2-metric-base_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.30 | 5.68 | 15% | 42% | +6.1% |
| pedestrian | 327 | 100% | 5.66 | 6.64 | 39% | 18% | +35.2% |
| truck | 134 | 100% | 3.15 | 5.24 | 12% | 47% | -0.2% |
| bus | 110 | 100% | 5.39 | 14.53 | 22% | 41% | -16.9% |
| parked two-wheeler | 24 | 100% | 7.97 | 7.71 | 41% | 4% | +39.8% |
| cyclist | 15 | 100% | 4.90 | 5.52 | 25% | 27% | +24.6% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
