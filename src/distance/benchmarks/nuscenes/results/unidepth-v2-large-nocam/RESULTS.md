# nuScenes distance benchmark: `unidepth-v2-large-nocam`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large-nocam_median`, `unidepth-v2-large-nocam_p10`, `unidepth-v2-large-nocam_p25` |
| Depth model | `unidepth-v2-large-nocam`, not given our focal length; inference 212.7 ms median, 237.9 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 404 (116 at night) |
| Objects | 1797 matched to a detection of 3918 labelled (visibility at least v40-60); 321 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `afa2151` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:56:29+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median | 321 | 100% | 1.86 | 3.02 | 12% | 47% | +10.7% |
| unidepth-v2-large-nocam_p10 | 321 | 100% | 1.28 | 2.29 | 9% | 64% | +6.7% |
| unidepth-v2-large-nocam_p25 | 321 | 100% | 1.49 | 2.44 | 9% | 60% | +8.1% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median / day | 227 | 100% | 1.79 | 3.22 | 11% | 53% | +10.2% |
| unidepth-v2-large-nocam_median / night | 94 | 100% | 2.12 | 2.54 | 14% | 32% | +11.8% |
| unidepth-v2-large-nocam_p10 / day | 227 | 100% | 1.21 | 2.35 | 8% | 71% | +6.1% |
| unidepth-v2-large-nocam_p10 / night | 94 | 100% | 1.89 | 2.14 | 11% | 47% | +8.3% |
| unidepth-v2-large-nocam_p25 / day | 227 | 100% | 1.40 | 2.53 | 8% | 67% | +7.5% |
| unidepth-v2-large-nocam_p25 / night | 94 | 100% | 1.90 | 2.22 | 12% | 43% | +9.5% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median | 1797 | 100% | 1.66 | 3.26 | 9% | 66% | +4.9% |
| unidepth-v2-large-nocam_p10 | 1797 | 100% | 1.28 | 3.00 | 8% | 72% | -0.2% |
| unidepth-v2-large-nocam_p25 | 1797 | 100% | 1.27 | 2.92 | 8% | 73% | +1.7% |

### `unidepth-v2-large-nocam_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.96 | 1.00 | 14% | 19% | +14.3% |
| 10-20 m | 97 | 100% | 1.41 | 1.54 | 10% | 53% | +8.0% |
| 20-30 m | 81 | 100% | 2.35 | 2.56 | 11% | 49% | +10.3% |
| 30-50 m | 31 | 100% | 3.68 | 5.55 | 14% | 55% | +13.6% |
| 50+ m | 53 | 100% | 5.32 | 7.21 | 11% | 58% | +10.5% |

### `unidepth-v2-large-nocam_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.84 | 3.43 | 9% | 66% | +5.3% |
| pedestrian | 327 | 100% | 0.97 | 1.86 | 8% | 68% | +4.3% |
| truck | 134 | 100% | 1.72 | 3.28 | 8% | 69% | +5.9% |
| bus | 110 | 100% | 2.76 | 5.73 | 11% | 57% | -1.9% |
| parked two-wheeler | 24 | 100% | 1.78 | 1.96 | 11% | 58% | +10.9% |
| cyclist | 15 | 100% | 0.80 | 4.73 | 12% | 60% | +11.6% |

### `unidepth-v2-large-nocam_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.70 | 0.69 | 10% | 41% | +9.9% |
| 10-20 m | 97 | 100% | 1.01 | 1.23 | 7% | 73% | +4.5% |
| 20-30 m | 81 | 100% | 1.87 | 2.33 | 10% | 63% | +6.7% |
| 30-50 m | 31 | 100% | 2.36 | 3.31 | 8% | 71% | +7.8% |
| 50+ m | 53 | 100% | 4.33 | 5.35 | 8% | 70% | +6.6% |

### `unidepth-v2-large-nocam_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.38 | 3.06 | 8% | 72% | +0.3% |
| pedestrian | 327 | 100% | 0.94 | 1.70 | 8% | 74% | +0.2% |
| truck | 134 | 100% | 1.39 | 2.76 | 7% | 78% | -0.4% |
| bus | 110 | 100% | 3.11 | 7.01 | 14% | 61% | -8.6% |
| parked two-wheeler | 24 | 100% | 1.25 | 1.39 | 7% | 75% | +5.5% |
| cyclist | 15 | 100% | 0.64 | 2.82 | 8% | 60% | +6.7% |

### `unidepth-v2-large-nocam_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 59 | 100% | 0.77 | 0.79 | 11% | 29% | +11.3% |
| 10-20 m | 97 | 100% | 1.16 | 1.29 | 8% | 72% | +5.9% |
| 20-30 m | 81 | 100% | 1.96 | 2.27 | 10% | 60% | +8.2% |
| 30-50 m | 31 | 100% | 2.58 | 3.82 | 10% | 68% | +9.2% |
| 50+ m | 53 | 100% | 4.63 | 5.82 | 9% | 64% | +7.9% |

### `unidepth-v2-large-nocam_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.40 | 3.02 | 8% | 73% | +2.1% |
| pedestrian | 327 | 100% | 0.96 | 1.60 | 7% | 73% | +1.9% |
| truck | 134 | 100% | 1.37 | 2.73 | 7% | 76% | +2.2% |
| bus | 110 | 100% | 3.03 | 6.14 | 12% | 65% | -5.6% |
| parked two-wheeler | 24 | 100% | 1.45 | 1.60 | 8% | 75% | +7.2% |
| cyclist | 15 | 100% | 0.51 | 3.66 | 10% | 60% | +8.8% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median | 321 | 100% | 1.18 | 2.26 | 8% | 72% | +0.5% |
| unidepth-v2-large-nocam_p10 | 321 | 100% | 1.41 | 2.12 | 9% | 70% | -3.1% |
| unidepth-v2-large-nocam_p25 | 321 | 100% | 1.28 | 2.06 | 8% | 73% | -1.8% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median / day | 227 | 100% | 0.99 | 2.45 | 8% | 76% | +1.5% |
| unidepth-v2-large-nocam_median / night | 94 | 100% | 1.37 | 1.83 | 9% | 62% | -2.0% |
| unidepth-v2-large-nocam_p10 / day | 227 | 100% | 1.22 | 2.21 | 8% | 73% | -2.3% |
| unidepth-v2-large-nocam_p10 / night | 94 | 100% | 1.64 | 1.90 | 10% | 62% | -5.0% |
| unidepth-v2-large-nocam_p25 / day | 227 | 100% | 1.11 | 2.15 | 8% | 77% | -1.0% |
| unidepth-v2-large-nocam_p25 / night | 94 | 100% | 1.57 | 1.84 | 10% | 62% | -4.0% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median | 1797 | 100% | 1.65 | 3.24 | 9% | 66% | -3.4% |
| unidepth-v2-large-nocam_p10 | 1797 | 100% | 2.25 | 3.78 | 11% | 58% | -8.0% |
| unidepth-v2-large-nocam_p25 | 1797 | 100% | 2.02 | 3.46 | 10% | 61% | -6.3% |

### `unidepth-v2-large-nocam_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.81 | 1.07 | 13% | 48% | -5.3% |
| 10-20 m | 82 | 100% | 0.78 | 0.89 | 5% | 88% | -1.9% |
| 20-30 m | 90 | 100% | 1.48 | 1.76 | 8% | 72% | -0.3% |
| 30-50 m | 44 | 100% | 1.48 | 3.64 | 9% | 70% | +5.9% |
| 50+ m | 53 | 100% | 3.24 | 5.28 | 8% | 72% | +6.7% |

### `unidepth-v2-large-nocam_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 1.68 | 3.17 | 8% | 65% | -3.9% |
| pedestrian | 327 | 100% | 0.96 | 1.80 | 7% | 78% | +1.4% |
| truck | 134 | 100% | 2.42 | 3.31 | 9% | 61% | -5.0% |
| bus | 110 | 100% | 5.09 | 8.44 | 15% | 39% | -14.0% |
| parked two-wheeler | 24 | 100% | 1.15 | 1.32 | 7% | 79% | +5.7% |
| cyclist | 15 | 100% | 0.57 | 4.25 | 10% | 60% | +9.2% |

### `unidepth-v2-large-nocam_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.73 | 1.13 | 14% | 52% | -8.2% |
| 10-20 m | 82 | 100% | 1.09 | 1.22 | 8% | 73% | -5.6% |
| 20-30 m | 90 | 100% | 1.68 | 1.96 | 8% | 69% | -2.9% |
| 30-50 m | 44 | 100% | 1.42 | 2.88 | 8% | 80% | +0.0% |
| 50+ m | 53 | 100% | 3.57 | 4.14 | 6% | 75% | +3.0% |

### `unidepth-v2-large-nocam_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.34 | 3.75 | 11% | 56% | -8.4% |
| pedestrian | 327 | 100% | 1.10 | 1.74 | 8% | 77% | -2.6% |
| truck | 134 | 100% | 3.29 | 4.02 | 13% | 49% | -10.4% |
| bus | 110 | 100% | 6.57 | 10.65 | 20% | 26% | -19.8% |
| parked two-wheeler | 24 | 100% | 0.80 | 1.14 | 6% | 88% | +0.6% |
| cyclist | 15 | 100% | 0.82 | 2.38 | 6% | 67% | +4.4% |

### `unidepth-v2-large-nocam_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 52 | 100% | 0.77 | 1.12 | 14% | 54% | -7.1% |
| 10-20 m | 82 | 100% | 0.96 | 1.05 | 7% | 84% | -4.3% |
| 20-30 m | 90 | 100% | 1.65 | 1.91 | 8% | 70% | -2.2% |
| 30-50 m | 44 | 100% | 1.25 | 2.69 | 7% | 77% | +2.4% |
| 50+ m | 53 | 100% | 2.69 | 4.25 | 6% | 74% | +4.2% |

### `unidepth-v2-large-nocam_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 1187 | 100% | 2.08 | 3.44 | 10% | 59% | -6.9% |
| pedestrian | 327 | 100% | 1.00 | 1.60 | 7% | 78% | -0.9% |
| truck | 134 | 100% | 3.04 | 3.58 | 11% | 51% | -8.1% |
| bus | 110 | 100% | 5.99 | 9.52 | 18% | 32% | -17.2% |
| parked two-wheeler | 24 | 100% | 0.89 | 1.19 | 6% | 88% | +2.2% |
| cyclist | 15 | 100% | 0.77 | 3.21 | 8% | 60% | +6.5% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
