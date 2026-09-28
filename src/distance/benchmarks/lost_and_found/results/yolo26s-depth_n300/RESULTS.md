# Lost and Found distance benchmark: `yolo26s-depth_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `yolo26s-depth_median`, `yolo26s-depth_p10`, `yolo26s-depth_p25` |
| Depth model | `yolo26s-depth`, not given our focal length; inference 15.3 ms median, 19.1 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:48:14+00:00 |

## Metrics

- **Coverage**: share of obstacles the estimator answered for, rather than returning unknown.
- **Median / mean error**: absolute distance error in metres (mean = MAE, Mean Absolute Error).
- **Relative error**: average absolute error as a percentage of the true distance.
- **Within 10%**: share of answers within 10% of the true distance.
- **Bias**: average signed error; negative = estimates too close, positive = too far.
- **0 to 20 m**: the range where the detector reliably finds obstacles, and where
  stereo ground truth is most trustworthy. Runs are ranked by it.

## 0 to 20 m

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 86 | 100% | 3.07 | 3.34 | 24% | 15% | -23.5% |
| yolo26s-depth_p10 | 86 | 100% | 3.57 | 3.80 | 28% | 9% | -27.7% |
| yolo26s-depth_p25 | 86 | 100% | 3.36 | 3.61 | 26% | 10% | -26.0% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yolo26s-depth_median | 436 | 100% | 18.82 | 21.92 | 46% | 5% | -46.2% |
| yolo26s-depth_p10 | 436 | 100% | 19.38 | 22.55 | 48% | 3% | -48.4% |
| yolo26s-depth_p25 | 436 | 100% | 19.13 | 22.30 | 48% | 3% | -47.5% |

## `yolo26s-depth_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.98 | 1.23 | 15% | 42% | -14.3% |
| 10-20 m | 62 | 100% | 3.96 | 4.16 | 28% | 5% | -27.0% |
| 20-30 m | 62 | 100% | 7.84 | 7.96 | 31% | 13% | -30.7% |
| 30-50 m | 147 | 100% | 19.04 | 19.78 | 49% | 0% | -48.8% |
| 50+ m | 141 | 100% | 38.94 | 41.63 | 64% | 0% | -64.1% |

## `yolo26s-depth_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 16.34 | 19.44 | 44% | 4% | -44.4% |
| standard objects | 135 | 100% | 22.26 | 24.51 | 47% | 6% | -46.9% |
| emotional hazards | 106 | 100% | 17.80 | 19.51 | 46% | 8% | -45.1% |
| humans | 52 | 100% | 34.12 | 26.96 | 51% | 0% | -51.3% |

## `yolo26s-depth_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.33 | 1.57 | 19% | 21% | -19.2% |
| 10-20 m | 62 | 100% | 4.44 | 4.66 | 31% | 5% | -30.9% |
| 20-30 m | 62 | 100% | 8.53 | 8.61 | 34% | 8% | -34.0% |
| 30-50 m | 147 | 100% | 19.63 | 20.52 | 51% | 0% | -50.6% |
| 50+ m | 141 | 100% | 39.47 | 42.23 | 65% | 0% | -65.0% |

## `yolo26s-depth_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 17.07 | 20.02 | 46% | 1% | -46.5% |
| standard objects | 135 | 100% | 23.19 | 25.20 | 49% | 4% | -49.4% |
| emotional hazards | 106 | 100% | 18.20 | 20.07 | 48% | 6% | -47.5% |
| humans | 52 | 100% | 35.44 | 27.67 | 53% | 0% | -53.2% |

## `yolo26s-depth_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.19 | 1.43 | 18% | 25% | -17.3% |
| 10-20 m | 62 | 100% | 4.27 | 4.46 | 30% | 5% | -29.4% |
| 20-30 m | 62 | 100% | 8.21 | 8.35 | 33% | 10% | -32.7% |
| 30-50 m | 147 | 100% | 19.37 | 20.23 | 50% | 0% | -49.9% |
| 50+ m | 141 | 100% | 39.18 | 41.99 | 65% | 0% | -64.6% |

## `yolo26s-depth_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 16.80 | 19.80 | 46% | 1% | -45.7% |
| standard objects | 135 | 100% | 22.69 | 24.93 | 49% | 4% | -48.4% |
| emotional hazards | 106 | 100% | 18.06 | 19.83 | 47% | 7% | -46.5% |
| humans | 52 | 100% | 34.90 | 27.40 | 52% | 0% | -52.5% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
