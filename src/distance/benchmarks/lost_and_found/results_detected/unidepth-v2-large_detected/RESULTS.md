# Lost and Found distance benchmark: `unidepth-v2-large_detected`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `unidepth-v2-large_median`, `unidepth-v2-large_p10`, `unidepth-v2-large_p25` |
| Depth model | `unidepth-v2-large`, given our focal length; inference 226.6 ms median, 238.6 ms p95 per frame |
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
| Created (UTC) | 2026-09-29T16:39:22+00:00 |

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
| unidepth-v2-large_median | 310 | 100% | 1.08 | 1.20 | 11% | 55% | +10.3% |
| unidepth-v2-large_p10 | 310 | 100% | 0.96 | 1.07 | 9% | 62% | +9.0% |
| unidepth-v2-large_p25 | 310 | 100% | 1.01 | 1.11 | 10% | 59% | +9.5% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unidepth-v2-large_median | 718 | 100% | 1.41 | 2.93 | 10% | 59% | +4.3% |
| unidepth-v2-large_p10 | 718 | 100% | 1.32 | 2.73 | 9% | 64% | +1.8% |
| unidepth-v2-large_p25 | 718 | 100% | 1.36 | 2.75 | 9% | 62% | +2.7% |

## `unidepth-v2-large_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 1.28 | 1.32 | 17% | 20% | +16.5% |
| 10-20 m | 223 | 100% | 1.03 | 1.15 | 8% | 68% | +7.9% |
| 20-30 m | 137 | 100% | 1.16 | 1.47 | 6% | 86% | -0.2% |
| 30-50 m | 155 | 100% | 2.35 | 3.40 | 9% | 66% | -3.4% |
| 50+ m | 116 | 100% | 8.04 | 8.64 | 14% | 31% | +4.1% |

## `unidepth-v2-large_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.36 | 3.02 | 11% | 59% | +1.9% |
| random hazards | 202 | 100% | 1.39 | 2.95 | 10% | 56% | +2.4% |
| humans | 171 | 100% | 1.58 | 3.38 | 7% | 67% | +6.7% |
| standard objects | 142 | 100% | 1.35 | 2.21 | 11% | 54% | +7.8% |

## `unidepth-v2-large_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 1.11 | 1.19 | 15% | 25% | +14.9% |
| 10-20 m | 223 | 100% | 0.89 | 1.01 | 7% | 77% | +6.7% |
| 20-30 m | 137 | 100% | 1.24 | 1.52 | 6% | 85% | -2.0% |
| 30-50 m | 155 | 100% | 2.64 | 3.50 | 9% | 62% | -6.4% |
| 50+ m | 116 | 100% | 6.42 | 7.59 | 12% | 47% | -1.8% |

## `unidepth-v2-large_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.37 | 2.90 | 10% | 58% | -0.3% |
| random hazards | 202 | 100% | 1.35 | 3.17 | 10% | 56% | -1.1% |
| humans | 171 | 100% | 1.33 | 2.42 | 5% | 84% | +4.0% |
| standard objects | 142 | 100% | 1.27 | 2.23 | 11% | 59% | +6.5% |

## `unidepth-v2-large_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 1.16 | 1.24 | 16% | 23% | +15.5% |
| 10-20 m | 223 | 100% | 0.96 | 1.06 | 8% | 74% | +7.1% |
| 20-30 m | 137 | 100% | 1.22 | 1.50 | 6% | 85% | -1.5% |
| 30-50 m | 155 | 100% | 2.60 | 3.47 | 9% | 63% | -5.3% |
| 50+ m | 116 | 100% | 6.93 | 7.67 | 12% | 41% | -0.1% |

## `unidepth-v2-large_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.41 | 2.98 | 10% | 58% | +0.5% |
| random hazards | 202 | 100% | 1.41 | 2.94 | 10% | 56% | -0.1% |
| humans | 171 | 100% | 1.32 | 2.71 | 6% | 78% | +4.9% |
| standard objects | 142 | 100% | 1.30 | 2.22 | 11% | 56% | +7.0% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
