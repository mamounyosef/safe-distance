# Lost and Found distance benchmark: `unidepth-v2-small_n300`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-small_median`, `unidepth-v2-small_p10`, `unidepth-v2-small_p25` |
| Depth model | `unidepth-v2-small`, given our focal length; inference 63.8 ms median, 65.3 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 301 (every 4th frame) |
| Obstacles | 436 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `f34bd71` (with uncommitted changes) |
| Created (UTC) | 2026-09-28T19:40:35+00:00 |

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
| unidepth-v2-small_median | 86 | 100% | 2.80 | 2.95 | 24% | 6% | +24.2% |
| unidepth-v2-small_p10 | 86 | 100% | 2.45 | 2.68 | 22% | 9% | +22.1% |
| unidepth-v2-small_p25 | 86 | 100% | 2.57 | 2.78 | 23% | 6% | +22.9% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-small_median | 436 | 100% | 3.57 | 5.09 | 14% | 39% | +5.5% |
| unidepth-v2-small_p10 | 436 | 100% | 3.54 | 5.46 | 14% | 40% | +1.6% |
| unidepth-v2-small_p25 | 436 | 100% | 3.60 | 5.25 | 14% | 41% | +3.1% |

## `unidepth-v2-small_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.33 | 2.50 | 31% | 0% | +31.1% |
| 10-20 m | 62 | 100% | 2.99 | 3.13 | 22% | 8% | +21.6% |
| 20-30 m | 62 | 100% | 2.90 | 3.20 | 13% | 42% | +11.8% |
| 30-50 m | 147 | 100% | 3.80 | 4.46 | 11% | 50% | +2.5% |
| 50+ m | 141 | 100% | 6.43 | 7.88 | 12% | 48% | -5.7% |

## `unidepth-v2-small_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.86 | 5.15 | 15% | 31% | +5.1% |
| standard objects | 135 | 100% | 4.13 | 6.60 | 17% | 35% | +6.8% |
| emotional hazards | 106 | 100% | 3.49 | 4.22 | 13% | 43% | +3.4% |
| humans | 52 | 100% | 2.36 | 2.77 | 9% | 65% | +7.3% |

## `unidepth-v2-small_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.06 | 2.30 | 29% | 0% | +28.6% |
| 10-20 m | 62 | 100% | 2.77 | 2.83 | 20% | 13% | +19.6% |
| 20-30 m | 62 | 100% | 2.37 | 2.62 | 11% | 52% | +8.2% |
| 30-50 m | 147 | 100% | 3.42 | 4.23 | 10% | 56% | -1.5% |
| 50+ m | 141 | 100% | 8.02 | 9.67 | 14% | 37% | -10.6% |

## `unidepth-v2-small_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.70 | 5.44 | 14% | 35% | +1.5% |
| standard objects | 135 | 100% | 4.34 | 7.33 | 17% | 29% | +2.3% |
| emotional hazards | 106 | 100% | 3.28 | 4.41 | 13% | 44% | -0.7% |
| humans | 52 | 100% | 2.65 | 2.77 | 8% | 73% | +4.7% |

## `unidepth-v2-small_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 24 | 100% | 2.20 | 2.38 | 30% | 0% | +29.6% |
| 10-20 m | 62 | 100% | 2.87 | 2.94 | 21% | 8% | +20.3% |
| 20-30 m | 62 | 100% | 2.33 | 2.82 | 12% | 52% | +9.7% |
| 30-50 m | 147 | 100% | 3.60 | 4.28 | 10% | 56% | +0.1% |
| 50+ m | 141 | 100% | 7.28 | 8.83 | 13% | 43% | -8.6% |

## `unidepth-v2-small_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 143 | 100% | 3.65 | 5.29 | 14% | 37% | +2.8% |
| standard objects | 135 | 100% | 4.27 | 6.99 | 17% | 33% | +4.0% |
| emotional hazards | 106 | 100% | 3.56 | 4.25 | 13% | 44% | +1.2% |
| humans | 52 | 100% | 2.45 | 2.67 | 8% | 69% | +5.7% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
