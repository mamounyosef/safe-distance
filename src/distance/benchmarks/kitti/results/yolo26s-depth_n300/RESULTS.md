# KITTI distance benchmark: `yolo26s-depth_n300`

Generated automatically from `results.json` by `benchmark_kitti_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Detector | `weights/yolo26s-seg.pt`, input size 1280, confidence 0.25 |
| Estimators | `yolo26s-depth_median`, `yolo26s-depth_p10`, `yolo26s-depth_p25` |
| Depth model | `yolo26s-depth`, not given our focal length; inference 12.1 ms median, 18.0 ms p95 per image |
| Camera | height 1.65 m, pitch 0.0 rad; focal length and centre from each image's calibration file |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (public labels) |
| Images | 300, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects | 1187 matched to a detection (IoU >= 0.5) of 1464 labelled |
| Ground truth | laser-measured 3D boxes; scored two ways, see below |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:29:27+00:00 |

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
| yolo26s-depth_median | 1187 | 100% | 6.61 | 11.93 | 37% | 14% | -22.4% |
| yolo26s-depth_p10 | 1187 | 100% | 7.52 | 12.50 | 38% | 14% | -28.3% |
| yolo26s-depth_p25 | 1187 | 100% | 7.07 | 12.23 | 37% | 15% | -25.9% |

## Overall, vs centre

| Estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 1187 | 100% | 8.44 | 13.22 | 36% | 15% | -32.3% |
| yolo26s-depth_p10 | 1187 | 100% | 9.47 | 14.02 | 39% | 10% | -37.4% |
| yolo26s-depth_p25 | 1187 | 100% | 8.93 | 13.66 | 38% | 13% | -35.3% |

## In our path vs beside it

In path: the object's footprint comes within 1.2 m of our car's centre line (it
overlaps our lane), so these are the objects a forward collision warning must get right.
206 of 1187 matched objects are in path.

### Overall, vs nearest surface

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / yolo26s-depth_median | 206 | 100% | 10.30 | 14.24 | 37% | 12% | -29.0% |
| in path / yolo26s-depth_p10 | 206 | 100% | 11.39 | 14.81 | 38% | 16% | -33.9% |
| in path / yolo26s-depth_p25 | 206 | 100% | 10.96 | 14.54 | 38% | 16% | -32.0% |
| beside / yolo26s-depth_median | 981 | 100% | 5.95 | 11.45 | 37% | 15% | -21.0% |
| beside / yolo26s-depth_p10 | 981 | 100% | 6.84 | 12.02 | 38% | 14% | -27.1% |
| beside / yolo26s-depth_p25 | 981 | 100% | 6.44 | 11.75 | 37% | 14% | -24.6% |

### `yolo26s-depth_median` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 1.32 | 1.94 | 29% | 33% | +24.8% |
| 10-20 m | 44 | 100% | 1.81 | 2.54 | 18% | 27% | -1.1% |
| 20-30 m | 46 | 100% | 5.55 | 6.36 | 25% | 13% | -21.8% |
| 30-50 m | 76 | 100% | 21.62 | 20.80 | 51% | 1% | -50.1% |
| 50+ m | 25 | 100% | 38.21 | 36.79 | 60% | 0% | -59.6% |

### `yolo26s-depth_p10` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.72 | 1.39 | 22% | 53% | +14.2% |
| 10-20 m | 44 | 100% | 1.83 | 2.47 | 16% | 39% | -9.4% |
| 20-30 m | 46 | 100% | 6.88 | 7.12 | 28% | 17% | -27.2% |
| 30-50 m | 76 | 100% | 22.63 | 21.67 | 53% | 1% | -52.5% |
| 50+ m | 25 | 100% | 39.39 | 37.86 | 61% | 0% | -61.3% |

### `yolo26s-depth_p25` in path, by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 15 | 100% | 0.83 | 1.55 | 24% | 47% | +17.7% |
| 10-20 m | 44 | 100% | 1.91 | 2.45 | 17% | 39% | -6.2% |
| 20-30 m | 46 | 100% | 6.43 | 6.77 | 27% | 20% | -25.0% |
| 30-50 m | 76 | 100% | 22.20 | 21.30 | 52% | 1% | -51.5% |
| 50+ m | 25 | 100% | 38.77 | 37.42 | 61% | 0% | -60.6% |

### Overall, vs centre

| Scope / estimator | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| in path / yolo26s-depth_median | 206 | 100% | 12.48 | 15.85 | 39% | 16% | -35.1% |
| in path / yolo26s-depth_p10 | 206 | 100% | 13.32 | 16.63 | 41% | 12% | -39.5% |
| in path / yolo26s-depth_p25 | 206 | 100% | 12.94 | 16.26 | 40% | 15% | -37.8% |
| beside / yolo26s-depth_median | 981 | 100% | 7.80 | 12.67 | 36% | 15% | -31.7% |
| beside / yolo26s-depth_p10 | 981 | 100% | 8.73 | 13.48 | 39% | 10% | -36.9% |
| beside / yolo26s-depth_p25 | 981 | 100% | 8.29 | 13.12 | 38% | 13% | -34.8% |

### `yolo26s-depth_median` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.16 | 1.87 | 23% | 36% | +8.6% |
| 10-20 m | 41 | 100% | 1.66 | 2.38 | 15% | 44% | -8.9% |
| 20-30 m | 49 | 100% | 6.14 | 7.01 | 27% | 20% | -25.6% |
| 30-50 m | 74 | 100% | 23.23 | 21.81 | 52% | 3% | -51.3% |
| 50+ m | 31 | 100% | 35.98 | 38.38 | 61% | 0% | -61.4% |

### `yolo26s-depth_p10` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.17 | 1.37 | 18% | 27% | -1.5% |
| 10-20 m | 41 | 100% | 1.74 | 2.81 | 18% | 37% | -16.1% |
| 20-30 m | 49 | 100% | 7.36 | 8.07 | 32% | 12% | -31.2% |
| 30-50 m | 74 | 100% | 24.18 | 22.68 | 54% | 1% | -53.7% |
| 50+ m | 31 | 100% | 36.97 | 39.38 | 63% | 0% | -63.0% |

### `yolo26s-depth_p25` in path, by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 11 | 100% | 1.25 | 1.54 | 20% | 18% | +1.7% |
| 10-20 m | 41 | 100% | 1.55 | 2.55 | 16% | 46% | -13.4% |
| 20-30 m | 49 | 100% | 6.78 | 7.57 | 29% | 14% | -28.9% |
| 30-50 m | 74 | 100% | 23.73 | 22.30 | 53% | 3% | -52.7% |
| 50+ m | 31 | 100% | 36.41 | 38.96 | 62% | 0% | -62.4% |

## `yolo26s-depth_median` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 1.75 | 1.89 | 37% | 20% | +25.0% |
| 10-20 m | 297 | 100% | 2.35 | 2.89 | 19% | 31% | -5.1% |
| 20-30 m | 226 | 100% | 7.24 | 7.33 | 29% | 15% | -27.6% |
| 30-50 m | 319 | 100% | 19.54 | 19.58 | 49% | 1% | -49.2% |
| 50+ m | 135 | 100% | 37.20 | 37.08 | 62% | 0% | -62.1% |

## `yolo26s-depth_median` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 7.92 | 12.43 | 39% | 12% | -24.3% |
| pedestrian | 126 | 100% | 1.74 | 3.05 | 19% | 33% | -0.9% |
| van | 84 | 100% | 14.00 | 16.44 | 47% | 10% | -26.7% |
| truck | 42 | 100% | 16.67 | 21.30 | 46% | 5% | -39.5% |
| cyclist | 20 | 100% | 4.71 | 6.54 | 21% | 40% | -13.5% |

## `yolo26s-depth_p10` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 1.44 | 1.58 | 31% | 23% | +14.5% |
| 10-20 m | 297 | 100% | 2.44 | 3.06 | 20% | 32% | -13.6% |
| 20-30 m | 226 | 100% | 8.43 | 8.37 | 33% | 11% | -32.9% |
| 30-50 m | 319 | 100% | 20.62 | 20.61 | 52% | 0% | -51.9% |
| 50+ m | 135 | 100% | 38.02 | 38.00 | 64% | 0% | -63.6% |

## `yolo26s-depth_p10` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 8.84 | 13.02 | 40% | 12% | -30.1% |
| pedestrian | 126 | 100% | 2.13 | 3.08 | 19% | 33% | -7.9% |
| van | 84 | 100% | 14.71 | 17.19 | 48% | 8% | -32.8% |
| truck | 42 | 100% | 18.19 | 22.45 | 49% | 5% | -44.5% |
| cyclist | 20 | 100% | 4.24 | 7.44 | 25% | 20% | -20.3% |

## `yolo26s-depth_p25` by distance, vs nearest surface

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 210 | 100% | 1.63 | 1.67 | 33% | 21% | +18.4% |
| 10-20 m | 297 | 100% | 2.21 | 2.94 | 19% | 33% | -10.2% |
| 20-30 m | 226 | 100% | 7.88 | 7.90 | 31% | 14% | -30.7% |
| 30-50 m | 319 | 100% | 20.21 | 20.17 | 51% | 0% | -50.7% |
| 50+ m | 135 | 100% | 37.60 | 37.60 | 63% | 0% | -62.9% |

## `yolo26s-depth_p25` by class, vs nearest surface

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 8.39 | 12.75 | 39% | 12% | -27.8% |
| pedestrian | 126 | 100% | 1.90 | 3.04 | 19% | 36% | -5.0% |
| van | 84 | 100% | 14.43 | 16.86 | 47% | 10% | -30.4% |
| truck | 42 | 100% | 17.39 | 21.93 | 47% | 2% | -42.5% |
| cyclist | 20 | 100% | 4.62 | 6.85 | 23% | 25% | -16.6% |

## `yolo26s-depth_median` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.20 | 1.53 | 21% | 29% | -4.4% |
| 10-20 m | 299 | 100% | 2.58 | 3.13 | 21% | 32% | -13.5% |
| 20-30 m | 246 | 100% | 7.87 | 7.85 | 31% | 15% | -30.0% |
| 30-50 m | 329 | 100% | 20.31 | 20.15 | 50% | 1% | -49.9% |
| 50+ m | 155 | 100% | 37.88 | 38.41 | 63% | 0% | -63.1% |

## `yolo26s-depth_median` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 9.75 | 13.68 | 38% | 13% | -34.7% |
| pedestrian | 126 | 100% | 2.16 | 3.16 | 19% | 37% | -5.2% |
| van | 84 | 100% | 16.33 | 18.30 | 44% | 12% | -40.6% |
| truck | 42 | 100% | 22.40 | 26.13 | 52% | 0% | -51.7% |
| cyclist | 20 | 100% | 4.37 | 6.99 | 22% | 25% | -17.2% |

## `yolo26s-depth_p10` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.30 | 1.58 | 21% | 25% | -11.8% |
| 10-20 m | 299 | 100% | 3.15 | 3.64 | 24% | 24% | -21.3% |
| 20-30 m | 246 | 100% | 9.04 | 9.09 | 36% | 4% | -35.5% |
| 30-50 m | 329 | 100% | 21.62 | 21.19 | 53% | 0% | -52.7% |
| 50+ m | 155 | 100% | 38.85 | 39.34 | 65% | 0% | -64.7% |

## `yolo26s-depth_p10` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 10.94 | 14.54 | 41% | 9% | -39.6% |
| pedestrian | 126 | 100% | 2.38 | 3.28 | 19% | 28% | -11.9% |
| van | 84 | 100% | 17.05 | 19.28 | 47% | 7% | -45.3% |
| truck | 42 | 100% | 24.03 | 27.34 | 55% | 0% | -55.4% |
| cyclist | 20 | 100% | 4.90 | 8.09 | 27% | 5% | -23.6% |

## `yolo26s-depth_p25` by distance, vs centre

| Distance | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 158 | 100% | 1.24 | 1.53 | 21% | 24% | -9.0% |
| 10-20 m | 299 | 100% | 2.90 | 3.39 | 22% | 29% | -18.2% |
| 20-30 m | 246 | 100% | 8.67 | 8.54 | 34% | 10% | -33.2% |
| 30-50 m | 329 | 100% | 20.84 | 20.75 | 52% | 1% | -51.5% |
| 50+ m | 155 | 100% | 38.56 | 38.94 | 64% | 0% | -64.0% |

## `yolo26s-depth_p25` by class, vs centre

| Class | Objects | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car | 915 | 100% | 10.44 | 14.16 | 39% | 11% | -37.7% |
| pedestrian | 126 | 100% | 2.24 | 3.20 | 19% | 30% | -9.1% |
| van | 84 | 100% | 16.76 | 18.86 | 46% | 8% | -43.4% |
| truck | 42 | 100% | 23.23 | 26.80 | 54% | 0% | -53.8% |
| cyclist | 20 | 100% | 3.75 | 7.46 | 24% | 20% | -20.1% |

## Estimator latency

| Estimator | Median ms per image |
| --- | --- |
| yolo26s-depth_median | 14.628 |
| yolo26s-depth_p10 | 2.323 |
| yolo26s-depth_p25 | 2.243 |

## Known limitations

- Only objects the detector found are scored; distance quality on missed objects is unknown.
- Camera height and pitch are KITTI's published values, assumed constant; the car pitches
  slightly when braking or on slopes, which the ground-plane method does not model.
- Known-size heights are general real-world averages, not fitted to KITTI.
