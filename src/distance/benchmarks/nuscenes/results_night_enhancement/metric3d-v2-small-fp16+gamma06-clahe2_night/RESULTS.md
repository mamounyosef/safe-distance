# nuScenes distance benchmark: `metric3d-v2-small-fp16+gamma06-clahe2_night`

Generated automatically from `results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16+gamma06-clahe2_median`, `metric3d-v2-small-fp16+gamma06-clahe2_p10`, `metric3d-v2-small-fp16+gamma06-clahe2_p25` |
| Depth model | `metric3d-v2-small-fp16+gamma06-clahe2`, given our focal length; inference 111.6 ms median, 128.7 ms p95 per frame |
| Dataset | [nuScenes v1.0-mini](https://www.nuscenes.org/nuscenes), camera CAM_FRONT |
| Frames | 121 (116 at night) |
| Objects | 347 matched to a detection of 782 labelled (visibility at least v40-60); 94 in path |
| Ground truth | LiDAR 3D boxes; ground distance from the road point below the camera |
| Camera | from each frame's calibration |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `12e710c` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T18:31:46+00:00 |

## Metrics

Same as the KITTI distance benchmark: coverage, median / mean absolute error, relative error,
share within 10% of the truth, and bias (negative = too close). In path = footprint within
1.2 m of our car's centre line.

## In path, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06-clahe2_median | 94 | 100% | 1.02 | 1.55 | 9% | 64% | +5.0% |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 | 94 | 100% | 0.98 | 1.55 | 8% | 73% | +1.2% |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 | 94 | 100% | 0.91 | 1.49 | 8% | 69% | +2.8% |

## Day vs night, in path, vs nearest surface

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06-clahe2_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06-clahe2_median / night | 94 | 100% | 1.02 | 1.55 | 9% | 64% | +5.0% |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 / night | 94 | 100% | 0.98 | 1.55 | 8% | 73% | +1.2% |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 / night | 94 | 100% | 0.91 | 1.49 | 8% | 69% | +2.8% |

## All objects, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06-clahe2_median | 347 | 100% | 3.00 | 7.16 | 16% | 39% | -10.4% |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 | 347 | 100% | 4.32 | 8.55 | 19% | 34% | -15.8% |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 | 347 | 100% | 3.68 | 7.82 | 17% | 36% | -13.4% |

### `metric3d-v2-small-fp16+gamma06-clahe2_median` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.83 | 1.18 | 18% | 15% | +17.8% |
| 10-20 m | 30 | 100% | 1.07 | 1.39 | 8% | 67% | +3.9% |
| 20-30 m | 48 | 100% | 1.04 | 1.24 | 6% | 79% | +4.0% |
| 30-50 m | 2 | 100% | 8.69 | 8.69 | 23% | 0% | -23.1% |
| 50+ m | 1 | 100% | 12.13 | 12.13 | 22% | 0% | -22.0% |

### `metric3d-v2-small-fp16+gamma06-clahe2_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.24 | 6.66 | 15% | 46% | -8.1% |
| pedestrian | 57 | 100% | 4.43 | 4.74 | 18% | 18% | -15.2% |
| bus | 25 | 100% | 20.43 | 19.85 | 29% | 4% | -28.9% |
| cyclist | 8 | 100% | 0.63 | 1.06 | 6% | 75% | +5.9% |
| parked two-wheeler | 1 | 100% | 3.31 | 3.31 | 13% | 0% | -13.2% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p10` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.55 | 0.65 | 10% | 38% | +10.3% |
| 10-20 m | 30 | 100% | 0.80 | 1.43 | 8% | 73% | -0.7% |
| 20-30 m | 48 | 100% | 1.07 | 1.24 | 6% | 88% | +1.8% |
| 30-50 m | 2 | 100% | 9.96 | 9.96 | 27% | 0% | -26.5% |
| 50+ m | 1 | 100% | 14.87 | 14.87 | 27% | 0% | -26.9% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.84 | 7.88 | 17% | 40% | -13.6% |
| pedestrian | 57 | 100% | 4.97 | 5.39 | 21% | 9% | -18.8% |
| bus | 25 | 100% | 25.94 | 25.33 | 37% | 4% | -37.4% |
| cyclist | 8 | 100% | 0.29 | 0.55 | 3% | 100% | +2.6% |
| parked two-wheeler | 1 | 100% | 3.67 | 3.67 | 15% | 0% | -14.6% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p25` in path by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 13 | 100% | 0.64 | 0.80 | 12% | 38% | +12.5% |
| 10-20 m | 30 | 100% | 0.87 | 1.34 | 8% | 67% | +1.2% |
| 20-30 m | 48 | 100% | 1.06 | 1.18 | 5% | 83% | +2.8% |
| 30-50 m | 2 | 100% | 9.76 | 9.76 | 26% | 0% | -26.0% |
| 50+ m | 1 | 100% | 12.84 | 12.84 | 23% | 0% | -23.2% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 2.39 | 7.22 | 16% | 42% | -11.1% |
| pedestrian | 57 | 100% | 4.77 | 5.11 | 19% | 14% | -17.4% |
| bus | 25 | 100% | 23.41 | 22.64 | 33% | 4% | -33.2% |
| cyclist | 8 | 100% | 0.54 | 0.78 | 4% | 88% | +4.2% |
| parked two-wheeler | 1 | 100% | 3.47 | 3.47 | 14% | 0% | -13.8% |

## In path, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06-clahe2_median | 94 | 100% | 1.68 | 2.06 | 10% | 55% | -8.2% |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 | 94 | 100% | 2.06 | 2.52 | 12% | 46% | -11.4% |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 | 94 | 100% | 1.92 | 2.28 | 11% | 49% | -10.1% |

## Day vs night, in path, vs centre

| Estimator / condition | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06-clahe2_median / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06-clahe2_median / night | 94 | 100% | 1.68 | 2.06 | 10% | 55% | -8.2% |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 / night | 94 | 100% | 2.06 | 2.52 | 12% | 46% | -11.4% |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 / day | 0 | - | - | - | - | - | - |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 / night | 94 | 100% | 1.92 | 2.28 | 11% | 49% | -10.1% |

## All objects, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16+gamma06-clahe2_median | 347 | 100% | 4.61 | 8.72 | 19% | 29% | -18.1% |
| metric3d-v2-small-fp16+gamma06-clahe2_p10 | 347 | 100% | 5.52 | 10.34 | 23% | 20% | -22.9% |
| metric3d-v2-small-fp16+gamma06-clahe2_p25 | 347 | 100% | 5.10 | 9.55 | 21% | 22% | -20.7% |

### `metric3d-v2-small-fp16+gamma06-clahe2_median` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.59 | 1.51 | 19% | 9% | -18.9% |
| 10-20 m | 20 | 100% | 2.21 | 2.01 | 12% | 40% | -6.2% |
| 20-30 m | 56 | 100% | 1.37 | 1.56 | 7% | 75% | -5.6% |
| 30-50 m | 6 | 100% | 3.29 | 5.85 | 16% | 17% | -16.2% |
| 50+ m | 1 | 100% | 14.71 | 14.71 | 25% | 0% | -25.4% |

### `metric3d-v2-small-fp16+gamma06-clahe2_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 3.66 | 8.12 | 18% | 33% | -17.3% |
| pedestrian | 57 | 100% | 4.92 | 5.08 | 19% | 18% | -17.0% |
| bus | 25 | 100% | 26.51 | 25.91 | 35% | 0% | -35.4% |
| cyclist | 8 | 100% | 0.36 | 0.82 | 5% | 75% | +4.4% |
| parked two-wheeler | 1 | 100% | 3.66 | 3.66 | 14% | 0% | -14.4% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p10` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.74 | 1.80 | 23% | 0% | -22.6% |
| 10-20 m | 20 | 100% | 2.54 | 2.56 | 15% | 40% | -12.6% |
| 20-30 m | 56 | 100% | 1.78 | 1.95 | 8% | 62% | -7.7% |
| 30-50 m | 6 | 100% | 3.67 | 6.55 | 18% | 0% | -18.3% |
| 50+ m | 1 | 100% | 17.45 | 17.45 | 30% | 0% | -30.2% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 5.26 | 9.64 | 23% | 21% | -22.2% |
| pedestrian | 57 | 100% | 5.42 | 5.76 | 22% | 11% | -20.5% |
| bus | 25 | 100% | 32.02 | 31.42 | 43% | 0% | -43.1% |
| cyclist | 8 | 100% | 0.41 | 0.46 | 3% | 100% | +1.2% |
| parked two-wheeler | 1 | 100% | 4.02 | 4.02 | 16% | 0% | -15.8% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p25` in path by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.67 | 1.71 | 21% | 0% | -21.4% |
| 10-20 m | 20 | 100% | 2.30 | 2.20 | 13% | 35% | -10.1% |
| 20-30 m | 56 | 100% | 1.62 | 1.76 | 7% | 70% | -6.8% |
| 30-50 m | 6 | 100% | 3.48 | 6.35 | 18% | 0% | -17.6% |
| 50+ m | 1 | 100% | 15.42 | 15.42 | 27% | 0% | -26.7% |

### `metric3d-v2-small-fp16+gamma06-clahe2_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 256 | 100% | 4.48 | 8.89 | 20% | 24% | -20.0% |
| pedestrian | 57 | 100% | 5.19 | 5.47 | 20% | 11% | -19.1% |
| bus | 25 | 100% | 29.48 | 28.73 | 39% | 0% | -39.3% |
| cyclist | 8 | 100% | 0.37 | 0.65 | 4% | 88% | +2.7% |
| parked two-wheeler | 1 | 100% | 3.82 | 3.82 | 15% | 0% | -15.0% |

## Known limitations

- nuScenes mini has only 10 scenes; frames within a scene are similar, so per-condition
  results (especially night, 3 scenes) are indicative, not statistically conclusive.
- Only objects the detector found are scored; objects under the visibility threshold are skipped.
- The ground truth box footprint is used for nearest surface; its accuracy is that of the labels.
