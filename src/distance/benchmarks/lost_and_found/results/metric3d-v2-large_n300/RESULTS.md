# Lost and Found distance benchmark: `metric3d-v2-large_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-large_median`, `metric3d-v2-large_p10`, `metric3d-v2-large_p25` |
| Depth model | `metric3d-v2-large`, given our focal length; inference 902.0 ms median, 982.4 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:39:53+00:00 |

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
| metric3d-v2-large_median | 86 | 100% | 0.43 | 0.60 | 5% | 85% | +3.4% |
| metric3d-v2-large_p10 | 86 | 100% | 0.37 | 0.57 | 4% | 88% | +1.9% |
| metric3d-v2-large_p25 | 86 | 100% | 0.38 | 0.58 | 4% | 87% | +2.5% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large_median | 436 | 100% | 2.39 | 5.32 | 11% | 62% | +8.9% |
| metric3d-v2-large_p10 | 436 | 100% | 2.32 | 4.36 | 9% | 68% | +4.0% |
| metric3d-v2-large_p25 | 436 | 100% | 2.46 | 4.59 | 10% | 67% | +5.6% |

## `metric3d-v2-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.26 | 0.46 | 6% | 79% | +4.6% |
| 10-20 m | 62 | 100% | 0.51 | 0.66 | 4% | 87% | +2.9% |
| 20-30 m | 62 | 100% | 1.27 | 2.08 | 8% | 82% | +7.3% |
| 30-50 m | 147 | 100% | 3.67 | 4.91 | 12% | 52% | +9.4% |
| 50+ m | 141 | 100% | 6.78 | 10.04 | 16% | 50% | +12.4% |

## `metric3d-v2-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.86 | 5.13 | 11% | 57% | +7.1% |
| standard objects | 135 | 100% | 2.28 | 6.26 | 13% | 59% | +10.2% |
| emotional hazards | 106 | 100% | 1.84 | 4.92 | 12% | 69% | +9.7% |
| humans | 52 | 100% | 4.29 | 4.22 | 8% | 71% | +8.5% |

## `metric3d-v2-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.27 | 0.41 | 5% | 83% | +2.6% |
| 10-20 m | 62 | 100% | 0.39 | 0.64 | 4% | 90% | +1.7% |
| 20-30 m | 62 | 100% | 1.10 | 1.55 | 6% | 85% | +3.9% |
| 30-50 m | 147 | 100% | 2.72 | 3.59 | 9% | 65% | +4.1% |
| 50+ m | 141 | 100% | 6.62 | 8.71 | 14% | 50% | +5.1% |

## `metric3d-v2-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.33 | 4.64 | 10% | 62% | +2.4% |
| standard objects | 135 | 100% | 2.77 | 5.57 | 11% | 61% | +5.4% |
| emotional hazards | 106 | 100% | 1.40 | 2.97 | 8% | 76% | +2.9% |
| humans | 52 | 100% | 3.59 | 3.27 | 7% | 83% | +6.7% |

## `metric3d-v2-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 0.21 | 0.40 | 5% | 83% | +3.5% |
| 10-20 m | 62 | 100% | 0.41 | 0.64 | 4% | 89% | +2.1% |
| 20-30 m | 62 | 100% | 1.08 | 1.72 | 7% | 87% | +5.0% |
| 30-50 m | 147 | 100% | 2.70 | 3.96 | 10% | 64% | +5.8% |
| 50+ m | 141 | 100% | 6.43 | 8.96 | 14% | 50% | +7.4% |

## `metric3d-v2-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.59 | 4.78 | 10% | 61% | +4.0% |
| standard objects | 135 | 100% | 2.49 | 5.55 | 11% | 61% | +6.8% |
| emotional hazards | 106 | 100% | 1.72 | 3.64 | 9% | 76% | +5.3% |
| humans | 52 | 100% | 3.77 | 3.52 | 7% | 83% | +7.2% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
