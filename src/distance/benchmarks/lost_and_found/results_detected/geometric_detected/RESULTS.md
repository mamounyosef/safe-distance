# Lost and Found distance benchmark: `geometric_detected`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `ground_plane`, `combined` |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 718 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the detector's mask of each obstacle it found (real pipeline) |
| Detector | `weights/yoloe-11s-seg.pt`, input size 1280, confidence 0.05, match IoU >= 0.3 |
| Detected | 718 of 1724 labelled obstacles (42%); statistics cover the detected ones |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `2c59c75` |
| Created (UTC) | 2026-09-29T16:20:52+00:00 |

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
| ground_plane | 310 | 100% | 1.78 | 3.24 | 24% | 35% | +19.8% |
| combined | 310 | 100% | 5.57 | 12.70 | 98% | 22% | +96.8% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ground_plane | 718 | 86% | 4.23 | 12.39 | 41% | 26% | +30.6% |
| combined | 718 | 98% | 17.84 | 32.94 | 108% | 14% | +104.4% |

## `ground_plane` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.95 | 1.54 | 19% | 39% | +18.6% |
| 10-20 m | 223 | 100% | 2.07 | 3.91 | 26% | 33% | +20.2% |
| 20-30 m | 137 | 96% | 8.39 | 12.34 | 49% | 20% | +37.6% |
| 30-50 m | 155 | 90% | 16.96 | 27.86 | 68% | 16% | +55.3% |
| 50+ m | 116 | 34% | 24.34 | 29.65 | 50% | 18% | +5.3% |

## `ground_plane` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 98% | 4.11 | 10.21 | 36% | 28% | +22.9% |
| random hazards | 202 | 92% | 3.21 | 8.78 | 33% | 33% | +18.1% |
| humans | 171 | 57% | 17.05 | 29.82 | 76% | 0% | +76.3% |
| standard objects | 142 | 97% | 2.48 | 7.97 | 34% | 33% | +26.2% |

## `combined` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 2.47 | 6.72 | 85% | 24% | +84.3% |
| 10-20 m | 223 | 100% | 7.59 | 15.04 | 103% | 22% | +101.7% |
| 20-30 m | 137 | 96% | 16.82 | 24.48 | 99% | 11% | +95.2% |
| 30-50 m | 155 | 98% | 30.40 | 47.53 | 120% | 9% | +113.5% |
| 50+ m | 116 | 97% | 60.07 | 79.15 | 130% | 4% | +124.0% |

## `combined` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 26.05 | 51.26 | 196% | 1% | +196.3% |
| random hazards | 202 | 97% | 4.98 | 19.25 | 63% | 29% | +56.1% |
| humans | 171 | 100% | 36.72 | 44.93 | 108% | 0% | +108.2% |
| standard objects | 142 | 97% | 2.56 | 10.63 | 41% | 31% | +33.4% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
