# Lost and Found distance benchmark: `unidepth-v2-base-nocam_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-base-nocam_median`, `unidepth-v2-base-nocam_p10`, `unidepth-v2-base-nocam_p25` |
| Depth model | `unidepth-v2-base-nocam`, not given our focal length; inference 116.9 ms median, 121.3 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `afa2151` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:46:55+00:00 |

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
| unidepth-v2-base-nocam_median | 353 | 100% | 2.96 | 3.08 | 24% | 18% | +22.7% |
| unidepth-v2-base-nocam_p10 | 353 | 100% | 2.70 | 2.89 | 23% | 19% | +20.8% |
| unidepth-v2-base-nocam_p25 | 353 | 100% | 2.79 | 2.97 | 23% | 19% | +21.6% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base-nocam_median | 1724 | 100% | 4.89 | 7.28 | 19% | 30% | +4.2% |
| unidepth-v2-base-nocam_p10 | 1724 | 100% | 4.58 | 7.39 | 18% | 31% | +0.9% |
| unidepth-v2-base-nocam_p25 | 1724 | 100% | 4.73 | 7.35 | 18% | 31% | +2.3% |

## `unidepth-v2-base-nocam_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 2.28 | 2.40 | 30% | 9% | +29.8% |
| 10-20 m | 265 | 100% | 3.22 | 3.31 | 22% | 21% | +20.3% |
| 20-30 m | 247 | 100% | 3.84 | 4.15 | 17% | 29% | +10.8% |
| 30-50 m | 584 | 100% | 6.05 | 6.51 | 16% | 32% | +1.8% |
| 50+ m | 540 | 100% | 9.74 | 12.29 | 19% | 37% | -8.3% |

## `unidepth-v2-base-nocam_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 5.41 | 7.89 | 20% | 24% | -1.0% |
| standard objects | 535 | 100% | 5.81 | 9.11 | 20% | 24% | +4.1% |
| emotional hazards | 423 | 100% | 3.87 | 5.18 | 17% | 36% | +6.2% |
| humans | 203 | 100% | 4.70 | 5.11 | 15% | 50% | +14.7% |

## `unidepth-v2-base-nocam_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 2.15 | 2.24 | 28% | 14% | +27.7% |
| 10-20 m | 265 | 100% | 2.98 | 3.11 | 21% | 21% | +18.6% |
| 20-30 m | 247 | 100% | 3.49 | 3.71 | 15% | 34% | +8.1% |
| 30-50 m | 584 | 100% | 5.81 | 6.26 | 15% | 35% | -1.9% |
| 50+ m | 540 | 100% | 10.62 | 13.24 | 20% | 34% | -12.3% |

## `unidepth-v2-base-nocam_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 5.66 | 8.34 | 20% | 23% | -3.9% |
| standard objects | 535 | 100% | 5.94 | 9.66 | 21% | 26% | +0.8% |
| emotional hazards | 423 | 100% | 3.50 | 4.91 | 15% | 38% | +2.1% |
| humans | 203 | 100% | 3.87 | 3.95 | 12% | 56% | +12.0% |

## `unidepth-v2-base-nocam_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 2.21 | 2.30 | 29% | 12% | +28.5% |
| 10-20 m | 265 | 100% | 3.08 | 3.19 | 22% | 21% | +19.3% |
| 20-30 m | 247 | 100% | 3.65 | 3.92 | 16% | 32% | +9.3% |
| 30-50 m | 584 | 100% | 6.04 | 6.36 | 16% | 33% | -0.4% |
| 50+ m | 540 | 100% | 10.52 | 12.84 | 19% | 35% | -10.7% |

## `unidepth-v2-base-nocam_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 5.72 | 8.16 | 20% | 22% | -2.8% |
| standard objects | 535 | 100% | 5.81 | 9.45 | 21% | 26% | +2.1% |
| emotional hazards | 423 | 100% | 3.68 | 5.01 | 16% | 37% | +4.0% |
| humans | 203 | 100% | 4.24 | 4.41 | 13% | 52% | +13.2% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
