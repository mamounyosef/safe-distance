# nuScenes distance benchmark: `geometric`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `ground_plane`, `known_size`, `combined` |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:40:28+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 321 | 91% | 3.19 | 8.15 | 30% | 24% | +29.2% |
| known_size | 321 | 100% | 1.64 | 4.72 | 16% | 52% | +5.1% |
| combined | 321 | 100% | 1.64 | 4.72 | 16% | 52% | +5.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane / day | 227 | 87% | 4.94 | 10.77 | 39% | 13% | +37.2% |
| ground_plane / night | 94 | 100% | 1.83 | 2.64 | 13% | 47% | +12.4% |
| known_size / day | 227 | 100% | 1.71 | 5.77 | 18% | 51% | +5.8% |
| known_size / night | 94 | 100% | 1.10 | 2.18 | 12% | 55% | +3.3% |
| combined / day | 227 | 100% | 1.71 | 5.77 | 18% | 51% | +5.8% |
| combined / night | 94 | 100% | 1.10 | 2.18 | 12% | 55% | +3.3% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 1797 | 91% | 4.96 | 11.61 | 35% | 25% | +28.0% |
| known_size | 1797 | 100% | 2.04 | 4.59 | 14% | 57% | +2.8% |
| combined | 1797 | 100% | 2.04 | 4.59 | 14% | 57% | +2.8% |

### `ground_plane` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.86 | 1.11 | 16% | 25% | +16.2% |
| 10-20 m | 97 | 100% | 3.38 | 4.67 | 28% | 23% | +27.2% |
| 20-30 m | 81 | 98% | 3.05 | 7.25 | 30% | 34% | +28.4% |
| 30-50 m | 31 | 94% | 24.06 | 25.22 | 64% | 3% | +63.4% |
| 50+ m | 53 | 51% | 14.63 | 20.27 | 35% | 15% | +30.3% |

### `ground_plane` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 91% | 4.84 | 11.97 | 34% | 27% | +28.2% |
| pedestrian | 327 | 98% | 4.94 | 9.18 | 36% | 21% | +23.6% |
| truck | 134 | 90% | 7.03 | 12.23 | 36% | 21% | +28.8% |
| bus | 110 | 67% | 8.68 | 16.23 | 44% | 31% | +36.9% |
| parked two-wheeler | 24 | 100% | 3.48 | 10.32 | 45% | 17% | +39.9% |
| cyclist | 15 | 100% | 4.04 | 12.51 | 51% | 13% | +35.2% |

### `known_size` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.54 | 1.43 | 21% | 58% | +18.2% |
| 10-20 m | 97 | 100% | 1.11 | 2.02 | 13% | 64% | +8.1% |
| 20-30 m | 81 | 100% | 2.06 | 2.54 | 10% | 52% | -2.2% |
| 30-50 m | 31 | 100% | 3.00 | 4.57 | 13% | 65% | +5.2% |
| 50+ m | 53 | 100% | 16.01 | 16.73 | 25% | 19% | -4.0% |

### `known_size` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.01 | 4.10 | 13% | 59% | +0.9% |
| pedestrian | 327 | 100% | 1.04 | 1.62 | 8% | 75% | +4.0% |
| truck | 134 | 100% | 9.43 | 11.79 | 38% | 8% | +25.5% |
| bus | 110 | 100% | 4.60 | 10.54 | 18% | 54% | -11.0% |
| parked two-wheeler | 24 | 100% | 2.24 | 2.99 | 15% | 42% | +15.1% |
| cyclist | 15 | 100% | 2.46 | 2.89 | 10% | 53% | +4.4% |

### `combined` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.54 | 1.43 | 21% | 58% | +18.2% |
| 10-20 m | 97 | 100% | 1.11 | 2.02 | 13% | 64% | +8.1% |
| 20-30 m | 81 | 100% | 2.06 | 2.54 | 10% | 52% | -2.2% |
| 30-50 m | 31 | 100% | 3.00 | 4.57 | 13% | 65% | +5.2% |
| 50+ m | 53 | 100% | 16.01 | 16.73 | 25% | 19% | -4.0% |

### `combined` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.01 | 4.10 | 13% | 59% | +0.9% |
| pedestrian | 327 | 100% | 1.04 | 1.62 | 8% | 75% | +4.0% |
| truck | 134 | 100% | 9.43 | 11.79 | 38% | 8% | +25.5% |
| bus | 110 | 100% | 4.60 | 10.54 | 18% | 54% | -11.0% |
| parked two-wheeler | 24 | 100% | 2.24 | 2.99 | 15% | 42% | +15.1% |
| cyclist | 15 | 100% | 2.46 | 2.89 | 10% | 53% | +4.4% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 321 | 91% | 2.03 | 7.09 | 23% | 50% | +16.9% |
| known_size | 321 | 100% | 2.56 | 5.36 | 16% | 44% | -5.1% |
| combined | 321 | 100% | 2.56 | 5.36 | 16% | 44% | -5.1% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane / day | 227 | 87% | 3.74 | 9.52 | 29% | 42% | +25.6% |
| ground_plane / night | 94 | 100% | 1.18 | 2.00 | 10% | 67% | -1.2% |
| known_size / day | 227 | 100% | 2.94 | 6.27 | 16% | 45% | -3.4% |
| known_size / night | 94 | 100% | 2.31 | 3.15 | 16% | 40% | -9.5% |
| combined / day | 227 | 100% | 2.94 | 6.27 | 16% | 45% | -3.4% |
| combined / night | 94 | 100% | 2.31 | 3.15 | 16% | 40% | -9.5% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 1797 | 91% | 4.43 | 10.96 | 30% | 34% | +17.8% |
| known_size | 1797 | 100% | 2.84 | 5.36 | 14% | 48% | -5.6% |
| combined | 1797 | 100% | 2.84 | 5.36 | 14% | 48% | -5.6% |

### `ground_plane` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.51 | 0.78 | 10% | 71% | -3.9% |
| 10-20 m | 82 | 100% | 1.95 | 3.50 | 20% | 44% | +15.6% |
| 20-30 m | 90 | 98% | 1.43 | 3.83 | 16% | 61% | +10.7% |
| 30-50 m | 44 | 95% | 12.44 | 21.38 | 56% | 26% | +52.3% |
| 50+ m | 53 | 51% | 13.16 | 18.57 | 31% | 26% | +26.2% |

### `ground_plane` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 91% | 4.03 | 11.19 | 28% | 36% | +16.8% |
| pedestrian | 327 | 98% | 4.70 | 8.99 | 33% | 31% | +20.3% |
| truck | 134 | 90% | 6.43 | 11.34 | 30% | 32% | +15.5% |
| bus | 110 | 67% | 7.18 | 15.49 | 35% | 22% | +17.5% |
| parked two-wheeler | 24 | 100% | 3.18 | 9.90 | 40% | 29% | +33.7% |
| cyclist | 15 | 100% | 3.93 | 12.69 | 49% | 13% | +31.7% |

### `known_size` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.95 | 1.51 | 18% | 42% | -1.1% |
| 10-20 m | 82 | 100% | 1.29 | 2.08 | 13% | 55% | -2.9% |
| 20-30 m | 90 | 100% | 2.59 | 3.37 | 13% | 46% | -8.6% |
| 30-50 m | 44 | 100% | 3.96 | 4.96 | 14% | 55% | -4.4% |
| 50+ m | 53 | 100% | 18.66 | 17.91 | 26% | 17% | -7.3% |

### `known_size` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.11 | 5.04 | 14% | 45% | -8.3% |
| pedestrian | 327 | 100% | 1.03 | 1.58 | 7% | 76% | +1.1% |
| truck | 134 | 100% | 7.08 | 10.78 | 29% | 25% | +11.9% |
| bus | 110 | 100% | 9.28 | 14.37 | 23% | 22% | -22.1% |
| parked two-wheeler | 24 | 100% | 1.48 | 2.32 | 11% | 54% | +9.7% |
| cyclist | 15 | 100% | 2.52 | 3.07 | 10% | 47% | +2.2% |

### `combined` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.95 | 1.51 | 18% | 42% | -1.1% |
| 10-20 m | 82 | 100% | 1.29 | 2.08 | 13% | 55% | -2.9% |
| 20-30 m | 90 | 100% | 2.59 | 3.37 | 13% | 46% | -8.6% |
| 30-50 m | 44 | 100% | 3.96 | 4.96 | 14% | 55% | -4.4% |
| 50+ m | 53 | 100% | 18.66 | 17.91 | 26% | 17% | -7.3% |

### `combined` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 3.11 | 5.04 | 14% | 45% | -8.3% |
| pedestrian | 327 | 100% | 1.03 | 1.58 | 7% | 76% | +1.1% |
| truck | 134 | 100% | 7.08 | 10.78 | 29% | 25% | +11.9% |
| bus | 110 | 100% | 9.28 | 14.37 | 23% | 22% | -22.1% |
| parked two-wheeler | 24 | 100% | 1.48 | 2.32 | 11% | 54% | +9.7% |
| cyclist | 15 | 100% | 2.52 | 3.07 | 10% | 47% | +2.2% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
