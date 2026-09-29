# nuScenes distance benchmark: traffic cones and barriers (labelled outlines)

Generated automatically from every `results/<run>/results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **in path, within 10%** of the true distance. `_median`, `_p10`, `_p25` mark how a
depth model's per-pixel depth inside the object's mask is summarised.

## vs nearest surface

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `combinations` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 83% | 1.19 | 83% | - | 100% | 88% | 80% | 77% | 50% | 54% | sum of members |
| 2 | `combinations` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 82% | 1.03 | 82% | - | 100% | 88% | 80% | 73% | 50% | 62% | sum of members |
| 3 | `unidepth-v2-large` | `unidepth-v2-large_p10` | 82% | 0.48 | 82% | - | 100% | 88% | 76% | 77% | 50% | 62% | 212.6 |
| 4 | `metric3d-v2-large` | `metric3d-v2-large_p25` | 81% | 1.43 | 81% | - | 92% | 84% | 80% | 77% | 50% | 57% | 885.8 |
| 5 | `metric3d-v2-large-fp16` | `metric3d-v2-large-fp16_p25` | 81% | 1.43 | 81% | - | 92% | 84% | 80% | 77% | 50% | 57% | 355.1 |
| 6 | `unidepth-v2-base` | `unidepth-v2-base_p10` | 80% | 0.62 | 80% | - | 100% | 88% | 76% | 70% | 50% | 64% | 110.3 |
| 7 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 79% | 1.15 | 79% | - | 100% | 88% | 72% | 70% | 50% | 46% | sum of members |
| 8 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 78% | 1.20 | 78% | - | 100% | 88% | 80% | 63% | 25% | 48% | sum of members |
| 9 | `unidepth-v2-large` | `unidepth-v2-large_p25` | 76% | 0.99 | 76% | - | 100% | 84% | 68% | 70% | 25% | 68% | 212.6 |
| 10 | `metric3d-v2-large` | `metric3d-v2-large_p10` | 74% | 1.42 | 74% | - | 92% | 81% | 76% | 63% | 25% | 48% | 885.8 |
| 11 | `metric3d-v2-large-fp16` | `metric3d-v2-large-fp16_p10` | 74% | 1.43 | 74% | - | 92% | 81% | 76% | 63% | 25% | 48% | 355.1 |
| 12 | `unidepth-v2-base` | `unidepth-v2-base_p25` | 74% | 1.01 | 74% | - | 85% | 84% | 68% | 67% | 50% | 65% | 110.3 |
| 13 | `metric3d-v2-large` | `metric3d-v2-large_median` | 71% | 1.35 | 71% | - | 31% | 78% | 80% | 77% | 50% | 62% | 885.8 |
| 14 | `metric3d-v2-large-fp16` | `metric3d-v2-large-fp16_median` | 71% | 1.35 | 71% | - | 31% | 78% | 80% | 77% | 50% | 62% | 355.1 |
| 15 | `metric3d-v2-small` | `metric3d-v2-small_p25` | 71% | 1.14 | 71% | - | 85% | 88% | 60% | 67% | 0% | 42% | 153.4 |
| 16 | `metric3d-v2-small-fp16` | `metric3d-v2-small-fp16_p25` | 71% | 1.14 | 71% | - | 85% | 88% | 60% | 67% | 0% | 42% | 83.4 |
| 17 | `metric3d-v2-small` | `metric3d-v2-small_median` | 63% | 1.39 | 63% | - | 8% | 69% | 88% | 70% | 0% | 51% | 153.4 |
| 18 | `metric3d-v2-small-fp16` | `metric3d-v2-small-fp16_median` | 63% | 1.40 | 63% | - | 8% | 69% | 88% | 70% | 0% | 51% | 83.4 |
| 19 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 62% | 1.32 | 62% | - | 100% | 84% | 48% | 40% | 0% | 31% | sum of members |
| 20 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 62% | 1.32 | 62% | - | 100% | 84% | 48% | 40% | 0% | 32% | sum of members |
| 21 | `metric3d-v2-small` | `metric3d-v2-small_p10` | 61% | 1.32 | 61% | - | 92% | 84% | 48% | 40% | 0% | 33% | 153.4 |
| 22 | `metric3d-v2-small-fp16` | `metric3d-v2-small-fp16_p10` | 61% | 1.33 | 61% | - | 92% | 84% | 48% | 40% | 0% | 33% | 83.4 |
| 23 | `unidepth-v2-large` | `unidepth-v2-large_median` | 38% | 3.23 | 38% | - | 31% | 44% | 44% | 37% | 0% | 44% | 212.6 |
| 24 | `unidepth-v2-base` | `unidepth-v2-base_median` | 36% | 3.62 | 36% | - | 31% | 47% | 40% | 23% | 25% | 40% | 110.3 |
| 25 | `geometric` | `ground_plane` | 29% | 5.00 | 29% | - | 85% | 53% | 8% | 0% | 0% | 47% | - |
| 26 | `geometric` | `combined` | 29% | 5.00 | 29% | - | 85% | 53% | 8% | 0% | 0% | 47% | - |
| 27 | `geometric` | `known_size` | - | - | - | - | - | - | - | - | - | - | - |

## vs centre

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `combinations` | `mean(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 80% | 1.27 | 80% | - | 90% | 91% | 73% | 73% | 50% | 55% | sum of members |
| 2 | `unidepth-v2-base` | `unidepth-v2-base_p25` | 79% | 0.67 | 79% | - | 100% | 88% | 77% | 67% | 50% | 62% | 110.3 |
| 3 | `unidepth-v2-base` | `unidepth-v2-base_p10` | 78% | 0.78 | 78% | - | 90% | 91% | 77% | 63% | 50% | 58% | 110.3 |
| 4 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 76% | 1.37 | 76% | - | 100% | 88% | 73% | 63% | 25% | 40% | sum of members |
| 5 | `unidepth-v2-large` | `unidepth-v2-large_p10` | 76% | 0.89 | 76% | - | 80% | 85% | 69% | 73% | 50% | 54% | 212.6 |
| 6 | `metric3d-v2-large-fp16` | `metric3d-v2-large-fp16_p25` | 75% | 1.49 | 75% | - | 80% | 88% | 65% | 70% | 50% | 51% | 355.1 |
| 7 | `unidepth-v2-large` | `unidepth-v2-large_p25` | 75% | 1.01 | 75% | - | 90% | 91% | 62% | 70% | 25% | 63% | 212.6 |
| 8 | `combinations` | `mean(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 74% | 1.36 | 74% | - | 90% | 88% | 65% | 63% | 50% | 37% | sum of members |
| 9 | `metric3d-v2-large` | `metric3d-v2-large_p25` | 74% | 1.49 | 74% | - | 80% | 88% | 65% | 67% | 50% | 51% | 885.8 |
| 10 | `combinations` | `min(metric3d-v2-large_p25,unidepth-v2-large_p10)` | 72% | 1.20 | 72% | - | 80% | 85% | 62% | 67% | 50% | 45% | sum of members |
| 11 | `metric3d-v2-large` | `metric3d-v2-large_median` | 71% | 1.21 | 71% | - | 30% | 82% | 69% | 77% | 50% | 61% | 885.8 |
| 12 | `metric3d-v2-large-fp16` | `metric3d-v2-large-fp16_median` | 71% | 1.21 | 71% | - | 30% | 82% | 69% | 77% | 50% | 61% | 355.1 |
| 13 | `metric3d-v2-large` | `metric3d-v2-large_p10` | 67% | 1.53 | 67% | - | 80% | 82% | 65% | 53% | 25% | 41% | 885.8 |
| 14 | `metric3d-v2-large-fp16` | `metric3d-v2-large-fp16_p10` | 67% | 1.51 | 67% | - | 80% | 82% | 65% | 53% | 25% | 41% | 355.1 |
| 15 | `metric3d-v2-small` | `metric3d-v2-small_median` | 67% | 1.36 | 67% | - | 50% | 76% | 73% | 67% | 0% | 47% | 153.4 |
| 16 | `metric3d-v2-small-fp16` | `metric3d-v2-small-fp16_median` | 67% | 1.35 | 67% | - | 50% | 76% | 73% | 67% | 0% | 47% | 83.4 |
| 17 | `metric3d-v2-small-fp16` | `metric3d-v2-small-fp16_p25` | 67% | 1.32 | 67% | - | 100% | 88% | 46% | 60% | 0% | 37% | 83.4 |
| 18 | `metric3d-v2-small` | `metric3d-v2-small_p25` | 66% | 1.32 | 66% | - | 100% | 88% | 46% | 57% | 0% | 36% | 153.4 |
| 19 | `metric3d-v2-small` | `metric3d-v2-small_p10` | 56% | 1.61 | 56% | - | 100% | 82% | 42% | 30% | 0% | 26% | 153.4 |
| 20 | `metric3d-v2-small-fp16` | `metric3d-v2-small-fp16_p10` | 56% | 1.61 | 56% | - | 100% | 82% | 42% | 30% | 0% | 26% | 83.4 |
| 21 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-base_p10)` | 55% | 1.61 | 55% | - | 90% | 82% | 42% | 30% | 0% | 24% | sum of members |
| 22 | `combinations` | `min(metric3d-v2-small_p10,unidepth-v2-large_p10)` | 52% | 1.61 | 52% | - | 80% | 76% | 42% | 30% | 0% | 23% | sum of members |
| 23 | `unidepth-v2-large` | `unidepth-v2-large_median` | 40% | 2.96 | 40% | - | 20% | 44% | 46% | 43% | 0% | 42% | 212.6 |
| 24 | `geometric` | `ground_plane` | 38% | 4.51 | 38% | - | 100% | 79% | 12% | 0% | 0% | 49% | - |
| 25 | `geometric` | `combined` | 38% | 4.51 | 38% | - | 100% | 79% | 12% | 0% | 0% | 49% | - |
| 26 | `unidepth-v2-base` | `unidepth-v2-base_median` | 35% | 3.33 | 35% | - | 20% | 44% | 42% | 23% | 25% | 40% | 110.3 |
| 27 | `geometric` | `known_size` | - | - | - | - | - | - | - | - | - | - | - |
