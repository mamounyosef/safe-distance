# Lost and Found distance benchmark: `geometric_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `ground_plane`, `combined` |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:06:25+00:00 |

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
| ground_plane | 353 | 100% | 1.56 | 3.00 | 22% | 41% | +16.9% |
| combined | 353 | 100% | 1.56 | 3.00 | 22% | 41% | +16.9% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 1724 | 85% | 9.51 | 16.90 | 42% | 23% | +19.8% |
| combined | 1724 | 85% | 9.51 | 16.90 | 42% | 23% | +19.8% |

## `ground_plane` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.81 | 1.39 | 17% | 49% | +16.6% |
| 10-20 m | 265 | 100% | 1.82 | 3.54 | 23% | 39% | +17.1% |
| 20-30 m | 247 | 94% | 6.95 | 11.29 | 45% | 20% | +31.7% |
| 30-50 m | 584 | 89% | 15.21 | 21.78 | 54% | 18% | +32.8% |
| 50+ m | 540 | 67% | 25.70 | 27.03 | 42% | 13% | -3.7% |

## `ground_plane` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 88% | 9.59 | 15.77 | 43% | 23% | +18.1% |
| standard objects | 535 | 89% | 10.71 | 16.68 | 36% | 24% | +6.5% |
| emotional hazards | 423 | 91% | 7.79 | 15.51 | 39% | 26% | +24.5% |
| humans | 203 | 52% | 14.35 | 28.47 | 71% | 2% | +70.8% |

## `combined` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.81 | 1.39 | 17% | 49% | +16.6% |
| 10-20 m | 265 | 100% | 1.82 | 3.54 | 23% | 39% | +17.1% |
| 20-30 m | 247 | 94% | 6.95 | 11.29 | 45% | 20% | +31.7% |
| 30-50 m | 584 | 89% | 15.21 | 21.78 | 54% | 18% | +32.8% |
| 50+ m | 540 | 67% | 25.70 | 27.03 | 42% | 13% | -3.7% |

## `combined` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 88% | 9.59 | 15.77 | 43% | 23% | +18.1% |
| standard objects | 535 | 89% | 10.71 | 16.68 | 36% | 24% | +6.5% |
| emotional hazards | 423 | 91% | 7.79 | 15.51 | 39% | 26% | +24.5% |
| humans | 203 | 52% | 14.35 | 28.47 | 71% | 2% | +70.8% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
