# Lost and Found distance benchmark: comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_laf_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **within 10%, 0 to 20 m**: obstacles whose estimated distance is within 10% of
the stereo ground truth, in the range where the detector reliably finds them. `_median`,
`_p10`, `_p25` mark how a depth model's per-pixel depth inside the outline is summarised.

| Rank | Run | Estimator | Frames | Coverage | Within 10%, 0-20 m | Median error (m), 0-20 m | Within 10%, 0-10 m | Within 10%, 10-20 m | Within 10%, 20-30 m | Within 10%, 30-50 m | Within 10%, 50+ m | Within 10%, all | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `combinations_full` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 1203 | 100% | 89% | 0.45 | 85% | 90% | 83% | 48% | 34% | 57% | sum of members |
| 2 | `metric3d-v2-large_n300` | `metric3d-v2-large_p10` | 301 | 100% | 88% | 0.37 | 83% | 90% | 85% | 65% | 50% | 68% | 902.0 |
| 3 | `metric3d-v2-large_n300` | `metric3d-v2-large_p25` | 301 | 100% | 87% | 0.38 | 83% | 89% | 87% | 64% | 50% | 67% | 902.0 |
| 4 | `combinations_full` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 1203 | 100% | 85% | 0.61 | 76% | 88% | 82% | 45% | 32% | 55% | sum of members |
| 5 | `metric3d-v2-large_n300` | `metric3d-v2-large_median` | 301 | 100% | 85% | 0.43 | 79% | 87% | 82% | 52% | 50% | 62% | 902.0 |
| 6 | `metric3d-v2-large_full` | `metric3d-v2-large_p25` | 1203 | 100% | 85% | 0.45 | 85% | 85% | 79% | 60% | 51% | 65% | 889.0 |
| 7 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_p10` | 1203 | 100% | 84% | 0.43 | 86% | 84% | 81% | 65% | 50% | 66% | 363.8 |
| 8 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_p25` | 1203 | 100% | 84% | 0.45 | 85% | 84% | 79% | 60% | 51% | 65% | 363.8 |
| 9 | `metric3d-v2-large_full` | `metric3d-v2-large_p10` | 1203 | 100% | 84% | 0.43 | 86% | 84% | 81% | 65% | 50% | 66% | 889.0 |
| 10 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_median` | 1203 | 100% | 82% | 0.49 | 81% | 83% | 72% | 49% | 51% | 60% | 363.8 |
| 11 | `metric3d-v2-large_full` | `metric3d-v2-large_median` | 1203 | 100% | 82% | 0.49 | 81% | 83% | 72% | 49% | 51% | 60% | 889.0 |
| 12 | `metric3d-v2-small_n300` | `metric3d-v2-small_p10` | 301 | 100% | 81% | 0.58 | 75% | 84% | 63% | 43% | 30% | 49% | 164.3 |
| 13 | `combinations_full` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 1203 | 100% | 80% | 0.61 | 64% | 86% | 87% | 73% | 46% | 68% | sum of members |
| 14 | `metric3d-v2-small_n300` | `metric3d-v2-small_p25` | 301 | 100% | 80% | 0.63 | 71% | 84% | 61% | 40% | 30% | 48% | 164.3 |
| 15 | `combinations_full` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 1203 | 100% | 78% | 0.71 | 65% | 83% | 77% | 53% | 28% | 54% | sum of members |
| 16 | `metric3d-v2-small_n300` | `metric3d-v2-small_median` | 301 | 100% | 78% | 0.57 | 62% | 84% | 52% | 38% | 32% | 46% | 164.3 |
| 17 | `combinations_full` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 1203 | 100% | 78% | 0.68 | 74% | 79% | 74% | 58% | 31% | 56% | sum of members |
| 18 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_p10` | 1203 | 100% | 76% | 0.69 | 74% | 77% | 63% | 43% | 33% | 50% | 87.8 |
| 19 | `metric3d-v2-small_full` | `metric3d-v2-small_p10` | 1203 | 100% | 76% | 0.68 | 74% | 77% | 63% | 43% | 33% | 50% | 156.4 |
| 20 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_p25` | 1203 | 100% | 74% | 0.73 | 73% | 75% | 61% | 41% | 34% | 48% | 87.8 |
| 21 | `metric3d-v2-small_full` | `metric3d-v2-small_p25` | 1203 | 100% | 74% | 0.73 | 73% | 75% | 61% | 42% | 34% | 49% | 156.4 |
| 22 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_median` | 1203 | 100% | 71% | 0.82 | 69% | 72% | 56% | 37% | 33% | 46% | 87.8 |
| 23 | `metric3d-v2-small_full` | `metric3d-v2-small_median` | 1203 | 100% | 71% | 0.82 | 69% | 72% | 55% | 37% | 33% | 45% | 156.4 |
| 24 | `depth-pro_n300` | `depth-pro_median` | 301 | 100% | 69% | 0.83 | 71% | 68% | 47% | 24% | 18% | 34% | 870.5 |
| 25 | `depth-pro_n300` | `depth-pro_p10` | 301 | 100% | 66% | 0.82 | 67% | 66% | 47% | 22% | 15% | 32% | 870.5 |
| 26 | `depth-pro_n300` | `depth-pro_p25` | 301 | 100% | 66% | 0.83 | 67% | 66% | 47% | 24% | 17% | 33% | 870.5 |
| 27 | `unidepth-v2-large_n300` | `unidepth-v2-large_p10` | 301 | 100% | 66% | 0.90 | 25% | 82% | 85% | 47% | 35% | 52% | 217.0 |
| 28 | `unidepth-v2-large_full` | `unidepth-v2-large_p10` | 1203 | 100% | 66% | 0.91 | 25% | 79% | 82% | 48% | 32% | 52% | 217.7 |
| 29 | `unidepth-v2-large_n300` | `unidepth-v2-large_p25` | 301 | 100% | 65% | 0.94 | 25% | 81% | 85% | 50% | 29% | 51% | 217.0 |
| 30 | `unidepth-v2-large_full` | `unidepth-v2-large_p25` | 1203 | 100% | 64% | 0.96 | 23% | 78% | 83% | 51% | 30% | 52% | 217.7 |
| 31 | `unidepth-v2-large_full` | `unidepth-v2-large_median` | 1203 | 100% | 60% | 1.03 | 19% | 73% | 85% | 57% | 31% | 54% | 217.7 |
| 32 | `combinations_full` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 1203 | 100% | 59% | 1.07 | 36% | 66% | 71% | 48% | 36% | 50% | sum of members |
| 33 | `da3-metric-large_n300` | `da3-metric-large_p10` | 301 | 100% | 58% | 1.15 | 54% | 60% | 82% | 65% | 55% | 63% | 89.7 |
| 34 | `unidepth-v2-large_n300` | `unidepth-v2-large_median` | 301 | 100% | 58% | 1.02 | 21% | 73% | 87% | 59% | 29% | 53% | 217.0 |
| 35 | `da3-metric-large_n300` | `da3-metric-large_p25` | 301 | 100% | 53% | 1.20 | 50% | 55% | 81% | 62% | 57% | 61% | 89.7 |
| 36 | `da3-metric-large_n300` | `da3-metric-large_median` | 301 | 100% | 47% | 1.43 | 42% | 48% | 76% | 57% | 50% | 56% | 89.7 |
| 37 | `unidepth-v2-large-nocam_full` | `unidepth-v2-large-nocam_p10` | 1203 | 100% | 44% | 1.46 | 18% | 53% | 77% | 51% | 20% | 44% | 217.6 |
| 38 | `unidepth-v2-large-nocam_full` | `unidepth-v2-large-nocam_p25` | 1203 | 100% | 43% | 1.51 | 17% | 52% | 76% | 53% | 21% | 44% | 217.6 |
| 39 | `geometric_full` | `ground_plane` | 1203 | 85% | 41% | 1.56 | 49% | 39% | 20% | 18% | 13% | 23% | - |
| 40 | `geometric_full` | `combined` | 1203 | 85% | 41% | 1.56 | 49% | 39% | 20% | 18% | 13% | 23% | - |
| 41 | `unidepth-v2-large-nocam_full` | `unidepth-v2-large-nocam_median` | 1203 | 100% | 40% | 1.59 | 12% | 49% | 75% | 57% | 20% | 44% | 217.6 |
| 42 | `geometric_n300` | `ground_plane` | 301 | 86% | 40% | 1.59 | 50% | 35% | 22% | 16% | 12% | 21% | - |
| 43 | `geometric_n300` | `combined` | 301 | 86% | 40% | 1.59 | 50% | 35% | 22% | 16% | 12% | 21% | - |
| 44 | `unidepth-v2-base_n300` | `unidepth-v2-base_p10` | 301 | 100% | 34% | 1.57 | 12% | 42% | 77% | 57% | 32% | 47% | 115.2 |
| 45 | `unidepth-v2-base_full` | `unidepth-v2-base_p10` | 1203 | 100% | 31% | 1.62 | 10% | 38% | 76% | 58% | 31% | 47% | 115.7 |
| 46 | `unidepth-v2-base_n300` | `unidepth-v2-base_p25` | 301 | 100% | 30% | 1.63 | 8% | 39% | 76% | 59% | 33% | 47% | 115.2 |
| 47 | `unidepth-v2-base_full` | `unidepth-v2-base_p25` | 1203 | 100% | 28% | 1.70 | 7% | 35% | 74% | 60% | 32% | 47% | 115.7 |
| 48 | `unidepth-v2-base_n300` | `unidepth-v2-base_median` | 301 | 100% | 27% | 1.78 | 4% | 35% | 71% | 58% | 35% | 46% | 115.2 |
| 49 | `unidepth-v2-base_full` | `unidepth-v2-base_median` | 1203 | 100% | 25% | 1.82 | 5% | 31% | 68% | 60% | 35% | 46% | 115.7 |
| 50 | `unidepth-v2-base-nocam_full` | `unidepth-v2-base-nocam_p10` | 1203 | 100% | 19% | 2.70 | 14% | 21% | 34% | 35% | 34% | 31% | 116.9 |
| 51 | `unidepth-v2-base-nocam_full` | `unidepth-v2-base-nocam_p25` | 1203 | 100% | 19% | 2.79 | 12% | 21% | 32% | 33% | 35% | 31% | 116.9 |
| 52 | `unidepth-v2-base-nocam_full` | `unidepth-v2-base-nocam_median` | 1203 | 100% | 18% | 2.96 | 9% | 21% | 29% | 32% | 37% | 30% | 116.9 |
| 53 | `da2-metric-small_n300` | `da2-metric-small_p10` | 301 | 100% | 17% | 2.85 | 8% | 21% | 27% | 39% | 38% | 33% | 40.4 |
| 54 | `yolo26s-depth_n300` | `yolo26s-depth_median` | 301 | 100% | 15% | 3.07 | 42% | 5% | 13% | 0% | 0% | 5% | 15.3 |
| 55 | `da2-metric-small_n300` | `da2-metric-small_p25` | 301 | 100% | 14% | 2.96 | 4% | 18% | 24% | 38% | 43% | 33% | 40.4 |
| 56 | `da2-metric-small_n300` | `da2-metric-small_median` | 301 | 100% | 12% | 3.22 | 0% | 16% | 19% | 37% | 42% | 31% | 40.4 |
| 57 | `da2-metric-large_n300` | `da2-metric-large_p10` | 301 | 100% | 10% | 3.03 | 0% | 15% | 42% | 49% | 35% | 36% | 155.6 |
| 58 | `yolo26s-depth_n300` | `yolo26s-depth_p25` | 301 | 100% | 10% | 3.36 | 25% | 5% | 10% | 0% | 0% | 3% | 15.3 |
| 59 | `unidepth-v2-small_n300` | `unidepth-v2-small_p10` | 301 | 100% | 9% | 2.45 | 0% | 13% | 52% | 56% | 37% | 40% | 63.8 |
| 60 | `yolo26s-depth_n300` | `yolo26s-depth_p10` | 301 | 100% | 9% | 3.57 | 21% | 5% | 8% | 0% | 0% | 3% | 15.3 |
| 61 | `da2-metric-base_n300` | `da2-metric-base_p10` | 301 | 100% | 8% | 3.20 | 0% | 11% | 29% | 50% | 45% | 37% | 66.4 |
| 62 | `da2-metric-base_n300` | `da2-metric-base_p25` | 301 | 100% | 8% | 3.34 | 0% | 11% | 24% | 46% | 48% | 36% | 66.4 |
| 63 | `da2-metric-large_n300` | `da2-metric-large_p25` | 301 | 100% | 8% | 3.19 | 0% | 11% | 35% | 48% | 40% | 36% | 155.6 |
| 64 | `unidepth-v2-small_n300` | `unidepth-v2-small_median` | 301 | 100% | 6% | 2.80 | 0% | 8% | 42% | 50% | 48% | 39% | 63.8 |
| 65 | `unidepth-v2-small_n300` | `unidepth-v2-small_p25` | 301 | 100% | 6% | 2.57 | 0% | 8% | 52% | 56% | 43% | 41% | 63.8 |
| 66 | `da2-metric-base_n300` | `da2-metric-base_median` | 301 | 100% | 5% | 3.56 | 0% | 6% | 24% | 44% | 52% | 36% | 66.4 |
| 67 | `da2-metric-large_n300` | `da2-metric-large_median` | 301 | 100% | 3% | 3.35 | 0% | 5% | 29% | 48% | 43% | 35% | 155.6 |
