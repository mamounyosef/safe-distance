# nuScenes distance benchmark: `unidepth-v2-base-nocam`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base-nocam_median`, `unidepth-v2-base-nocam_p10`, `unidepth-v2-base-nocam_p25` |
| Depth model | `unidepth-v2-base-nocam`, not given our focal length; inference 109.2 ms median, 111.1 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `afa2151` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:54:29+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 321 | 100% | 2.39 | 3.37 | 13% | 36% | +12.3% |
| unidepth-v2-base-nocam_p10 | 321 | 100% | 1.80 | 2.54 | 10% | 52% | +8.4% |
| unidepth-v2-base-nocam_p25 | 321 | 100% | 1.99 | 2.72 | 11% | 46% | +9.8% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median / day | 227 | 100% | 2.34 | 3.63 | 13% | 38% | +12.5% |
| unidepth-v2-base-nocam_median / night | 94 | 100% | 2.48 | 2.76 | 15% | 30% | +12.0% |
| unidepth-v2-base-nocam_p10 / day | 227 | 100% | 1.59 | 2.60 | 9% | 57% | +8.2% |
| unidepth-v2-base-nocam_p10 / night | 94 | 100% | 2.09 | 2.40 | 13% | 41% | +8.9% |
| unidepth-v2-base-nocam_p25 / day | 227 | 100% | 1.78 | 2.83 | 10% | 49% | +9.7% |
| unidepth-v2-base-nocam_p25 / night | 94 | 100% | 2.16 | 2.47 | 14% | 38% | +10.0% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 1797 | 100% | 2.37 | 3.58 | 11% | 54% | +7.3% |
| unidepth-v2-base-nocam_p10 | 1797 | 100% | 1.70 | 3.20 | 9% | 66% | +2.0% |
| unidepth-v2-base-nocam_p25 | 1797 | 100% | 1.80 | 3.18 | 9% | 64% | +4.0% |

### `unidepth-v2-base-nocam_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.94 | 1.08 | 16% | 14% | +15.7% |
| 10-20 m | 97 | 100% | 2.09 | 2.04 | 13% | 35% | +10.5% |
| 20-30 m | 81 | 100% | 2.62 | 2.97 | 13% | 41% | +11.3% |
| 30-50 m | 31 | 100% | 4.81 | 6.55 | 16% | 35% | +16.4% |
| 50+ m | 53 | 100% | 5.95 | 7.12 | 11% | 55% | +11.2% |

### `unidepth-v2-base-nocam_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.54 | 3.72 | 11% | 53% | +7.5% |
| pedestrian | 327 | 100% | 1.29 | 2.49 | 11% | 58% | +8.5% |
| truck | 134 | 100% | 2.30 | 2.68 | 9% | 62% | +5.9% |
| bus | 110 | 100% | 3.33 | 5.92 | 12% | 54% | -0.8% |
| parked two-wheeler | 24 | 100% | 3.03 | 3.26 | 17% | 12% | +17.3% |
| cyclist | 15 | 100% | 3.91 | 7.05 | 23% | 7% | +23.3% |

### `unidepth-v2-base-nocam_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.80 | 0.78 | 11% | 42% | +11.5% |
| 10-20 m | 97 | 100% | 1.54 | 1.72 | 10% | 48% | +7.0% |
| 20-30 m | 81 | 100% | 2.24 | 2.70 | 12% | 56% | +7.7% |
| 30-50 m | 31 | 100% | 3.44 | 4.39 | 11% | 52% | +11.0% |
| 50+ m | 53 | 100% | 3.37 | 4.66 | 7% | 66% | +6.8% |

### `unidepth-v2-base-nocam_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.77 | 3.16 | 9% | 67% | +2.2% |
| pedestrian | 327 | 100% | 1.17 | 2.04 | 9% | 67% | +4.2% |
| truck | 134 | 100% | 1.73 | 2.64 | 8% | 74% | -0.2% |
| bus | 110 | 100% | 3.73 | 7.78 | 15% | 54% | -8.3% |
| parked two-wheeler | 24 | 100% | 2.33 | 2.51 | 13% | 25% | +11.8% |
| cyclist | 15 | 100% | 3.46 | 4.49 | 17% | 13% | +16.8% |

### `unidepth-v2-base-nocam_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.83 | 0.89 | 13% | 29% | +13.0% |
| 10-20 m | 97 | 100% | 1.67 | 1.80 | 11% | 42% | +8.4% |
| 20-30 m | 81 | 100% | 2.27 | 2.62 | 11% | 53% | +9.1% |
| 30-50 m | 31 | 100% | 3.73 | 5.02 | 13% | 48% | +12.6% |
| 50+ m | 53 | 100% | 4.15 | 5.26 | 8% | 60% | +8.2% |

### `unidepth-v2-base-nocam_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.93 | 3.21 | 9% | 65% | +4.1% |
| pedestrian | 327 | 100% | 1.23 | 2.10 | 9% | 65% | +6.1% |
| truck | 134 | 100% | 1.68 | 2.44 | 7% | 75% | +2.2% |
| bus | 110 | 100% | 3.55 | 6.75 | 13% | 57% | -5.1% |
| parked two-wheeler | 24 | 100% | 2.56 | 2.77 | 14% | 17% | +13.6% |
| cyclist | 15 | 100% | 3.59 | 5.95 | 20% | 7% | +20.2% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 321 | 100% | 1.31 | 2.44 | 9% | 66% | +2.0% |
| unidepth-v2-base-nocam_p10 | 321 | 100% | 1.48 | 2.17 | 9% | 68% | -1.6% |
| unidepth-v2-base-nocam_p25 | 321 | 100% | 1.41 | 2.16 | 9% | 68% | -0.3% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median / day | 227 | 100% | 1.38 | 2.65 | 9% | 68% | +3.6% |
| unidepth-v2-base-nocam_median / night | 94 | 100% | 1.31 | 1.91 | 9% | 61% | -1.9% |
| unidepth-v2-base-nocam_p10 / day | 227 | 100% | 1.49 | 2.27 | 8% | 73% | -0.4% |
| unidepth-v2-base-nocam_p10 / night | 94 | 100% | 1.39 | 1.93 | 10% | 55% | -4.5% |
| unidepth-v2-base-nocam_p25 / day | 227 | 100% | 1.43 | 2.28 | 8% | 73% | +1.1% |
| unidepth-v2-base-nocam_p25 / night | 94 | 100% | 1.37 | 1.87 | 10% | 56% | -3.6% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 1797 | 100% | 1.60 | 3.17 | 9% | 68% | -1.2% |
| unidepth-v2-base-nocam_p10 | 1797 | 100% | 1.99 | 3.62 | 10% | 61% | -6.0% |
| unidepth-v2-base-nocam_p25 | 1797 | 100% | 1.78 | 3.32 | 9% | 65% | -4.2% |

### `unidepth-v2-base-nocam_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.68 | 0.97 | 12% | 50% | -4.2% |
| 10-20 m | 82 | 100% | 0.97 | 1.22 | 7% | 73% | +1.1% |
| 20-30 m | 90 | 100% | 1.33 | 2.01 | 9% | 67% | +0.2% |
| 30-50 m | 44 | 100% | 2.32 | 4.23 | 11% | 66% | +8.0% |
| 50+ m | 53 | 100% | 3.42 | 4.99 | 8% | 70% | +7.4% |

### `unidepth-v2-base-nocam_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.55 | 2.99 | 8% | 71% | -2.0% |
| pedestrian | 327 | 100% | 1.17 | 2.26 | 9% | 70% | +5.5% |
| truck | 134 | 100% | 1.87 | 2.59 | 8% | 70% | -5.1% |
| bus | 110 | 100% | 4.79 | 8.20 | 14% | 43% | -13.2% |
| parked two-wheeler | 24 | 100% | 2.15 | 2.47 | 12% | 42% | +11.9% |
| cyclist | 15 | 100% | 3.67 | 6.44 | 21% | 7% | +20.7% |

### `unidepth-v2-base-nocam_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.57 | 1.03 | 13% | 52% | -7.2% |
| 10-20 m | 82 | 100% | 1.20 | 1.39 | 8% | 77% | -2.5% |
| 20-30 m | 90 | 100% | 1.62 | 2.14 | 9% | 60% | -2.4% |
| 30-50 m | 44 | 100% | 1.54 | 3.28 | 9% | 70% | +2.5% |
| 50+ m | 53 | 100% | 2.87 | 3.63 | 5% | 79% | +3.2% |

### `unidepth-v2-base-nocam_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.99 | 3.40 | 10% | 63% | -6.7% |
| pedestrian | 327 | 100% | 1.11 | 1.91 | 8% | 73% | +1.4% |
| truck | 134 | 100% | 2.93 | 3.91 | 12% | 51% | -10.4% |
| bus | 110 | 100% | 6.80 | 11.16 | 20% | 26% | -19.7% |
| parked two-wheeler | 24 | 100% | 1.60 | 1.90 | 9% | 58% | +6.6% |
| cyclist | 15 | 100% | 3.19 | 3.89 | 14% | 20% | +14.3% |

### `unidepth-v2-base-nocam_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.64 | 1.01 | 12% | 52% | -6.1% |
| 10-20 m | 82 | 100% | 1.19 | 1.27 | 8% | 77% | -1.1% |
| 20-30 m | 90 | 100% | 1.63 | 2.11 | 9% | 62% | -1.7% |
| 30-50 m | 44 | 100% | 1.84 | 3.30 | 9% | 68% | +4.9% |
| 50+ m | 53 | 100% | 2.38 | 3.78 | 6% | 79% | +4.5% |

### `unidepth-v2-base-nocam_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.77 | 3.11 | 9% | 67% | -5.1% |
| pedestrian | 327 | 100% | 1.13 | 1.93 | 8% | 73% | +3.2% |
| truck | 134 | 100% | 2.49 | 3.28 | 10% | 60% | -8.3% |
| bus | 110 | 100% | 5.82 | 9.77 | 17% | 34% | -16.9% |
| parked two-wheeler | 24 | 100% | 1.78 | 2.10 | 10% | 54% | +8.3% |
| cyclist | 15 | 100% | 3.35 | 5.34 | 18% | 7% | +17.6% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
