# Lost and Found distance benchmark: `metric3d-v2-large_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-large_median`, `metric3d-v2-large_p10`, `metric3d-v2-large_p25` |
| Depth model | `metric3d-v2-large`, given our focal length; inference 889.0 ms median, 941.2 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `da640ed` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T11:29:52+00:00 |

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
| metric3d-v2-large_median | 353 | 100% | 0.49 | 0.74 | 6% | 82% | +4.1% |
| metric3d-v2-large_p10 | 353 | 100% | 0.43 | 0.70 | 5% | 84% | +2.6% |
| metric3d-v2-large_p25 | 353 | 100% | 0.45 | 0.71 | 5% | 85% | +3.2% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 1724 | 100% | 2.77 | 5.28 | 12% | 60% | +9.0% |
| metric3d-v2-large_p10 | 1724 | 100% | 2.28 | 4.22 | 9% | 66% | +4.1% |
| metric3d-v2-large_p25 | 1724 | 100% | 2.43 | 4.45 | 10% | 65% | +5.7% |

## `metric3d-v2-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.31 | 0.46 | 6% | 81% | +4.2% |
| 10-20 m | 265 | 100% | 0.56 | 0.84 | 6% | 83% | +4.1% |
| 20-30 m | 247 | 100% | 1.54 | 2.25 | 9% | 72% | +6.7% |
| 30-50 m | 584 | 100% | 3.95 | 5.00 | 12% | 49% | +10.1% |
| 50+ m | 540 | 100% | 6.50 | 9.94 | 16% | 51% | +12.2% |

## `metric3d-v2-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.12 | 5.01 | 11% | 54% | +7.3% |
| standard objects | 535 | 100% | 3.09 | 6.63 | 14% | 53% | +11.6% |
| emotional hazards | 423 | 100% | 1.71 | 4.54 | 11% | 71% | +8.5% |
| humans | 203 | 100% | 3.80 | 4.03 | 9% | 71% | +8.5% |

## `metric3d-v2-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.29 | 0.43 | 5% | 86% | +2.5% |
| 10-20 m | 265 | 100% | 0.50 | 0.79 | 5% | 84% | +2.7% |
| 20-30 m | 247 | 100% | 1.20 | 1.83 | 7% | 81% | +3.7% |
| 30-50 m | 584 | 100% | 2.78 | 3.52 | 9% | 65% | +4.6% |
| 50+ m | 540 | 100% | 6.33 | 8.36 | 13% | 50% | +4.8% |

## `metric3d-v2-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.34 | 4.40 | 10% | 61% | +2.7% |
| standard objects | 535 | 100% | 2.83 | 5.69 | 12% | 55% | +6.6% |
| emotional hazards | 423 | 100% | 1.32 | 2.66 | 7% | 79% | +1.9% |
| humans | 203 | 100% | 3.05 | 3.08 | 7% | 84% | +6.4% |

## `metric3d-v2-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.30 | 0.43 | 5% | 85% | +3.2% |
| 10-20 m | 265 | 100% | 0.51 | 0.80 | 5% | 85% | +3.2% |
| 20-30 m | 247 | 100% | 1.24 | 1.94 | 8% | 79% | +4.7% |
| 30-50 m | 584 | 100% | 3.19 | 3.94 | 10% | 60% | +6.3% |
| 50+ m | 540 | 100% | 6.36 | 8.60 | 14% | 51% | +7.1% |

## `metric3d-v2-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.82 | 4.57 | 10% | 58% | +4.2% |
| standard objects | 535 | 100% | 2.71 | 5.75 | 12% | 56% | +8.1% |
| emotional hazards | 423 | 100% | 1.32 | 3.18 | 8% | 78% | +4.1% |
| humans | 203 | 100% | 3.37 | 3.34 | 7% | 80% | +7.0% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
