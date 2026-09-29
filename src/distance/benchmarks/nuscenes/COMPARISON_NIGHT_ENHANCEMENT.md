# nuScenes distance benchmark: night image enhancement (night frames only)

Generated automatically from every `results/<run>/results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **in path, within 10%** of the true distance. `_median`, `_p10`, `_p25` mark how a
depth model's per-pixel depth inside the object's mask is summarised.

## vs nearest surface

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p10` | 82% | 0.82 | - | 82% | 62% | 80% | 94% | 0% | 0% | 35% | 106.2 |
| 2 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p25` | 79% | 0.83 | - | 79% | 38% | 80% | 94% | 0% | 0% | 38% | 106.2 |
| 3 | `metric3d-v2-small-fp16+clahe2_night` | `metric3d-v2-small-fp16+clahe2_p10` | 76% | 1.04 | - | 76% | 62% | 80% | 79% | 50% | 0% | 37% | 107.0 |
| 4 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_median` | 73% | 0.97 | - | 73% | 0% | 83% | 92% | 0% | 0% | 41% | 106.2 |
| 5 | `metric3d-v2-small-fp16+gamma06-clahe2_night` | `metric3d-v2-small-fp16+gamma06-clahe2_p10` | 73% | 0.98 | - | 73% | 38% | 73% | 88% | 0% | 0% | 34% | 111.6 |
| 6 | `metric3d-v2-small-fp16+clahe2_night` | `metric3d-v2-small-fp16+clahe2_p25` | 70% | 1.01 | - | 70% | 46% | 73% | 77% | 50% | 0% | 37% | 107.0 |
| 7 | `metric3d-v2-small-fp16+gamma06-clahe2_night` | `metric3d-v2-small-fp16+gamma06-clahe2_p25` | 69% | 0.91 | - | 69% | 38% | 67% | 83% | 0% | 0% | 36% | 111.6 |
| 8 | `metric3d-v2-small-fp16+clahe2_night` | `metric3d-v2-small-fp16+clahe2_median` | 66% | 1.07 | - | 66% | 31% | 70% | 75% | 50% | 0% | 41% | 107.0 |
| 9 | `metric3d-v2-small-fp16+gamma06-clahe2_night` | `metric3d-v2-small-fp16+gamma06-clahe2_median` | 64% | 1.02 | - | 64% | 15% | 67% | 79% | 0% | 0% | 39% | 111.6 |
| 10 | `metric3d-v2-small-fp16+gamma06_night` | `metric3d-v2-small-fp16+gamma06_p10` | 61% | 1.17 | - | 61% | 54% | 80% | 52% | 50% | 0% | 35% | 91.5 |
| 11 | `metric3d-v2-small-fp16+gamma06_night` | `metric3d-v2-small-fp16+gamma06_p25` | 61% | 1.28 | - | 61% | 54% | 77% | 54% | 50% | 0% | 37% | 91.5 |
| 12 | `metric3d-v2-small-fp16+bright-contrast_night` | `metric3d-v2-small-fp16+bright-contrast_p10` | 59% | 1.13 | - | 59% | 62% | 73% | 50% | 50% | 0% | 34% | 85.2 |
| 13 | `metric3d-v2-small-fp16+bright-contrast_night` | `metric3d-v2-small-fp16+bright-contrast_p25` | 56% | 1.14 | - | 56% | 54% | 73% | 48% | 50% | 0% | 35% | 85.2 |
| 14 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p25` | 56% | 1.35 | - | 56% | 54% | 77% | 46% | 50% | 0% | 37% | 87.0 |
| 15 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p10` | 55% | 1.16 | - | 55% | 62% | 73% | 44% | 50% | 0% | 34% | 87.0 |
| 16 | `metric3d-v2-small-fp16+bright-contrast_night` | `metric3d-v2-small-fp16+bright-contrast_median` | 48% | 1.62 | - | 48% | 23% | 63% | 46% | 50% | 0% | 37% | 85.2 |
| 17 | `metric3d-v2-small-fp16+gamma06_night` | `metric3d-v2-small-fp16+gamma06_median` | 47% | 1.54 | - | 47% | 31% | 53% | 48% | 50% | 0% | 38% | 91.5 |
| 18 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_median` | 44% | 1.74 | - | 44% | 31% | 50% | 44% | 50% | 0% | 36% | 87.0 |

## vs centre

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-small-fp16+gamma06_night` | `metric3d-v2-small-fp16+gamma06_median` | 68% | 1.44 | - | 68% | 0% | 65% | 82% | 83% | 0% | 33% | 91.5 |
| 2 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_median` | 67% | 1.50 | - | 67% | 0% | 60% | 82% | 83% | 0% | 33% | 87.0 |
| 3 | `metric3d-v2-small-fp16+gamma06_night` | `metric3d-v2-small-fp16+gamma06_p25` | 66% | 1.59 | - | 66% | 0% | 55% | 82% | 83% | 0% | 29% | 91.5 |
| 4 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p25` | 66% | 1.58 | - | 66% | 0% | 50% | 84% | 83% | 0% | 29% | 87.0 |
| 5 | `metric3d-v2-small-fp16+bright-contrast_night` | `metric3d-v2-small-fp16+bright-contrast_median` | 65% | 1.58 | - | 65% | 0% | 50% | 82% | 83% | 0% | 31% | 85.2 |
| 6 | `metric3d-v2-small-fp16+clahe2_night` | `metric3d-v2-small-fp16+clahe2_median` | 63% | 1.63 | - | 63% | 0% | 45% | 86% | 33% | 0% | 30% | 107.0 |
| 7 | `metric3d-v2-small-fp16+bright-contrast_night` | `metric3d-v2-small-fp16+bright-contrast_p25` | 62% | 1.70 | - | 62% | 0% | 45% | 80% | 67% | 0% | 27% | 85.2 |
| 8 | `metric3d-v2-small-fp16+gamma06_night` | `metric3d-v2-small-fp16+gamma06_p10` | 61% | 1.72 | - | 61% | 0% | 40% | 80% | 67% | 0% | 25% | 91.5 |
| 9 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p10` | 61% | 1.72 | - | 61% | 0% | 30% | 82% | 83% | 0% | 26% | 87.0 |
| 10 | `metric3d-v2-small-fp16+bright-contrast_night` | `metric3d-v2-small-fp16+bright-contrast_p10` | 59% | 1.85 | - | 59% | 0% | 40% | 79% | 50% | 0% | 24% | 85.2 |
| 11 | `metric3d-v2-small-fp16+clahe2_night` | `metric3d-v2-small-fp16+clahe2_p25` | 57% | 1.74 | - | 57% | 0% | 55% | 73% | 33% | 0% | 25% | 107.0 |
| 12 | `metric3d-v2-small-fp16+gamma06-clahe2_night` | `metric3d-v2-small-fp16+gamma06-clahe2_median` | 55% | 1.68 | - | 55% | 9% | 40% | 75% | 17% | 0% | 29% | 111.6 |
| 13 | `metric3d-v2-small-fp16+clahe2_night` | `metric3d-v2-small-fp16+clahe2_p10` | 52% | 1.81 | - | 52% | 0% | 40% | 71% | 17% | 0% | 21% | 107.0 |
| 14 | `metric3d-v2-small-fp16+gamma06-clahe2_night` | `metric3d-v2-small-fp16+gamma06-clahe2_p25` | 49% | 1.92 | - | 49% | 0% | 35% | 70% | 0% | 0% | 22% | 111.6 |
| 15 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_median` | 46% | 1.68 | - | 46% | 0% | 35% | 64% | 0% | 0% | 23% | 106.2 |
| 16 | `metric3d-v2-small-fp16+gamma06-clahe2_night` | `metric3d-v2-small-fp16+gamma06-clahe2_p10` | 46% | 2.06 | - | 46% | 0% | 40% | 62% | 0% | 0% | 20% | 111.6 |
| 17 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p25` | 43% | 1.96 | - | 43% | 0% | 30% | 61% | 0% | 0% | 19% | 106.2 |
| 18 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p10` | 37% | 2.15 | - | 37% | 0% | 15% | 57% | 0% | 0% | 17% | 106.2 |
