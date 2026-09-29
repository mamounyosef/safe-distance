# Lost and Found distance benchmark: `metric3d-v2-large-fp16_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-large-fp16_median`, `metric3d-v2-large-fp16_p10`, `metric3d-v2-large-fp16_p25` |
| Depth model | `metric3d-v2-large-fp16`, given our focal length; inference 363.8 ms median, 387.2 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T13:55:58+00:00 |

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
| metric3d-v2-large-fp16_median | 353 | 100% | 0.49 | 0.75 | 6% | 82% | +4.1% |
| metric3d-v2-large-fp16_p10 | 353 | 100% | 0.43 | 0.70 | 5% | 84% | +2.6% |
| metric3d-v2-large-fp16_p25 | 353 | 100% | 0.45 | 0.71 | 5% | 84% | +3.2% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 1724 | 100% | 2.79 | 5.29 | 12% | 60% | +8.9% |
| metric3d-v2-large-fp16_p10 | 1724 | 100% | 2.29 | 4.23 | 9% | 66% | +4.0% |
| metric3d-v2-large-fp16_p25 | 1724 | 100% | 2.45 | 4.46 | 10% | 65% | +5.6% |

## `metric3d-v2-large-fp16_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.31 | 0.46 | 6% | 81% | +4.2% |
| 10-20 m | 265 | 100% | 0.56 | 0.84 | 6% | 83% | +4.1% |
| 20-30 m | 247 | 100% | 1.54 | 2.25 | 9% | 72% | +6.7% |
| 30-50 m | 584 | 100% | 3.96 | 5.00 | 12% | 49% | +10.1% |
| 50+ m | 540 | 100% | 6.52 | 9.96 | 16% | 51% | +11.9% |

## `metric3d-v2-large-fp16_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.12 | 5.03 | 11% | 54% | +7.0% |
| standard objects | 535 | 100% | 3.09 | 6.63 | 14% | 53% | +11.6% |
| emotional hazards | 423 | 100% | 1.70 | 4.54 | 11% | 71% | +8.5% |
| humans | 203 | 100% | 3.81 | 4.03 | 9% | 71% | +8.5% |

## `metric3d-v2-large-fp16_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.29 | 0.43 | 5% | 86% | +2.5% |
| 10-20 m | 265 | 100% | 0.50 | 0.79 | 5% | 84% | +2.7% |
| 20-30 m | 247 | 100% | 1.20 | 1.83 | 7% | 81% | +3.7% |
| 30-50 m | 584 | 100% | 2.80 | 3.53 | 9% | 65% | +4.6% |
| 50+ m | 540 | 100% | 6.32 | 8.40 | 13% | 50% | +4.5% |

## `metric3d-v2-large-fp16_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.34 | 4.43 | 10% | 61% | +2.4% |
| standard objects | 535 | 100% | 2.82 | 5.69 | 12% | 55% | +6.6% |
| emotional hazards | 423 | 100% | 1.32 | 2.67 | 7% | 78% | +1.8% |
| humans | 203 | 100% | 3.07 | 3.08 | 7% | 84% | +6.4% |

## `metric3d-v2-large-fp16_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.30 | 0.43 | 5% | 85% | +3.2% |
| 10-20 m | 265 | 100% | 0.52 | 0.81 | 5% | 84% | +3.2% |
| 20-30 m | 247 | 100% | 1.24 | 1.94 | 8% | 79% | +4.7% |
| 30-50 m | 584 | 100% | 3.20 | 3.94 | 10% | 60% | +6.3% |
| 50+ m | 540 | 100% | 6.36 | 8.62 | 14% | 51% | +6.8% |

## `metric3d-v2-large-fp16_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.82 | 4.60 | 10% | 58% | +3.9% |
| standard objects | 535 | 100% | 2.70 | 5.75 | 12% | 56% | +8.1% |
| emotional hazards | 423 | 100% | 1.33 | 3.19 | 8% | 78% | +4.0% |
| humans | 203 | 100% | 3.36 | 3.34 | 7% | 80% | +7.0% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
