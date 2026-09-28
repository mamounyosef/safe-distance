# Lost and Found distance benchmark: `metric3d-v2-small_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-small_median`, `metric3d-v2-small_p10`, `metric3d-v2-small_p25` |
| Depth model | `metric3d-v2-small`, given our focal length; inference 164.3 ms median, 169.5 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:35:07+00:00 |

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
| metric3d-v2-small_median | 86 | 100% | 0.57 | 0.91 | 7% | 78% | +5.4% |
| metric3d-v2-small_p10 | 86 | 100% | 0.58 | 0.79 | 6% | 81% | +2.9% |
| metric3d-v2-small_p25 | 86 | 100% | 0.63 | 0.82 | 6% | 80% | +3.8% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small_median | 436 | 100% | 3.86 | 8.87 | 19% | 46% | +11.8% |
| metric3d-v2-small_p10 | 436 | 100% | 3.43 | 8.10 | 16% | 49% | +6.1% |
| metric3d-v2-small_p25 | 436 | 100% | 3.56 | 8.26 | 17% | 48% | +8.1% |

## `metric3d-v2-small_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.52 | 0.76 | 10% | 62% | +8.9% |
| 10-20 m | 62 | 100% | 0.62 | 0.96 | 6% | 84% | +4.1% |
| 20-30 m | 62 | 100% | 2.48 | 3.44 | 14% | 52% | +12.2% |
| 30-50 m | 147 | 100% | 5.75 | 8.21 | 20% | 38% | +13.5% |
| 50+ m | 141 | 100% | 12.18 | 16.81 | 27% | 32% | +13.8% |

## `metric3d-v2-small_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.89 | 9.05 | 20% | 41% | +9.4% |
| standard objects | 135 | 100% | 5.31 | 11.38 | 23% | 41% | +14.4% |
| emotional hazards | 106 | 100% | 2.50 | 6.74 | 15% | 62% | +11.4% |
| humans | 52 | 100% | 4.76 | 6.21 | 13% | 37% | +12.8% |

## `metric3d-v2-small_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.44 | 0.54 | 7% | 75% | +5.2% |
| 10-20 m | 62 | 100% | 0.64 | 0.89 | 6% | 84% | +2.1% |
| 20-30 m | 62 | 100% | 1.58 | 2.60 | 11% | 63% | +7.6% |
| 30-50 m | 147 | 100% | 5.09 | 7.09 | 17% | 43% | +7.6% |
| 50+ m | 141 | 100% | 11.45 | 16.02 | 24% | 30% | +5.7% |

## `metric3d-v2-small_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.92 | 8.61 | 18% | 47% | +3.7% |
| standard objects | 135 | 100% | 4.69 | 10.80 | 21% | 41% | +7.0% |
| emotional hazards | 106 | 100% | 2.12 | 5.66 | 13% | 62% | +6.3% |
| humans | 52 | 100% | 3.31 | 4.65 | 10% | 52% | +9.8% |

## `metric3d-v2-small_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.42 | 0.60 | 8% | 71% | +6.4% |
| 10-20 m | 62 | 100% | 0.64 | 0.91 | 6% | 84% | +2.8% |
| 20-30 m | 62 | 100% | 1.87 | 2.83 | 12% | 61% | +9.2% |
| 30-50 m | 147 | 100% | 4.94 | 7.41 | 18% | 40% | +9.7% |
| 50+ m | 141 | 100% | 11.27 | 16.07 | 25% | 30% | +8.6% |

## `metric3d-v2-small_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.19 | 8.66 | 18% | 47% | +5.7% |
| standard objects | 135 | 100% | 4.93 | 10.80 | 21% | 41% | +9.5% |
| emotional hazards | 106 | 100% | 2.12 | 5.99 | 13% | 59% | +8.1% |
| humans | 52 | 100% | 3.62 | 5.20 | 11% | 44% | +10.9% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
