# Lost and Found distance benchmark: real pipeline (detector masks)

Generated automatically from every `results/<run>/results.json` by `benchmark_laf_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **within 10%, 0 to 20 m**: obstacles whose estimated distance is within 10% of
the stereo ground truth, in the range where the detector reliably finds them. `_median`,
`_p10`, `_p25` mark how a depth model's per-pixel depth inside the outline is summarised.

| Rank | Run | Estimator | Frames | Coverage | Within 10%, 0-20 m | Median error (m), 0-20 m | Within 10%, 0-10 m | Within 10%, 10-20 m | Within 10%, 20-30 m | Within 10%, 30-50 m | Within 10%, 50+ m | Within 10%, all | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-large-fp16_detected` | `metric3d-v2-large-fp16_p10` | 1203 | 100% | 83% | 0.43 | 86% | 81% | 82% | 70% | 66% | 77% | 365.7 |
| 2 | `metric3d-v2-large-fp16_detected` | `metric3d-v2-large-fp16_p25` | 1203 | 100% | 83% | 0.45 | 85% | 82% | 81% | 68% | 61% | 76% | 365.7 |
| 3 | `metric3d-v2-large-fp16_detected` | `metric3d-v2-large-fp16_median` | 1203 | 100% | 80% | 0.49 | 80% | 80% | 75% | 59% | 54% | 70% | 365.7 |
| 4 | `metric3d-v2-small-fp16_detected` | `metric3d-v2-small-fp16_p10` | 1203 | 100% | 75% | 0.68 | 74% | 76% | 65% | 37% | 35% | 59% | 89.4 |
| 5 | `metric3d-v2-small-fp16_detected` | `metric3d-v2-small-fp16_p25` | 1203 | 100% | 72% | 0.73 | 72% | 72% | 62% | 35% | 34% | 56% | 89.4 |
| 6 | `metric3d-v2-small-fp16_detected` | `metric3d-v2-small-fp16_median` | 1203 | 100% | 70% | 0.81 | 69% | 70% | 58% | 28% | 30% | 52% | 89.4 |
| 7 | `unidepth-v2-large_detected` | `unidepth-v2-large_p10` | 1203 | 100% | 62% | 0.96 | 25% | 77% | 85% | 62% | 47% | 64% | 226.6 |
| 8 | `unidepth-v2-large_detected` | `unidepth-v2-large_p25` | 1203 | 100% | 59% | 1.01 | 23% | 74% | 85% | 63% | 41% | 62% | 226.6 |
| 9 | `unidepth-v2-large_detected` | `unidepth-v2-large_median` | 1203 | 100% | 55% | 1.08 | 20% | 68% | 86% | 66% | 31% | 59% | 226.6 |
| 10 | `geometric_detected` | `ground_plane` | 1203 | 86% | 35% | 1.78 | 39% | 33% | 20% | 16% | 18% | 26% | - |
| 11 | `unidepth-v2-base_detected` | `unidepth-v2-base_p10` | 1203 | 100% | 26% | 1.68 | 10% | 33% | 72% | 65% | 62% | 49% | 122.9 |
| 12 | `unidepth-v2-base_detected` | `unidepth-v2-base_p25` | 1203 | 100% | 24% | 1.74 | 7% | 30% | 72% | 63% | 62% | 47% | 122.9 |
| 13 | `geometric_detected` | `combined` | 1203 | 98% | 22% | 5.57 | 24% | 22% | 11% | 9% | 4% | 14% | - |
| 14 | `unidepth-v2-base_detected` | `unidepth-v2-base_median` | 1203 | 100% | 21% | 1.88 | 6% | 27% | 64% | 60% | 65% | 45% | 122.9 |
