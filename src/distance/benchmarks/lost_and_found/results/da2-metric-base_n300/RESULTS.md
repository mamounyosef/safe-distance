# Lost and Found distance benchmark: `da2-metric-base_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `da2-metric-base_median`, `da2-metric-base_p10`, `da2-metric-base_p25` |
| Depth model | `da2-metric-base`, not given our focal length; inference 66.4 ms median, 77.5 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:31:36+00:00 |

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
| da2-metric-base_median | 86 | 100% | 3.56 | 4.36 | 35% | 5% | +34.7% |
| da2-metric-base_p10 | 86 | 100% | 3.20 | 3.87 | 31% | 8% | +30.8% |
| da2-metric-base_p25 | 86 | 100% | 3.34 | 4.08 | 33% | 8% | +32.4% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-base_median | 436 | 100% | 4.36 | 6.70 | 20% | 36% | +11.9% |
| da2-metric-base_p10 | 436 | 100% | 4.17 | 6.57 | 19% | 37% | +8.2% |
| da2-metric-base_p25 | 436 | 100% | 4.17 | 6.61 | 19% | 36% | +9.7% |

## `da2-metric-base_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.39 | 3.33 | 41% | 0% | +40.8% |
| 10-20 m | 62 | 100% | 3.96 | 4.76 | 33% | 6% | +32.3% |
| 20-30 m | 62 | 100% | 4.88 | 6.49 | 27% | 24% | +25.7% |
| 30-50 m | 147 | 100% | 4.30 | 6.13 | 15% | 44% | +8.2% |
| 50+ m | 141 | 100% | 5.78 | 8.82 | 13% | 52% | -4.0% |

## `da2-metric-base_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.65 | 6.92 | 21% | 27% | +10.2% |
| standard objects | 135 | 100% | 4.97 | 7.96 | 21% | 34% | +10.2% |
| emotional hazards | 106 | 100% | 3.93 | 5.69 | 20% | 42% | +14.2% |
| humans | 52 | 100% | 3.14 | 4.90 | 17% | 56% | +16.5% |

## `da2-metric-base_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.10 | 3.03 | 37% | 0% | +37.1% |
| 10-20 m | 62 | 100% | 3.45 | 4.20 | 29% | 11% | +28.3% |
| 20-30 m | 62 | 100% | 3.80 | 5.61 | 23% | 29% | +21.3% |
| 30-50 m | 147 | 100% | 4.26 | 5.67 | 14% | 50% | +4.2% |
| 50+ m | 141 | 100% | 6.96 | 9.57 | 14% | 45% | -7.3% |

## `da2-metric-base_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.29 | 6.70 | 19% | 29% | +6.6% |
| standard objects | 135 | 100% | 4.79 | 8.35 | 21% | 30% | +6.2% |
| emotional hazards | 106 | 100% | 3.87 | 5.33 | 18% | 44% | +10.6% |
| humans | 52 | 100% | 2.74 | 4.10 | 14% | 62% | +12.5% |

## `da2-metric-base_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.19 | 3.15 | 39% | 0% | +38.7% |
| 10-20 m | 62 | 100% | 3.64 | 4.44 | 31% | 11% | +30.0% |
| 20-30 m | 62 | 100% | 4.33 | 5.96 | 25% | 24% | +23.0% |
| 30-50 m | 147 | 100% | 4.31 | 5.84 | 15% | 46% | +5.8% |
| 50+ m | 141 | 100% | 6.54 | 9.25 | 14% | 48% | -6.0% |

## `da2-metric-base_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.31 | 6.76 | 20% | 28% | +8.0% |
| standard objects | 135 | 100% | 4.82 | 8.21 | 21% | 32% | +7.8% |
| emotional hazards | 106 | 100% | 3.84 | 5.49 | 19% | 41% | +12.2% |
| humans | 52 | 100% | 3.01 | 4.36 | 15% | 60% | +14.2% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
