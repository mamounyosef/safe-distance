# Lost and Found distance benchmark: `metric3d-v2-large-fp16_detected`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-large-fp16_median`, `metric3d-v2-large-fp16_p10`, `metric3d-v2-large-fp16_p25` |
| Depth model | `metric3d-v2-large-fp16`, given our focal length; inference 365.7 ms median, 402.9 ms p95 per frame |
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
| Created (UTC) | 2026-09-29T16:30:37+00:00 |

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
| metric3d-v2-large-fp16_median | 310 | 100% | 0.49 | 0.81 | 6% | 80% | +4.8% |
| metric3d-v2-large-fp16_p10 | 310 | 100% | 0.43 | 0.76 | 6% | 83% | +3.3% |
| metric3d-v2-large-fp16_p25 | 310 | 100% | 0.45 | 0.77 | 6% | 83% | +3.9% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-large-fp16_median | 718 | 100% | 1.28 | 3.00 | 9% | 70% | +6.3% |
| metric3d-v2-large-fp16_p10 | 718 | 100% | 1.14 | 2.35 | 7% | 77% | +2.9% |
| metric3d-v2-large-fp16_p25 | 718 | 100% | 1.14 | 2.42 | 7% | 76% | +3.9% |

## `metric3d-v2-large-fp16_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.31 | 0.45 | 6% | 80% | +4.1% |
| 10-20 m | 223 | 100% | 0.59 | 0.95 | 6% | 80% | +5.0% |
| 20-30 m | 137 | 100% | 1.27 | 1.88 | 8% | 75% | +4.7% |
| 30-50 m | 155 | 100% | 3.26 | 4.34 | 11% | 59% | +8.6% |
| 50+ m | 116 | 100% | 5.78 | 8.36 | 13% | 54% | +9.3% |

## `metric3d-v2-large-fp16_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 0.67 | 2.02 | 7% | 78% | +4.6% |
| random hazards | 202 | 100% | 1.01 | 2.57 | 7% | 74% | +3.4% |
| humans | 171 | 100% | 3.30 | 4.38 | 10% | 67% | +9.6% |
| standard objects | 142 | 100% | 0.96 | 3.34 | 11% | 60% | +9.0% |

## `metric3d-v2-large-fp16_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.29 | 0.43 | 5% | 86% | +2.5% |
| 10-20 m | 223 | 100% | 0.54 | 0.89 | 6% | 81% | +3.6% |
| 20-30 m | 137 | 100% | 1.19 | 1.62 | 7% | 82% | +2.2% |
| 30-50 m | 155 | 100% | 2.55 | 3.14 | 8% | 70% | +3.1% |
| 50+ m | 116 | 100% | 5.20 | 6.41 | 10% | 66% | +2.2% |

## `metric3d-v2-large-fp16_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 0.65 | 1.70 | 7% | 83% | +1.0% |
| random hazards | 202 | 100% | 0.91 | 2.15 | 6% | 78% | -1.1% |
| humans | 171 | 100% | 2.86 | 3.02 | 7% | 82% | +6.4% |
| standard objects | 142 | 100% | 1.01 | 2.77 | 10% | 62% | +7.0% |

## `metric3d-v2-large-fp16_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.28 | 0.43 | 5% | 85% | +3.2% |
| 10-20 m | 223 | 100% | 0.53 | 0.90 | 6% | 82% | +4.1% |
| 20-30 m | 137 | 100% | 1.14 | 1.65 | 7% | 81% | +2.9% |
| 30-50 m | 155 | 100% | 2.85 | 3.40 | 9% | 68% | +4.7% |
| 50+ m | 116 | 100% | 5.20 | 6.40 | 10% | 61% | +3.9% |

## `metric3d-v2-large-fp16_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 0.61 | 1.68 | 6% | 83% | +2.1% |
| random hazards | 202 | 100% | 0.91 | 1.99 | 6% | 79% | -0.0% |
| humans | 171 | 100% | 3.05 | 3.34 | 7% | 75% | +7.3% |
| standard objects | 142 | 100% | 1.04 | 2.96 | 10% | 61% | +7.7% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
