# KITTI distance benchmark: `metric3d-v2-small-fp16_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 80.2 ms median, 86.2 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` |
| Created (UTC) | 2026-09-29T13:33:16+00:00 |

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
| metric3d-v2-small-fp16_median | 6484 | 100% | 1.14 | 2.33 | 9% | 69% | -1.5% |
| metric3d-v2-small-fp16_p10 | 6484 | 100% | 1.37 | 3.03 | 11% | 62% | -8.0% |
| metric3d-v2-small-fp16_p25 | 6484 | 100% | 1.19 | 2.53 | 9% | 67% | -5.3% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 6484 | 100% | 2.22 | 3.33 | 13% | 46% | -11.6% |
| metric3d-v2-small-fp16_p10 | 6484 | 100% | 3.02 | 4.56 | 18% | 30% | -17.2% |
| metric3d-v2-small-fp16_p25 | 6484 | 100% | 2.70 | 3.91 | 16% | 36% | -14.8% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-small-fp16_median | 1020 | 100% | 0.98 | 1.82 | 5% | 87% | +1.9% |
| in path / metric3d-v2-small-fp16_p10 | 1020 | 100% | 0.91 | 1.89 | 5% | 88% | -2.1% |
| in path / metric3d-v2-small-fp16_p25 | 1020 | 100% | 0.92 | 1.67 | 5% | 90% | -0.4% |
| beside / metric3d-v2-small-fp16_median | 5464 | 100% | 1.18 | 2.42 | 10% | 66% | -2.1% |
| beside / metric3d-v2-small-fp16_p10 | 5464 | 100% | 1.49 | 3.25 | 12% | 58% | -9.1% |
| beside / metric3d-v2-small-fp16_p25 | 5464 | 100% | 1.25 | 2.69 | 10% | 63% | -6.2% |

### `metric3d-v2-small-fp16_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.26 | 0.33 | 5% | 90% | +0.5% |
| 10-20 m | 183 | 100% | 0.55 | 0.76 | 5% | 90% | +2.6% |
| 20-30 m | 279 | 100% | 0.89 | 1.18 | 5% | 93% | +2.5% |
| 30-50 m | 335 | 100% | 1.56 | 2.09 | 5% | 87% | +1.8% |
| 50+ m | 125 | 100% | 4.15 | 5.26 | 8% | 69% | +1.1% |

### `metric3d-v2-small-fp16_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.30 | 0.32 | 4% | 92% | -2.5% |
| 10-20 m | 183 | 100% | 0.42 | 0.63 | 4% | 92% | -1.4% |
| 20-30 m | 279 | 100% | 0.81 | 0.95 | 4% | 96% | -0.4% |
| 30-50 m | 335 | 100% | 1.67 | 2.33 | 6% | 85% | -2.8% |
| 50+ m | 125 | 100% | 4.65 | 5.86 | 9% | 66% | -4.6% |

### `metric3d-v2-small-fp16_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.25 | 0.31 | 4% | 93% | -1.5% |
| 10-20 m | 183 | 100% | 0.44 | 0.59 | 4% | 94% | +0.2% |
| 20-30 m | 279 | 100% | 0.88 | 0.98 | 4% | 96% | +0.8% |
| 30-50 m | 335 | 100% | 1.54 | 1.96 | 5% | 89% | -0.8% |
| 50+ m | 125 | 100% | 4.26 | 5.06 | 8% | 70% | -2.3% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / metric3d-v2-small-fp16_median | 1020 | 100% | 1.74 | 2.45 | 8% | 71% | -5.5% |
| in path / metric3d-v2-small-fp16_p10 | 1020 | 100% | 2.29 | 3.16 | 10% | 58% | -9.2% |
| in path / metric3d-v2-small-fp16_p25 | 1020 | 100% | 2.04 | 2.72 | 9% | 64% | -7.7% |
| beside / metric3d-v2-small-fp16_median | 5464 | 100% | 2.35 | 3.49 | 14% | 41% | -12.7% |
| beside / metric3d-v2-small-fp16_p10 | 5464 | 100% | 3.20 | 4.82 | 19% | 25% | -18.7% |
| beside / metric3d-v2-small-fp16_p25 | 5464 | 100% | 2.84 | 4.13 | 17% | 31% | -16.2% |

### `metric3d-v2-small-fp16_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.79 | 1.01 | 12% | 51% | -12.4% |
| 10-20 m | 160 | 100% | 1.28 | 1.35 | 9% | 61% | -8.0% |
| 20-30 m | 278 | 100% | 1.46 | 1.51 | 6% | 78% | -5.3% |
| 30-50 m | 348 | 100% | 2.21 | 2.63 | 7% | 80% | -3.7% |
| 50+ m | 149 | 100% | 5.08 | 5.79 | 9% | 60% | -3.4% |

### `metric3d-v2-small-fp16_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.96 | 1.23 | 15% | 35% | -15.1% |
| 10-20 m | 160 | 100% | 1.81 | 1.83 | 12% | 40% | -11.6% |
| 20-30 m | 278 | 100% | 1.94 | 1.98 | 8% | 69% | -7.7% |
| 30-50 m | 348 | 100% | 3.14 | 3.53 | 9% | 66% | -8.2% |
| 50+ m | 149 | 100% | 6.00 | 7.06 | 11% | 52% | -8.6% |

### `metric3d-v2-small-fp16_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.90 | 1.15 | 14% | 41% | -14.1% |
| 10-20 m | 160 | 100% | 1.61 | 1.60 | 10% | 48% | -10.1% |
| 20-30 m | 278 | 100% | 1.76 | 1.76 | 7% | 73% | -6.8% |
| 30-50 m | 348 | 100% | 2.69 | 2.94 | 7% | 72% | -6.2% |
| 50+ m | 149 | 100% | 5.30 | 6.06 | 9% | 56% | -6.5% |

## `metric3d-v2-small-fp16_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.50 | 0.62 | 13% | 60% | +4.5% |
| 10-20 m | 1589 | 100% | 0.77 | 1.08 | 7% | 75% | -2.5% |
| 20-30 m | 1382 | 100% | 1.25 | 1.85 | 7% | 75% | -2.2% |
| 30-50 m | 1705 | 100% | 2.32 | 3.30 | 9% | 69% | -3.6% |
| 50+ m | 691 | 100% | 4.71 | 6.51 | 11% | 60% | -2.4% |

## `metric3d-v2-small-fp16_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.14 | 2.26 | 9% | 70% | -1.1% |
| pedestrian | 590 | 100% | 0.77 | 1.52 | 9% | 68% | -5.4% |
| van | 432 | 100% | 1.45 | 3.19 | 11% | 64% | -4.1% |
| truck | 187 | 100% | 2.27 | 3.66 | 11% | 67% | +0.2% |
| cyclist | 152 | 100% | 1.57 | 3.51 | 11% | 57% | +3.9% |

## `metric3d-v2-small-fp16_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.48 | 0.65 | 11% | 58% | -5.1% |
| 10-20 m | 1589 | 100% | 0.83 | 1.31 | 9% | 68% | -7.6% |
| 20-30 m | 1382 | 100% | 1.43 | 2.31 | 9% | 69% | -7.2% |
| 30-50 m | 1705 | 100% | 2.99 | 4.58 | 12% | 59% | -9.8% |
| 50+ m | 691 | 100% | 5.77 | 8.47 | 14% | 50% | -10.5% |

## `metric3d-v2-small-fp16_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.39 | 3.07 | 11% | 63% | -7.9% |
| pedestrian | 590 | 100% | 0.98 | 1.59 | 10% | 59% | -9.2% |
| van | 432 | 100% | 2.02 | 4.02 | 12% | 55% | -10.6% |
| truck | 187 | 100% | 2.19 | 4.31 | 11% | 66% | -5.9% |
| cyclist | 152 | 100% | 1.15 | 2.89 | 9% | 65% | -2.4% |

## `metric3d-v2-small-fp16_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.45 | 0.60 | 11% | 62% | -2.0% |
| 10-20 m | 1589 | 100% | 0.74 | 1.15 | 8% | 72% | -5.8% |
| 20-30 m | 1382 | 100% | 1.25 | 1.98 | 8% | 74% | -4.9% |
| 30-50 m | 1705 | 100% | 2.52 | 3.73 | 10% | 66% | -6.8% |
| 50+ m | 691 | 100% | 5.06 | 6.98 | 11% | 58% | -6.6% |

## `metric3d-v2-small-fp16_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.18 | 2.51 | 9% | 69% | -5.0% |
| pedestrian | 590 | 100% | 0.91 | 1.48 | 9% | 64% | -7.6% |
| van | 432 | 100% | 1.66 | 3.44 | 11% | 61% | -7.9% |
| truck | 187 | 100% | 2.23 | 4.04 | 11% | 64% | -3.7% |
| cyclist | 152 | 100% | 1.16 | 3.03 | 10% | 65% | -0.0% |

## `metric3d-v2-small-fp16_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.58 | 1.58 | 21% | 12% | -21.2% |
| 10-20 m | 1594 | 100% | 1.95 | 2.14 | 15% | 33% | -14.4% |
| 20-30 m | 1422 | 100% | 2.11 | 2.58 | 10% | 57% | -9.5% |
| 30-50 m | 1838 | 100% | 3.03 | 4.06 | 10% | 60% | -8.5% |
| 50+ m | 782 | 100% | 5.64 | 7.27 | 12% | 53% | -6.4% |

## `metric3d-v2-small-fp16_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.23 | 3.24 | 13% | 46% | -11.7% |
| pedestrian | 590 | 100% | 1.18 | 1.84 | 11% | 53% | -9.2% |
| van | 432 | 100% | 3.55 | 4.92 | 17% | 30% | -15.8% |
| truck | 187 | 100% | 5.30 | 6.70 | 17% | 32% | -15.8% |
| cyclist | 152 | 100% | 1.23 | 3.44 | 10% | 66% | -0.8% |

## `metric3d-v2-small-fp16_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.11 | 2.04 | 28% | 7% | -28.4% |
| 10-20 m | 1594 | 100% | 2.55 | 2.78 | 19% | 16% | -19.0% |
| 20-30 m | 1422 | 100% | 2.97 | 3.55 | 14% | 38% | -14.1% |
| 30-50 m | 1838 | 100% | 4.44 | 5.76 | 15% | 42% | -14.2% |
| 50+ m | 782 | 100% | 7.66 | 9.93 | 16% | 41% | -14.1% |

## `metric3d-v2-small-fp16_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.06 | 4.62 | 18% | 29% | -17.6% |
| pedestrian | 590 | 100% | 1.44 | 2.01 | 14% | 42% | -12.9% |
| van | 432 | 100% | 4.44 | 6.29 | 21% | 16% | -21.1% |
| truck | 187 | 100% | 6.22 | 8.15 | 20% | 21% | -20.3% |
| cyclist | 152 | 100% | 1.42 | 3.16 | 10% | 60% | -6.8% |

## `metric3d-v2-small-fp16_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.96 | 1.89 | 26% | 9% | -26.0% |
| 10-20 m | 1594 | 100% | 2.34 | 2.55 | 18% | 21% | -17.4% |
| 20-30 m | 1422 | 100% | 2.61 | 3.09 | 13% | 45% | -12.1% |
| 30-50 m | 1838 | 100% | 3.77 | 4.80 | 12% | 50% | -11.4% |
| 50+ m | 782 | 100% | 6.41 | 8.21 | 13% | 47% | -10.4% |

## `metric3d-v2-small-fp16_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.73 | 3.89 | 16% | 36% | -15.0% |
| pedestrian | 590 | 100% | 1.33 | 1.87 | 12% | 46% | -11.4% |
| van | 432 | 100% | 4.05 | 5.54 | 19% | 21% | -18.9% |
| truck | 187 | 100% | 5.95 | 7.56 | 19% | 24% | -18.6% |
| cyclist | 152 | 100% | 1.33 | 3.20 | 10% | 63% | -4.5% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| metric3d-v2-small-fp16_median | 83.15 |
| metric3d-v2-small-fp16_p10 | 2.569 |
| metric3d-v2-small-fp16_p25 | 2.45 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
