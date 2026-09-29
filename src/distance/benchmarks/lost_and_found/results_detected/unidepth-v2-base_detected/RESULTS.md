# Lost and Found distance benchmark: `unidepth-v2-base_detected`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-base_median`, `unidepth-v2-base_p10`, `unidepth-v2-base_p25` |
| Depth model | `unidepth-v2-base`, given our focal length; inference 122.9 ms median, 132.9 ms p95 per frame |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 (every 1th frame) |
| Obstacles | 718 (0 skipped: no stereo depth) |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground truth | median stereo depth inside the labelled outline |
| Estimator input | the detector's mask of each obstacle it found (real pipeline) |
| Detector | `weights/yoloe-11s-seg.pt`, input size 1280, confidence 0.05, match IoU >= 0.3 |
| Detected | 718 of 1724 labelled obstacles (42%); statistics cover the detected ones |
| Hardware | NVIDIA GeForce RTX 4060 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `2c59c75` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T16:34:37+00:00 |

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
| unidepth-v2-base_median | 310 | 100% | 1.88 | 2.07 | 17% | 21% | +17.2% |
| unidepth-v2-base_p10 | 310 | 100% | 1.68 | 1.88 | 16% | 26% | +15.6% |
| unidepth-v2-base_p25 | 310 | 100% | 1.74 | 1.95 | 16% | 24% | +16.2% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-base_median | 718 | 100% | 2.20 | 3.17 | 13% | 45% | +8.8% |
| unidepth-v2-base_p10 | 718 | 100% | 1.81 | 2.99 | 12% | 49% | +6.2% |
| unidepth-v2-base_p25 | 718 | 100% | 1.93 | 3.06 | 12% | 47% | +7.1% |

## `unidepth-v2-base_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 1.78 | 1.86 | 23% | 6% | +23.1% |
| 10-20 m | 223 | 100% | 1.95 | 2.16 | 15% | 27% | +14.9% |
| 20-30 m | 137 | 100% | 1.58 | 2.32 | 9% | 64% | +6.1% |
| 30-50 m | 155 | 100% | 3.38 | 3.75 | 10% | 60% | +2.0% |
| 50+ m | 116 | 100% | 4.62 | 6.30 | 10% | 65% | -1.5% |

## `unidepth-v2-base_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.81 | 2.99 | 13% | 46% | +9.1% |
| random hazards | 202 | 100% | 2.07 | 3.50 | 13% | 39% | +4.3% |
| humans | 171 | 100% | 2.86 | 2.98 | 8% | 70% | +8.5% |
| standard objects | 142 | 100% | 2.44 | 3.17 | 17% | 21% | +15.0% |

## `unidepth-v2-base_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 1.59 | 1.71 | 21% | 10% | +21.2% |
| 10-20 m | 223 | 100% | 1.71 | 1.95 | 14% | 33% | +13.4% |
| 20-30 m | 137 | 100% | 1.50 | 1.99 | 8% | 72% | +3.7% |
| 30-50 m | 155 | 100% | 2.68 | 3.44 | 9% | 65% | -1.3% |
| 50+ m | 116 | 100% | 3.08 | 6.53 | 10% | 62% | -5.7% |

## `unidepth-v2-base_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.69 | 2.71 | 12% | 53% | +6.4% |
| random hazards | 202 | 100% | 1.95 | 4.13 | 14% | 37% | +1.5% |
| humans | 171 | 100% | 1.74 | 1.95 | 6% | 81% | +5.8% |
| standard objects | 142 | 100% | 2.31 | 3.01 | 16% | 25% | +13.2% |

## `unidepth-v2-base_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 1.67 | 1.76 | 22% | 7% | +21.9% |
| 10-20 m | 223 | 100% | 1.81 | 2.02 | 14% | 30% | +13.9% |
| 20-30 m | 137 | 100% | 1.51 | 2.09 | 8% | 72% | +4.5% |
| 30-50 m | 155 | 100% | 2.99 | 3.54 | 9% | 63% | -0.2% |
| 50+ m | 116 | 100% | 3.68 | 6.51 | 10% | 62% | -4.4% |

## `unidepth-v2-base_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.73 | 2.83 | 13% | 50% | +7.3% |
| random hazards | 202 | 100% | 1.94 | 3.96 | 14% | 38% | +2.3% |
| humans | 171 | 100% | 1.99 | 2.27 | 7% | 78% | +6.7% |
| standard objects | 142 | 100% | 2.36 | 3.05 | 16% | 22% | +13.9% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
