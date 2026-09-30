# nuScenes distance benchmark: night enhancement confirmed on 82 never-seen night scenes

Generated automatically from every `results/<run>/results.json` by `benchmark_nuscenes_distance.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

Ranked by **in path, within 10%** of the true distance. `_median`, `_p10`, `_p25` mark how a
depth model's per-pixel depth inside the object's mask is summarised.

## vs nearest surface

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p10` | 68% | 0.80 | - | 68% | 68% | 79% | 71% | 53% | 34% | 51% | 112.3 |
| 2 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p25` | 67% | 0.83 | - | 67% | 64% | 75% | 74% | 62% | 39% | 54% | 112.3 |
| 3 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_median` | 62% | 0.96 | - | 62% | 58% | 65% | 71% | 66% | 43% | 54% | 112.3 |
| 4 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p10` | 51% | 1.19 | - | 51% | 47% | 46% | 66% | 66% | 22% | 49% | 88.4 |
| 5 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p25` | 47% | 1.25 | - | 47% | 42% | 40% | 64% | 70% | 29% | 50% | 88.4 |
| 6 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_median` | 38% | 1.46 | - | 38% | 28% | 28% | 56% | 70% | 30% | 46% | 88.4 |

## vs centre

| Rank | Run | Estimator | In path within 10% | In path median error (m) | In path, day | In path, night | In path, 0-10 m | In path, 10-20 m | In path, 20-30 m | In path, 30-50 m | In path, 50+ m | All objects within 10% | Depth model ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_median` | 57% | 1.35 | - | 57% | 15% | 79% | 78% | 69% | 28% | 41% | 88.4 |
| 2 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p25` | 51% | 1.44 | - | 51% | 8% | 74% | 76% | 63% | 22% | 35% | 88.4 |
| 3 | `metric3d-v2-small-fp16_night` | `metric3d-v2-small-fp16_p10` | 48% | 1.51 | - | 48% | 6% | 72% | 74% | 54% | 17% | 31% | 88.4 |
| 4 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_median` | 36% | 1.80 | - | 36% | 5% | 50% | 53% | 43% | 35% | 30% | 112.3 |
| 5 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p25` | 32% | 1.93 | - | 32% | 4% | 42% | 50% | 40% | 30% | 24% | 112.3 |
| 6 | `metric3d-v2-small-fp16+clahe4_night` | `metric3d-v2-small-fp16+clahe4_p10` | 28% | 2.02 | - | 28% | 3% | 38% | 45% | 33% | 27% | 20% | 112.3 |
