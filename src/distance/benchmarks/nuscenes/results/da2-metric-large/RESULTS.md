# nuScenes distance benchmark: `da2-metric-large`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da2-metric-large_median`, `da2-metric-large_p10`, `da2-metric-large_p25` |
| Depth model | `da2-metric-large`, not given our focal length; inference 132.6 ms median, 136.0 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T12:04:26+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median | 321 | 100% | 7.88 | 8.93 | 47% | 7% | +46.5% |
| da2-metric-large_p10 | 321 | 100% | 6.05 | 7.84 | 40% | 10% | +38.6% |
| da2-metric-large_p25 | 321 | 100% | 6.75 | 8.23 | 42% | 8% | +41.5% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median / day | 227 | 100% | 7.11 | 8.50 | 44% | 10% | +43.5% |
| da2-metric-large_median / night | 94 | 100% | 10.31 | 9.98 | 54% | 0% | +53.8% |
| da2-metric-large_p10 / day | 227 | 100% | 5.54 | 7.32 | 36% | 12% | +34.3% |
| da2-metric-large_p10 / night | 94 | 100% | 9.46 | 9.10 | 49% | 3% | +48.8% |
| da2-metric-large_p25 / day | 227 | 100% | 6.01 | 7.73 | 39% | 11% | +37.8% |
| da2-metric-large_p25 / night | 94 | 100% | 9.64 | 9.41 | 51% | 0% | +50.5% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median | 1797 | 100% | 6.51 | 8.10 | 33% | 16% | +29.3% |
| da2-metric-large_p10 | 1797 | 100% | 5.38 | 7.20 | 28% | 20% | +22.2% |
| da2-metric-large_p25 | 1797 | 100% | 5.83 | 7.53 | 30% | 19% | +25.1% |

### `da2-metric-large_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 5.52 | 5.75 | 84% | 0% | +84.0% |
| 10-20 m | 97 | 100% | 6.37 | 7.89 | 48% | 0% | +48.3% |
| 20-30 m | 81 | 100% | 10.93 | 10.31 | 45% | 4% | +44.8% |
| 30-50 m | 31 | 100% | 9.28 | 10.74 | 27% | 10% | +27.5% |
| 50+ m | 53 | 100% | 10.42 | 11.19 | 18% | 30% | +15.0% |

### `da2-metric-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 6.12 | 7.80 | 29% | 17% | +25.5% |
| pedestrian | 327 | 100% | 7.52 | 8.41 | 53% | 11% | +52.2% |
| truck | 134 | 100% | 5.82 | 7.05 | 25% | 25% | +21.4% |
| bus | 110 | 100% | 9.14 | 11.29 | 26% | 18% | +5.5% |
| parked two-wheeler | 24 | 100% | 10.18 | 10.21 | 57% | 0% | +57.0% |
| cyclist | 15 | 100% | 6.80 | 7.46 | 33% | 13% | +32.9% |

### `da2-metric-large_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.38 | 4.26 | 63% | 0% | +62.7% |
| 10-20 m | 97 | 100% | 5.68 | 6.97 | 43% | 2% | +42.5% |
| 20-30 m | 81 | 100% | 10.28 | 9.44 | 41% | 6% | +39.8% |
| 30-50 m | 31 | 100% | 8.16 | 8.51 | 22% | 16% | +21.6% |
| 50+ m | 53 | 100% | 9.86 | 10.59 | 17% | 36% | +12.5% |

### `da2-metric-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.23 | 7.01 | 25% | 21% | +20.3% |
| pedestrian | 327 | 100% | 5.32 | 6.52 | 40% | 17% | +37.9% |
| truck | 134 | 100% | 5.18 | 6.26 | 21% | 29% | +14.8% |
| bus | 110 | 100% | 8.78 | 12.22 | 25% | 15% | -1.3% |
| parked two-wheeler | 24 | 100% | 9.17 | 8.52 | 48% | 8% | +47.9% |
| cyclist | 15 | 100% | 6.07 | 6.27 | 29% | 13% | +28.6% |

### `da2-metric-large_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.67 | 4.73 | 69% | 0% | +69.3% |
| 10-20 m | 97 | 100% | 5.91 | 7.36 | 45% | 0% | +45.0% |
| 20-30 m | 81 | 100% | 10.52 | 9.65 | 42% | 6% | +42.0% |
| 30-50 m | 31 | 100% | 8.62 | 9.41 | 24% | 16% | +24.0% |
| 50+ m | 53 | 100% | 10.56 | 10.84 | 18% | 28% | +13.8% |

### `da2-metric-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.54 | 7.29 | 26% | 20% | +22.4% |
| pedestrian | 327 | 100% | 6.32 | 7.32 | 45% | 13% | +43.8% |
| truck | 134 | 100% | 5.46 | 6.49 | 22% | 28% | +17.4% |
| bus | 110 | 100% | 8.90 | 11.62 | 25% | 17% | +1.5% |
| parked two-wheeler | 24 | 100% | 9.57 | 9.35 | 52% | 4% | +52.3% |
| cyclist | 15 | 100% | 6.42 | 6.80 | 31% | 13% | +30.6% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median | 321 | 100% | 6.66 | 7.32 | 34% | 12% | +32.7% |
| da2-metric-large_p10 | 321 | 100% | 4.90 | 6.34 | 27% | 19% | +25.4% |
| da2-metric-large_p25 | 321 | 100% | 5.51 | 6.68 | 29% | 16% | +28.1% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median / day | 227 | 100% | 5.83 | 7.12 | 33% | 17% | +31.9% |
| da2-metric-large_median / night | 94 | 100% | 8.17 | 7.79 | 35% | 1% | +34.6% |
| da2-metric-large_p10 / day | 227 | 100% | 4.42 | 6.09 | 26% | 23% | +23.4% |
| da2-metric-large_p10 / night | 94 | 100% | 7.18 | 6.95 | 31% | 7% | +30.3% |
| da2-metric-large_p25 / day | 227 | 100% | 4.85 | 6.46 | 28% | 20% | +26.6% |
| da2-metric-large_p25 / night | 94 | 100% | 7.38 | 7.23 | 32% | 4% | +31.8% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median | 1797 | 100% | 5.04 | 6.95 | 24% | 26% | +18.8% |
| da2-metric-large_p10 | 1797 | 100% | 4.16 | 6.33 | 20% | 34% | +12.3% |
| da2-metric-large_p25 | 1797 | 100% | 4.50 | 6.53 | 21% | 32% | +15.0% |

### `da2-metric-large_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 5.66 | 4.44 | 59% | 2% | +59.1% |
| 10-20 m | 82 | 100% | 4.01 | 5.79 | 35% | 0% | +34.5% |
| 20-30 m | 90 | 100% | 8.46 | 8.03 | 34% | 8% | +33.8% |
| 30-50 m | 44 | 100% | 6.58 | 8.60 | 23% | 27% | +21.5% |
| 50+ m | 53 | 100% | 9.39 | 10.24 | 16% | 38% | +11.1% |

### `da2-metric-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 4.39 | 6.27 | 18% | 29% | +13.8% |
| pedestrian | 327 | 100% | 7.18 | 8.03 | 48% | 11% | +47.5% |
| truck | 134 | 100% | 4.61 | 5.81 | 15% | 34% | +8.1% |
| bus | 110 | 100% | 6.41 | 12.01 | 18% | 34% | -8.7% |
| parked two-wheeler | 24 | 100% | 9.30 | 9.37 | 50% | 4% | +49.6% |
| cyclist | 15 | 100% | 6.42 | 6.86 | 30% | 13% | +30.1% |

### `da2-metric-large_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 3.80 | 2.88 | 38% | 21% | +38.3% |
| 10-20 m | 82 | 100% | 3.26 | 4.90 | 29% | 4% | +28.7% |
| 20-30 m | 90 | 100% | 7.43 | 7.20 | 30% | 10% | +29.6% |
| 30-50 m | 44 | 100% | 5.58 | 7.29 | 20% | 36% | +15.5% |
| 50+ m | 53 | 100% | 8.03 | 9.72 | 15% | 40% | +8.6% |

### `da2-metric-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.59 | 5.77 | 16% | 39% | +9.2% |
| pedestrian | 327 | 100% | 4.92 | 6.17 | 36% | 18% | +33.8% |
| truck | 134 | 100% | 3.97 | 5.59 | 13% | 34% | +2.4% |
| bus | 110 | 100% | 6.51 | 13.51 | 21% | 37% | -14.3% |
| parked two-wheeler | 24 | 100% | 8.41 | 7.74 | 41% | 8% | +40.9% |
| cyclist | 15 | 100% | 5.38 | 5.69 | 26% | 13% | +25.9% |

### `da2-metric-large_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 4.22 | 3.38 | 45% | 6% | +44.9% |
| 10-20 m | 82 | 100% | 3.45 | 5.23 | 31% | 1% | +31.0% |
| 20-30 m | 90 | 100% | 7.88 | 7.53 | 32% | 10% | +31.3% |
| 30-50 m | 44 | 100% | 5.55 | 7.64 | 20% | 36% | +18.5% |
| 50+ m | 53 | 100% | 9.15 | 9.94 | 16% | 40% | +9.9% |

### `da2-metric-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.88 | 5.91 | 17% | 36% | +11.1% |
| pedestrian | 327 | 100% | 5.91 | 6.96 | 41% | 15% | +39.5% |
| truck | 134 | 100% | 3.94 | 5.57 | 14% | 37% | +4.8% |
| bus | 110 | 100% | 5.99 | 12.72 | 20% | 38% | -11.9% |
| parked two-wheeler | 24 | 100% | 8.81 | 8.51 | 45% | 4% | +45.0% |
| cyclist | 15 | 100% | 5.95 | 6.20 | 28% | 13% | +27.8% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
