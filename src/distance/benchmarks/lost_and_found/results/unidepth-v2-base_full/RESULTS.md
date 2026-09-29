# Lost and Found distance benchmark: `unidepth-v2-base_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 115.7 ms median, 117.8 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:33:54+00:00 |

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
| unidepth-v2-base_median | 353 | 100% | 1.82 | 2.00 | 16% | 25% | +16.2% |
| unidepth-v2-base_p10 | 353 | 100% | 1.62 | 1.80 | 15% | 31% | +14.5% |
| unidepth-v2-base_p25 | 353 | 100% | 1.70 | 1.88 | 15% | 28% | +15.2% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 1724 | 100% | 2.80 | 5.07 | 12% | 46% | +1.2% |
| unidepth-v2-base_p10 | 1724 | 100% | 2.81 | 5.50 | 13% | 47% | -1.9% |
| unidepth-v2-base_p25 | 1724 | 100% | 2.75 | 5.30 | 13% | 47% | -0.7% |

## `unidepth-v2-base_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.79 | 1.87 | 23% | 5% | +23.3% |
| 10-20 m | 265 | 100% | 1.86 | 2.04 | 14% | 31% | +13.9% |
| 20-30 m | 247 | 100% | 1.46 | 2.09 | 8% | 68% | +6.3% |
| 30-50 m | 584 | 100% | 3.09 | 3.89 | 9% | 60% | -1.5% |
| 50+ m | 540 | 100% | 9.05 | 9.71 | 15% | 35% | -8.1% |

## `unidepth-v2-base_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.61 | 5.17 | 13% | 44% | -1.2% |
| standard objects | 535 | 100% | 3.77 | 6.73 | 15% | 33% | +0.9% |
| emotional hazards | 423 | 100% | 2.18 | 4.00 | 12% | 51% | +1.8% |
| humans | 203 | 100% | 2.45 | 2.64 | 7% | 77% | +7.3% |

## `unidepth-v2-base_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.61 | 1.71 | 21% | 10% | +21.3% |
| 10-20 m | 265 | 100% | 1.65 | 1.83 | 13% | 38% | +12.3% |
| 20-30 m | 247 | 100% | 1.31 | 1.78 | 7% | 76% | +4.0% |
| 30-50 m | 584 | 100% | 3.29 | 4.16 | 10% | 58% | -4.8% |
| 50+ m | 540 | 100% | 9.78 | 11.07 | 17% | 31% | -12.2% |

## `unidepth-v2-base_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.90 | 5.72 | 13% | 42% | -4.0% |
| standard objects | 535 | 100% | 3.97 | 7.60 | 16% | 34% | -2.1% |
| emotional hazards | 423 | 100% | 2.68 | 4.33 | 12% | 52% | -2.0% |
| humans | 203 | 100% | 1.62 | 1.78 | 5% | 84% | +4.8% |

## `unidepth-v2-base_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.67 | 1.77 | 22% | 7% | +22.1% |
| 10-20 m | 265 | 100% | 1.72 | 1.91 | 13% | 35% | +12.9% |
| 20-30 m | 247 | 100% | 1.37 | 1.89 | 8% | 74% | +4.9% |
| 30-50 m | 584 | 100% | 3.18 | 4.03 | 10% | 60% | -3.5% |
| 50+ m | 540 | 100% | 9.66 | 10.48 | 16% | 32% | -10.5% |

## `unidepth-v2-base_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.83 | 5.48 | 13% | 44% | -2.9% |
| standard objects | 535 | 100% | 4.06 | 7.28 | 15% | 32% | -1.0% |
| emotional hazards | 423 | 100% | 2.30 | 4.12 | 12% | 52% | -0.3% |
| humans | 203 | 100% | 1.84 | 2.08 | 6% | 83% | +5.8% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
