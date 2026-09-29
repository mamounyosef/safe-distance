# Lost and Found distance benchmark: `metric3d-v2-small-fp16_detected`

Generated automatically from `results.json` by `benchmark_laf_distance.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Estimators | `metric3d-v2-small-fp16_median`, `metric3d-v2-small-fp16_p10`, `metric3d-v2-small-fp16_p25` |
| Depth model | `metric3d-v2-small-fp16`, given our focal length; inference 89.4 ms median, 98.5 ms p95 per frame |
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
| Created (UTC) | 2026-09-29T16:24:20+00:00 |

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
| metric3d-v2-small-fp16_median | 310 | 100% | 0.81 | 1.15 | 9% | 70% | +6.8% |
| metric3d-v2-small-fp16_p10 | 310 | 100% | 0.68 | 0.99 | 7% | 75% | +4.6% |
| metric3d-v2-small-fp16_p25 | 310 | 100% | 0.73 | 1.04 | 8% | 72% | +5.4% |

## All distances

| Estimator | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| metric3d-v2-small-fp16_median | 718 | 100% | 1.94 | 4.88 | 14% | 52% | +9.5% |
| metric3d-v2-small-fp16_p10 | 718 | 100% | 1.68 | 4.10 | 12% | 59% | +5.2% |
| metric3d-v2-small-fp16_p25 | 718 | 100% | 1.77 | 4.27 | 12% | 56% | +6.6% |

## `metric3d-v2-small-fp16_median` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.48 | 0.69 | 9% | 69% | +7.0% |
| 10-20 m | 223 | 100% | 0.97 | 1.32 | 9% | 70% | +6.6% |
| 20-30 m | 137 | 100% | 1.88 | 3.16 | 13% | 58% | +9.3% |
| 30-50 m | 155 | 100% | 5.92 | 8.24 | 21% | 28% | +14.1% |
| 50+ m | 116 | 100% | 10.30 | 12.38 | 20% | 30% | +10.9% |

## `metric3d-v2-small-fp16_median` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.07 | 3.14 | 11% | 72% | +7.2% |
| random hazards | 202 | 100% | 1.85 | 4.39 | 13% | 51% | +1.9% |
| humans | 171 | 100% | 5.79 | 7.45 | 16% | 27% | +15.9% |
| standard objects | 142 | 100% | 1.30 | 4.95 | 17% | 55% | +15.8% |

## `metric3d-v2-small-fp16_p10` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.44 | 0.56 | 7% | 74% | +4.6% |
| 10-20 m | 223 | 100% | 0.85 | 1.16 | 8% | 76% | +4.6% |
| 20-30 m | 137 | 100% | 1.68 | 2.63 | 11% | 65% | +5.2% |
| 30-50 m | 155 | 100% | 5.22 | 6.79 | 17% | 37% | +8.1% |
| 50+ m | 116 | 100% | 9.88 | 10.55 | 17% | 35% | +3.1% |

## `metric3d-v2-small-fp16_p10` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.03 | 2.61 | 9% | 75% | +3.0% |
| random hazards | 202 | 100% | 1.47 | 4.57 | 12% | 53% | -3.1% |
| humans | 171 | 100% | 3.93 | 5.46 | 12% | 46% | +12.0% |
| standard objects | 142 | 100% | 1.19 | 3.92 | 14% | 58% | +12.2% |

## `metric3d-v2-small-fp16_p25` by distance

| Distance | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 87 | 100% | 0.43 | 0.60 | 8% | 72% | +5.5% |
| 10-20 m | 223 | 100% | 0.88 | 1.22 | 8% | 72% | +5.4% |
| 20-30 m | 137 | 100% | 1.80 | 2.77 | 11% | 62% | +6.5% |
| 30-50 m | 155 | 100% | 5.92 | 7.18 | 18% | 35% | +9.9% |
| 50+ m | 116 | 100% | 9.45 | 10.78 | 17% | 34% | +5.4% |

## `metric3d-v2-small-fp16_p25` by obstacle group

| Group | Obstacles | Coverage | Median error (m) | Mean error (m) | Relative error | Within 10% | Bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| emotional hazards | 203 | 100% | 1.08 | 2.72 | 9% | 73% | +4.4% |
| random hazards | 202 | 100% | 1.67 | 4.34 | 12% | 53% | -1.6% |
| humans | 171 | 100% | 4.45 | 6.05 | 13% | 39% | +13.2% |
| standard objects | 142 | 100% | 1.26 | 4.25 | 15% | 56% | +13.4% |

## Known limitations

- Ground truth is stereo, which becomes noisy far away; bands beyond 30 m are less reliable.
- Estimators see the labelled outline; with a real detector's masks results will be somewhat worse.
- Obstacles are staged objects in low-speed, mostly suburban scenes; no highway, night or rain.
