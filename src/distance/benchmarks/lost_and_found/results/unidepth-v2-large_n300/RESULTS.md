# Lost and Found distance benchmark: `unidepth-v2-large_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 217.0 ms median, 219.1 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:43:08+00:00 |

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
| unidepth-v2-large_median | 86 | 100% | 1.02 | 1.06 | 10% | 58% | +9.4% |
| unidepth-v2-large_p10 | 86 | 100% | 0.90 | 0.94 | 8% | 66% | +8.0% |
| unidepth-v2-large_p25 | 86 | 100% | 0.94 | 0.99 | 9% | 65% | +8.5% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 436 | 100% | 2.68 | 4.62 | 10% | 53% | -2.7% |
| unidepth-v2-large_p10 | 436 | 100% | 2.74 | 5.14 | 11% | 52% | -5.2% |
| unidepth-v2-large_p25 | 436 | 100% | 2.86 | 4.94 | 11% | 51% | -4.3% |

## `unidepth-v2-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.20 | 1.30 | 16% | 21% | +16.2% |
| 10-20 m | 62 | 100% | 0.98 | 0.97 | 7% | 73% | +6.8% |
| 20-30 m | 62 | 100% | 0.77 | 1.36 | 5% | 87% | -0.1% |
| 30-50 m | 147 | 100% | 3.19 | 4.09 | 10% | 59% | -6.7% |
| 50+ m | 141 | 100% | 8.19 | 8.78 | 14% | 29% | -7.0% |

## `unidepth-v2-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.15 | 4.16 | 10% | 56% | -4.2% |
| standard objects | 135 | 100% | 2.55 | 5.10 | 11% | 48% | -3.5% |
| emotional hazards | 106 | 100% | 3.39 | 5.08 | 12% | 46% | -3.9% |
| humans | 52 | 100% | 2.29 | 3.68 | 7% | 73% | +6.5% |

## `unidepth-v2-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.07 | 1.15 | 14% | 25% | +14.3% |
| 10-20 m | 62 | 100% | 0.87 | 0.86 | 6% | 82% | +5.6% |
| 20-30 m | 62 | 100% | 1.07 | 1.46 | 6% | 85% | -1.7% |
| 30-50 m | 147 | 100% | 3.85 | 4.58 | 11% | 47% | -9.2% |
| 50+ m | 141 | 100% | 9.27 | 9.90 | 15% | 35% | -10.8% |

## `unidepth-v2-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.11 | 4.94 | 11% | 54% | -6.8% |
| standard objects | 135 | 100% | 3.01 | 6.12 | 12% | 47% | -5.9% |
| emotional hazards | 106 | 100% | 3.88 | 5.36 | 13% | 40% | -7.0% |
| humans | 52 | 100% | 1.87 | 2.72 | 5% | 87% | +4.2% |

## `unidepth-v2-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.15 | 1.21 | 15% | 25% | +15.0% |
| 10-20 m | 62 | 100% | 0.89 | 0.90 | 7% | 81% | +6.0% |
| 20-30 m | 62 | 100% | 0.94 | 1.42 | 6% | 85% | -1.1% |
| 30-50 m | 147 | 100% | 3.55 | 4.40 | 11% | 50% | -8.2% |
| 50+ m | 141 | 100% | 8.66 | 9.47 | 15% | 29% | -9.3% |

## `unidepth-v2-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.24 | 4.63 | 11% | 56% | -5.9% |
| standard objects | 135 | 100% | 2.83 | 5.79 | 12% | 46% | -5.1% |
| emotional hazards | 106 | 100% | 3.92 | 5.22 | 13% | 40% | -5.7% |
| humans | 52 | 100% | 2.05 | 3.04 | 6% | 77% | +5.1% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
