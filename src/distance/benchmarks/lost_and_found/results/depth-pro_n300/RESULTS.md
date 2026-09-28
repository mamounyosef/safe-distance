# Lost and Found distance benchmark: `depth-pro_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `depth-pro_median`, `depth-pro_p10`, `depth-pro_p25` |
| Depth model | `depth-pro`, given our focal length; inference 870.5 ms median, 955.5 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:47:45+00:00 |

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
| depth-pro_median | 86 | 100% | 0.83 | 1.32 | 9% | 69% | -3.6% |
| depth-pro_p10 | 86 | 100% | 0.82 | 1.39 | 10% | 66% | -4.8% |
| depth-pro_p25 | 86 | 100% | 0.83 | 1.36 | 10% | 66% | -4.3% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| depth-pro_median | 436 | 100% | 5.05 | 9.52 | 19% | 34% | -15.8% |
| depth-pro_p10 | 436 | 100% | 5.92 | 10.06 | 20% | 32% | -18.0% |
| depth-pro_p25 | 436 | 100% | 5.45 | 9.78 | 19% | 33% | -17.0% |

## `depth-pro_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.48 | 0.60 | 7% | 71% | +2.1% |
| 10-20 m | 62 | 100% | 1.01 | 1.60 | 10% | 68% | -5.8% |
| 20-30 m | 62 | 100% | 2.59 | 2.67 | 11% | 47% | -6.5% |
| 30-50 m | 147 | 100% | 6.43 | 7.61 | 19% | 24% | -16.9% |
| 50+ m | 141 | 100% | 13.55 | 19.52 | 28% | 18% | -26.1% |

## `depth-pro_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.39 | 9.02 | 18% | 41% | -15.8% |
| standard objects | 135 | 100% | 4.86 | 12.33 | 22% | 36% | -19.8% |
| emotional hazards | 106 | 100% | 4.79 | 6.64 | 16% | 33% | -9.5% |
| humans | 52 | 100% | 10.96 | 9.50 | 18% | 13% | -18.1% |

## `depth-pro_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.40 | 0.59 | 7% | 67% | +0.6% |
| 10-20 m | 62 | 100% | 1.07 | 1.69 | 11% | 66% | -6.9% |
| 20-30 m | 62 | 100% | 2.62 | 2.81 | 11% | 47% | -7.9% |
| 30-50 m | 147 | 100% | 7.02 | 8.28 | 20% | 22% | -19.7% |
| 50+ m | 141 | 100% | 14.71 | 20.40 | 30% | 15% | -28.8% |

## `depth-pro_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.69 | 9.47 | 19% | 41% | -17.2% |
| standard objects | 135 | 100% | 5.24 | 12.82 | 23% | 35% | -21.4% |
| emotional hazards | 106 | 100% | 5.87 | 7.16 | 17% | 26% | -13.9% |
| humans | 52 | 100% | 12.39 | 10.43 | 20% | 12% | -19.9% |

## `depth-pro_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.42 | 0.60 | 7% | 67% | +1.2% |
| 10-20 m | 62 | 100% | 1.01 | 1.65 | 10% | 66% | -6.5% |
| 20-30 m | 62 | 100% | 2.58 | 2.75 | 11% | 47% | -7.3% |
| 30-50 m | 147 | 100% | 6.72 | 7.92 | 20% | 24% | -18.4% |
| 50+ m | 141 | 100% | 14.25 | 19.93 | 29% | 17% | -27.6% |

## `depth-pro_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.42 | 9.27 | 19% | 41% | -16.6% |
| standard objects | 135 | 100% | 5.03 | 12.64 | 23% | 35% | -20.8% |
| emotional hazards | 106 | 100% | 5.19 | 6.67 | 16% | 31% | -11.7% |
| humans | 52 | 100% | 11.87 | 10.08 | 19% | 13% | -19.2% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
