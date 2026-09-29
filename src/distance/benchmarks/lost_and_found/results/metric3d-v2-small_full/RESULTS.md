# Lost and Found distance benchmark: `metric3d-v2-small_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-small_median`, `metric3d-v2-small_p10`, `metric3d-v2-small_p25` |
| Depth model | `metric3d-v2-small`, given our focal length; inference 156.4 ms median, 167.2 ms p95 per frame |
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
| metric3d-v2-small_median | 353 | 100% | 0.82 | 1.13 | 8% | 71% | +6.5% |
| metric3d-v2-small_p10 | 353 | 100% | 0.68 | 0.97 | 7% | 76% | +4.2% |
| metric3d-v2-small_p25 | 353 | 100% | 0.73 | 1.03 | 8% | 74% | +5.1% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small_median | 1724 | 100% | 3.96 | 8.68 | 19% | 45% | +12.1% |
| metric3d-v2-small_p10 | 1724 | 100% | 3.48 | 7.87 | 16% | 50% | +6.4% |
| metric3d-v2-small_p25 | 1724 | 100% | 3.62 | 8.07 | 17% | 49% | +8.5% |

## `metric3d-v2-small_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.48 | 0.69 | 9% | 69% | +7.0% |
| 10-20 m | 265 | 100% | 0.92 | 1.28 | 8% | 72% | +6.3% |
| 20-30 m | 247 | 100% | 2.16 | 3.25 | 13% | 55% | +10.1% |
| 30-50 m | 584 | 100% | 5.74 | 8.17 | 20% | 37% | +14.8% |
| 50+ m | 540 | 100% | 12.44 | 16.65 | 26% | 33% | +13.7% |

## `metric3d-v2-small_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 4.26 | 8.55 | 19% | 41% | +8.9% |
| standard objects | 535 | 100% | 5.40 | 11.27 | 23% | 40% | +15.5% |
| emotional hazards | 423 | 100% | 2.16 | 6.44 | 14% | 65% | +10.9% |
| humans | 203 | 100% | 5.81 | 6.87 | 15% | 33% | +14.5% |

## `metric3d-v2-small_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.40 | 0.55 | 7% | 74% | +4.5% |
| 10-20 m | 265 | 100% | 0.81 | 1.11 | 7% | 77% | +4.1% |
| 20-30 m | 247 | 100% | 1.75 | 2.65 | 11% | 63% | +5.8% |
| 30-50 m | 584 | 100% | 4.82 | 6.83 | 17% | 43% | +8.7% |
| 50+ m | 540 | 100% | 11.08 | 15.91 | 25% | 33% | +5.7% |

## `metric3d-v2-small_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.66 | 8.09 | 17% | 45% | +3.4% |
| standard objects | 535 | 100% | 4.96 | 10.68 | 21% | 40% | +8.2% |
| emotional hazards | 423 | 100% | 1.83 | 5.34 | 12% | 68% | +5.9% |
| humans | 203 | 100% | 4.17 | 5.19 | 11% | 49% | +11.0% |

## `metric3d-v2-small_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.40 | 0.59 | 7% | 73% | +5.4% |
| 10-20 m | 265 | 100% | 0.87 | 1.17 | 8% | 75% | +5.0% |
| 20-30 m | 247 | 100% | 1.81 | 2.82 | 11% | 61% | +7.3% |
| 30-50 m | 584 | 100% | 5.00 | 7.25 | 18% | 42% | +10.8% |
| 50+ m | 540 | 100% | 11.49 | 15.96 | 25% | 34% | +8.6% |

## `metric3d-v2-small_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.73 | 8.21 | 18% | 45% | +5.4% |
| standard objects | 535 | 100% | 5.26 | 10.67 | 21% | 41% | +10.8% |
| emotional hazards | 423 | 100% | 1.99 | 5.71 | 13% | 66% | +7.7% |
| humans | 203 | 100% | 4.78 | 5.75 | 12% | 42% | +12.3% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
