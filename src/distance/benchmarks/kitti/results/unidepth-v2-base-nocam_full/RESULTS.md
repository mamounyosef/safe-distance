# KITTI distance benchmark: `unidepth-v2-base-nocam_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base-nocam_median`, `unidepth-v2-base-nocam_p10`, `unidepth-v2-base-nocam_p25` |
| Depth model | `unidepth-v2-base-nocam`, not given our focal length; inference 107.2 ms median, 113.8 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `afa2151` |
| Created (UTC) | 2026-09-29T15:36:13+00:00 |

## Metrics

- **Nearest surface**: true distance to the closest point of the object's footprint on the road
  (e.g. the rear bumper of the car ahead). The gap that matters for braking.
- **Centre**: true distance to the middle of the object, as KITTI records it.
- **Coverage**: share of objects the estimator answered for, rather than returning unknown.
- **Median / mean error**: absolute distance error in metres (mean = MAE, Mean Absolute Error).
- **Relative error**: average absolute error as a percentage of the true distance.
- **Within 10%**: share of answers within 10% of the true distance.
- **Bias**: average signed error; negative = estimates too close, positive = too far.
  Bias is systematic and correctable; the spread around it is not.

## Overall, vs nearest surface

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 6484 | 100% | 1.76 | 2.70 | 11% | 56% | +7.1% |
| unidepth-v2-base-nocam_p10 | 6484 | 100% | 1.45 | 2.42 | 9% | 65% | +1.0% |
| unidepth-v2-base-nocam_p25 | 6484 | 100% | 1.50 | 2.39 | 10% | 63% | +3.1% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 6484 | 100% | 1.69 | 2.55 | 10% | 60% | -3.7% |
| unidepth-v2-base-nocam_p10 | 6484 | 100% | 2.09 | 2.93 | 12% | 52% | -9.0% |
| unidepth-v2-base-nocam_p25 | 6484 | 100% | 1.93 | 2.69 | 11% | 56% | -7.1% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-base-nocam_median | 1020 | 100% | 2.61 | 3.35 | 12% | 47% | +11.7% |
| in path / unidepth-v2-base-nocam_p10 | 1020 | 100% | 1.92 | 2.54 | 9% | 64% | +8.1% |
| in path / unidepth-v2-base-nocam_p25 | 1020 | 100% | 2.11 | 2.76 | 10% | 59% | +9.3% |
| beside / unidepth-v2-base-nocam_median | 5464 | 100% | 1.57 | 2.58 | 11% | 58% | +6.2% |
| beside / unidepth-v2-base-nocam_p10 | 5464 | 100% | 1.36 | 2.40 | 9% | 65% | -0.4% |
| beside / unidepth-v2-base-nocam_p25 | 5464 | 100% | 1.36 | 2.32 | 9% | 64% | +2.0% |

### `unidepth-v2-base-nocam_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 1.03 | 1.00 | 14% | 33% | +13.6% |
| 10-20 m | 183 | 100% | 1.70 | 2.02 | 13% | 38% | +13.2% |
| 20-30 m | 279 | 100% | 2.96 | 3.35 | 14% | 39% | +13.7% |
| 30-50 m | 335 | 100% | 3.40 | 3.93 | 10% | 57% | +10.0% |
| 50+ m | 125 | 100% | 4.96 | 5.53 | 9% | 61% | +7.7% |

### `unidepth-v2-base-nocam_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.74 | 0.80 | 11% | 50% | +10.4% |
| 10-20 m | 183 | 100% | 1.13 | 1.42 | 9% | 64% | +9.1% |
| 20-30 m | 279 | 100% | 2.26 | 2.53 | 10% | 54% | +10.3% |
| 30-50 m | 335 | 100% | 2.58 | 2.94 | 8% | 75% | +6.5% |
| 50+ m | 125 | 100% | 3.68 | 4.47 | 7% | 70% | +4.5% |

### `unidepth-v2-base-nocam_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.87 | 0.87 | 12% | 43% | +11.5% |
| 10-20 m | 183 | 100% | 1.25 | 1.59 | 10% | 54% | +10.3% |
| 20-30 m | 279 | 100% | 2.44 | 2.77 | 11% | 51% | +11.3% |
| 30-50 m | 335 | 100% | 2.76 | 3.21 | 8% | 70% | +7.8% |
| 50+ m | 125 | 100% | 4.29 | 4.73 | 8% | 67% | +5.6% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-base-nocam_median | 1020 | 100% | 1.39 | 2.21 | 7% | 77% | +3.6% |
| in path / unidepth-v2-base-nocam_p10 | 1020 | 100% | 1.27 | 1.91 | 6% | 79% | +0.3% |
| in path / unidepth-v2-base-nocam_p25 | 1020 | 100% | 1.30 | 1.93 | 7% | 80% | +1.4% |
| beside / unidepth-v2-base-nocam_median | 5464 | 100% | 1.74 | 2.61 | 11% | 57% | -5.1% |
| beside / unidepth-v2-base-nocam_p10 | 5464 | 100% | 2.23 | 3.13 | 14% | 47% | -10.7% |
| beside / unidepth-v2-base-nocam_p25 | 5464 | 100% | 2.06 | 2.83 | 12% | 51% | -8.7% |

### `unidepth-v2-base-nocam_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.95 | 0.99 | 12% | 38% | -0.0% |
| 10-20 m | 160 | 100% | 0.79 | 1.07 | 7% | 78% | +1.4% |
| 20-30 m | 278 | 100% | 1.22 | 1.83 | 7% | 78% | +5.7% |
| 30-50 m | 348 | 100% | 1.78 | 2.47 | 6% | 85% | +4.1% |
| 50+ m | 149 | 100% | 3.86 | 4.24 | 7% | 81% | +2.9% |

### `unidepth-v2-base-nocam_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.97 | 1.02 | 13% | 41% | -2.5% |
| 10-20 m | 160 | 100% | 0.98 | 1.11 | 7% | 72% | -2.2% |
| 20-30 m | 278 | 100% | 1.04 | 1.42 | 6% | 83% | +2.5% |
| 30-50 m | 348 | 100% | 1.59 | 2.11 | 5% | 85% | +0.7% |
| 50+ m | 149 | 100% | 3.22 | 3.73 | 6% | 86% | -0.2% |

### `unidepth-v2-base-nocam_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.00 | 1.02 | 13% | 35% | -1.7% |
| 10-20 m | 160 | 100% | 0.95 | 1.10 | 7% | 76% | -1.1% |
| 20-30 m | 278 | 100% | 1.02 | 1.50 | 6% | 83% | +3.4% |
| 30-50 m | 348 | 100% | 1.51 | 2.09 | 5% | 87% | +2.0% |
| 50+ m | 149 | 100% | 3.31 | 3.81 | 6% | 86% | +0.8% |

## `unidepth-v2-base-nocam_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.64 | 0.75 | 15% | 53% | +11.7% |
| 10-20 m | 1589 | 100% | 1.27 | 1.58 | 10% | 56% | +6.1% |
| 20-30 m | 1382 | 100% | 2.30 | 2.78 | 11% | 53% | +7.5% |
| 30-50 m | 1705 | 100% | 3.23 | 3.87 | 10% | 58% | +5.7% |
| 50+ m | 691 | 100% | 4.05 | 5.37 | 9% | 65% | +4.3% |

## `unidepth-v2-base-nocam_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.74 | 2.54 | 10% | 59% | +6.2% |
| pedestrian | 590 | 100% | 1.26 | 2.34 | 14% | 48% | +11.0% |
| van | 432 | 100% | 2.42 | 3.53 | 13% | 53% | +7.0% |
| truck | 187 | 100% | 2.72 | 4.11 | 14% | 52% | +10.4% |
| cyclist | 152 | 100% | 3.30 | 5.11 | 19% | 26% | +17.5% |

## `unidepth-v2-base-nocam_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.46 | 0.61 | 11% | 61% | +1.9% |
| 10-20 m | 1589 | 100% | 1.01 | 1.33 | 9% | 65% | +0.7% |
| 20-30 m | 1382 | 100% | 1.90 | 2.36 | 10% | 62% | +2.0% |
| 30-50 m | 1705 | 100% | 2.68 | 3.53 | 9% | 68% | +0.4% |
| 50+ m | 691 | 100% | 4.09 | 5.28 | 9% | 68% | -0.7% |

## `unidepth-v2-base-nocam_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.44 | 2.36 | 9% | 67% | +0.0% |
| pedestrian | 590 | 100% | 1.00 | 1.75 | 11% | 57% | +6.6% |
| van | 432 | 100% | 1.78 | 3.22 | 11% | 60% | +0.5% |
| truck | 187 | 100% | 2.32 | 3.89 | 12% | 56% | +4.2% |
| cyclist | 152 | 100% | 2.17 | 3.11 | 12% | 49% | +8.5% |

## `unidepth-v2-base-nocam_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.47 | 0.61 | 11% | 62% | +5.1% |
| 10-20 m | 1589 | 100% | 1.06 | 1.36 | 9% | 63% | +2.5% |
| 20-30 m | 1382 | 100% | 1.98 | 2.37 | 10% | 59% | +4.0% |
| 30-50 m | 1705 | 100% | 2.78 | 3.49 | 9% | 66% | +2.5% |
| 50+ m | 691 | 100% | 3.79 | 4.93 | 8% | 69% | +1.5% |

## `unidepth-v2-base-nocam_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.47 | 2.28 | 9% | 66% | +2.2% |
| pedestrian | 590 | 100% | 1.11 | 1.91 | 12% | 53% | +8.3% |
| van | 432 | 100% | 2.00 | 3.24 | 11% | 59% | +2.9% |
| truck | 187 | 100% | 2.46 | 3.79 | 12% | 58% | +6.5% |
| cyclist | 152 | 100% | 2.45 | 3.67 | 14% | 39% | +11.9% |

## `unidepth-v2-base-nocam_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.26 | 1.31 | 18% | 23% | -15.2% |
| 10-20 m | 1594 | 100% | 1.36 | 1.62 | 11% | 52% | -7.1% |
| 20-30 m | 1422 | 100% | 1.50 | 2.15 | 9% | 70% | -0.5% |
| 30-50 m | 1838 | 100% | 2.28 | 3.19 | 8% | 71% | +0.4% |
| 50+ m | 782 | 100% | 4.13 | 4.99 | 8% | 71% | +0.1% |

## `unidepth-v2-base-nocam_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.68 | 2.39 | 10% | 61% | -5.1% |
| pedestrian | 590 | 100% | 0.94 | 2.09 | 11% | 57% | +6.6% |
| van | 432 | 100% | 2.49 | 3.60 | 12% | 51% | -6.0% |
| truck | 187 | 100% | 3.53 | 4.31 | 11% | 62% | -7.4% |
| cyclist | 152 | 100% | 2.47 | 4.47 | 15% | 45% | +12.3% |

## `unidepth-v2-base-nocam_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.79 | 1.72 | 24% | 18% | -22.3% |
| 10-20 m | 1594 | 100% | 1.86 | 2.07 | 14% | 37% | -12.0% |
| 20-30 m | 1422 | 100% | 1.75 | 2.39 | 10% | 64% | -5.5% |
| 30-50 m | 1838 | 100% | 2.50 | 3.53 | 9% | 67% | -4.8% |
| 50+ m | 782 | 100% | 4.20 | 5.61 | 9% | 66% | -4.6% |

## `unidepth-v2-base-nocam_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.13 | 2.93 | 13% | 51% | -10.4% |
| pedestrian | 590 | 100% | 0.88 | 1.61 | 9% | 62% | +2.3% |
| van | 432 | 100% | 2.89 | 4.01 | 15% | 43% | -11.3% |
| truck | 187 | 100% | 3.95 | 5.05 | 13% | 51% | -12.1% |
| cyclist | 152 | 100% | 1.65 | 2.66 | 9% | 70% | +3.6% |

## `unidepth-v2-base-nocam_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.65 | 1.59 | 22% | 19% | -20.0% |
| 10-20 m | 1594 | 100% | 1.71 | 1.92 | 13% | 41% | -10.4% |
| 20-30 m | 1422 | 100% | 1.62 | 2.22 | 9% | 67% | -3.8% |
| 30-50 m | 1838 | 100% | 2.32 | 3.22 | 8% | 70% | -2.7% |
| 50+ m | 782 | 100% | 4.01 | 5.02 | 8% | 70% | -2.6% |

## `unidepth-v2-base-nocam_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.96 | 2.62 | 12% | 56% | -8.5% |
| pedestrian | 590 | 100% | 0.89 | 1.72 | 10% | 61% | +3.9% |
| van | 432 | 100% | 2.75 | 3.73 | 14% | 46% | -9.3% |
| truck | 187 | 100% | 3.82 | 4.64 | 12% | 55% | -10.4% |
| cyclist | 152 | 100% | 1.88 | 3.12 | 10% | 59% | +6.9% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-base-nocam_median | 110.091 |
| unidepth-v2-base-nocam_p10 | 2.468 |
| unidepth-v2-base-nocam_p25 | 2.339 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
