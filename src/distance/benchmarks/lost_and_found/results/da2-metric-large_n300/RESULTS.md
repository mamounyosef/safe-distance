# Lost and Found distance benchmark: `da2-metric-large_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `da2-metric-large_median`, `da2-metric-large_p10`, `da2-metric-large_p25` |
| Depth model | `da2-metric-large`, not given our focal length; inference 155.6 ms median, 168.2 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:32:53+00:00 |

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
| da2-metric-large_median | 86 | 100% | 3.35 | 4.05 | 33% | 3% | +32.6% |
| da2-metric-large_p10 | 86 | 100% | 3.03 | 3.65 | 30% | 10% | +29.4% |
| da2-metric-large_p25 | 86 | 100% | 3.19 | 3.80 | 31% | 8% | +30.7% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-large_median | 436 | 100% | 4.56 | 6.29 | 19% | 35% | +11.6% |
| da2-metric-large_p10 | 436 | 100% | 4.57 | 6.25 | 18% | 36% | +8.3% |
| da2-metric-large_p25 | 436 | 100% | 4.58 | 6.23 | 18% | 36% | +9.6% |

## `da2-metric-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.43 | 3.30 | 40% | 0% | +40.4% |
| 10-20 m | 62 | 100% | 3.60 | 4.34 | 30% | 5% | +29.6% |
| 20-30 m | 62 | 100% | 3.77 | 5.69 | 24% | 29% | +22.4% |
| 30-50 m | 147 | 100% | 4.05 | 5.54 | 14% | 48% | +6.7% |
| 50+ m | 141 | 100% | 6.96 | 8.70 | 13% | 43% | -0.7% |

## `da2-metric-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.87 | 6.02 | 19% | 34% | +9.6% |
| standard objects | 135 | 100% | 4.50 | 6.97 | 19% | 36% | +10.2% |
| emotional hazards | 106 | 100% | 4.00 | 4.77 | 17% | 44% | +11.0% |
| humans | 52 | 100% | 7.81 | 8.38 | 22% | 15% | +22.4% |

## `da2-metric-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.20 | 3.01 | 37% | 0% | +36.8% |
| 10-20 m | 62 | 100% | 3.23 | 3.90 | 27% | 15% | +26.6% |
| 20-30 m | 62 | 100% | 3.15 | 5.04 | 21% | 42% | +18.8% |
| 30-50 m | 147 | 100% | 4.02 | 5.42 | 14% | 49% | +3.2% |
| 50+ m | 141 | 100% | 7.79 | 9.23 | 14% | 35% | -4.0% |

## `da2-metric-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.32 | 6.16 | 18% | 31% | +6.2% |
| standard objects | 135 | 100% | 4.41 | 7.17 | 19% | 36% | +6.7% |
| emotional hazards | 106 | 100% | 3.64 | 4.71 | 16% | 48% | +7.7% |
| humans | 52 | 100% | 6.55 | 7.23 | 19% | 25% | +19.4% |

## `da2-metric-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.31 | 3.14 | 38% | 0% | +38.4% |
| 10-20 m | 62 | 100% | 3.34 | 4.06 | 28% | 11% | +27.7% |
| 20-30 m | 62 | 100% | 3.37 | 5.28 | 22% | 35% | +20.1% |
| 30-50 m | 147 | 100% | 3.99 | 5.45 | 14% | 48% | +4.5% |
| 50+ m | 141 | 100% | 7.59 | 8.95 | 13% | 40% | -2.7% |

## `da2-metric-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.14 | 6.10 | 18% | 31% | +7.4% |
| standard objects | 135 | 100% | 4.55 | 7.03 | 19% | 37% | +8.0% |
| emotional hazards | 106 | 100% | 3.61 | 4.68 | 16% | 46% | +9.1% |
| humans | 52 | 100% | 6.97 | 7.69 | 21% | 23% | +20.6% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
