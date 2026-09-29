# nuScenes distance benchmark: `geometric`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `ground_plane`, `known_size`, `combined` |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (17 at night) |
| Objects | 838 matched to a detection of 838 labelled (visibility at least v40-60); 104 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T14:00:41+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 104 | 100% | 5.00 | 10.99 | 36% | 29% | +35.7% |
| known_size | 104 | 0% | - | - | - | - | - |
| combined | 104 | 100% | 5.00 | 10.99 | 36% | 29% | +35.7% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane / day | 104 | 100% | 5.00 | 10.99 | 36% | 29% | +35.7% |
| ground_plane / night | 0 | - | - | - | - | - | - |
| known_size / day | 104 | 0% | - | - | - | - | - |
| known_size / night | 0 | - | - | - | - | - | - |
| combined / day | 104 | 100% | 5.00 | 10.99 | 36% | 29% | +35.7% |
| combined / night | 0 | - | - | - | - | - | - |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 838 | 96% | 2.73 | 8.68 | 24% | 47% | +15.6% |
| known_size | 838 | 0% | - | - | - | - | - |
| combined | 838 | 96% | 2.73 | 8.68 | 24% | 47% | +15.6% |

### `ground_plane` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.34 | 0.44 | 5% | 85% | +5.3% |
| 10-20 m | 32 | 100% | 1.37 | 1.77 | 12% | 53% | +11.2% |
| 20-30 m | 25 | 100% | 7.94 | 12.32 | 51% | 8% | +50.9% |
| 30-50 m | 30 | 100% | 21.29 | 22.76 | 62% | 0% | +62.0% |
| 50+ m | 4 | 100% | 21.44 | 22.36 | 39% | 0% | +38.6% |

### `ground_plane` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 94% | 2.08 | 6.24 | 20% | 54% | +16.1% |
| barrier | 369 | 99% | 7.35 | 11.63 | 29% | 39% | +14.8% |

### `known_size` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 0% | - | - | - | - | - |
| 10-20 m | 32 | 0% | - | - | - | - | - |
| 20-30 m | 25 | 0% | - | - | - | - | - |
| 30-50 m | 30 | 0% | - | - | - | - | - |
| 50+ m | 4 | 0% | - | - | - | - | - |

### `known_size` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 0% | - | - | - | - | - |
| barrier | 369 | 0% | - | - | - | - | - |

### `combined` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.34 | 0.44 | 5% | 85% | +5.3% |
| 10-20 m | 32 | 100% | 1.37 | 1.77 | 12% | 53% | +11.2% |
| 20-30 m | 25 | 100% | 7.94 | 12.32 | 51% | 8% | +50.9% |
| 30-50 m | 30 | 100% | 21.29 | 22.76 | 62% | 0% | +62.0% |
| 50+ m | 4 | 100% | 21.44 | 22.36 | 39% | 0% | +38.6% |

### `combined` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 94% | 2.08 | 6.24 | 20% | 54% | +16.1% |
| barrier | 369 | 99% | 7.35 | 11.63 | 29% | 39% | +14.8% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 104 | 100% | 4.51 | 10.63 | 33% | 38% | +32.7% |
| known_size | 104 | 0% | - | - | - | - | - |
| combined | 104 | 100% | 4.51 | 10.63 | 33% | 38% | +32.7% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane / day | 104 | 100% | 4.51 | 10.63 | 33% | 38% | +32.7% |
| ground_plane / night | 0 | - | - | - | - | - | - |
| known_size / day | 104 | 0% | - | - | - | - | - |
| known_size / night | 0 | - | - | - | - | - | - |
| combined / day | 104 | 100% | 4.51 | 10.63 | 33% | 38% | +32.7% |
| combined / night | 0 | - | - | - | - | - | - |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 838 | 96% | 3.58 | 8.85 | 24% | 49% | +13.2% |
| known_size | 838 | 0% | - | - | - | - | - |
| combined | 838 | 96% | 3.58 | 8.85 | 24% | 49% | +13.2% |

### `ground_plane` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.12 | 0.17 | 2% | 100% | -0.9% |
| 10-20 m | 34 | 100% | 0.81 | 1.31 | 8% | 79% | +7.3% |
| 20-30 m | 26 | 100% | 7.20 | 11.52 | 47% | 12% | +46.3% |
| 30-50 m | 30 | 100% | 21.04 | 22.40 | 60% | 0% | +60.2% |
| 50+ m | 4 | 100% | 21.16 | 22.08 | 38% | 0% | +37.9% |

### `ground_plane` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 94% | 2.06 | 6.14 | 20% | 56% | +14.7% |
| barrier | 369 | 99% | 6.75 | 12.13 | 28% | 40% | +11.3% |

### `known_size` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 0% | - | - | - | - | - |
| 10-20 m | 34 | 0% | - | - | - | - | - |
| 20-30 m | 26 | 0% | - | - | - | - | - |
| 30-50 m | 30 | 0% | - | - | - | - | - |
| 50+ m | 4 | 0% | - | - | - | - | - |

### `known_size` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 0% | - | - | - | - | - |
| barrier | 369 | 0% | - | - | - | - | - |

### `combined` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 10 | 100% | 0.12 | 0.17 | 2% | 100% | -0.9% |
| 10-20 m | 34 | 100% | 0.81 | 1.31 | 8% | 79% | +7.3% |
| 20-30 m | 26 | 100% | 7.20 | 11.52 | 47% | 12% | +46.3% |
| 30-50 m | 30 | 100% | 21.04 | 22.40 | 60% | 0% | +60.2% |
| 50+ m | 4 | 100% | 21.16 | 22.08 | 38% | 0% | +37.9% |

### `combined` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traffic cone | 469 | 94% | 2.06 | 6.14 | 20% | 56% | +14.7% |
| barrier | 369 | 99% | 6.75 | 12.13 | 28% | 40% | +11.3% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
