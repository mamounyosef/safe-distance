# KITTI distance benchmark: `metric3d-v2-large_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-large_median`, `metric3d-v2-large_p10`, `metric3d-v2-large_p25` |
| Depth model | `metric3d-v2-large`, given our focal length; inference 897.7 ms median, 1292.1 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `d5c1a3f` |
| Created (UTC) | 2026-09-29T08:23:21+00:00 |

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
| metric3d-v2-large_median | 6484 | 100% | 1.03 | 1.88 | 7% | 75% | +0.6% |
| metric3d-v2-large_p10 | 6484 | 100% | 1.09 | 2.44 | 9% | 69% | -5.6% |
| metric3d-v2-large_p25 | 6484 | 100% | 1.00 | 1.96 | 7% | 74% | -2.9% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 6484 | 100% | 1.89 | 2.59 | 11% | 55% | -9.5% |
| metric3d-v2-large_p10 | 6484 | 100% | 2.53 | 3.73 | 16% | 40% | -14.9% |
| metric3d-v2-large_p25 | 6484 | 100% | 2.29 | 3.07 | 14% | 47% | -12.5% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-large_median | 1020 | 100% | 1.09 | 1.83 | 5% | 86% | +4.2% |
| in path / metric3d-v2-large_p10 | 1020 | 100% | 0.69 | 1.47 | 4% | 92% | +1.0% |
| in path / metric3d-v2-large_p25 | 1020 | 100% | 0.77 | 1.44 | 4% | 92% | +2.5% |
| beside / metric3d-v2-large_median | 5464 | 100% | 1.02 | 1.89 | 8% | 73% | -0.1% |
| beside / metric3d-v2-large_p10 | 5464 | 100% | 1.21 | 2.62 | 10% | 64% | -6.8% |
| beside / metric3d-v2-large_p25 | 5464 | 100% | 1.06 | 2.06 | 8% | 71% | -4.0% |

### `metric3d-v2-large_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.19 | 0.29 | 4% | 92% | +0.2% |
| 10-20 m | 183 | 100% | 0.51 | 0.73 | 5% | 87% | +3.2% |
| 20-30 m | 279 | 100% | 0.81 | 1.13 | 5% | 90% | +3.8% |
| 30-50 m | 335 | 100% | 1.90 | 2.32 | 6% | 84% | +5.2% |
| 50+ m | 125 | 100% | 3.19 | 4.87 | 8% | 75% | +7.0% |

### `metric3d-v2-large_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.20 | 0.28 | 4% | 95% | -2.4% |
| 10-20 m | 183 | 100% | 0.35 | 0.52 | 3% | 96% | -0.1% |
| 20-30 m | 279 | 100% | 0.59 | 0.84 | 3% | 97% | +1.4% |
| 30-50 m | 335 | 100% | 1.41 | 1.93 | 5% | 88% | +1.6% |
| 50+ m | 125 | 100% | 2.06 | 4.01 | 6% | 82% | +2.6% |

### `metric3d-v2-large_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.19 | 0.27 | 4% | 95% | -1.4% |
| 10-20 m | 183 | 100% | 0.38 | 0.52 | 3% | 97% | +1.2% |
| 20-30 m | 279 | 100% | 0.64 | 0.88 | 4% | 96% | +2.4% |
| 30-50 m | 335 | 100% | 1.54 | 1.82 | 5% | 92% | +3.4% |
| 50+ m | 125 | 100% | 2.44 | 3.93 | 6% | 78% | +5.0% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-large_median | 1020 | 100% | 1.36 | 1.84 | 6% | 82% | -3.3% |
| in path / metric3d-v2-large_p10 | 1020 | 100% | 1.67 | 2.16 | 8% | 74% | -6.3% |
| in path / metric3d-v2-large_p25 | 1020 | 100% | 1.51 | 1.86 | 7% | 79% | -4.9% |
| beside / metric3d-v2-large_median | 5464 | 100% | 2.02 | 2.72 | 12% | 49% | -10.7% |
| beside / metric3d-v2-large_p10 | 5464 | 100% | 2.72 | 4.02 | 17% | 34% | -16.5% |
| beside / metric3d-v2-large_p25 | 5464 | 100% | 2.46 | 3.30 | 15% | 41% | -13.9% |

### `metric3d-v2-large_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.86 | 1.03 | 13% | 46% | -12.7% |
| 10-20 m | 160 | 100% | 1.28 | 1.26 | 8% | 63% | -7.7% |
| 20-30 m | 278 | 100% | 1.22 | 1.26 | 5% | 94% | -4.0% |
| 30-50 m | 348 | 100% | 1.36 | 1.74 | 4% | 92% | -0.8% |
| 50+ m | 149 | 100% | 3.38 | 4.21 | 6% | 81% | +2.1% |

### `metric3d-v2-large_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.99 | 1.20 | 15% | 34% | -14.9% |
| 10-20 m | 160 | 100% | 1.72 | 1.65 | 11% | 44% | -10.7% |
| 20-30 m | 278 | 100% | 1.59 | 1.59 | 6% | 86% | -6.0% |
| 30-50 m | 348 | 100% | 1.66 | 2.24 | 6% | 83% | -4.3% |
| 50+ m | 149 | 100% | 2.74 | 4.16 | 6% | 85% | -1.8% |

### `metric3d-v2-large_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.94 | 1.14 | 14% | 38% | -14.1% |
| 10-20 m | 160 | 100% | 1.60 | 1.49 | 10% | 51% | -9.5% |
| 20-30 m | 278 | 100% | 1.46 | 1.44 | 6% | 92% | -5.3% |
| 30-50 m | 348 | 100% | 1.39 | 1.74 | 4% | 91% | -2.5% |
| 50+ m | 149 | 100% | 2.94 | 3.74 | 6% | 83% | +0.3% |

## `metric3d-v2-large_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.43 | 0.55 | 11% | 63% | +3.2% |
| 10-20 m | 1589 | 100% | 0.68 | 0.96 | 7% | 80% | -1.3% |
| 20-30 m | 1382 | 100% | 1.13 | 1.54 | 6% | 80% | -0.4% |
| 30-50 m | 1705 | 100% | 2.07 | 2.65 | 7% | 76% | +0.3% |
| 50+ m | 691 | 100% | 3.54 | 4.91 | 8% | 72% | +3.5% |

## `metric3d-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.06 | 1.89 | 7% | 76% | +1.2% |
| pedestrian | 590 | 100% | 0.69 | 1.11 | 7% | 72% | -4.8% |
| van | 432 | 100% | 1.16 | 2.30 | 8% | 70% | -0.4% |
| truck | 187 | 100% | 1.57 | 2.50 | 9% | 81% | +2.8% |
| cyclist | 152 | 100% | 1.20 | 2.59 | 8% | 72% | +2.4% |

## `metric3d-v2-large_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.46 | 0.61 | 10% | 59% | -6.0% |
| 10-20 m | 1589 | 100% | 0.65 | 1.11 | 8% | 72% | -6.2% |
| 20-30 m | 1382 | 100% | 1.14 | 1.97 | 8% | 74% | -5.2% |
| 30-50 m | 1705 | 100% | 2.34 | 3.68 | 10% | 68% | -5.7% |
| 50+ m | 691 | 100% | 3.94 | 6.36 | 10% | 66% | -4.1% |

## `metric3d-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.13 | 2.51 | 9% | 69% | -5.6% |
| pedestrian | 590 | 100% | 0.84 | 1.31 | 9% | 63% | -7.3% |
| van | 432 | 100% | 1.45 | 2.90 | 9% | 63% | -6.4% |
| truck | 187 | 100% | 1.33 | 3.23 | 9% | 74% | -3.1% |
| cyclist | 152 | 100% | 0.84 | 2.18 | 7% | 80% | -1.2% |

## `metric3d-v2-large_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.41 | 0.55 | 10% | 63% | -3.1% |
| 10-20 m | 1589 | 100% | 0.59 | 0.97 | 7% | 76% | -4.5% |
| 20-30 m | 1382 | 100% | 1.05 | 1.62 | 7% | 79% | -3.0% |
| 30-50 m | 1705 | 100% | 2.08 | 2.84 | 7% | 76% | -2.4% |
| 50+ m | 691 | 100% | 3.48 | 5.00 | 8% | 72% | -0.2% |

## `metric3d-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.02 | 1.98 | 7% | 75% | -2.7% |
| pedestrian | 590 | 100% | 0.75 | 1.17 | 8% | 68% | -6.1% |
| van | 432 | 100% | 1.28 | 2.43 | 8% | 67% | -3.9% |
| truck | 187 | 100% | 1.53 | 2.68 | 8% | 78% | -0.6% |
| cyclist | 152 | 100% | 1.10 | 2.27 | 7% | 80% | +0.1% |

## `metric3d-v2-large_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.63 | 1.64 | 23% | 10% | -22.3% |
| 10-20 m | 1594 | 100% | 1.85 | 2.01 | 14% | 35% | -13.6% |
| 20-30 m | 1422 | 100% | 1.68 | 2.18 | 9% | 68% | -8.0% |
| 30-50 m | 1838 | 100% | 2.13 | 2.88 | 7% | 74% | -4.9% |
| 50+ m | 782 | 100% | 3.62 | 4.82 | 8% | 72% | -0.9% |

## `metric3d-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.90 | 2.54 | 11% | 55% | -9.5% |
| pedestrian | 590 | 100% | 1.08 | 1.42 | 10% | 57% | -8.6% |
| van | 432 | 100% | 2.88 | 3.66 | 14% | 42% | -12.3% |
| truck | 187 | 100% | 4.35 | 5.15 | 14% | 43% | -13.5% |
| cyclist | 152 | 100% | 1.00 | 2.52 | 8% | 74% | -2.1% |

## `metric3d-v2-large_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.14 | 2.06 | 29% | 6% | -29.1% |
| 10-20 m | 1594 | 100% | 2.40 | 2.62 | 18% | 18% | -18.0% |
| 20-30 m | 1422 | 100% | 2.45 | 3.11 | 13% | 49% | -12.3% |
| 30-50 m | 1838 | 100% | 3.11 | 4.49 | 12% | 57% | -10.6% |
| 50+ m | 782 | 100% | 4.80 | 7.10 | 12% | 62% | -8.0% |

## `metric3d-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.54 | 3.80 | 16% | 39% | -15.3% |
| pedestrian | 590 | 100% | 1.26 | 1.68 | 12% | 48% | -11.1% |
| van | 432 | 100% | 3.63 | 4.85 | 18% | 29% | -17.2% |
| truck | 187 | 100% | 5.01 | 6.79 | 18% | 32% | -18.0% |
| cyclist | 152 | 100% | 1.15 | 2.35 | 8% | 71% | -5.5% |

## `metric3d-v2-large_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.96 | 1.92 | 27% | 8% | -26.9% |
| 10-20 m | 1594 | 100% | 2.23 | 2.41 | 17% | 23% | -16.5% |
| 20-30 m | 1422 | 100% | 2.11 | 2.67 | 11% | 59% | -10.4% |
| 30-50 m | 1838 | 100% | 2.59 | 3.48 | 9% | 67% | -7.5% |
| 50+ m | 782 | 100% | 3.95 | 5.46 | 9% | 68% | -4.2% |

## `metric3d-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.31 | 3.08 | 14% | 46% | -12.7% |
| pedestrian | 590 | 100% | 1.16 | 1.52 | 11% | 53% | -9.8% |
| van | 432 | 100% | 3.30 | 4.19 | 16% | 36% | -15.1% |
| truck | 187 | 100% | 4.72 | 5.86 | 16% | 37% | -16.0% |
| cyclist | 152 | 100% | 1.09 | 2.35 | 8% | 74% | -4.3% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| metric3d-v2-large_median | 900.402 |
| metric3d-v2-large_p10 | 2.444 |
| metric3d-v2-large_p25 | 2.358 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
