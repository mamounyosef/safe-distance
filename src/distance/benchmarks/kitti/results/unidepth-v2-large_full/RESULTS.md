# KITTI distance benchmark: `unidepth-v2-large_full`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 209.6 ms median, 1638.4 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:04:35+00:00 |

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
| unidepth-v2-large_median | 6484 | 100% | 1.07 | 1.97 | 8% | 73% | -3.2% |
| unidepth-v2-large_p10 | 6484 | 100% | 1.54 | 2.58 | 10% | 60% | -8.9% |
| unidepth-v2-large_p25 | 6484 | 100% | 1.35 | 2.24 | 9% | 66% | -6.9% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 6484 | 100% | 2.56 | 3.29 | 14% | 40% | -12.9% |
| unidepth-v2-large_p10 | 6484 | 100% | 3.36 | 4.28 | 18% | 26% | -17.9% |
| unidepth-v2-large_p25 | 6484 | 100% | 3.09 | 3.84 | 17% | 30% | -16.1% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-large_median | 1020 | 100% | 0.86 | 1.57 | 5% | 92% | -0.2% |
| in path / unidepth-v2-large_p10 | 1020 | 100% | 1.12 | 1.58 | 5% | 90% | -3.7% |
| in path / unidepth-v2-large_p25 | 1020 | 100% | 1.04 | 1.50 | 5% | 92% | -2.5% |
| beside / unidepth-v2-large_median | 5464 | 100% | 1.11 | 2.05 | 9% | 69% | -3.8% |
| beside / unidepth-v2-large_p10 | 5464 | 100% | 1.63 | 2.77 | 11% | 54% | -9.9% |
| beside / unidepth-v2-large_p25 | 5464 | 100% | 1.42 | 2.38 | 10% | 61% | -7.8% |

### `unidepth-v2-large_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.27 | 0.32 | 4% | 93% | -3.3% |
| 10-20 m | 183 | 100% | 0.62 | 0.80 | 5% | 90% | -1.1% |
| 20-30 m | 279 | 100% | 0.84 | 1.24 | 5% | 94% | +0.1% |
| 30-50 m | 335 | 100% | 1.31 | 1.79 | 5% | 95% | -0.1% |
| 50+ m | 125 | 100% | 2.62 | 3.87 | 6% | 84% | +2.8% |

### `unidepth-v2-large_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.44 | 0.47 | 6% | 89% | -6.1% |
| 10-20 m | 183 | 100% | 0.78 | 0.86 | 6% | 88% | -4.7% |
| 20-30 m | 279 | 100% | 0.95 | 1.10 | 5% | 94% | -3.4% |
| 30-50 m | 335 | 100% | 1.88 | 2.11 | 5% | 88% | -3.8% |
| 50+ m | 125 | 100% | 2.40 | 3.13 | 5% | 89% | -1.0% |

### `unidepth-v2-large_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 100% | 0.36 | 0.41 | 6% | 92% | -5.2% |
| 10-20 m | 183 | 100% | 0.72 | 0.81 | 5% | 91% | -3.6% |
| 20-30 m | 279 | 100% | 0.90 | 1.14 | 5% | 94% | -2.2% |
| 30-50 m | 335 | 100% | 1.63 | 1.82 | 5% | 94% | -2.5% |
| 50+ m | 125 | 100% | 2.40 | 3.29 | 5% | 88% | +0.3% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / unidepth-v2-large_median | 1020 | 100% | 2.28 | 2.75 | 9% | 61% | -7.3% |
| in path / unidepth-v2-large_p10 | 1020 | 100% | 2.90 | 3.21 | 11% | 46% | -10.6% |
| in path / unidepth-v2-large_p25 | 1020 | 100% | 2.69 | 2.98 | 10% | 51% | -9.5% |
| beside / unidepth-v2-large_median | 5464 | 100% | 2.61 | 3.39 | 15% | 37% | -14.0% |
| beside / unidepth-v2-large_p10 | 5464 | 100% | 3.46 | 4.48 | 20% | 22% | -19.2% |
| beside / unidepth-v2-large_p25 | 5464 | 100% | 3.17 | 4.01 | 18% | 26% | -17.3% |

### `unidepth-v2-large_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 0.89 | 1.26 | 15% | 45% | -15.4% |
| 10-20 m | 160 | 100% | 2.02 | 1.92 | 12% | 32% | -11.4% |
| 20-30 m | 278 | 100% | 2.14 | 2.37 | 10% | 59% | -7.4% |
| 30-50 m | 348 | 100% | 2.76 | 3.01 | 8% | 73% | -5.7% |
| 50+ m | 149 | 100% | 3.71 | 4.62 | 7% | 76% | -2.1% |

### `unidepth-v2-large_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.04 | 1.44 | 18% | 27% | -17.7% |
| 10-20 m | 160 | 100% | 2.45 | 2.28 | 15% | 23% | -14.5% |
| 20-30 m | 278 | 100% | 2.84 | 2.69 | 11% | 40% | -10.7% |
| 30-50 m | 348 | 100% | 3.71 | 3.80 | 10% | 54% | -9.2% |
| 50+ m | 149 | 100% | 4.34 | 4.77 | 8% | 72% | -5.7% |

### `unidepth-v2-large_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 100% | 1.01 | 1.38 | 17% | 32% | -17.0% |
| 10-20 m | 160 | 100% | 2.30 | 2.16 | 14% | 25% | -13.5% |
| 20-30 m | 278 | 100% | 2.60 | 2.59 | 10% | 46% | -9.6% |
| 30-50 m | 348 | 100% | 3.30 | 3.40 | 9% | 62% | -8.0% |
| 50+ m | 149 | 100% | 3.85 | 4.52 | 7% | 74% | -4.5% |

## `unidepth-v2-large_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.54 | 0.65 | 12% | 57% | -1.4% |
| 10-20 m | 1589 | 100% | 0.77 | 1.12 | 8% | 73% | -5.5% |
| 20-30 m | 1382 | 100% | 1.19 | 1.78 | 7% | 77% | -3.5% |
| 30-50 m | 1705 | 100% | 1.87 | 2.74 | 7% | 78% | -3.1% |
| 50+ m | 691 | 100% | 3.19 | 4.56 | 8% | 75% | -1.2% |

## `unidepth-v2-large_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.05 | 1.86 | 8% | 74% | -3.4% |
| pedestrian | 590 | 100% | 0.85 | 1.55 | 9% | 64% | -4.8% |
| van | 432 | 100% | 1.59 | 2.75 | 10% | 66% | -3.5% |
| truck | 187 | 100% | 1.82 | 2.93 | 10% | 76% | -1.1% |
| cyclist | 152 | 100% | 1.20 | 3.81 | 11% | 64% | +5.7% |

## `unidepth-v2-large_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.75 | 0.86 | 13% | 38% | -9.9% |
| 10-20 m | 1589 | 100% | 1.21 | 1.55 | 11% | 59% | -10.2% |
| 20-30 m | 1382 | 100% | 1.74 | 2.34 | 9% | 67% | -8.7% |
| 30-50 m | 1705 | 100% | 2.63 | 3.66 | 10% | 67% | -8.3% |
| 50+ m | 691 | 100% | 3.97 | 5.58 | 9% | 68% | -6.5% |

## `unidepth-v2-large_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.59 | 2.60 | 10% | 60% | -9.2% |
| pedestrian | 590 | 100% | 1.00 | 1.46 | 10% | 56% | -8.7% |
| van | 432 | 100% | 2.15 | 3.40 | 12% | 54% | -9.5% |
| truck | 187 | 100% | 2.07 | 3.86 | 11% | 67% | -6.9% |
| cyclist | 152 | 100% | 1.07 | 2.56 | 8% | 74% | -2.4% |

## `unidepth-v2-large_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 100% | 0.65 | 0.78 | 13% | 45% | -7.2% |
| 10-20 m | 1589 | 100% | 1.03 | 1.37 | 9% | 65% | -8.7% |
| 20-30 m | 1382 | 100% | 1.48 | 2.03 | 8% | 72% | -6.8% |
| 30-50 m | 1705 | 100% | 2.27 | 3.12 | 8% | 73% | -6.3% |
| 50+ m | 691 | 100% | 3.50 | 4.88 | 8% | 72% | -4.3% |

## `unidepth-v2-large_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.38 | 2.21 | 9% | 67% | -7.2% |
| pedestrian | 590 | 100% | 0.96 | 1.39 | 9% | 61% | -7.3% |
| van | 432 | 100% | 1.88 | 3.03 | 10% | 59% | -7.3% |
| truck | 187 | 100% | 1.84 | 3.44 | 10% | 72% | -4.6% |
| cyclist | 152 | 100% | 1.29 | 2.84 | 9% | 72% | +0.3% |

## `unidepth-v2-large_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 1.90 | 1.87 | 26% | 7% | -25.6% |
| 10-20 m | 1594 | 100% | 2.43 | 2.57 | 18% | 17% | -17.3% |
| 20-30 m | 1422 | 100% | 2.63 | 3.02 | 12% | 46% | -10.9% |
| 30-50 m | 1838 | 100% | 3.12 | 3.83 | 10% | 61% | -8.2% |
| 50+ m | 782 | 100% | 4.10 | 5.49 | 9% | 66% | -5.2% |

## `unidepth-v2-large_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 2.60 | 3.21 | 14% | 41% | -13.5% |
| pedestrian | 590 | 100% | 1.30 | 1.88 | 12% | 47% | -8.6% |
| van | 432 | 100% | 3.70 | 4.42 | 16% | 31% | -15.1% |
| truck | 187 | 100% | 6.43 | 6.91 | 17% | 18% | -16.9% |
| cyclist | 152 | 100% | 1.38 | 3.83 | 12% | 61% | +1.1% |

## `unidepth-v2-large_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.38 | 2.29 | 32% | 4% | -31.9% |
| 10-20 m | 1594 | 100% | 3.01 | 3.16 | 22% | 9% | -21.6% |
| 20-30 m | 1422 | 100% | 3.49 | 3.90 | 16% | 24% | -15.6% |
| 30-50 m | 1838 | 100% | 4.46 | 5.22 | 14% | 41% | -13.2% |
| 50+ m | 782 | 100% | 5.73 | 7.19 | 12% | 52% | -10.2% |

## `unidepth-v2-large_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.43 | 4.34 | 19% | 24% | -18.5% |
| pedestrian | 590 | 100% | 1.47 | 1.86 | 13% | 37% | -12.3% |
| van | 432 | 100% | 4.51 | 5.59 | 20% | 19% | -20.0% |
| truck | 187 | 100% | 7.53 | 8.42 | 21% | 12% | -21.3% |
| cyclist | 152 | 100% | 1.50 | 2.92 | 10% | 66% | -6.7% |

## `unidepth-v2-large_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 100% | 2.24 | 2.15 | 30% | 5% | -29.8% |
| 10-20 m | 1594 | 100% | 2.85 | 2.97 | 20% | 10% | -20.2% |
| 20-30 m | 1422 | 100% | 3.20 | 3.56 | 14% | 30% | -14.0% |
| 30-50 m | 1838 | 100% | 3.96 | 4.57 | 12% | 48% | -11.2% |
| 50+ m | 782 | 100% | 5.12 | 6.29 | 10% | 58% | -8.2% |

## `unidepth-v2-large_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 3.15 | 3.86 | 17% | 29% | -16.8% |
| pedestrian | 590 | 100% | 1.39 | 1.77 | 12% | 41% | -11.0% |
| van | 432 | 100% | 4.17 | 5.06 | 19% | 22% | -18.1% |
| truck | 187 | 100% | 7.03 | 7.76 | 20% | 15% | -19.5% |
| cyclist | 152 | 100% | 1.38 | 3.08 | 10% | 66% | -4.1% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| unidepth-v2-large_median | 212.823 |
| unidepth-v2-large_p10 | 2.579 |
| unidepth-v2-large_p25 | 2.415 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
