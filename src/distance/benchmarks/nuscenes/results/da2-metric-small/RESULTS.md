# nuScenes distance benchmark: `da2-metric-small`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `da2-metric-small_median`, `da2-metric-small_p10`, `da2-metric-small_p25` |
| Depth model | `da2-metric-small`, not given our focal length; inference 32.0 ms median, 36.4 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T12:02:06+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median | 321 | 100% | 5.64 | 7.17 | 38% | 17% | +32.4% |
| da2-metric-small_p10 | 321 | 100% | 5.06 | 5.99 | 31% | 20% | +23.2% |
| da2-metric-small_p25 | 321 | 100% | 5.19 | 6.45 | 33% | 17% | +27.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median / day | 227 | 100% | 6.80 | 8.28 | 43% | 12% | +42.1% |
| da2-metric-small_median / night | 94 | 100% | 3.17 | 4.48 | 24% | 27% | +9.0% |
| da2-metric-small_p10 / day | 227 | 100% | 5.58 | 6.61 | 34% | 15% | +31.5% |
| da2-metric-small_p10 / night | 94 | 100% | 3.04 | 4.50 | 23% | 31% | +3.2% |
| da2-metric-small_p25 / day | 227 | 100% | 6.18 | 7.29 | 38% | 12% | +36.0% |
| da2-metric-small_p25 / night | 94 | 100% | 3.00 | 4.44 | 23% | 29% | +5.7% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median | 1797 | 100% | 5.88 | 9.03 | 32% | 17% | +16.1% |
| da2-metric-small_p10 | 1797 | 100% | 4.92 | 8.42 | 27% | 22% | +8.4% |
| da2-metric-small_p25 | 1797 | 100% | 5.27 | 8.63 | 29% | 20% | +11.6% |

### `da2-metric-small_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.78 | 5.14 | 75% | 0% | +75.1% |
| 10-20 m | 97 | 100% | 5.34 | 6.40 | 39% | 12% | +35.1% |
| 20-30 m | 81 | 100% | 4.44 | 6.08 | 26% | 21% | +18.8% |
| 30-50 m | 31 | 100% | 9.75 | 11.82 | 31% | 13% | +21.1% |
| 50+ m | 53 | 100% | 8.56 | 9.78 | 16% | 38% | +7.4% |

### `da2-metric-small_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.61 | 8.56 | 27% | 18% | +10.8% |
| pedestrian | 327 | 100% | 7.27 | 8.65 | 50% | 8% | +40.6% |
| truck | 134 | 100% | 4.40 | 6.21 | 21% | 31% | +14.9% |
| bus | 110 | 100% | 8.93 | 19.13 | 37% | 20% | -5.1% |
| parked two-wheeler | 24 | 100% | 10.16 | 9.68 | 54% | 8% | +52.2% |
| cyclist | 15 | 100% | 1.74 | 4.85 | 21% | 67% | +5.4% |

### `da2-metric-small_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.00 | 3.97 | 58% | 0% | +58.1% |
| 10-20 m | 97 | 100% | 4.94 | 5.67 | 34% | 12% | +28.2% |
| 20-30 m | 81 | 100% | 3.93 | 4.77 | 20% | 33% | +9.6% |
| 30-50 m | 31 | 100% | 7.34 | 8.27 | 21% | 19% | +10.9% |
| 50+ m | 53 | 100% | 9.69 | 9.36 | 15% | 36% | +3.5% |

### `da2-metric-small_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 4.73 | 8.17 | 24% | 24% | +4.7% |
| pedestrian | 327 | 100% | 5.47 | 6.97 | 40% | 13% | +27.9% |
| truck | 134 | 100% | 3.75 | 5.79 | 17% | 34% | +7.2% |
| bus | 110 | 100% | 8.02 | 19.37 | 35% | 23% | -13.6% |
| parked two-wheeler | 24 | 100% | 8.13 | 7.88 | 45% | 0% | +40.7% |
| cyclist | 15 | 100% | 2.26 | 4.59 | 20% | 53% | +1.2% |

### `da2-metric-small_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 4.20 | 4.39 | 64% | 0% | +64.1% |
| 10-20 m | 97 | 100% | 5.07 | 5.98 | 36% | 12% | +31.4% |
| 20-30 m | 81 | 100% | 4.07 | 5.19 | 22% | 26% | +13.7% |
| 30-50 m | 31 | 100% | 7.81 | 10.01 | 26% | 16% | +15.9% |
| 50+ m | 53 | 100% | 8.78 | 9.47 | 15% | 32% | +5.3% |

### `da2-metric-small_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 5.08 | 8.28 | 25% | 21% | +7.2% |
| pedestrian | 327 | 100% | 6.22 | 7.63 | 44% | 11% | +33.2% |
| truck | 134 | 100% | 3.78 | 5.80 | 18% | 32% | +10.2% |
| bus | 110 | 100% | 8.46 | 19.22 | 36% | 20% | -9.6% |
| parked two-wheeler | 24 | 100% | 9.50 | 8.87 | 49% | 4% | +46.6% |
| cyclist | 15 | 100% | 2.12 | 4.72 | 21% | 53% | +3.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median | 321 | 100% | 4.70 | 6.15 | 28% | 26% | +20.0% |
| da2-metric-small_p10 | 321 | 100% | 4.05 | 5.19 | 22% | 33% | +11.6% |
| da2-metric-small_p25 | 321 | 100% | 4.29 | 5.56 | 24% | 30% | +15.2% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median / day | 227 | 100% | 5.56 | 6.95 | 32% | 21% | +30.5% |
| da2-metric-small_median / night | 94 | 100% | 2.39 | 4.24 | 17% | 39% | -5.5% |
| da2-metric-small_p10 / day | 227 | 100% | 4.29 | 5.43 | 24% | 30% | +20.7% |
| da2-metric-small_p10 / night | 94 | 100% | 3.02 | 4.63 | 18% | 39% | -10.5% |
| da2-metric-small_p25 / day | 227 | 100% | 4.93 | 6.04 | 27% | 26% | +24.9% |
| da2-metric-small_p25 / night | 94 | 100% | 2.62 | 4.40 | 17% | 40% | -8.3% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median | 1797 | 100% | 4.69 | 8.43 | 25% | 32% | +6.5% |
| da2-metric-small_p10 | 1797 | 100% | 4.05 | 8.15 | 22% | 39% | -0.5% |
| da2-metric-small_p25 | 1797 | 100% | 4.26 | 8.19 | 23% | 36% | +2.5% |

### `da2-metric-small_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 4.74 | 3.91 | 52% | 15% | +51.8% |
| 10-20 m | 82 | 100% | 3.52 | 5.39 | 32% | 12% | +25.9% |
| 20-30 m | 90 | 100% | 3.95 | 4.91 | 21% | 36% | +8.6% |
| 30-50 m | 44 | 100% | 5.61 | 9.05 | 24% | 36% | +14.2% |
| 50+ m | 53 | 100% | 9.75 | 9.25 | 14% | 36% | +3.8% |

### `da2-metric-small_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 4.10 | 7.75 | 19% | 36% | +0.3% |
| pedestrian | 327 | 100% | 7.06 | 8.37 | 46% | 9% | +36.3% |
| truck | 134 | 100% | 2.79 | 5.48 | 13% | 51% | +2.3% |
| bus | 110 | 100% | 7.37 | 19.89 | 30% | 35% | -18.3% |
| parked two-wheeler | 24 | 100% | 9.25 | 9.07 | 48% | 8% | +45.0% |
| cyclist | 15 | 100% | 2.00 | 4.54 | 20% | 53% | +2.9% |

### `da2-metric-small_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 3.79 | 2.74 | 37% | 37% | +35.4% |
| 10-20 m | 82 | 100% | 2.80 | 4.61 | 27% | 20% | +19.8% |
| 20-30 m | 90 | 100% | 3.77 | 4.32 | 18% | 36% | +1.1% |
| 30-50 m | 44 | 100% | 4.29 | 6.41 | 17% | 43% | +3.6% |
| 50+ m | 53 | 100% | 9.44 | 8.98 | 13% | 36% | -0.0% |

### `da2-metric-small_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.55 | 7.70 | 18% | 44% | -5.2% |
| pedestrian | 327 | 100% | 5.12 | 6.72 | 36% | 15% | +24.0% |
| truck | 134 | 100% | 2.60 | 5.73 | 13% | 52% | -4.3% |
| bus | 110 | 100% | 9.09 | 20.92 | 32% | 35% | -25.4% |
| parked two-wheeler | 24 | 100% | 7.45 | 7.27 | 39% | 8% | +33.9% |
| cyclist | 15 | 100% | 2.38 | 4.46 | 19% | 53% | -1.2% |

### `da2-metric-small_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 4.10 | 3.16 | 42% | 31% | +41.4% |
| 10-20 m | 82 | 100% | 2.95 | 4.96 | 29% | 16% | +22.4% |
| 20-30 m | 90 | 100% | 3.96 | 4.46 | 19% | 37% | +4.3% |
| 30-50 m | 44 | 100% | 4.89 | 7.60 | 20% | 39% | +9.1% |
| 50+ m | 53 | 100% | 9.52 | 9.02 | 14% | 34% | +1.8% |

### `da2-metric-small_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.73 | 7.64 | 18% | 42% | -2.9% |
| pedestrian | 327 | 100% | 5.87 | 7.37 | 40% | 12% | +29.1% |
| truck | 134 | 100% | 2.62 | 5.44 | 12% | 52% | -1.7% |
| bus | 110 | 100% | 8.64 | 20.40 | 31% | 35% | -22.0% |
| parked two-wheeler | 24 | 100% | 8.61 | 8.26 | 44% | 4% | +39.6% |
| cyclist | 15 | 100% | 2.38 | 4.46 | 20% | 53% | +0.9% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
