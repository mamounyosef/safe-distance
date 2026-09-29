# Lost and Found distance benchmark: `metric3d-v2-small-fp16_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 87.8 ms median, 97.1 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `7c6bf85` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T13:47:12+00:00 |

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
| metric3d-v2-small-fp16_median | 353 | 100% | 0.82 | 1.13 | 8% | 71% | +6.5% |
| metric3d-v2-small-fp16_p10 | 353 | 100% | 0.69 | 0.97 | 7% | 76% | +4.2% |
| metric3d-v2-small-fp16_p25 | 353 | 100% | 0.73 | 1.02 | 8% | 74% | +5.0% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 1724 | 100% | 3.96 | 8.70 | 19% | 46% | +12.1% |
| metric3d-v2-small-fp16_p10 | 1724 | 100% | 3.47 | 7.89 | 16% | 50% | +6.4% |
| metric3d-v2-small-fp16_p25 | 1724 | 100% | 3.62 | 8.09 | 17% | 48% | +8.5% |

## `metric3d-v2-small-fp16_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.48 | 0.68 | 9% | 69% | +7.0% |
| 10-20 m | 265 | 100% | 0.92 | 1.27 | 8% | 72% | +6.3% |
| 20-30 m | 247 | 100% | 2.15 | 3.25 | 13% | 56% | +10.1% |
| 30-50 m | 584 | 100% | 5.76 | 8.19 | 20% | 37% | +14.8% |
| 50+ m | 540 | 100% | 12.48 | 16.69 | 27% | 33% | +13.8% |

## `metric3d-v2-small-fp16_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 4.24 | 8.55 | 19% | 41% | +8.9% |
| standard objects | 535 | 100% | 5.40 | 11.31 | 23% | 40% | +15.6% |
| emotional hazards | 423 | 100% | 2.16 | 6.50 | 15% | 65% | +10.9% |
| humans | 203 | 100% | 5.73 | 6.79 | 14% | 33% | +14.2% |

## `metric3d-v2-small-fp16_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.40 | 0.55 | 7% | 74% | +4.5% |
| 10-20 m | 265 | 100% | 0.82 | 1.10 | 7% | 77% | +4.0% |
| 20-30 m | 247 | 100% | 1.74 | 2.64 | 10% | 63% | +5.9% |
| 30-50 m | 584 | 100% | 4.85 | 6.85 | 17% | 43% | +8.6% |
| 50+ m | 540 | 100% | 11.07 | 15.96 | 25% | 33% | +5.8% |

## `metric3d-v2-small-fp16_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.66 | 8.09 | 17% | 45% | +3.4% |
| standard objects | 535 | 100% | 4.96 | 10.73 | 21% | 40% | +8.3% |
| emotional hazards | 423 | 100% | 1.83 | 5.37 | 12% | 67% | +5.9% |
| humans | 203 | 100% | 4.10 | 5.15 | 11% | 49% | +10.9% |

## `metric3d-v2-small-fp16_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 0.40 | 0.59 | 7% | 73% | +5.4% |
| 10-20 m | 265 | 100% | 0.87 | 1.17 | 8% | 75% | +4.9% |
| 20-30 m | 247 | 100% | 1.81 | 2.82 | 11% | 61% | +7.4% |
| 30-50 m | 584 | 100% | 5.02 | 7.27 | 18% | 41% | +10.8% |
| 50+ m | 540 | 100% | 11.48 | 16.01 | 25% | 34% | +8.7% |

## `metric3d-v2-small-fp16_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 3.72 | 8.21 | 18% | 45% | +5.4% |
| standard objects | 535 | 100% | 5.24 | 10.72 | 21% | 41% | +10.9% |
| emotional hazards | 423 | 100% | 1.99 | 5.75 | 13% | 65% | +7.8% |
| humans | 203 | 100% | 4.71 | 5.70 | 12% | 42% | +12.1% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
