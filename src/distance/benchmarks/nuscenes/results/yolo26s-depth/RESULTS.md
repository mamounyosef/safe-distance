# nuScenes distance benchmark: `yolo26s-depth`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `yolo26s-depth_median`, `yolo26s-depth_p10`, `yolo26s-depth_p25` |
| Depth model | `yolo26s-depth`, not given our focal length; inference 13.1 ms median, 17.7 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T12:04:59+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 321 | 100% | 6.63 | 11.67 | 33% | 10% | -32.1% |
| yolo26s-depth_p10 | 321 | 100% | 8.14 | 13.02 | 39% | 5% | -38.6% |
| yolo26s-depth_p25 | 321 | 100% | 7.64 | 12.48 | 36% | 7% | -36.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median / day | 227 | 100% | 6.18 | 13.51 | 33% | 11% | -32.3% |
| yolo26s-depth_median / night | 94 | 100% | 7.04 | 7.22 | 34% | 10% | -31.7% |
| yolo26s-depth_p10 / day | 227 | 100% | 7.60 | 14.92 | 38% | 4% | -38.2% |
| yolo26s-depth_p10 / night | 94 | 100% | 8.36 | 8.43 | 39% | 9% | -39.4% |
| yolo26s-depth_p25 / day | 227 | 100% | 6.98 | 14.35 | 36% | 6% | -35.8% |
| yolo26s-depth_p25 / night | 94 | 100% | 7.94 | 7.98 | 37% | 10% | -36.6% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 1797 | 100% | 9.15 | 15.76 | 38% | 8% | -37.0% |
| yolo26s-depth_p10 | 1797 | 100% | 10.78 | 17.20 | 43% | 4% | -42.9% |
| yolo26s-depth_p25 | 1797 | 100% | 10.09 | 16.62 | 41% | 5% | -40.6% |

### `yolo26s-depth_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.69 | 0.96 | 13% | 42% | -10.5% |
| 10-20 m | 97 | 100% | 4.31 | 4.51 | 27% | 7% | -26.1% |
| 20-30 m | 81 | 100% | 7.85 | 8.21 | 35% | 1% | -34.7% |
| 30-50 m | 31 | 100% | 14.28 | 15.10 | 39% | 0% | -38.6% |
| 50+ m | 53 | 100% | 38.27 | 39.97 | 60% | 0% | -59.5% |

### `yolo26s-depth_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 10.26 | 16.79 | 40% | 7% | -38.8% |
| pedestrian | 327 | 100% | 4.41 | 7.19 | 28% | 12% | -27.2% |
| truck | 134 | 100% | 8.97 | 15.62 | 36% | 5% | -35.0% |
| bus | 110 | 100% | 29.76 | 32.77 | 53% | 6% | -49.7% |
| parked two-wheeler | 24 | 100% | 4.42 | 6.13 | 30% | 4% | -30.4% |
| cyclist | 15 | 100% | 10.21 | 13.05 | 47% | 0% | -47.4% |

### `yolo26s-depth_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 1.23 | 1.31 | 18% | 22% | -18.1% |
| 10-20 m | 97 | 100% | 5.43 | 5.48 | 33% | 4% | -32.8% |
| 20-30 m | 81 | 100% | 9.80 | 10.04 | 42% | 0% | -42.3% |
| 30-50 m | 31 | 100% | 16.39 | 17.42 | 45% | 0% | -44.8% |
| 50+ m | 53 | 100% | 40.02 | 41.86 | 62% | 0% | -62.5% |

### `yolo26s-depth_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 12.01 | 18.29 | 45% | 3% | -44.5% |
| pedestrian | 327 | 100% | 5.81 | 8.15 | 33% | 6% | -32.9% |
| truck | 134 | 100% | 11.50 | 17.51 | 42% | 3% | -42.2% |
| bus | 110 | 100% | 33.60 | 34.68 | 57% | 4% | -56.5% |
| parked two-wheeler | 24 | 100% | 5.99 | 6.96 | 35% | 4% | -34.8% |
| cyclist | 15 | 100% | 10.69 | 14.30 | 51% | 0% | -51.3% |

### `yolo26s-depth_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.97 | 1.13 | 16% | 29% | -14.9% |
| 10-20 m | 97 | 100% | 5.08 | 5.08 | 30% | 5% | -30.2% |
| 20-30 m | 81 | 100% | 9.11 | 9.38 | 40% | 0% | -39.6% |
| 30-50 m | 31 | 100% | 15.87 | 16.49 | 42% | 0% | -42.3% |
| 50+ m | 53 | 100% | 39.24 | 41.06 | 61% | 0% | -61.2% |

### `yolo26s-depth_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 11.24 | 17.70 | 43% | 5% | -42.4% |
| pedestrian | 327 | 100% | 5.24 | 7.70 | 31% | 7% | -30.4% |
| truck | 134 | 100% | 9.96 | 16.75 | 40% | 4% | -39.5% |
| bus | 110 | 100% | 32.10 | 33.81 | 55% | 5% | -53.5% |
| parked two-wheeler | 24 | 100% | 5.43 | 6.58 | 33% | 4% | -32.9% |
| cyclist | 15 | 100% | 10.49 | 13.70 | 49% | 0% | -49.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 321 | 100% | 8.85 | 13.52 | 39% | 1% | -39.1% |
| yolo26s-depth_p10 | 321 | 100% | 10.24 | 14.92 | 45% | 1% | -44.9% |
| yolo26s-depth_p25 | 321 | 100% | 9.74 | 14.37 | 43% | 1% | -42.6% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median / day | 227 | 100% | 8.09 | 15.28 | 39% | 1% | -38.3% |
| yolo26s-depth_median / night | 94 | 100% | 9.23 | 9.28 | 41% | 0% | -41.0% |
| yolo26s-depth_p10 / day | 227 | 100% | 9.26 | 16.70 | 44% | 1% | -43.7% |
| yolo26s-depth_p10 / night | 94 | 100% | 10.54 | 10.61 | 48% | 0% | -47.6% |
| yolo26s-depth_p25 / day | 227 | 100% | 8.76 | 16.12 | 42% | 2% | -41.5% |
| yolo26s-depth_p25 / night | 94 | 100% | 10.16 | 10.14 | 45% | 0% | -45.3% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 1797 | 100% | 11.14 | 17.80 | 43% | 2% | -42.6% |
| yolo26s-depth_p10 | 1797 | 100% | 12.81 | 19.29 | 48% | 1% | -47.9% |
| yolo26s-depth_p25 | 1797 | 100% | 12.12 | 18.69 | 46% | 1% | -45.9% |

### `yolo26s-depth_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 1.92 | 1.99 | 25% | 0% | -24.9% |
| 10-20 m | 82 | 100% | 5.09 | 5.31 | 32% | 4% | -31.5% |
| 20-30 m | 90 | 100% | 9.74 | 9.87 | 41% | 0% | -40.7% |
| 30-50 m | 44 | 100% | 14.85 | 15.29 | 41% | 0% | -40.7% |
| 50+ m | 53 | 100% | 40.91 | 42.29 | 61% | 0% | -60.9% |

### `yolo26s-depth_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 12.56 | 18.97 | 45% | 1% | -45.1% |
| pedestrian | 327 | 100% | 4.83 | 7.58 | 30% | 9% | -29.3% |
| truck | 134 | 100% | 11.90 | 18.51 | 43% | 1% | -42.5% |
| bus | 110 | 100% | 36.20 | 37.60 | 57% | 0% | -57.5% |
| parked two-wheeler | 24 | 100% | 5.35 | 6.98 | 34% | 0% | -33.9% |
| cyclist | 15 | 100% | 10.48 | 13.66 | 49% | 0% | -48.6% |

### `yolo26s-depth_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 2.42 | 2.50 | 31% | 0% | -31.4% |
| 10-20 m | 82 | 100% | 5.97 | 6.18 | 37% | 4% | -37.4% |
| 20-30 m | 90 | 100% | 11.28 | 11.45 | 47% | 0% | -47.1% |
| 30-50 m | 44 | 100% | 17.70 | 17.74 | 47% | 0% | -47.4% |
| 50+ m | 53 | 100% | 42.66 | 44.18 | 64% | 0% | -63.7% |

### `yolo26s-depth_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 14.24 | 20.51 | 50% | 0% | -50.2% |
| pedestrian | 327 | 100% | 6.30 | 8.56 | 35% | 4% | -34.8% |
| truck | 134 | 100% | 13.82 | 20.46 | 49% | 0% | -48.9% |
| bus | 110 | 100% | 39.12 | 39.72 | 63% | 0% | -63.0% |
| parked two-wheeler | 24 | 100% | 6.89 | 7.80 | 38% | 0% | -38.0% |
| cyclist | 15 | 100% | 10.96 | 14.91 | 52% | 0% | -52.4% |

### `yolo26s-depth_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 2.17 | 2.28 | 29% | 0% | -28.6% |
| 10-20 m | 82 | 100% | 5.59 | 5.81 | 35% | 5% | -35.0% |
| 20-30 m | 90 | 100% | 10.97 | 10.90 | 45% | 0% | -44.9% |
| 30-50 m | 44 | 100% | 16.87 | 16.75 | 45% | 0% | -44.7% |
| 50+ m | 53 | 100% | 41.88 | 43.38 | 63% | 0% | -62.5% |

### `yolo26s-depth_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 13.47 | 19.91 | 48% | 0% | -48.2% |
| pedestrian | 327 | 100% | 5.68 | 8.11 | 33% | 6% | -32.4% |
| truck | 134 | 100% | 13.08 | 19.69 | 46% | 0% | -46.5% |
| bus | 110 | 100% | 38.04 | 38.80 | 61% | 0% | -60.6% |
| parked two-wheeler | 24 | 100% | 6.35 | 7.43 | 36% | 0% | -36.1% |
| cyclist | 15 | 100% | 10.76 | 14.31 | 51% | 0% | -50.6% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
