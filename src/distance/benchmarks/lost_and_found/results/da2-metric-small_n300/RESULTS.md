# Lost and Found distance benchmark: `da2-metric-small_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `da2-metric-small_median`, `da2-metric-small_p10`, `da2-metric-small_p25` |
| Depth model | `da2-metric-small`, not given our focal length; inference 40.4 ms median, 44.5 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:30:46+00:00 |

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
| da2-metric-small_median | 86 | 100% | 3.22 | 3.99 | 32% | 12% | +31.1% |
| da2-metric-small_p10 | 86 | 100% | 2.85 | 3.52 | 28% | 17% | +27.3% |
| da2-metric-small_p25 | 86 | 100% | 2.96 | 3.72 | 29% | 14% | +28.8% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| da2-metric-small_median | 436 | 100% | 5.10 | 7.51 | 21% | 31% | +10.9% |
| da2-metric-small_p10 | 436 | 100% | 4.86 | 7.37 | 20% | 33% | +7.1% |
| da2-metric-small_p25 | 436 | 100% | 5.00 | 7.39 | 20% | 33% | +8.7% |

## `da2-metric-small_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.97 | 2.84 | 35% | 0% | +34.9% |
| 10-20 m | 62 | 100% | 3.70 | 4.43 | 30% | 16% | +29.6% |
| 20-30 m | 62 | 100% | 5.22 | 6.94 | 29% | 19% | +26.0% |
| 30-50 m | 147 | 100% | 5.30 | 7.02 | 18% | 37% | +8.8% |
| 50+ m | 141 | 100% | 7.83 | 10.41 | 15% | 42% | -5.8% |

## `da2-metric-small_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 5.18 | 8.02 | 22% | 24% | +8.6% |
| standard objects | 135 | 100% | 5.48 | 8.70 | 22% | 30% | +8.9% |
| emotional hazards | 106 | 100% | 4.29 | 5.76 | 20% | 38% | +12.5% |
| humans | 52 | 100% | 6.11 | 6.53 | 19% | 38% | +19.4% |

## `da2-metric-small_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.66 | 2.53 | 31% | 8% | +31.1% |
| 10-20 m | 62 | 100% | 3.29 | 3.91 | 27% | 21% | +25.8% |
| 20-30 m | 62 | 100% | 4.30 | 6.20 | 26% | 27% | +22.1% |
| 30-50 m | 147 | 100% | 5.12 | 6.44 | 16% | 39% | +4.8% |
| 50+ m | 141 | 100% | 8.12 | 11.18 | 16% | 38% | -9.3% |

## `da2-metric-small_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 5.03 | 7.81 | 21% | 27% | +4.9% |
| standard objects | 135 | 100% | 5.22 | 9.09 | 22% | 28% | +5.0% |
| emotional hazards | 106 | 100% | 3.99 | 5.65 | 18% | 38% | +8.8% |
| humans | 52 | 100% | 4.96 | 5.16 | 16% | 52% | +15.4% |

## `da2-metric-small_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.76 | 2.64 | 32% | 4% | +32.4% |
| 10-20 m | 62 | 100% | 3.49 | 4.14 | 28% | 18% | +27.5% |
| 20-30 m | 62 | 100% | 4.69 | 6.49 | 27% | 24% | +23.6% |
| 30-50 m | 147 | 100% | 5.16 | 6.63 | 17% | 38% | +6.4% |
| 50+ m | 141 | 100% | 7.94 | 10.81 | 16% | 43% | -7.8% |

## `da2-metric-small_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 4.95 | 7.84 | 21% | 29% | +6.2% |
| standard objects | 135 | 100% | 5.31 | 8.90 | 22% | 30% | +6.6% |
| emotional hazards | 106 | 100% | 4.21 | 5.66 | 19% | 35% | +10.4% |
| humans | 52 | 100% | 5.49 | 5.73 | 17% | 50% | +17.2% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
