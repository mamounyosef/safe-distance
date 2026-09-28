# Lost and Found distance benchmark: `da3-metric-large_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `da3-metric-large_median`, `da3-metric-large_p10`, `da3-metric-large_p25` |
| Depth model | `da3-metric-large`, given our focal length; inference 89.7 ms median, 98.3 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:33:53+00:00 |

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
| da3-metric-large_median | 86 | 100% | 1.43 | 1.58 | 13% | 47% | +12.4% |
| da3-metric-large_p10 | 86 | 100% | 1.15 | 1.36 | 11% | 58% | +10.5% |
| da3-metric-large_p25 | 86 | 100% | 1.20 | 1.43 | 11% | 53% | +11.2% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da3-metric-large_median | 436 | 100% | 2.59 | 4.24 | 11% | 56% | +4.5% |
| da3-metric-large_p10 | 436 | 100% | 2.19 | 3.93 | 10% | 63% | +0.4% |
| da3-metric-large_p25 | 436 | 100% | 2.26 | 3.93 | 10% | 61% | +1.9% |

## `da3-metric-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.98 | 1.23 | 15% | 42% | +14.9% |
| 10-20 m | 62 | 100% | 1.50 | 1.72 | 12% | 48% | +11.5% |
| 20-30 m | 62 | 100% | 1.27 | 2.02 | 8% | 76% | +6.2% |
| 30-50 m | 147 | 100% | 3.26 | 4.13 | 10% | 57% | +2.5% |
| 50+ m | 141 | 100% | 6.20 | 6.93 | 11% | 50% | +0.9% |

## `da3-metric-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.16 | 4.19 | 11% | 55% | +4.4% |
| standard objects | 135 | 100% | 3.08 | 5.00 | 12% | 46% | +6.6% |
| emotional hazards | 106 | 100% | 2.92 | 4.22 | 12% | 52% | +2.2% |
| humans | 52 | 100% | 2.15 | 2.43 | 6% | 88% | +3.8% |

## `da3-metric-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.75 | 1.09 | 13% | 54% | +12.9% |
| 10-20 m | 62 | 100% | 1.23 | 1.46 | 10% | 60% | +9.6% |
| 20-30 m | 62 | 100% | 1.12 | 1.69 | 7% | 82% | +3.2% |
| 30-50 m | 147 | 100% | 2.72 | 3.86 | 9% | 65% | -1.9% |
| 50+ m | 141 | 100% | 5.62 | 6.56 | 11% | 55% | -4.7% |

## `da3-metric-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 1.82 | 3.75 | 10% | 63% | +0.5% |
| standard objects | 135 | 100% | 2.88 | 4.63 | 11% | 57% | +1.9% |
| emotional hazards | 106 | 100% | 2.78 | 4.28 | 11% | 54% | -2.2% |
| humans | 52 | 100% | 1.42 | 1.90 | 4% | 96% | +1.2% |

## `da3-metric-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.84 | 1.14 | 14% | 50% | +13.6% |
| 10-20 m | 62 | 100% | 1.33 | 1.55 | 11% | 55% | +10.2% |
| 20-30 m | 62 | 100% | 1.16 | 1.80 | 7% | 81% | +4.4% |
| 30-50 m | 147 | 100% | 2.79 | 3.87 | 9% | 62% | -0.2% |
| 50+ m | 141 | 100% | 5.25 | 6.47 | 10% | 57% | -2.5% |

## `da3-metric-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 1.87 | 3.83 | 10% | 60% | +2.0% |
| standard objects | 135 | 100% | 2.93 | 4.61 | 11% | 56% | +3.7% |
| emotional hazards | 106 | 100% | 2.65 | 4.16 | 11% | 53% | -0.4% |
| humans | 52 | 100% | 1.75 | 2.00 | 5% | 94% | +2.1% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
