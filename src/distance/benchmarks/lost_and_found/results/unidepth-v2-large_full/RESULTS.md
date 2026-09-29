# Lost and Found distance benchmark: `unidepth-v2-large_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 217.7 ms median, 219.8 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:39:50+00:00 |

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
| unidepth-v2-large_median | 353 | 100% | 1.03 | 1.13 | 10% | 60% | +9.3% |
| unidepth-v2-large_p10 | 353 | 100% | 0.91 | 1.01 | 9% | 66% | +8.0% |
| unidepth-v2-large_p25 | 353 | 100% | 0.96 | 1.05 | 9% | 64% | +8.5% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 1724 | 100% | 2.75 | 4.59 | 10% | 54% | -2.6% |
| unidepth-v2-large_p10 | 1724 | 100% | 2.99 | 5.16 | 11% | 52% | -5.2% |
| unidepth-v2-large_p25 | 1724 | 100% | 2.98 | 4.94 | 11% | 52% | -4.2% |

## `unidepth-v2-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.28 | 1.32 | 17% | 19% | +16.5% |
| 10-20 m | 265 | 100% | 0.94 | 1.06 | 8% | 73% | +7.0% |
| 20-30 m | 247 | 100% | 0.98 | 1.49 | 6% | 85% | -0.3% |
| 30-50 m | 584 | 100% | 3.30 | 4.02 | 10% | 57% | -6.2% |
| 50+ m | 540 | 100% | 8.30 | 8.88 | 14% | 31% | -7.5% |

## `unidepth-v2-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.20 | 4.23 | 10% | 58% | -4.5% |
| standard objects | 535 | 100% | 3.09 | 5.09 | 11% | 49% | -2.7% |
| emotional hazards | 423 | 100% | 3.49 | 4.95 | 12% | 46% | -4.3% |
| humans | 203 | 100% | 1.81 | 3.50 | 7% | 70% | +6.6% |

## `unidepth-v2-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.11 | 1.19 | 15% | 25% | +14.9% |
| 10-20 m | 265 | 100% | 0.83 | 0.94 | 7% | 79% | +5.7% |
| 20-30 m | 247 | 100% | 1.21 | 1.60 | 6% | 82% | -2.0% |
| 30-50 m | 584 | 100% | 3.87 | 4.57 | 11% | 48% | -8.8% |
| 50+ m | 540 | 100% | 9.66 | 10.16 | 16% | 32% | -11.3% |

## `unidepth-v2-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.49 | 4.98 | 11% | 53% | -6.9% |
| standard objects | 535 | 100% | 3.36 | 6.17 | 12% | 46% | -5.2% |
| emotional hazards | 423 | 100% | 4.09 | 5.36 | 13% | 39% | -7.4% |
| humans | 203 | 100% | 1.83 | 2.61 | 5% | 88% | +4.1% |

## `unidepth-v2-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.17 | 1.24 | 16% | 23% | +15.5% |
| 10-20 m | 265 | 100% | 0.87 | 0.99 | 7% | 78% | +6.2% |
| 20-30 m | 247 | 100% | 1.02 | 1.55 | 6% | 83% | -1.4% |
| 30-50 m | 584 | 100% | 3.70 | 4.36 | 11% | 51% | -7.8% |
| 50+ m | 540 | 100% | 9.21 | 9.66 | 15% | 30% | -9.9% |

## `unidepth-v2-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.43 | 4.68 | 11% | 54% | -6.0% |
| standard objects | 535 | 100% | 3.46 | 5.81 | 12% | 46% | -4.3% |
| emotional hazards | 423 | 100% | 3.90 | 5.15 | 13% | 42% | -6.1% |
| humans | 203 | 100% | 1.82 | 2.92 | 6% | 79% | +5.0% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
