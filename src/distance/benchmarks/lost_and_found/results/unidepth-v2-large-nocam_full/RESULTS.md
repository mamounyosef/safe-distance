# Lost and Found distance benchmark: `unidepth-v2-large-nocam_full`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-large-nocam_median`, `unidepth-v2-large-nocam_p10`, `unidepth-v2-large-nocam_p25` |
| Depth model | `unidepth-v2-large-nocam`, not given our focal length; inference 217.6 ms median, 243.4 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 1724 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the labelled outline (distance quality only, independent of detection) |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `afa2151` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T15:53:00+00:00 |

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
| unidepth-v2-large-nocam_median | 353 | 100% | 1.59 | 1.57 | 13% | 40% | +11.8% |
| unidepth-v2-large-nocam_p10 | 353 | 100% | 1.46 | 1.43 | 12% | 44% | +10.4% |
| unidepth-v2-large-nocam_p25 | 353 | 100% | 1.51 | 1.48 | 12% | 43% | +10.9% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large-nocam_median | 1724 | 100% | 3.23 | 5.42 | 13% | 44% | -1.0% |
| unidepth-v2-large-nocam_p10 | 1724 | 100% | 3.26 | 5.83 | 13% | 44% | -3.7% |
| unidepth-v2-large-nocam_p25 | 1724 | 100% | 3.23 | 5.67 | 13% | 44% | -2.7% |

## `unidepth-v2-large-nocam_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.60 | 1.56 | 20% | 12% | +19.6% |
| 10-20 m | 265 | 100% | 1.58 | 1.57 | 11% | 49% | +9.2% |
| 20-30 m | 247 | 100% | 1.24 | 1.87 | 8% | 75% | +2.3% |
| 30-50 m | 584 | 100% | 3.39 | 4.52 | 11% | 57% | -4.3% |
| 50+ m | 540 | 100% | 10.66 | 10.53 | 16% | 20% | -7.3% |

## `unidepth-v2-large-nocam_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.32 | 4.94 | 12% | 50% | -3.5% |
| standard objects | 535 | 100% | 3.96 | 6.33 | 14% | 38% | -3.5% |
| emotional hazards | 423 | 100% | 2.92 | 4.51 | 12% | 52% | -1.4% |
| humans | 203 | 100% | 4.87 | 6.26 | 13% | 31% | +13.2% |

## `unidepth-v2-large-nocam_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.47 | 1.44 | 18% | 18% | +17.8% |
| 10-20 m | 265 | 100% | 1.45 | 1.43 | 10% | 53% | +7.9% |
| 20-30 m | 247 | 100% | 1.16 | 1.76 | 7% | 77% | +0.5% |
| 30-50 m | 584 | 100% | 3.74 | 4.79 | 12% | 51% | -7.1% |
| 50+ m | 540 | 100% | 10.84 | 11.69 | 18% | 20% | -11.2% |

## `unidepth-v2-large-nocam_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.37 | 5.55 | 13% | 49% | -6.0% |
| standard objects | 535 | 100% | 4.27 | 7.24 | 15% | 37% | -6.0% |
| emotional hazards | 423 | 100% | 3.26 | 4.85 | 12% | 46% | -4.7% |
| humans | 203 | 100% | 3.73 | 4.94 | 11% | 43% | +10.5% |

## `unidepth-v2-large-nocam_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 88 | 100% | 1.53 | 1.48 | 19% | 17% | +18.5% |
| 10-20 m | 265 | 100% | 1.48 | 1.48 | 10% | 52% | +8.4% |
| 20-30 m | 247 | 100% | 1.14 | 1.79 | 7% | 76% | +1.1% |
| 30-50 m | 584 | 100% | 3.61 | 4.68 | 11% | 53% | -6.0% |
| 50+ m | 540 | 100% | 10.75 | 11.25 | 17% | 21% | -9.7% |

## `unidepth-v2-large-nocam_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random hazards | 563 | 100% | 2.27 | 5.30 | 12% | 50% | -5.1% |
| standard objects | 535 | 100% | 4.19 | 6.94 | 14% | 37% | -5.2% |
| emotional hazards | 423 | 100% | 3.09 | 4.66 | 12% | 49% | -3.2% |
| humans | 203 | 100% | 4.28 | 5.44 | 12% | 36% | +11.5% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
