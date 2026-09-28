# KITTI distance benchmark: `yolo26s-seg_geometric-v1`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `ground_plane`, `known_size` |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 6484 matched to a detection (IoU >= 0.5) of 7922 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f972a33` (with uncommitted changes) |
| Created (UTC) | 2026-09-27T20:34:57+00:00 |

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
| ground_plane | 6484 | 99% | 2.61 | 5.56 | 24% | 39% | +13.4% |
| known_size | 6484 | 100% | 1.68 | 2.97 | 18% | 63% | +12.7% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 6484 | 99% | 2.75 | 5.78 | 19% | 37% | +0.6% |
| known_size | 6484 | 100% | 1.79 | 3.05 | 13% | 58% | -0.6% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
1020 of 6484 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / ground_plane | 1020 | 99% | 2.47 | 5.96 | 18% | 46% | +10.0% |
| in path / known_size | 1020 | 100% | 1.46 | 2.88 | 9% | 77% | +2.6% |
| beside / ground_plane | 5464 | 99% | 2.61 | 5.49 | 25% | 38% | +14.0% |
| beside / known_size | 5464 | 99% | 1.72 | 2.99 | 20% | 60% | +14.6% |

### `ground_plane` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 98% | 1.04 | 1.11 | 15% | 24% | +14.5% |
| 10-20 m | 183 | 100% | 1.39 | 2.40 | 16% | 52% | +12.8% |
| 20-30 m | 279 | 100% | 1.91 | 3.03 | 12% | 58% | +6.6% |
| 30-50 m | 335 | 100% | 5.05 | 8.83 | 23% | 41% | +11.5% |
| 50+ m | 125 | 91% | 8.18 | 14.54 | 24% | 38% | +5.4% |

### `known_size` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 98 | 98% | 0.32 | 0.52 | 8% | 74% | +5.5% |
| 10-20 m | 183 | 100% | 0.90 | 1.79 | 12% | 75% | +6.4% |
| 20-30 m | 279 | 100% | 1.34 | 1.86 | 7% | 86% | +1.7% |
| 30-50 m | 335 | 100% | 2.12 | 2.85 | 7% | 79% | -0.3% |
| 50+ m | 125 | 100% | 5.02 | 8.62 | 13% | 58% | +4.8% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / ground_plane | 1020 | 99% | 2.91 | 6.17 | 17% | 43% | +2.0% |
| in path / known_size | 1020 | 100% | 2.19 | 3.29 | 10% | 59% | -4.9% |
| beside / ground_plane | 5464 | 99% | 2.72 | 5.70 | 20% | 36% | +0.3% |
| beside / known_size | 5464 | 99% | 1.72 | 3.01 | 14% | 57% | +0.2% |

### `ground_plane` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 98% | 0.88 | 0.92 | 11% | 43% | +0.9% |
| 10-20 m | 160 | 100% | 1.66 | 2.26 | 14% | 41% | +1.8% |
| 20-30 m | 278 | 100% | 2.18 | 2.99 | 12% | 56% | -0.4% |
| 30-50 m | 348 | 100% | 5.60 | 8.39 | 21% | 36% | +4.8% |
| 50+ m | 149 | 93% | 8.89 | 14.67 | 24% | 35% | +0.6% |

### `known_size` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 85 | 98% | 0.65 | 0.83 | 10% | 63% | -7.6% |
| 10-20 m | 160 | 100% | 1.75 | 2.03 | 13% | 44% | -5.2% |
| 20-30 m | 278 | 100% | 2.15 | 2.41 | 10% | 58% | -5.0% |
| 30-50 m | 348 | 100% | 3.18 | 3.42 | 9% | 65% | -6.2% |
| 50+ m | 149 | 100% | 3.53 | 7.33 | 11% | 64% | -0.1% |

## `ground_plane` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 99% | 1.42 | 1.84 | 45% | 24% | +44.6% |
| 10-20 m | 1589 | 100% | 1.37 | 2.31 | 15% | 52% | +10.5% |
| 20-30 m | 1382 | 100% | 2.64 | 4.45 | 18% | 46% | +7.3% |
| 30-50 m | 1705 | 99% | 5.40 | 8.70 | 23% | 37% | +5.7% |
| 50+ m | 691 | 92% | 10.20 | 14.19 | 24% | 28% | +0.5% |

## `ground_plane` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 99% | 2.53 | 5.38 | 22% | 42% | +11.4% |
| pedestrian | 590 | 98% | 1.89 | 4.68 | 28% | 27% | +26.2% |
| van | 432 | 97% | 3.93 | 7.61 | 29% | 31% | +16.3% |
| truck | 187 | 96% | 4.91 | 8.13 | 30% | 37% | +18.0% |
| cyclist | 152 | 100% | 4.20 | 6.34 | 28% | 26% | +19.3% |

## `known_size` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 1117 | 97% | 1.14 | 2.19 | 57% | 36% | +55.4% |
| 10-20 m | 1589 | 100% | 1.09 | 1.77 | 12% | 65% | +7.6% |
| 20-30 m | 1382 | 100% | 1.64 | 2.44 | 10% | 71% | +3.8% |
| 30-50 m | 1705 | 100% | 2.37 | 3.57 | 9% | 72% | +1.8% |
| 50+ m | 691 | 100% | 4.42 | 6.54 | 11% | 62% | +1.9% |

## `known_size` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.62 | 2.51 | 18% | 67% | +12.6% |
| pedestrian | 590 | 97% | 0.77 | 1.48 | 11% | 75% | +8.4% |
| van | 432 | 99% | 7.28 | 9.44 | 38% | 8% | +22.5% |
| truck | 187 | 95% | 3.69 | 5.93 | 15% | 54% | +7.5% |
| cyclist | 152 | 100% | 1.75 | 2.40 | 14% | 60% | +12.3% |

## `ground_plane` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 98% | 1.00 | 1.23 | 21% | 37% | +11.8% |
| 10-20 m | 1594 | 100% | 1.58 | 2.18 | 14% | 44% | -2.4% |
| 20-30 m | 1422 | 100% | 3.00 | 4.33 | 17% | 42% | -0.3% |
| 30-50 m | 1838 | 99% | 6.06 | 8.64 | 22% | 32% | +0.5% |
| 50+ m | 782 | 93% | 11.23 | 14.53 | 24% | 25% | -3.7% |

## `ground_plane` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 99% | 2.76 | 5.66 | 18% | 37% | -1.9% |
| pedestrian | 590 | 98% | 1.47 | 4.34 | 24% | 43% | +21.2% |
| van | 432 | 97% | 3.74 | 7.64 | 22% | 33% | -0.1% |
| truck | 187 | 96% | 6.30 | 8.99 | 21% | 29% | -3.5% |
| cyclist | 152 | 100% | 3.76 | 6.07 | 23% | 31% | +13.3% |

## `known_size` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 848 | 97% | 1.16 | 1.78 | 32% | 34% | +20.3% |
| 10-20 m | 1594 | 100% | 1.31 | 1.78 | 12% | 54% | -4.8% |
| 20-30 m | 1422 | 100% | 1.86 | 2.58 | 10% | 61% | -3.7% |
| 30-50 m | 1838 | 100% | 2.41 | 3.68 | 9% | 67% | -3.0% |
| 50+ m | 782 | 100% | 4.31 | 6.37 | 10% | 62% | -2.4% |

## `known_size` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 5123 | 100% | 1.75 | 2.67 | 12% | 59% | -1.6% |
| pedestrian | 590 | 97% | 0.78 | 1.41 | 10% | 78% | +3.9% |
| van | 432 | 99% | 6.22 | 8.81 | 28% | 14% | +6.0% |
| truck | 187 | 95% | 4.55 | 6.37 | 15% | 43% | -6.5% |
| cyclist | 152 | 100% | 1.38 | 1.96 | 10% | 72% | +6.6% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| ground_plane | 0.261 |
| known_size | 0.008 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
