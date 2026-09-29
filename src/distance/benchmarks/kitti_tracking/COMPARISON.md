# Distance stability benchmark (KITTI tracking): comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_distance_stability.py`. Do not edit by hand. Each run's full results are in `results/<run>/RESULTS.md`.

In-path objects. Ranked by **speed error over 5 frames (0.5 s)**, lowest first: the error in
closing speed that the Time To Collision stage would inherit.

| Rank | Run | Estimator | Jitter median | Jitter p90 | Speed error 1 frame, median (m/s) | 1 frame, p90 | Speed error 5 frames, median (m/s) | 5 frames, p90 | Within 10% | Pairs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `unidepth-v2-large_f150` | `unidepth-v2-large_p10` | 1.0% | 3.0% | 1.91 | 10.67 | 0.60 | 3.25 | 91% | 2564 |
| 2 | `metric3d-v2-large-fp16_f150` | `metric3d-v2-large-fp16_p25` | 1.1% | 3.1% | 2.00 | 10.61 | 0.60 | 3.05 | 94% | 2564 |
| 3 | `geometric_f150` | `known_size` | 1.1% | 4.3% | 2.20 | 14.10 | 0.61 | 3.95 | 81% | 2515 |
| 4 | `geometric_f150` | `combined` | 1.1% | 4.3% | 2.20 | 14.10 | 0.61 | 3.95 | 81% | 2515 |
| 5 | `unidepth-v2-large_f150` | `unidepth-v2-large_p25` | 1.0% | 3.0% | 1.88 | 10.44 | 0.61 | 3.26 | 94% | 2564 |
| 6 | `metric3d-v2-large-fp16_f150` | `metric3d-v2-large-fp16_median` | 1.1% | 3.0% | 2.03 | 10.26 | 0.61 | 3.27 | 91% | 2564 |
| 7 | `metric3d-v2-large-fp16_f150` | `metric3d-v2-large-fp16_p10` | 1.1% | 3.5% | 2.14 | 12.57 | 0.63 | 3.64 | 93% | 2564 |
| 8 | `unidepth-v2-large_f150` | `unidepth-v2-large_median` | 1.1% | 3.2% | 2.02 | 11.49 | 0.63 | 3.47 | 95% | 2564 |
| 9 | `unidepth-v2-base_f150` | `unidepth-v2-base_p10` | 1.1% | 3.0% | 2.08 | 10.59 | 0.65 | 3.15 | 90% | 2564 |
| 10 | `unidepth-v2-base_f150` | `unidepth-v2-base_p25` | 1.1% | 3.1% | 2.10 | 10.14 | 0.68 | 3.23 | 92% | 2564 |
| 11 | `unidepth-v2-base_f150` | `unidepth-v2-base_median` | 1.1% | 3.3% | 2.21 | 11.24 | 0.72 | 3.56 | 93% | 2564 |
| 12 | `metric3d-v2-small-fp16_f150` | `metric3d-v2-small-fp16_p10` | 1.4% | 4.5% | 2.73 | 14.49 | 0.80 | 4.18 | 85% | 2564 |
| 13 | `metric3d-v2-small-fp16_f150` | `metric3d-v2-small-fp16_p25` | 1.4% | 4.3% | 2.77 | 14.01 | 0.82 | 4.04 | 88% | 2564 |
| 14 | `metric3d-v2-small-fp16_f150` | `metric3d-v2-small-fp16_median` | 1.4% | 4.5% | 2.80 | 14.28 | 0.85 | 4.15 | 89% | 2564 |
| 15 | `geometric_f150` | `ground_plane` | 1.6% | 8.5% | 3.02 | 33.17 | 2.18 | 15.37 | 33% | 2479 |
