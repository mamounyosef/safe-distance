# nuScenes distance benchmark: comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **in path, within 10%** of the true distance. `_median`, `_p10`, `_p25` mark how a
depth model's per-pixel depth inside the object's mask is summarised.

## vs nearest surface

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `combinations` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 90% | 0.67 | 94% | 81% | 86% | 94% | 85% | 94% | 92% | 72% | sum of members |
| 2 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 86% | 0.68 | 90% | 76% | 95% | 92% | 75% | 84% | 83% | 68% | sum of members |
| 3 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 85% | 0.74 | 87% | 81% | 98% | 90% | 79% | 81% | 74% | 57% | sum of members |
| 4 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 85% | 0.78 | 92% | 68% | 90% | 89% | 72% | 87% | 91% | 68% | sum of members |
| 5 | `unidepth-v2-large` | `unidepth-v2-large_p10` | 85% | 0.70 | 86% | 81% | 86% | 92% | 83% | 84% | 74% | 74% | 213.1 |
| 6 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 84% | 0.81 | 87% | 76% | 95% | 90% | 74% | 81% | 77% | 58% | sum of members |
| 7 | `unidepth-v2-base` | `unidepth-v2-base_p10` | 83% | 0.85 | 87% | 71% | 83% | 87% | 75% | 81% | 87% | 74% | 111.5 |
| 8 | `unidepth-v2-large` | `unidepth-v2-large_p25` | 82% | 0.78 | 84% | 77% | 71% | 93% | 80% | 84% | 74% | 76% | 213.1 |
| 9 | `unidepth-v2-base` | `unidepth-v2-base_p25` | 79% | 0.90 | 84% | 67% | 78% | 81% | 73% | 74% | 87% | 76% | 111.5 |
| 10 | `combinations` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 77% | 0.84 | 86% | 55% | 59% | 87% | 64% | 87% | 94% | 75% | sum of members |
| 11 | `metric3d-v2-small` | `metric3d-v2-small_p10` | 76% | 0.97 | 85% | 54% | 88% | 85% | 58% | 81% | 72% | 57% | 156.0 |
| 12 | `metric3d-v2-small` | `metric3d-v2-small_p25` | 76% | 0.94 | 85% | 55% | 85% | 82% | 62% | 81% | 74% | 63% | 156.0 |
| 13 | `unidepth-v2-large` | `unidepth-v2-large_median` | 72% | 0.99 | 74% | 68% | 41% | 85% | 79% | 77% | 70% | 76% | 213.1 |
| 14 | `metric3d-v2-small` | `metric3d-v2-small_median` | 70% | 1.17 | 82% | 43% | 73% | 72% | 60% | 81% | 74% | 67% | 156.0 |
| 15 | `unidepth-v2-base` | `unidepth-v2-base_median` | 70% | 1.17 | 75% | 59% | 68% | 70% | 72% | 65% | 75% | 74% | 111.5 |
| 16 | `metric3d-v2-large` | `metric3d-v2-large_p10` | 69% | 1.07 | 82% | 38% | 36% | 81% | 54% | 94% | 92% | 64% | 886.8 |
| 17 | `metric3d-v2-large` | `metric3d-v2-large_p25` | 68% | 1.04 | 81% | 38% | 27% | 82% | 54% | 94% | 94% | 71% | 886.8 |
| 18 | `unidepth-v2-small` | `unidepth-v2-small_p10` | 63% | 1.30 | 66% | 55% | 37% | 71% | 65% | 65% | 70% | 66% | 60.7 |
| 19 | `da3-metric-large` | `da3-metric-large_p10` | 61% | 1.40 | 63% | 57% | 37% | 76% | 64% | 74% | 47% | 60% | 80.7 |
| 20 | `unidepth-v2-small` | `unidepth-v2-small_p25` | 61% | 1.44 | 63% | 55% | 34% | 71% | 64% | 61% | 68% | 67% | 60.7 |
| 21 | `da3-metric-large` | `da3-metric-large_p25` | 61% | 1.28 | 63% | 55% | 32% | 76% | 63% | 74% | 53% | 62% | 80.7 |
| 22 | `metric3d-v2-large` | `metric3d-v2-large_median` | 61% | 1.18 | 73% | 32% | 17% | 71% | 46% | 90% | 96% | 74% | 886.8 |
| 23 | `da3-metric-large` | `da3-metric-large_median` | 60% | 1.40 | 65% | 48% | 19% | 71% | 67% | 81% | 64% | 64% | 80.7 |
| 24 | `geometric` | `known_size` | 52% | 1.64 | 51% | 55% | 58% | 64% | 52% | 65% | 19% | 57% | - |
| 25 | `geometric` | `combined` | 52% | 1.64 | 51% | 55% | 58% | 64% | 52% | 65% | 19% | 57% | - |
| 26 | `unidepth-v2-small` | `unidepth-v2-small_median` | 49% | 1.84 | 52% | 41% | 22% | 56% | 48% | 55% | 64% | 62% | 60.7 |
| 27 | `depth-pro` | `depth-pro_median` | 42% | 2.62 | 34% | 63% | 86% | 42% | 42% | 16% | 9% | 24% | 853.0 |
| 28 | `depth-pro` | `depth-pro_p25` | 41% | 2.73 | 31% | 66% | 86% | 39% | 44% | 10% | 8% | 20% | 853.0 |
| 29 | `depth-pro` | `depth-pro_p10` | 40% | 2.81 | 30% | 63% | 83% | 37% | 44% | 6% | 8% | 18% | 853.0 |
| 30 | `geometric` | `ground_plane` | 24% | 3.19 | 13% | 47% | 25% | 23% | 34% | 3% | 15% | 25% | - |
| 31 | `da2-metric-small` | `da2-metric-small_p10` | 20% | 5.06 | 15% | 31% | 0% | 12% | 33% | 19% | 36% | 22% | 32.0 |
| 32 | `da2-metric-small` | `da2-metric-small_p25` | 17% | 5.19 | 12% | 29% | 0% | 12% | 26% | 16% | 32% | 20% | 32.0 |
| 33 | `da2-metric-small` | `da2-metric-small_median` | 17% | 5.64 | 12% | 27% | 0% | 12% | 21% | 13% | 38% | 17% | 32.0 |
| 34 | `da2-metric-base` | `da2-metric-base_p10` | 14% | 5.31 | 18% | 3% | 0% | 1% | 12% | 29% | 45% | 23% | 54.2 |
| 35 | `da2-metric-base` | `da2-metric-base_p25` | 13% | 5.80 | 17% | 2% | 0% | 0% | 11% | 26% | 45% | 22% | 54.2 |
| 36 | `yolo26s-depth` | `yolo26s-depth_median` | 10% | 6.63 | 11% | 10% | 42% | 7% | 1% | 0% | 0% | 8% | 13.1 |
| 37 | `da2-metric-base` | `da2-metric-base_median` | 10% | 6.47 | 13% | 1% | 0% | 0% | 6% | 13% | 42% | 19% | 54.2 |
| 38 | `da2-metric-large` | `da2-metric-large_p10` | 10% | 6.05 | 12% | 3% | 0% | 2% | 6% | 16% | 36% | 20% | 132.6 |
| 39 | `da2-metric-large` | `da2-metric-large_p25` | 8% | 6.75 | 11% | 0% | 0% | 0% | 6% | 16% | 28% | 19% | 132.6 |
| 40 | `da2-metric-large` | `da2-metric-large_median` | 7% | 7.88 | 10% | 0% | 0% | 0% | 4% | 10% | 30% | 16% | 132.6 |
| 41 | `yolo26s-depth` | `yolo26s-depth_p25` | 7% | 7.64 | 6% | 10% | 29% | 5% | 0% | 0% | 0% | 5% | 13.1 |
| 42 | `yolo26s-depth` | `yolo26s-depth_p10` | 5% | 8.14 | 4% | 9% | 22% | 4% | 0% | 0% | 0% | 4% | 13.1 |

## vs centre

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `unidepth-v2-large` | `unidepth-v2-large_median` | 76% | 1.34 | 78% | 71% | 54% | 79% | 83% | 80% | 79% | 61% | 213.1 |
| 2 | `unidepth-v2-base` | `unidepth-v2-base_median` | 76% | 1.40 | 79% | 68% | 54% | 78% | 83% | 73% | 85% | 62% | 111.5 |
| 3 | `metric3d-v2-large` | `metric3d-v2-large_median` | 75% | 1.39 | 77% | 72% | 56% | 71% | 78% | 82% | 92% | 55% | 886.8 |
| 4 | `unidepth-v2-base` | `unidepth-v2-base_p25` | 72% | 1.58 | 75% | 64% | 52% | 61% | 77% | 77% | 96% | 55% | 111.5 |
| 5 | `combinations` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 71% | 1.60 | 72% | 70% | 52% | 56% | 81% | 82% | 89% | 49% | sum of members |
| 6 | `metric3d-v2-large` | `metric3d-v2-large_p25` | 70% | 1.53 | 71% | 68% | 54% | 57% | 73% | 86% | 87% | 46% | 886.8 |
| 7 | `unidepth-v2-large` | `unidepth-v2-large_p25` | 69% | 1.68 | 72% | 64% | 52% | 56% | 76% | 80% | 89% | 53% | 213.1 |
| 8 | `unidepth-v2-small` | `unidepth-v2-small_median` | 69% | 1.24 | 69% | 71% | 29% | 76% | 86% | 68% | 74% | 59% | 60.7 |
| 9 | `unidepth-v2-base` | `unidepth-v2-base_p10` | 69% | 1.72 | 72% | 61% | 52% | 50% | 73% | 82% | 94% | 49% | 111.5 |
| 10 | `unidepth-v2-large` | `unidepth-v2-large_p10` | 68% | 1.78 | 70% | 63% | 52% | 52% | 74% | 77% | 91% | 47% | 213.1 |
| 11 | `metric3d-v2-small` | `metric3d-v2-small_median` | 68% | 1.70 | 68% | 66% | 54% | 65% | 70% | 70% | 79% | 45% | 156.0 |
| 12 | `unidepth-v2-small` | `unidepth-v2-small_p25` | 67% | 1.42 | 66% | 70% | 44% | 61% | 80% | 68% | 77% | 53% | 60.7 |
| 13 | `metric3d-v2-large` | `metric3d-v2-large_p10` | 67% | 1.61 | 67% | 67% | 54% | 54% | 69% | 82% | 85% | 40% | 886.8 |
| 14 | `combinations` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 67% | 1.77 | 69% | 61% | 52% | 50% | 71% | 84% | 85% | 39% | sum of members |
| 15 | `unidepth-v2-small` | `unidepth-v2-small_p10` | 65% | 1.47 | 64% | 68% | 48% | 57% | 78% | 66% | 74% | 48% | 60.7 |
| 16 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 64% | 1.86 | 66% | 62% | 52% | 43% | 73% | 75% | 87% | 38% | sum of members |
| 17 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 64% | 1.77 | 65% | 63% | 52% | 41% | 73% | 75% | 89% | 40% | sum of members |
| 18 | `metric3d-v2-small` | `metric3d-v2-small_p25` | 60% | 1.80 | 57% | 65% | 52% | 46% | 67% | 59% | 75% | 35% | 156.0 |
| 19 | `da3-metric-large` | `da3-metric-large_median` | 57% | 1.79 | 52% | 69% | 35% | 72% | 64% | 52% | 49% | 47% | 80.7 |
| 20 | `metric3d-v2-small` | `metric3d-v2-small_p10` | 55% | 1.93 | 52% | 60% | 50% | 35% | 61% | 55% | 77% | 30% | 156.0 |
| 21 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 53% | 2.19 | 52% | 55% | 50% | 33% | 56% | 55% | 79% | 28% | sum of members |
| 22 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 52% | 2.11 | 51% | 55% | 50% | 30% | 59% | 55% | 75% | 29% | sum of members |
| 23 | `da3-metric-large` | `da3-metric-large_p25` | 51% | 1.93 | 45% | 65% | 42% | 61% | 63% | 41% | 32% | 39% | 80.7 |
| 24 | `geometric` | `ground_plane` | 50% | 2.03 | 42% | 67% | 71% | 44% | 61% | 26% | 26% | 34% | - |
| 25 | `da3-metric-large` | `da3-metric-large_p10` | 48% | 2.06 | 42% | 62% | 50% | 50% | 62% | 34% | 28% | 34% | 80.7 |
| 26 | `geometric` | `known_size` | 44% | 2.56 | 45% | 40% | 42% | 55% | 46% | 55% | 17% | 48% | - |
| 27 | `geometric` | `combined` | 44% | 2.56 | 45% | 40% | 42% | 55% | 46% | 55% | 17% | 48% | - |
| 28 | `da2-metric-small` | `da2-metric-small_p10` | 33% | 4.05 | 30% | 39% | 37% | 20% | 36% | 43% | 36% | 39% | 32.0 |
| 29 | `depth-pro` | `depth-pro_median` | 31% | 3.54 | 20% | 59% | 50% | 18% | 56% | 16% | 6% | 12% | 853.0 |
| 30 | `da2-metric-small` | `da2-metric-small_p25` | 30% | 4.29 | 26% | 40% | 31% | 16% | 37% | 39% | 34% | 36% | 32.0 |
| 31 | `depth-pro` | `depth-pro_p25` | 28% | 3.82 | 18% | 54% | 46% | 16% | 52% | 11% | 4% | 9% | 853.0 |
| 32 | `da2-metric-base` | `da2-metric-base_p10` | 28% | 3.95 | 33% | 16% | 33% | 10% | 24% | 45% | 42% | 39% | 54.2 |
| 33 | `depth-pro` | `depth-pro_p10` | 27% | 4.15 | 16% | 54% | 46% | 12% | 52% | 11% | 4% | 8% | 853.0 |
| 34 | `da2-metric-small` | `da2-metric-small_median` | 26% | 4.70 | 21% | 39% | 15% | 12% | 36% | 36% | 36% | 32% | 32.0 |
| 35 | `da2-metric-base` | `da2-metric-base_p25` | 23% | 4.30 | 27% | 13% | 15% | 6% | 21% | 41% | 45% | 37% | 54.2 |
| 36 | `da2-metric-large` | `da2-metric-large_p10` | 19% | 4.90 | 23% | 7% | 21% | 4% | 10% | 36% | 40% | 34% | 132.6 |
| 37 | `da2-metric-base` | `da2-metric-base_median` | 17% | 5.42 | 22% | 6% | 2% | 4% | 14% | 34% | 45% | 31% | 54.2 |
| 38 | `da2-metric-large` | `da2-metric-large_p25` | 16% | 5.51 | 20% | 4% | 6% | 1% | 10% | 36% | 40% | 32% | 132.6 |
| 39 | `da2-metric-large` | `da2-metric-large_median` | 12% | 6.66 | 17% | 1% | 2% | 0% | 8% | 27% | 38% | 26% | 132.6 |
| 40 | `yolo26s-depth` | `yolo26s-depth_p25` | 1% | 9.74 | 2% | 0% | 0% | 5% | 0% | 0% | 0% | 1% | 13.1 |
| 41 | `yolo26s-depth` | `yolo26s-depth_median` | 1% | 8.85 | 1% | 0% | 0% | 4% | 0% | 0% | 0% | 2% | 13.1 |
| 42 | `yolo26s-depth` | `yolo26s-depth_p10` | 1% | 10.24 | 1% | 0% | 0% | 4% | 0% | 0% | 0% | 1% | 13.1 |
