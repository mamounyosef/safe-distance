# KITTI distance benchmark: comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_kitti_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **in path, within 10%**: the share of objects in our driving corridor whose
estimated distance is within 10% of the truth. `_median`, `_p10`, `_p25` mark how a depth
model's per-pixel depth inside the object's mask is summarised (median, 10th or 25th
percentile). Depth model time is inference only, per image, on the hardware in each run.

## vs nearest surface

| Rank | Run | Estimator | Images | Coverage | In path within 10% | In path median error (m) | In path within 10%, 0-10 m | In path within 10%, 10-20 m | In path within 10%, 20-30 m | In path within 10%, 30-50 m | In path within 10%, 50+ m | All objects within 10% | All objects median error (m) | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `combinations_full` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 1500 | 100% | 96% | 0.67 | 97% | 96% | 100% | 97% | 87% | 70% | 1.06 | sum of members |
| 2 | `metric3d-v2-large_n300` | `metric3d-v2-large_p25` | 300 | 100% | 95% | 0.83 | 93% | 98% | 96% | 97% | 84% | 75% | 0.99 | 914.4 |
| 3 | `unidepth-v2-large_n300` | `unidepth-v2-large_median` | 300 | 100% | 94% | 0.96 | 100% | 86% | 96% | 96% | 96% | 74% | 1.12 | 215.1 |
| 4 | `unidepth-v2-large_n300` | `unidepth-v2-large_p25` | 300 | 100% | 94% | 1.00 | 93% | 91% | 98% | 93% | 96% | 66% | 1.38 | 215.1 |
| 5 | `metric3d-v2-large_n300` | `metric3d-v2-large_p10` | 300 | 100% | 93% | 0.74 | 93% | 98% | 93% | 93% | 84% | 69% | 1.09 | 914.4 |
| 6 | `combinations_full` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 1500 | 100% | 93% | 0.87 | 92% | 93% | 97% | 90% | 89% | 63% | 1.41 | sum of members |
| 7 | `unidepth-v2-large_full` | `unidepth-v2-large_p25` | 1500 | 100% | 92% | 1.04 | 92% | 91% | 94% | 94% | 88% | 66% | 1.35 | 209.6 |
| 8 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_p25` | 1500 | 100% | 92% | 0.78 | 95% | 97% | 96% | 92% | 78% | 74% | 1.00 | 354.2 |
| 9 | `metric3d-v2-large_full` | `metric3d-v2-large_p25` | 1500 | 100% | 92% | 0.77 | 95% | 97% | 96% | 92% | 78% | 74% | 1.00 | 897.7 |
| 10 | `unidepth-v2-base_full` | `unidepth-v2-base_median` | 1500 | 100% | 92% | 0.77 | 94% | 93% | 96% | 93% | 80% | 70% | 1.15 | 466.1 |
| 11 | `unidepth-v2-large_full` | `unidepth-v2-large_median` | 1500 | 100% | 92% | 0.86 | 93% | 90% | 94% | 95% | 84% | 73% | 1.07 | 209.6 |
| 12 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_p10` | 1500 | 100% | 92% | 0.69 | 95% | 96% | 97% | 88% | 82% | 69% | 1.09 | 354.2 |
| 13 | `metric3d-v2-large_full` | `metric3d-v2-large_p10` | 1500 | 100% | 92% | 0.69 | 95% | 96% | 97% | 88% | 82% | 69% | 1.09 | 897.7 |
| 14 | `combinations_full` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 1500 | 100% | 92% | 0.77 | 94% | 95% | 98% | 90% | 77% | 61% | 1.47 | sum of members |
| 15 | `metric3d-v2-small_n300` | `metric3d-v2-small_p25` | 300 | 100% | 92% | 0.86 | 93% | 93% | 96% | 92% | 80% | 69% | 1.19 | 149.2 |
| 16 | `unidepth-v2-large_n300` | `unidepth-v2-large_p10` | 300 | 100% | 92% | 1.09 | 93% | 86% | 98% | 91% | 92% | 60% | 1.62 | 215.1 |
| 17 | `unidepth-v2-base_full` | `unidepth-v2-base_p25` | 1500 | 100% | 91% | 0.94 | 90% | 95% | 97% | 91% | 77% | 62% | 1.45 | 466.1 |
| 18 | `metric3d-v2-small_n300` | `metric3d-v2-small_median` | 300 | 100% | 91% | 0.92 | 80% | 89% | 96% | 95% | 84% | 72% | 1.10 | 149.2 |
| 19 | `unidepth-v2-base_n300` | `unidepth-v2-base_median` | 300 | 100% | 91% | 0.74 | 100% | 93% | 91% | 93% | 76% | 70% | 1.10 | 110.1 |
| 20 | `unidepth-v2-base_n300` | `unidepth-v2-base_p25` | 300 | 100% | 91% | 0.94 | 93% | 98% | 93% | 92% | 72% | 61% | 1.45 | 110.1 |
| 21 | `combinations_full` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 1500 | 100% | 90% | 1.11 | 86% | 88% | 95% | 89% | 91% | 59% | 1.56 | sum of members |
| 22 | `unidepth-v2-base_n300` | `unidepth-v2-base_p10` | 300 | 100% | 90% | 1.02 | 93% | 93% | 98% | 89% | 72% | 56% | 1.67 | 110.1 |
| 23 | `unidepth-v2-large_full` | `unidepth-v2-large_p10` | 1500 | 100% | 90% | 1.12 | 89% | 88% | 94% | 88% | 89% | 60% | 1.54 | 209.6 |
| 24 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_p25` | 1500 | 100% | 90% | 0.92 | 93% | 94% | 96% | 89% | 70% | 67% | 1.19 | 80.2 |
| 25 | `metric3d-v2-small_full` | `metric3d-v2-small_p25` | 1500 | 100% | 90% | 0.92 | 93% | 94% | 96% | 89% | 69% | 67% | 1.18 | 152.1 |
| 26 | `unidepth-v2-base_full` | `unidepth-v2-base_p10` | 1500 | 100% | 90% | 1.02 | 85% | 94% | 98% | 88% | 73% | 56% | 1.66 | 466.1 |
| 27 | `metric3d-v2-small_n300` | `metric3d-v2-small_p10` | 300 | 100% | 88% | 0.91 | 93% | 91% | 93% | 88% | 72% | 63% | 1.40 | 149.2 |
| 28 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_p10` | 1500 | 100% | 88% | 0.91 | 92% | 92% | 96% | 85% | 66% | 62% | 1.37 | 80.2 |
| 29 | `metric3d-v2-small_full` | `metric3d-v2-small_p10` | 1500 | 100% | 88% | 0.91 | 92% | 92% | 96% | 85% | 66% | 62% | 1.37 | 152.1 |
| 30 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_median` | 1500 | 100% | 87% | 0.98 | 90% | 90% | 93% | 87% | 69% | 69% | 1.14 | 80.2 |
| 31 | `metric3d-v2-small_full` | `metric3d-v2-small_median` | 1500 | 100% | 87% | 0.99 | 90% | 90% | 93% | 87% | 69% | 69% | 1.14 | 152.1 |
| 32 | `metric3d-v2-large_n300` | `metric3d-v2-large_median` | 300 | 100% | 87% | 1.08 | 87% | 84% | 87% | 89% | 84% | 77% | 0.98 | 914.4 |
| 33 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_median` | 1500 | 100% | 86% | 1.09 | 92% | 87% | 90% | 84% | 75% | 75% | 1.03 | 354.2 |
| 34 | `metric3d-v2-large_full` | `metric3d-v2-large_median` | 1500 | 100% | 86% | 1.09 | 92% | 87% | 90% | 84% | 75% | 75% | 1.03 | 897.7 |
| 35 | `unidepth-v2-small_n300` | `unidepth-v2-small_p10` | 300 | 100% | 85% | 1.25 | 87% | 80% | 96% | 82% | 88% | 53% | 1.73 | 60.1 |
| 36 | `unidepth-v2-small_n300` | `unidepth-v2-small_p25` | 300 | 100% | 85% | 1.17 | 87% | 80% | 96% | 83% | 80% | 58% | 1.53 | 60.1 |
| 37 | `combinations_full` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 1500 | 100% | 85% | 1.24 | 87% | 85% | 92% | 83% | 69% | 53% | 1.78 | sum of members |
| 38 | `combinations_full` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 1500 | 100% | 84% | 1.15 | 83% | 92% | 95% | 82% | 56% | 51% | 1.87 | sum of members |
| 39 | `unidepth-v2-small_n300` | `unidepth-v2-small_median` | 300 | 100% | 84% | 1.23 | 100% | 86% | 89% | 79% | 76% | 64% | 1.31 | 60.1 |
| 40 | `geometric_full` | `known_size` | 1500 | 100% | 77% | 1.46 | 74% | 75% | 86% | 79% | 58% | 63% | 1.68 | - |
| 41 | `geometric_full` | `combined` | 1500 | 100% | 77% | 1.46 | 74% | 75% | 86% | 79% | 58% | 63% | 1.69 | - |
| 42 | `yolo26s-seg_geometric-v1` | `known_size` | 1500 | 100% | 77% | 1.46 | 74% | 75% | 86% | 79% | 58% | 63% | 1.68 | - |
| 43 | `geometric_n300` | `known_size` | 300 | 100% | 75% | 1.52 | 60% | 82% | 85% | 75% | 52% | 64% | 1.65 | - |
| 44 | `geometric_n300` | `combined` | 300 | 100% | 75% | 1.52 | 60% | 82% | 85% | 75% | 52% | 64% | 1.65 | - |
| 45 | `da2-metric-small_n300` | `da2-metric-small_p10` | 300 | 100% | 69% | 1.46 | 33% | 75% | 74% | 72% | 64% | 53% | 1.69 | 49.1 |
| 46 | `depth-pro_n300` | `depth-pro_median` | 300 | 100% | 67% | 1.75 | 67% | 77% | 72% | 63% | 56% | 52% | 1.88 | 865.7 |
| 47 | `da3-metric-large_n300` | `da3-metric-large_median` | 300 | 100% | 67% | 1.92 | 80% | 84% | 72% | 61% | 40% | 49% | 2.01 | 50.5 |
| 48 | `depth-pro_n300` | `depth-pro_p25` | 300 | 100% | 65% | 1.92 | 60% | 86% | 70% | 57% | 48% | 47% | 2.28 | 865.7 |
| 49 | `da2-metric-large_n300` | `da2-metric-large_p10` | 300 | 100% | 65% | 1.88 | 27% | 70% | 72% | 68% | 52% | 54% | 1.71 | 266.8 |
| 50 | `da3-metric-large_n300` | `da3-metric-large_p25` | 300 | 100% | 62% | 1.91 | 73% | 80% | 63% | 55% | 40% | 39% | 2.39 | 50.5 |
| 51 | `da2-metric-small_n300` | `da2-metric-small_p25` | 300 | 100% | 61% | 1.82 | 27% | 66% | 67% | 63% | 56% | 51% | 1.79 | 49.1 |
| 52 | `depth-pro_n300` | `depth-pro_p10` | 300 | 100% | 61% | 2.17 | 53% | 82% | 65% | 55% | 36% | 40% | 2.61 | 865.7 |
| 53 | `da2-metric-base_n300` | `da2-metric-base_p10` | 300 | 100% | 60% | 2.08 | 27% | 70% | 70% | 51% | 72% | 51% | 1.94 | 99.4 |
| 54 | `da3-metric-large_n300` | `da3-metric-large_p10` | 300 | 100% | 56% | 1.95 | 67% | 68% | 63% | 49% | 36% | 31% | 2.75 | 50.5 |
| 55 | `da2-metric-large_n300` | `da2-metric-large_p25` | 300 | 100% | 53% | 2.42 | 20% | 52% | 61% | 54% | 56% | 50% | 1.93 | 266.8 |
| 56 | `da2-metric-base_n300` | `da2-metric-base_p25` | 300 | 100% | 51% | 2.61 | 27% | 59% | 59% | 42% | 64% | 46% | 2.18 | 99.4 |
| 57 | `geometric_n300` | `ground_plane` | 300 | 99% | 48% | 2.43 | 20% | 59% | 59% | 42% | 41% | 39% | 2.66 | - |
| 58 | `geometric_full` | `ground_plane` | 1500 | 99% | 46% | 2.47 | 24% | 52% | 58% | 41% | 38% | 39% | 2.61 | - |
| 59 | `yolo26s-seg_geometric-v1` | `ground_plane` | 1500 | 99% | 46% | 2.47 | 24% | 52% | 58% | 41% | 38% | 39% | 2.61 | - |
| 60 | `da2-metric-small_n300` | `da2-metric-small_median` | 300 | 100% | 45% | 2.87 | 27% | 43% | 48% | 43% | 60% | 41% | 2.39 | 49.1 |
| 61 | `da2-metric-large_n300` | `da2-metric-large_median` | 300 | 100% | 42% | 3.22 | 7% | 32% | 50% | 45% | 56% | 42% | 2.50 | 266.8 |
| 62 | `da2-metric-base_n300` | `da2-metric-base_median` | 300 | 100% | 34% | 3.85 | 13% | 30% | 37% | 30% | 60% | 38% | 2.75 | 99.4 |
| 63 | `yolo26s-depth_n300` | `yolo26s-depth_p10` | 300 | 100% | 16% | 11.39 | 53% | 39% | 17% | 1% | 0% | 14% | 7.52 | 12.1 |
| 64 | `yolo26s-depth_n300` | `yolo26s-depth_p25` | 300 | 100% | 16% | 10.96 | 47% | 39% | 20% | 1% | 0% | 15% | 7.07 | 12.1 |
| 65 | `yolo26s-depth_n300` | `yolo26s-depth_median` | 300 | 100% | 12% | 10.30 | 33% | 27% | 13% | 1% | 0% | 14% | 6.61 | 12.1 |

## vs centre

| Rank | Run | Estimator | Images | Coverage | In path within 10% | In path median error (m) | In path within 10%, 0-10 m | In path within 10%, 10-20 m | In path within 10%, 20-30 m | In path within 10%, 30-50 m | In path within 10%, 50+ m | All objects within 10% | All objects median error (m) | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-large_n300` | `metric3d-v2-large_median` | 300 | 100% | 83% | 1.36 | 55% | 51% | 96% | 95% | 87% | 57% | 1.89 | 914.4 |
| 2 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_median` | 1500 | 100% | 82% | 1.36 | 46% | 63% | 94% | 91% | 82% | 55% | 1.89 | 354.2 |
| 3 | `metric3d-v2-large_full` | `metric3d-v2-large_median` | 1500 | 100% | 82% | 1.36 | 46% | 63% | 94% | 92% | 81% | 55% | 1.89 | 897.7 |
| 4 | `metric3d-v2-large_n300` | `metric3d-v2-large_p25` | 300 | 100% | 80% | 1.50 | 36% | 46% | 94% | 93% | 84% | 49% | 2.31 | 914.4 |
| 5 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_p25` | 1500 | 100% | 79% | 1.51 | 38% | 51% | 92% | 91% | 83% | 47% | 2.29 | 354.2 |
| 6 | `metric3d-v2-large_full` | `metric3d-v2-large_p25` | 1500 | 100% | 79% | 1.51 | 38% | 51% | 92% | 91% | 83% | 47% | 2.29 | 897.7 |
| 7 | `metric3d-v2-large_full` | `metric3d-v2-large_p10` | 1500 | 100% | 74% | 1.67 | 34% | 44% | 86% | 83% | 85% | 40% | 2.53 | 897.7 |
| 8 | `metric3d-v2-large-fp16_full` | `metric3d-v2-large-fp16_p10` | 1500 | 100% | 74% | 1.68 | 34% | 44% | 86% | 82% | 85% | 40% | 2.53 | 354.2 |
| 9 | `metric3d-v2-large_n300` | `metric3d-v2-large_p10` | 300 | 100% | 71% | 1.69 | 27% | 37% | 86% | 81% | 87% | 41% | 2.51 | 914.4 |
| 10 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_median` | 1500 | 100% | 71% | 1.74 | 51% | 61% | 78% | 80% | 60% | 46% | 2.22 | 80.2 |
| 11 | `metric3d-v2-small_full` | `metric3d-v2-small_median` | 1500 | 100% | 71% | 1.74 | 51% | 61% | 78% | 80% | 60% | 46% | 2.22 | 152.1 |
| 12 | `da2-metric-large_n300` | `da2-metric-large_p10` | 300 | 100% | 71% | 1.74 | 0% | 56% | 84% | 81% | 71% | 45% | 2.25 | 266.8 |
| 13 | `metric3d-v2-small_n300` | `metric3d-v2-small_median` | 300 | 100% | 70% | 1.75 | 55% | 56% | 76% | 77% | 71% | 45% | 2.21 | 149.2 |
| 14 | `da2-metric-large_n300` | `da2-metric-large_p25` | 300 | 100% | 68% | 1.80 | 0% | 56% | 82% | 74% | 71% | 46% | 2.23 | 266.8 |
| 15 | `combinations_full` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 1500 | 100% | 67% | 2.11 | 34% | 29% | 71% | 80% | 85% | 37% | 2.74 | sum of members |
| 16 | `da2-metric-large_n300` | `da2-metric-large_median` | 300 | 100% | 66% | 2.11 | 18% | 59% | 76% | 68% | 71% | 49% | 2.25 | 266.8 |
| 17 | `da2-metric-base_n300` | `da2-metric-base_p25` | 300 | 100% | 64% | 1.70 | 9% | 51% | 78% | 66% | 74% | 44% | 2.36 | 99.4 |
| 18 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_p25` | 1500 | 100% | 64% | 2.04 | 41% | 48% | 73% | 72% | 56% | 36% | 2.70 | 80.2 |
| 19 | `metric3d-v2-small_full` | `metric3d-v2-small_p25` | 1500 | 100% | 64% | 2.03 | 41% | 48% | 73% | 72% | 56% | 36% | 2.70 | 152.1 |
| 20 | `da2-metric-base_n300` | `da2-metric-base_p10` | 300 | 100% | 64% | 1.51 | 9% | 51% | 78% | 65% | 74% | 42% | 2.32 | 99.4 |
| 21 | `da2-metric-small_n300` | `da2-metric-small_median` | 300 | 100% | 63% | 2.00 | 18% | 61% | 71% | 65% | 65% | 44% | 2.46 | 49.1 |
| 22 | `metric3d-v2-small_n300` | `metric3d-v2-small_p25` | 300 | 100% | 62% | 2.09 | 45% | 41% | 73% | 72% | 55% | 36% | 2.75 | 149.2 |
| 23 | `unidepth-v2-large_full` | `unidepth-v2-large_median` | 1500 | 100% | 61% | 2.28 | 45% | 32% | 59% | 73% | 76% | 40% | 2.56 | 209.6 |
| 24 | `da2-metric-small_n300` | `da2-metric-small_p10` | 300 | 100% | 61% | 1.91 | 27% | 44% | 76% | 65% | 61% | 37% | 2.72 | 49.1 |
| 25 | `unidepth-v2-base_full` | `unidepth-v2-base_median` | 1500 | 100% | 61% | 2.22 | 33% | 38% | 66% | 70% | 68% | 37% | 2.70 | 466.1 |
| 26 | `da2-metric-small_n300` | `da2-metric-small_p25` | 300 | 100% | 60% | 1.91 | 0% | 44% | 73% | 69% | 61% | 40% | 2.38 | 49.1 |
| 27 | `metric3d-v2-small_n300` | `metric3d-v2-small_p10` | 300 | 100% | 60% | 2.35 | 45% | 39% | 73% | 68% | 52% | 29% | 3.04 | 149.2 |
| 28 | `geometric_full` | `known_size` | 1500 | 100% | 59% | 2.19 | 63% | 44% | 58% | 65% | 64% | 58% | 1.79 | - |
| 29 | `geometric_full` | `combined` | 1500 | 100% | 59% | 2.19 | 63% | 44% | 58% | 65% | 64% | 58% | 1.79 | - |
| 30 | `yolo26s-seg_geometric-v1` | `known_size` | 1500 | 100% | 59% | 2.19 | 63% | 44% | 58% | 65% | 64% | 58% | 1.79 | - |
| 31 | `geometric_n300` | `known_size` | 300 | 100% | 59% | 2.26 | 64% | 41% | 57% | 65% | 68% | 59% | 1.73 | - |
| 32 | `geometric_n300` | `combined` | 300 | 100% | 59% | 2.26 | 64% | 41% | 57% | 65% | 68% | 59% | 1.73 | - |
| 33 | `metric3d-v2-small-fp16_full` | `metric3d-v2-small-fp16_p10` | 1500 | 100% | 58% | 2.29 | 35% | 40% | 69% | 66% | 52% | 30% | 3.02 | 80.2 |
| 34 | `metric3d-v2-small_full` | `metric3d-v2-small_p10` | 1500 | 100% | 58% | 2.29 | 35% | 41% | 69% | 66% | 51% | 30% | 3.02 | 152.1 |
| 35 | `da2-metric-base_n300` | `da2-metric-base_median` | 300 | 100% | 58% | 2.43 | 9% | 56% | 71% | 53% | 68% | 44% | 2.51 | 99.4 |
| 36 | `unidepth-v2-small_n300` | `unidepth-v2-small_median` | 300 | 100% | 58% | 2.36 | 27% | 29% | 61% | 70% | 71% | 37% | 2.75 | 60.1 |
| 37 | `unidepth-v2-large_n300` | `unidepth-v2-large_median` | 300 | 100% | 57% | 2.22 | 64% | 22% | 65% | 66% | 65% | 40% | 2.54 | 215.1 |
| 38 | `unidepth-v2-base_n300` | `unidepth-v2-base_median` | 300 | 100% | 54% | 2.23 | 18% | 27% | 65% | 62% | 65% | 35% | 2.70 | 110.1 |
| 39 | `unidepth-v2-small_n300` | `unidepth-v2-small_p25` | 300 | 100% | 53% | 2.58 | 18% | 20% | 55% | 66% | 77% | 31% | 3.15 | 60.1 |
| 40 | `combinations_full` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 1500 | 100% | 53% | 2.51 | 32% | 28% | 59% | 64% | 52% | 25% | 3.28 | sum of members |
| 41 | `combinations_full` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 1500 | 100% | 52% | 2.60 | 32% | 26% | 56% | 62% | 64% | 27% | 3.20 | sum of members |
| 42 | `unidepth-v2-large_full` | `unidepth-v2-large_p25` | 1500 | 100% | 51% | 2.69 | 32% | 25% | 46% | 62% | 74% | 30% | 3.09 | 209.6 |
| 43 | `unidepth-v2-base_n300` | `unidepth-v2-base_p25` | 300 | 100% | 49% | 2.69 | 18% | 15% | 59% | 58% | 65% | 27% | 3.21 | 110.1 |
| 44 | `unidepth-v2-small_n300` | `unidepth-v2-small_p10` | 300 | 100% | 49% | 2.66 | 18% | 12% | 49% | 59% | 81% | 26% | 3.40 | 60.1 |
| 45 | `unidepth-v2-base_full` | `unidepth-v2-base_p25` | 1500 | 100% | 49% | 2.63 | 26% | 26% | 51% | 58% | 58% | 26% | 3.26 | 466.1 |
| 46 | `unidepth-v2-large_full` | `unidepth-v2-large_p10` | 1500 | 100% | 46% | 2.90 | 27% | 23% | 40% | 54% | 72% | 26% | 3.36 | 209.6 |
| 47 | `unidepth-v2-large_n300` | `unidepth-v2-large_p25` | 300 | 100% | 46% | 2.68 | 36% | 17% | 47% | 55% | 61% | 30% | 3.08 | 215.1 |
| 48 | `combinations_full` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 1500 | 100% | 45% | 2.89 | 21% | 23% | 39% | 55% | 71% | 25% | 3.41 | sum of members |
| 49 | `geometric_n300` | `ground_plane` | 300 | 99% | 45% | 2.70 | 55% | 51% | 49% | 41% | 36% | 37% | 2.75 | - |
| 50 | `unidepth-v2-base_full` | `unidepth-v2-base_p10` | 1500 | 100% | 43% | 2.85 | 25% | 22% | 43% | 53% | 54% | 22% | 3.52 | 466.1 |
| 51 | `geometric_full` | `ground_plane` | 1500 | 99% | 43% | 2.91 | 43% | 41% | 56% | 36% | 35% | 37% | 2.75 | - |
| 52 | `yolo26s-seg_geometric-v1` | `ground_plane` | 1500 | 99% | 43% | 2.91 | 43% | 41% | 56% | 36% | 35% | 37% | 2.75 | - |
| 53 | `unidepth-v2-large_n300` | `unidepth-v2-large_p10` | 300 | 100% | 43% | 2.93 | 36% | 17% | 47% | 50% | 55% | 25% | 3.38 | 215.1 |
| 54 | `unidepth-v2-base_n300` | `unidepth-v2-base_p10` | 300 | 100% | 42% | 2.90 | 18% | 12% | 47% | 53% | 58% | 22% | 3.48 | 110.1 |
| 55 | `depth-pro_n300` | `depth-pro_median` | 300 | 100% | 40% | 3.06 | 27% | 46% | 49% | 36% | 29% | 25% | 3.49 | 865.7 |
| 56 | `combinations_full` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 1500 | 100% | 36% | 3.14 | 22% | 18% | 37% | 44% | 46% | 18% | 3.68 | sum of members |
| 57 | `combinations_full` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 1500 | 100% | 34% | 3.07 | 16% | 18% | 40% | 41% | 36% | 16% | 3.78 | sum of members |
| 58 | `da3-metric-large_n300` | `da3-metric-large_median` | 300 | 100% | 33% | 3.20 | 9% | 20% | 39% | 38% | 39% | 20% | 3.66 | 50.5 |
| 59 | `depth-pro_n300` | `depth-pro_p25` | 300 | 100% | 32% | 3.50 | 18% | 41% | 41% | 30% | 16% | 19% | 4.02 | 865.7 |
| 60 | `da3-metric-large_n300` | `da3-metric-large_p25` | 300 | 100% | 25% | 3.66 | 0% | 7% | 33% | 31% | 29% | 12% | 4.25 | 50.5 |
| 61 | `depth-pro_n300` | `depth-pro_p10` | 300 | 100% | 25% | 3.85 | 18% | 32% | 35% | 22% | 10% | 15% | 4.45 | 865.7 |
| 62 | `da3-metric-large_n300` | `da3-metric-large_p10` | 300 | 100% | 22% | 3.80 | 0% | 5% | 35% | 28% | 19% | 10% | 4.68 | 50.5 |
| 63 | `yolo26s-depth_n300` | `yolo26s-depth_median` | 300 | 100% | 16% | 12.48 | 36% | 44% | 20% | 3% | 0% | 15% | 8.44 | 12.1 |
| 64 | `yolo26s-depth_n300` | `yolo26s-depth_p25` | 300 | 100% | 15% | 12.94 | 18% | 46% | 14% | 3% | 0% | 13% | 8.93 | 12.1 |
| 65 | `yolo26s-depth_n300` | `yolo26s-depth_p10` | 300 | 100% | 12% | 13.32 | 27% | 37% | 12% | 1% | 0% | 10% | 9.47 | 12.1 |
