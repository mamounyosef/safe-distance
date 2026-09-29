# KITTI distance benchmark: `unidepth-v2-large-nocam_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large-nocam_median`, `unidepth-v2-large-nocam_p10`, `unidepth-v2-large-nocam_p25` |
| Depth model | `unidepth-v2-large-nocam`, not given our focal length; inference 210.2 ms median, 218.1 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `afa2151` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:42:38+00:00 |

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
| unidepth-v2-large-nocam_median | 6484 | 100% | 1.66 | 2.66 | 10% | 61% | +6.9% |
| unidepth-v2-large-nocam_p10 | 6484 | 100% | 1.25 | 2.28 | 9% | 70% | +0.9% |
| unidepth-v2-large-nocam_p25 | 6484 | 100% | 1.30 | 2.27 | 9% | 70% | +3.0% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median | 6484 | 100% | 1.62 | 2.46 | 10% | 61% | -3.8% |
| unidepth-v2-large-nocam_p10 | 6484 | 100% | 2.01 | 2.82 | 12% | 54% | -9.1% |
| unidepth-v2-large-nocam_p25 | 6484 | 100% | 1.85 | 2.57 | 11% | 58% | -7.2% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-large-nocam_median | 1020 | 100% | 2.30 | 3.44 | 11% | 58% | +10.3% |
| in path / unidepth-v2-large-nocam_p10 | 1020 | 100% | 1.60 | 2.43 | 7% | 77% | +6.6% |
| in path / unidepth-v2-large-nocam_p25 | 1020 | 100% | 1.80 | 2.72 | 8% | 72% | +7.8% |
| beside / unidepth-v2-large-nocam_median | 5464 | 100% | 1.55 | 2.52 | 10% | 62% | +6.3% |
| beside / unidepth-v2-large-nocam_p10 | 5464 | 100% | 1.18 | 2.25 | 9% | 69% | -0.2% |
| beside / unidepth-v2-large-nocam_p25 | 5464 | 100% | 1.22 | 2.18 | 9% | 69% | +2.1% |

### `unidepth-v2-large-nocam_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.44 | 0.47 | 6% | 83% | +5.7% |
| 10-20 m | 183 | 100% | 1.19 | 1.43 | 10% | 62% | +9.0% |
| 20-30 m | 279 | 100% | 2.28 | 2.91 | 12% | 56% | +11.6% |
| 30-50 m | 335 | 100% | 3.58 | 4.30 | 11% | 54% | +10.8% |
| 50+ m | 125 | 100% | 6.77 | 7.57 | 12% | 46% | +11.8% |

### `unidepth-v2-large-nocam_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.25 | 0.32 | 4% | 96% | +2.8% |
| 10-20 m | 183 | 100% | 0.77 | 0.94 | 6% | 84% | +5.2% |
| 20-30 m | 279 | 100% | 1.67 | 2.03 | 8% | 77% | +7.8% |
| 30-50 m | 335 | 100% | 2.64 | 3.10 | 8% | 70% | +6.9% |
| 50+ m | 125 | 100% | 4.75 | 5.36 | 9% | 67% | +7.9% |

### `unidepth-v2-large-nocam_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.33 | 0.36 | 5% | 92% | +3.7% |
| 10-20 m | 183 | 100% | 0.86 | 1.09 | 7% | 80% | +6.4% |
| 20-30 m | 279 | 100% | 1.87 | 2.33 | 9% | 72% | +9.2% |
| 30-50 m | 335 | 100% | 2.96 | 3.38 | 8% | 66% | +8.3% |
| 50+ m | 125 | 100% | 5.68 | 6.07 | 10% | 59% | +9.2% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-large-nocam_median | 1020 | 100% | 1.31 | 2.37 | 7% | 78% | +2.4% |
| in path / unidepth-v2-large-nocam_p10 | 1020 | 100% | 1.39 | 1.97 | 7% | 81% | -1.1% |
| in path / unidepth-v2-large-nocam_p25 | 1020 | 100% | 1.36 | 2.02 | 7% | 81% | +0.1% |
| beside / unidepth-v2-large-nocam_median | 5464 | 100% | 1.68 | 2.48 | 11% | 58% | -5.0% |
| beside / unidepth-v2-large-nocam_p10 | 5464 | 100% | 2.14 | 2.98 | 13% | 49% | -10.6% |
| beside / unidepth-v2-large-nocam_p25 | 5464 | 100% | 1.97 | 2.67 | 12% | 53% | -8.5% |

### `unidepth-v2-large-nocam_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.29 | 0.74 | 9% | 59% | -7.5% |
| 10-20 m | 160 | 100% | 1.11 | 1.19 | 8% | 77% | -2.3% |
| 20-30 m | 278 | 100% | 0.89 | 1.62 | 6% | 86% | +3.2% |
| 30-50 m | 348 | 100% | 1.84 | 2.67 | 7% | 80% | +4.7% |
| 50+ m | 149 | 100% | 3.96 | 5.24 | 8% | 69% | +6.5% |

### `unidepth-v2-large-nocam_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.43 | 0.88 | 11% | 58% | -9.9% |
| 10-20 m | 160 | 100% | 1.36 | 1.35 | 9% | 64% | -5.7% |
| 20-30 m | 278 | 100% | 0.86 | 1.35 | 5% | 89% | -0.2% |
| 30-50 m | 348 | 100% | 1.65 | 2.18 | 5% | 87% | +0.9% |
| 50+ m | 149 | 100% | 3.10 | 3.92 | 6% | 83% | +2.8% |

### `unidepth-v2-large-nocam_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.36 | 0.83 | 10% | 58% | -9.1% |
| 10-20 m | 160 | 100% | 1.30 | 1.29 | 9% | 71% | -4.6% |
| 20-30 m | 278 | 100% | 0.84 | 1.42 | 6% | 88% | +0.9% |
| 30-50 m | 348 | 100% | 1.57 | 2.16 | 5% | 86% | +2.3% |
| 50+ m | 149 | 100% | 3.42 | 4.30 | 7% | 81% | +4.0% |

## `unidepth-v2-large-nocam_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.51 | 0.67 | 14% | 60% | +10.0% |
| 10-20 m | 1589 | 100% | 1.08 | 1.35 | 9% | 66% | +5.0% |
| 20-30 m | 1382 | 100% | 2.09 | 2.50 | 10% | 60% | +6.6% |
| 30-50 m | 1705 | 100% | 3.29 | 3.87 | 10% | 58% | +6.6% |
| 50+ m | 691 | 100% | 5.04 | 6.26 | 10% | 60% | +7.6% |

## `unidepth-v2-large-nocam_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.67 | 2.53 | 10% | 62% | +6.4% |
| pedestrian | 590 | 100% | 0.87 | 2.40 | 13% | 60% | +8.7% |
| van | 432 | 100% | 1.97 | 3.31 | 12% | 59% | +6.9% |
| truck | 187 | 100% | 2.50 | 3.29 | 12% | 65% | +8.9% |
| cyclist | 152 | 100% | 2.81 | 5.41 | 18% | 37% | +16.0% |

## `unidepth-v2-large-nocam_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.39 | 0.55 | 10% | 66% | +0.8% |
| 10-20 m | 1589 | 100% | 0.77 | 1.13 | 8% | 76% | -0.1% |
| 20-30 m | 1382 | 100% | 1.60 | 2.09 | 8% | 70% | +1.1% |
| 30-50 m | 1705 | 100% | 2.65 | 3.35 | 9% | 68% | +1.1% |
| 50+ m | 691 | 100% | 3.96 | 5.45 | 9% | 69% | +2.0% |

## `unidepth-v2-large-nocam_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.24 | 2.21 | 8% | 72% | +0.2% |
| pedestrian | 590 | 100% | 0.86 | 1.93 | 11% | 63% | +4.5% |
| van | 432 | 100% | 1.49 | 2.80 | 9% | 67% | +0.6% |
| truck | 187 | 100% | 2.10 | 3.17 | 10% | 71% | +2.6% |
| cyclist | 152 | 100% | 1.92 | 3.42 | 12% | 51% | +7.8% |

## `unidepth-v2-large-nocam_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.39 | 0.55 | 11% | 67% | +3.8% |
| 10-20 m | 1589 | 100% | 0.83 | 1.15 | 8% | 76% | +1.5% |
| 20-30 m | 1382 | 100% | 1.72 | 2.10 | 8% | 70% | +3.2% |
| 30-50 m | 1705 | 100% | 2.76 | 3.30 | 9% | 66% | +3.2% |
| 50+ m | 691 | 100% | 4.20 | 5.39 | 9% | 67% | +4.3% |

## `unidepth-v2-large-nocam_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.30 | 2.17 | 8% | 72% | +2.4% |
| pedestrian | 590 | 100% | 0.86 | 2.01 | 12% | 62% | +5.9% |
| van | 432 | 100% | 1.51 | 2.85 | 10% | 65% | +2.9% |
| truck | 187 | 100% | 2.09 | 3.10 | 10% | 72% | +5.1% |
| cyclist | 152 | 100% | 2.19 | 3.99 | 14% | 46% | +10.5% |

## `unidepth-v2-large-nocam_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.35 | 1.35 | 18% | 20% | -16.8% |
| 10-20 m | 1594 | 100% | 1.41 | 1.65 | 11% | 52% | -8.1% |
| 20-30 m | 1422 | 100% | 1.18 | 1.91 | 8% | 75% | -1.5% |
| 30-50 m | 1838 | 100% | 2.15 | 2.94 | 8% | 74% | +1.1% |
| 50+ m | 782 | 100% | 3.92 | 5.19 | 8% | 70% | +3.3% |

## `unidepth-v2-large-nocam_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.60 | 2.29 | 10% | 62% | -4.8% |
| pedestrian | 590 | 100% | 0.92 | 2.32 | 12% | 59% | +4.4% |
| van | 432 | 100% | 2.33 | 3.29 | 11% | 54% | -6.0% |
| truck | 187 | 100% | 3.11 | 3.76 | 11% | 65% | -8.5% |
| cyclist | 152 | 100% | 2.24 | 4.89 | 15% | 51% | +10.9% |

## `unidepth-v2-large-nocam_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.86 | 1.76 | 25% | 15% | -23.5% |
| 10-20 m | 1594 | 100% | 1.94 | 2.16 | 15% | 33% | -12.7% |
| 20-30 m | 1422 | 100% | 1.62 | 2.32 | 9% | 67% | -6.5% |
| 30-50 m | 1838 | 100% | 2.24 | 3.24 | 8% | 72% | -4.3% |
| 50+ m | 782 | 100% | 3.59 | 5.25 | 9% | 72% | -2.1% |

## `unidepth-v2-large-nocam_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.02 | 2.76 | 12% | 54% | -10.2% |
| pedestrian | 590 | 100% | 1.05 | 1.95 | 12% | 57% | +0.3% |
| van | 432 | 100% | 2.73 | 3.71 | 14% | 48% | -11.2% |
| truck | 187 | 100% | 4.13 | 4.93 | 14% | 49% | -13.3% |
| cyclist | 152 | 100% | 1.47 | 3.09 | 10% | 63% | +3.0% |

## `unidepth-v2-large-nocam_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.72 | 1.63 | 23% | 16% | -21.3% |
| 10-20 m | 1594 | 100% | 1.77 | 1.99 | 14% | 39% | -11.2% |
| 20-30 m | 1422 | 100% | 1.44 | 2.08 | 8% | 71% | -4.7% |
| 30-50 m | 1838 | 100% | 2.07 | 2.89 | 7% | 75% | -2.1% |
| 50+ m | 782 | 100% | 3.58 | 4.89 | 8% | 75% | +0.1% |

## `unidepth-v2-large-nocam_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.85 | 2.46 | 11% | 58% | -8.2% |
| pedestrian | 590 | 100% | 0.98 | 1.99 | 11% | 58% | +1.7% |
| van | 432 | 100% | 2.45 | 3.44 | 13% | 52% | -9.2% |
| truck | 187 | 100% | 3.96 | 4.41 | 13% | 57% | -11.3% |
| cyclist | 152 | 100% | 1.80 | 3.56 | 11% | 57% | +5.6% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-large-nocam_median | 213.123 |
| unidepth-v2-large-nocam_p10 | 2.416 |
| unidepth-v2-large-nocam_p25 | 2.326 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
