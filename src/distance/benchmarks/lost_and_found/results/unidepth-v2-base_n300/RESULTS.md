# Lost and Found distance benchmark: `unidepth-v2-base_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 115.2 ms median, 118.8 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:41:36+00:00 |

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
| unidepth-v2-base_median | 86 | 100% | 1.78 | 1.83 | 16% | 27% | +15.7% |
| unidepth-v2-base_p10 | 86 | 100% | 1.57 | 1.64 | 14% | 34% | +13.9% |
| unidepth-v2-base_p25 | 86 | 100% | 1.63 | 1.71 | 15% | 30% | +14.6% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 436 | 100% | 2.67 | 5.14 | 12% | 46% | +0.9% |
| unidepth-v2-base_p10 | 436 | 100% | 2.57 | 5.53 | 13% | 47% | -2.1% |
| unidepth-v2-base_p25 | 436 | 100% | 2.54 | 5.37 | 12% | 47% | -0.9% |

## `unidepth-v2-base_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.56 | 1.84 | 23% | 4% | +22.9% |
| 10-20 m | 62 | 100% | 1.79 | 1.83 | 13% | 35% | +12.8% |
| 20-30 m | 62 | 100% | 1.42 | 2.00 | 8% | 71% | +6.8% |
| 30-50 m | 147 | 100% | 3.30 | 4.12 | 10% | 58% | -2.1% |
| 50+ m | 141 | 100% | 8.94 | 9.60 | 14% | 35% | -7.5% |

## `unidepth-v2-base_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.44 | 5.26 | 12% | 43% | -1.5% |
| standard objects | 135 | 100% | 3.52 | 6.69 | 15% | 35% | +0.6% |
| emotional hazards | 106 | 100% | 2.45 | 4.37 | 12% | 47% | +2.1% |
| humans | 52 | 100% | 2.03 | 2.33 | 6% | 81% | +6.1% |

## `unidepth-v2-base_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.40 | 1.67 | 21% | 12% | +20.7% |
| 10-20 m | 62 | 100% | 1.62 | 1.63 | 12% | 42% | +11.3% |
| 20-30 m | 62 | 100% | 1.26 | 1.67 | 7% | 77% | +4.4% |
| 30-50 m | 147 | 100% | 3.19 | 4.36 | 10% | 57% | -5.2% |
| 50+ m | 141 | 100% | 9.22 | 10.82 | 16% | 32% | -11.7% |

## `unidepth-v2-base_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.67 | 5.84 | 13% | 43% | -4.3% |
| standard objects | 135 | 100% | 3.42 | 7.61 | 16% | 35% | -2.5% |
| emotional hazards | 106 | 100% | 2.57 | 4.46 | 12% | 49% | -1.8% |
| humans | 52 | 100% | 1.22 | 1.47 | 4% | 87% | +3.9% |

## `unidepth-v2-base_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 1.46 | 1.74 | 22% | 8% | +21.6% |
| 10-20 m | 62 | 100% | 1.68 | 1.70 | 12% | 39% | +11.9% |
| 20-30 m | 62 | 100% | 1.31 | 1.84 | 8% | 76% | +5.5% |
| 30-50 m | 147 | 100% | 3.21 | 4.28 | 10% | 59% | -3.9% |
| 50+ m | 141 | 100% | 8.83 | 10.28 | 15% | 33% | -10.0% |

## `unidepth-v2-base_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 2.62 | 5.60 | 13% | 44% | -3.2% |
| standard objects | 135 | 100% | 3.51 | 7.27 | 15% | 33% | -1.3% |
| emotional hazards | 106 | 100% | 2.36 | 4.40 | 12% | 51% | +0.1% |
| humans | 52 | 100% | 1.67 | 1.75 | 5% | 85% | +4.8% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
