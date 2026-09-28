# Lost and Found distance benchmark: comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_laf_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **within 10%, 0 to 20 m**: obstacles whose estimated distance is within 10% of
the stereo ground truth, in the range where the detector reliably finds them. `_median`,
`_p10`, `_p25` mark how a depth model's per-pixel depth inside the outline is summarised.

| Rank | Run | Estimator | Frames | Coverage | Within 10%, 0-20 m | Median error (m), 0-20 m | Within 10%, 0-10 m | Within 10%, 10-20 m | Within 10%, 20-30 m | Within 10%, 30-50 m | Within 10%, 50+ m | Within 10%, all | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-large_n300` | `metric3d-v2-large_p10` | 301 | 100% | 88% | 0.37 | 83% | 90% | 85% | 65% | 50% | 68% | 902.0 |
| 2 | `metric3d-v2-large_n300` | `metric3d-v2-large_p25` | 301 | 100% | 87% | 0.38 | 83% | 89% | 87% | 64% | 50% | 67% | 902.0 |
| 3 | `metric3d-v2-large_n300` | `metric3d-v2-large_median` | 301 | 100% | 85% | 0.43 | 79% | 87% | 82% | 52% | 50% | 62% | 902.0 |
| 4 | `metric3d-v2-small_n300` | `metric3d-v2-small_p10` | 301 | 100% | 81% | 0.58 | 75% | 84% | 63% | 43% | 30% | 49% | 164.3 |
| 5 | `metric3d-v2-small_n300` | `metric3d-v2-small_p25` | 301 | 100% | 80% | 0.63 | 71% | 84% | 61% | 40% | 30% | 48% | 164.3 |
| 6 | `metric3d-v2-small_n300` | `metric3d-v2-small_median` | 301 | 100% | 78% | 0.57 | 62% | 84% | 52% | 38% | 32% | 46% | 164.3 |
| 7 | `depth-pro_n300` | `depth-pro_median` | 301 | 100% | 69% | 0.83 | 71% | 68% | 47% | 24% | 18% | 34% | 870.5 |
| 8 | `depth-pro_n300` | `depth-pro_p10` | 301 | 100% | 66% | 0.82 | 67% | 66% | 47% | 22% | 15% | 32% | 870.5 |
| 9 | `depth-pro_n300` | `depth-pro_p25` | 301 | 100% | 66% | 0.83 | 67% | 66% | 47% | 24% | 17% | 33% | 870.5 |
| 10 | `unidepth-v2-large_n300` | `unidepth-v2-large_p10` | 301 | 100% | 66% | 0.90 | 25% | 82% | 85% | 47% | 35% | 52% | 217.0 |
| 11 | `unidepth-v2-large_n300` | `unidepth-v2-large_p25` | 301 | 100% | 65% | 0.94 | 25% | 81% | 85% | 50% | 29% | 51% | 217.0 |
| 12 | `da3-metric-large_n300` | `da3-metric-large_p10` | 301 | 100% | 58% | 1.15 | 54% | 60% | 82% | 65% | 55% | 63% | 89.7 |
| 13 | `unidepth-v2-large_n300` | `unidepth-v2-large_median` | 301 | 100% | 58% | 1.02 | 21% | 73% | 87% | 59% | 29% | 53% | 217.0 |
| 14 | `da3-metric-large_n300` | `da3-metric-large_p25` | 301 | 100% | 53% | 1.20 | 50% | 55% | 81% | 62% | 57% | 61% | 89.7 |
| 15 | `da3-metric-large_n300` | `da3-metric-large_median` | 301 | 100% | 47% | 1.43 | 42% | 48% | 76% | 57% | 50% | 56% | 89.7 |
| 16 | `geometric_n300` | `ground_plane` | 301 | 86% | 40% | 1.59 | 50% | 35% | 22% | 16% | 12% | 21% | - |
| 17 | `geometric_n300` | `combined` | 301 | 86% | 40% | 1.59 | 50% | 35% | 22% | 16% | 12% | 21% | - |
| 18 | `unidepth-v2-base_n300` | `unidepth-v2-base_p10` | 301 | 100% | 34% | 1.57 | 12% | 42% | 77% | 57% | 32% | 47% | 115.2 |
| 19 | `unidepth-v2-base_n300` | `unidepth-v2-base_p25` | 301 | 100% | 30% | 1.63 | 8% | 39% | 76% | 59% | 33% | 47% | 115.2 |
| 20 | `unidepth-v2-base_n300` | `unidepth-v2-base_median` | 301 | 100% | 27% | 1.78 | 4% | 35% | 71% | 58% | 35% | 46% | 115.2 |
| 21 | `da2-metric-small_n300` | `da2-metric-small_p10` | 301 | 100% | 17% | 2.85 | 8% | 21% | 27% | 39% | 38% | 33% | 40.4 |
| 22 | `yolo26s-depth_n300` | `yolo26s-depth_median` | 301 | 100% | 15% | 3.07 | 42% | 5% | 13% | 0% | 0% | 5% | 15.3 |
| 23 | `da2-metric-small_n300` | `da2-metric-small_p25` | 301 | 100% | 14% | 2.96 | 4% | 18% | 24% | 38% | 43% | 33% | 40.4 |
| 24 | `da2-metric-small_n300` | `da2-metric-small_median` | 301 | 100% | 12% | 3.22 | 0% | 16% | 19% | 37% | 42% | 31% | 40.4 |
| 25 | `da2-metric-large_n300` | `da2-metric-large_p10` | 301 | 100% | 10% | 3.03 | 0% | 15% | 42% | 49% | 35% | 36% | 155.6 |
| 26 | `yolo26s-depth_n300` | `yolo26s-depth_p25` | 301 | 100% | 10% | 3.36 | 25% | 5% | 10% | 0% | 0% | 3% | 15.3 |
| 27 | `unidepth-v2-small_n300` | `unidepth-v2-small_p10` | 301 | 100% | 9% | 2.45 | 0% | 13% | 52% | 56% | 37% | 40% | 63.8 |
| 28 | `yolo26s-depth_n300` | `yolo26s-depth_p10` | 301 | 100% | 9% | 3.57 | 21% | 5% | 8% | 0% | 0% | 3% | 15.3 |
| 29 | `da2-metric-base_n300` | `da2-metric-base_p10` | 301 | 100% | 8% | 3.20 | 0% | 11% | 29% | 50% | 45% | 37% | 66.4 |
| 30 | `da2-metric-base_n300` | `da2-metric-base_p25` | 301 | 100% | 8% | 3.34 | 0% | 11% | 24% | 46% | 48% | 36% | 66.4 |
| 31 | `da2-metric-large_n300` | `da2-metric-large_p25` | 301 | 100% | 8% | 3.19 | 0% | 11% | 35% | 48% | 40% | 36% | 155.6 |
| 32 | `unidepth-v2-small_n300` | `unidepth-v2-small_median` | 301 | 100% | 6% | 2.80 | 0% | 8% | 42% | 50% | 48% | 39% | 63.8 |
| 33 | `unidepth-v2-small_n300` | `unidepth-v2-small_p25` | 301 | 100% | 6% | 2.57 | 0% | 8% | 52% | 56% | 43% | 41% | 63.8 |
| 34 | `da2-metric-base_n300` | `da2-metric-base_median` | 301 | 100% | 5% | 3.56 | 0% | 6% | 24% | 44% | 52% | 36% | 66.4 |
| 35 | `da2-metric-large_n300` | `da2-metric-large_median` | 301 | 100% | 3% | 3.35 | 0% | 5% | 29% | 48% | 43% | 35% | 155.6 |
