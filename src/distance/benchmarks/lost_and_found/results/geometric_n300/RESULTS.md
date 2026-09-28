# Lost and Found distance benchmark: `geometric_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `ground_plane`, `combined` |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:29:59+00:00 |

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
| ground_plane | 86 | 100% | 1.59 | 2.32 | 17% | 40% | +11.8% |
| combined | 86 | 100% | 1.59 | 2.32 | 17% | 40% | +11.8% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 436 | 86% | 10.56 | 17.90 | 43% | 21% | +21.6% |
| combined | 436 | 86% | 10.56 | 17.90 | 43% | 21% | +21.6% |

## `ground_plane` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.79 | 1.40 | 17% | 50% | +15.7% |
| 10-20 m | 62 | 100% | 1.79 | 2.68 | 17% | 35% | +10.3% |
| 20-30 m | 62 | 94% | 7.40 | 12.71 | 54% | 22% | +44.7% |
| 30-50 m | 147 | 92% | 16.13 | 23.19 | 57% | 16% | +37.1% |
| 50+ m | 141 | 70% | 26.74 | 27.34 | 41% | 12% | -4.7% |

## `ground_plane` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 89% | 10.22 | 17.23 | 46% | 21% | +20.5% |
| standard objects | 135 | 93% | 12.36 | 17.13 | 36% | 21% | +6.6% |
| emotional hazards | 106 | 92% | 8.82 | 16.22 | 40% | 28% | +28.2% |
| humans | 52 | 50% | 14.81 | 31.19 | 75% | 0% | +75.3% |

## `combined` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.79 | 1.40 | 17% | 50% | +15.7% |
| 10-20 m | 62 | 100% | 1.79 | 2.68 | 17% | 35% | +10.3% |
| 20-30 m | 62 | 94% | 7.40 | 12.71 | 54% | 22% | +44.7% |
| 30-50 m | 147 | 92% | 16.13 | 23.19 | 57% | 16% | +37.1% |
| 50+ m | 141 | 70% | 26.74 | 27.34 | 41% | 12% | -4.7% |

## `combined` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 89% | 10.22 | 17.23 | 46% | 21% | +20.5% |
| standard objects | 135 | 93% | 12.36 | 17.13 | 36% | 21% | +6.6% |
| emotional hazards | 106 | 92% | 8.82 | 16.22 | 40% | 28% | +28.2% |
| humans | 52 | 50% | 14.81 | 31.19 | 75% | 0% | +75.3% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
