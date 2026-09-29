# Lost and Found distance benchmark: `combinations_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)`, `min(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)`, `min(metric3d-v2-small_p10,unidepth-v2-base_p10)`, `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` |
| Depth model | `combination of saved runs: metric3d-v2-small_full, metric3d-v2-large_full, unidepth-v2-base_full, unidepth-v2-large_full`, given our focal length; inference sum of members ms median, sum of members ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:11:25+00:00 |

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
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 353 | 100% | 0.61 | 0.72 | 6% | 85% | +2.3% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 353 | 100% | 0.71 | 0.88 | 7% | 78% | +6.1% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 353 | 100% | 0.45 | 0.63 | 5% | 89% | +2.3% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 353 | 100% | 0.61 | 0.78 | 6% | 80% | +5.6% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 353 | 100% | 0.68 | 0.92 | 7% | 78% | +3.9% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 353 | 100% | 1.07 | 1.27 | 10% | 59% | +9.4% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| min(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1724 | 100% | 2.94 | 5.88 | 12% | 55% | -7.8% |
| mean(metric3d-v2-small_p10,unidepth-v2-large_p10) | 1724 | 100% | 3.17 | 5.75 | 12% | 54% | +0.6% |
| min(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1724 | 100% | 2.90 | 5.05 | 10% | 57% | -6.5% |
| mean(metric3d-v2-large_p25,unidepth-v2-large_p10) | 1724 | 100% | 2.20 | 3.83 | 8% | 68% | +0.2% |
| min(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1724 | 100% | 2.65 | 5.74 | 12% | 56% | -5.1% |
| mean(metric3d-v2-small_p10,unidepth-v2-base_p10) | 1724 | 100% | 3.13 | 6.04 | 13% | 50% | +2.2% |

## `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.40 | 0.54 | 7% | 76% | +4.3% |
| 10-20 m | 265 | 100% | 0.65 | 0.78 | 5% | 88% | +1.6% |
| 20-30 m | 247 | 100% | 1.28 | 1.62 | 6% | 82% | -3.6% |
| 30-50 m | 584 | 100% | 4.10 | 4.81 | 12% | 45% | -9.5% |
| 50+ m | 540 | 100% | 10.82 | 12.35 | 18% | 32% | -14.4% |

## `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.52 | 6.13 | 13% | 55% | -10.5% |
| standard objects | 535 | 100% | 3.33 | 7.35 | 13% | 50% | -8.2% |
| emotional hazards | 423 | 100% | 4.09 | 5.35 | 12% | 42% | -9.1% |
| humans | 203 | 100% | 1.51 | 2.38 | 5% | 90% | +3.6% |

## `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.73 | 0.79 | 10% | 65% | +9.7% |
| 10-20 m | 265 | 100% | 0.71 | 0.91 | 6% | 83% | +4.9% |
| 20-30 m | 247 | 100% | 1.17 | 1.74 | 7% | 77% | +1.9% |
| 30-50 m | 584 | 100% | 3.93 | 4.86 | 12% | 53% | -0.1% |
| 50+ m | 540 | 100% | 9.29 | 11.75 | 18% | 28% | -2.8% |

## `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.81 | 5.90 | 13% | 51% | -1.8% |
| standard objects | 535 | 100% | 3.74 | 7.51 | 15% | 45% | +1.5% |
| emotional hazards | 423 | 100% | 2.75 | 4.34 | 10% | 60% | -0.8% |
| humans | 203 | 100% | 3.42 | 3.65 | 8% | 72% | +7.6% |

## `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.30 | 0.43 | 5% | 85% | +3.2% |
| 10-20 m | 265 | 100% | 0.53 | 0.70 | 5% | 90% | +2.0% |
| 20-30 m | 247 | 100% | 1.23 | 1.61 | 6% | 83% | -2.3% |
| 30-50 m | 584 | 100% | 3.87 | 4.57 | 11% | 48% | -8.8% |
| 50+ m | 540 | 100% | 9.66 | 10.02 | 15% | 34% | -11.6% |

## `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.49 | 4.91 | 10% | 59% | -8.2% |
| standard objects | 535 | 100% | 3.33 | 6.08 | 11% | 50% | -6.3% |
| emotional hazards | 423 | 100% | 4.09 | 5.30 | 12% | 44% | -9.0% |
| humans | 203 | 100% | 1.52 | 2.17 | 5% | 95% | +3.2% |

## `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.59 | 0.73 | 9% | 64% | +9.0% |
| 10-20 m | 265 | 100% | 0.63 | 0.80 | 6% | 86% | +4.5% |
| 20-30 m | 247 | 100% | 0.98 | 1.48 | 6% | 87% | +1.3% |
| 30-50 m | 584 | 100% | 2.51 | 3.18 | 8% | 73% | -1.2% |
| 50+ m | 540 | 100% | 6.79 | 7.59 | 12% | 46% | -2.1% |

## `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 1.56 | 3.73 | 8% | 67% | -1.4% |
| standard objects | 535 | 100% | 2.95 | 4.73 | 10% | 60% | +1.4% |
| emotional hazards | 423 | 100% | 2.39 | 3.33 | 8% | 69% | -1.7% |
| humans | 203 | 100% | 2.23 | 2.73 | 6% | 91% | +5.6% |

## `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.40 | 0.55 | 7% | 74% | +4.5% |
| 10-20 m | 265 | 100% | 0.84 | 1.04 | 7% | 79% | +3.7% |
| 20-30 m | 247 | 100% | 1.25 | 1.75 | 7% | 74% | +1.4% |
| 30-50 m | 584 | 100% | 3.27 | 4.31 | 10% | 58% | -5.3% |
| 50+ m | 540 | 100% | 10.04 | 12.26 | 18% | 31% | -13.8% |

## `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.77 | 6.11 | 13% | 51% | -7.7% |
| standard objects | 535 | 100% | 3.82 | 8.14 | 15% | 43% | -5.5% |
| emotional hazards | 423 | 100% | 2.78 | 4.19 | 10% | 61% | -5.6% |
| humans | 203 | 100% | 1.40 | 1.60 | 4% | 93% | +3.7% |

## `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.99 | 1.04 | 13% | 36% | +12.9% |
| 10-20 m | 265 | 100% | 1.13 | 1.34 | 9% | 66% | +8.2% |
| 20-30 m | 247 | 100% | 1.28 | 2.06 | 8% | 71% | +4.9% |
| 30-50 m | 584 | 100% | 4.05 | 5.05 | 12% | 48% | +1.9% |
| 50+ m | 540 | 100% | 8.47 | 12.06 | 18% | 36% | -3.3% |

## `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.28 | 6.48 | 14% | 47% | -0.3% |
| standard objects | 535 | 100% | 3.96 | 8.19 | 17% | 37% | +3.0% |
| emotional hazards | 423 | 100% | 1.89 | 4.02 | 10% | 62% | +1.9% |
| humans | 203 | 100% | 3.20 | 3.37 | 8% | 67% | +7.9% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
