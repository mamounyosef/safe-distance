# KITTI distance benchmark: `unidepth-v2-base_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 466.1 ms median, 499.2 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `d5c1a3f` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T08:37:14+00:00 |

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
| unidepth-v2-base_median | 6484 | 100% | 1.15 | 2.14 | 9% | 70% | -4.1% |
| unidepth-v2-base_p10 | 6484 | 100% | 1.66 | 2.85 | 11% | 56% | -9.8% |
| unidepth-v2-base_p25 | 6484 | 100% | 1.45 | 2.49 | 10% | 62% | -7.8% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 6484 | 100% | 2.70 | 3.57 | 15% | 37% | -13.8% |
| unidepth-v2-base_p10 | 6484 | 100% | 3.52 | 4.61 | 19% | 22% | -18.7% |
| unidepth-v2-base_p25 | 6484 | 100% | 3.26 | 4.16 | 17% | 26% | -17.0% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-base_median | 1020 | 100% | 0.77 | 1.46 | 5% | 92% | -0.9% |
| in path / unidepth-v2-base_p10 | 1020 | 100% | 1.02 | 1.69 | 5% | 90% | -4.3% |
| in path / unidepth-v2-base_p25 | 1020 | 100% | 0.94 | 1.53 | 5% | 91% | -3.2% |
| beside / unidepth-v2-base_median | 5464 | 100% | 1.26 | 2.27 | 9% | 66% | -4.7% |
| beside / unidepth-v2-base_p10 | 5464 | 100% | 1.85 | 3.07 | 12% | 50% | -10.9% |
| beside / unidepth-v2-base_p25 | 5464 | 100% | 1.61 | 2.67 | 11% | 56% | -8.7% |

### `unidepth-v2-base_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.35 | 0.36 | 5% | 94% | -2.6% |
| 10-20 m | 183 | 100% | 0.47 | 0.67 | 4% | 93% | +0.1% |
| 20-30 m | 279 | 100% | 0.63 | 0.96 | 4% | 96% | +0.4% |
| 30-50 m | 335 | 100% | 1.36 | 1.74 | 4% | 93% | -1.3% |
| 50+ m | 125 | 100% | 3.32 | 3.87 | 6% | 80% | -2.8% |

### `unidepth-v2-base_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.46 | 0.44 | 6% | 85% | -5.5% |
| 10-20 m | 183 | 100% | 0.57 | 0.72 | 5% | 94% | -3.8% |
| 20-30 m | 279 | 100% | 0.83 | 0.91 | 4% | 98% | -3.0% |
| 30-50 m | 335 | 100% | 1.80 | 2.17 | 6% | 88% | -4.6% |
| 50+ m | 125 | 100% | 3.95 | 4.56 | 7% | 73% | -5.8% |

### `unidepth-v2-base_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.40 | 0.40 | 5% | 90% | -4.6% |
| 10-20 m | 183 | 100% | 0.51 | 0.67 | 4% | 95% | -2.6% |
| 20-30 m | 279 | 100% | 0.76 | 0.87 | 4% | 97% | -2.1% |
| 30-50 m | 335 | 100% | 1.47 | 1.88 | 5% | 91% | -3.4% |
| 50+ m | 125 | 100% | 3.58 | 4.21 | 7% | 77% | -4.8% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-base_median | 1020 | 100% | 2.22 | 2.79 | 9% | 61% | -8.1% |
| in path / unidepth-v2-base_p10 | 1020 | 100% | 2.85 | 3.47 | 11% | 43% | -11.2% |
| in path / unidepth-v2-base_p25 | 1020 | 100% | 2.63 | 3.18 | 10% | 49% | -10.2% |
| beside / unidepth-v2-base_median | 5464 | 100% | 2.81 | 3.71 | 16% | 32% | -14.9% |
| beside / unidepth-v2-base_p10 | 5464 | 100% | 3.72 | 4.83 | 20% | 18% | -20.1% |
| beside / unidepth-v2-base_p25 | 5464 | 100% | 3.40 | 4.35 | 19% | 22% | -18.3% |

### `unidepth-v2-base_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.98 | 1.21 | 15% | 33% | -15.0% |
| 10-20 m | 160 | 100% | 1.88 | 1.77 | 11% | 38% | -10.2% |
| 20-30 m | 278 | 100% | 2.10 | 2.13 | 9% | 66% | -7.0% |
| 30-50 m | 348 | 100% | 2.86 | 3.12 | 8% | 70% | -6.7% |
| 50+ m | 149 | 100% | 4.37 | 5.27 | 8% | 68% | -7.0% |

### `unidepth-v2-base_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.18 | 1.40 | 17% | 25% | -17.3% |
| 10-20 m | 160 | 100% | 2.37 | 2.13 | 14% | 22% | -13.6% |
| 20-30 m | 278 | 100% | 2.60 | 2.54 | 10% | 43% | -10.2% |
| 30-50 m | 348 | 100% | 3.64 | 3.99 | 10% | 53% | -9.9% |
| 50+ m | 149 | 100% | 5.79 | 6.58 | 10% | 54% | -9.9% |

### `unidepth-v2-base_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.12 | 1.34 | 17% | 26% | -16.6% |
| 10-20 m | 160 | 100% | 2.22 | 2.01 | 13% | 26% | -12.6% |
| 20-30 m | 278 | 100% | 2.44 | 2.38 | 10% | 51% | -9.3% |
| 30-50 m | 348 | 100% | 3.35 | 3.59 | 9% | 58% | -8.8% |
| 50+ m | 149 | 100% | 5.37 | 6.03 | 9% | 58% | -9.0% |

## `unidepth-v2-base_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.52 | 0.65 | 12% | 57% | -0.8% |
| 10-20 m | 1589 | 100% | 0.78 | 1.16 | 8% | 72% | -5.4% |
| 20-30 m | 1382 | 100% | 1.21 | 1.86 | 8% | 75% | -3.8% |
| 30-50 m | 1705 | 100% | 2.14 | 3.02 | 8% | 74% | -4.9% |
| 50+ m | 691 | 100% | 4.30 | 5.20 | 9% | 66% | -5.5% |

## `unidepth-v2-base_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.14 | 2.04 | 8% | 72% | -4.3% |
| pedestrian | 590 | 100% | 0.89 | 1.50 | 9% | 62% | -4.8% |
| van | 432 | 100% | 1.68 | 3.08 | 11% | 59% | -5.1% |
| truck | 187 | 100% | 2.19 | 3.94 | 11% | 64% | -2.4% |
| cyclist | 152 | 100% | 1.71 | 3.24 | 11% | 59% | +6.0% |

## `unidepth-v2-base_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.73 | 0.86 | 13% | 39% | -9.7% |
| 10-20 m | 1589 | 100% | 1.25 | 1.59 | 11% | 57% | -10.5% |
| 20-30 m | 1382 | 100% | 1.73 | 2.40 | 10% | 65% | -9.0% |
| 30-50 m | 1705 | 100% | 3.09 | 4.10 | 11% | 61% | -9.8% |
| 50+ m | 691 | 100% | 5.70 | 6.81 | 11% | 52% | -10.2% |

## `unidepth-v2-base_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.75 | 2.88 | 11% | 56% | -10.1% |
| pedestrian | 590 | 100% | 1.02 | 1.45 | 10% | 56% | -9.0% |
| van | 432 | 100% | 2.49 | 3.99 | 13% | 46% | -11.1% |
| truck | 187 | 100% | 2.62 | 4.54 | 12% | 56% | -8.0% |
| cyclist | 152 | 100% | 1.06 | 2.14 | 8% | 76% | -2.8% |

## `unidepth-v2-base_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.65 | 0.78 | 13% | 45% | -6.8% |
| 10-20 m | 1589 | 100% | 1.08 | 1.42 | 10% | 63% | -8.9% |
| 20-30 m | 1382 | 100% | 1.47 | 2.09 | 8% | 70% | -7.2% |
| 30-50 m | 1705 | 100% | 2.72 | 3.54 | 9% | 67% | -7.9% |
| 50+ m | 691 | 100% | 4.93 | 5.92 | 10% | 58% | -8.2% |

## `unidepth-v2-base_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.49 | 2.48 | 10% | 63% | -8.1% |
| pedestrian | 590 | 100% | 0.95 | 1.34 | 9% | 59% | -7.5% |
| van | 432 | 100% | 2.17 | 3.57 | 12% | 53% | -9.0% |
| truck | 187 | 100% | 2.64 | 4.16 | 11% | 59% | -6.0% |
| cyclist | 152 | 100% | 1.13 | 2.27 | 8% | 72% | +0.4% |

## `unidepth-v2-base_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.88 | 1.85 | 25% | 7% | -25.1% |
| 10-20 m | 1594 | 100% | 2.43 | 2.57 | 18% | 18% | -17.1% |
| 20-30 m | 1422 | 100% | 2.66 | 3.08 | 12% | 45% | -11.1% |
| 30-50 m | 1838 | 100% | 3.69 | 4.29 | 11% | 52% | -9.7% |
| 50+ m | 782 | 100% | 5.65 | 6.66 | 11% | 53% | -9.3% |

## `unidepth-v2-base_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.73 | 3.52 | 15% | 36% | -14.5% |
| pedestrian | 590 | 100% | 1.27 | 1.80 | 12% | 47% | -8.6% |
| van | 432 | 100% | 4.06 | 5.03 | 18% | 26% | -16.6% |
| truck | 187 | 100% | 5.99 | 7.53 | 19% | 17% | -17.9% |
| cyclist | 152 | 100% | 1.62 | 3.13 | 10% | 59% | +1.4% |

## `unidepth-v2-base_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.37 | 2.27 | 32% | 4% | -31.6% |
| 10-20 m | 1594 | 100% | 3.03 | 3.19 | 22% | 9% | -21.8% |
| 20-30 m | 1422 | 100% | 3.45 | 3.95 | 16% | 24% | -15.9% |
| 30-50 m | 1838 | 100% | 5.00 | 5.70 | 15% | 34% | -14.5% |
| 50+ m | 782 | 100% | 7.57 | 8.71 | 14% | 34% | -13.7% |

## `unidepth-v2-base_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.63 | 4.70 | 19% | 20% | -19.4% |
| pedestrian | 590 | 100% | 1.48 | 1.86 | 13% | 39% | -12.7% |
| van | 432 | 100% | 4.89 | 6.28 | 22% | 12% | -21.5% |
| truck | 187 | 100% | 6.97 | 8.90 | 22% | 10% | -22.2% |
| cyclist | 152 | 100% | 1.51 | 2.52 | 9% | 63% | -7.1% |

## `unidepth-v2-base_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.20 | 2.14 | 30% | 5% | -29.5% |
| 10-20 m | 1594 | 100% | 2.85 | 2.99 | 21% | 11% | -20.3% |
| 20-30 m | 1422 | 100% | 3.21 | 3.59 | 15% | 30% | -14.3% |
| 30-50 m | 1838 | 100% | 4.45 | 5.05 | 13% | 40% | -12.6% |
| 50+ m | 782 | 100% | 6.71 | 7.71 | 13% | 41% | -11.9% |

## `unidepth-v2-base_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.33 | 4.22 | 18% | 24% | -17.7% |
| pedestrian | 590 | 100% | 1.34 | 1.72 | 12% | 43% | -11.2% |
| van | 432 | 100% | 4.57 | 5.74 | 20% | 17% | -19.7% |
| truck | 187 | 100% | 6.65 | 8.23 | 21% | 13% | -20.6% |
| cyclist | 152 | 100% | 1.40 | 2.44 | 9% | 67% | -4.1% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-base_median | 469.058 |
| unidepth-v2-base_p10 | 2.491 |
| unidepth-v2-base_p25 | 2.378 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
