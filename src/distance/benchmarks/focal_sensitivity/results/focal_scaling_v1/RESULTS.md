# Focal length sensitivity: `focal_scaling_v1`

Generated automatically from `results.json` by `benchmark_focal_sensitivity.py`. Do not edit by hand.

Share of objects within 10% of the true distance when the focal length given to each method
is off by the stated amount. Computed from the saved estimates of the accuracy benchmarks: for
these methods the distance is exactly proportional to the focal length, so no re-run is needed.

Git commit `70d771f` (with uncommitted changes), created 2026-09-29T14:32:00+00:00 UTC.

## KITTI, in path

| Estimator | Objects | Run | Focal -20% | Focal -10% | Focal -5% | Focal exact | Focal +5% | Focal +10% | Focal +20% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `metric3d-v2-small-fp16_p10` | 1020 | `metric3d-v2-small-fp16_full` | 2% | 39% | 72% | 88% | 83% | 59% | 12% |
| `metric3d-v2-large-fp16_p25` | 1020 | `metric3d-v2-large-fp16_full` | 3% | 71% | 94% | 92% | 72% | 29% | 2% |
| `da3-metric-large_p10` | 206 | `da3-metric-large_n300` | 0% | 16% | 33% | 56% | 72% | 70% | 49% |
| `depth-pro_median` | 206 | `depth-pro_n300` | 2% | 26% | 47% | 67% | 67% | 61% | 28% |
| `known_size` | 1018 | `geometric_full` | 7% | 46% | 72% | 77% | 61% | 46% | 10% |

## Lost and Found, under 20 m

| Estimator | Objects | Run | Focal -20% | Focal -10% | Focal -5% | Focal exact | Focal +5% | Focal +10% | Focal +20% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `metric3d-v2-small-fp16_p10` | 353 | `metric3d-v2-small-fp16_full` | 14% | 67% | 77% | 76% | 58% | 29% | 5% |
| `metric3d-v2-large-fp16_p25` | 353 | `metric3d-v2-large-fp16_full` | 10% | 63% | 91% | 84% | 67% | 35% | 1% |
| `da3-metric-large_p10` | 86 | `da3-metric-large_n300` | 35% | 84% | 79% | 58% | 20% | 6% | 0% |
| `depth-pro_median` | 86 | `depth-pro_n300` | 6% | 38% | 59% | 69% | 59% | 48% | 22% |

## nuScenes, in path

| Estimator | Objects | Run | Focal -20% | Focal -10% | Focal -5% | Focal exact | Focal +5% | Focal +10% | Focal +20% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `metric3d-v2-small-fp16_p10` | 321 | `metric3d-v2-small-fp16` | 9% | 56% | 76% | 76% | 64% | 40% | 9% |
| `metric3d-v2-large-fp16_p25` | 321 | `metric3d-v2-large-fp16` | 18% | 72% | 81% | 69% | 49% | 24% | 2% |
| `da3-metric-large_p10` | 321 | `da3-metric-large` | 15% | 50% | 61% | 61% | 53% | 42% | 18% |
| `depth-pro_median` | 321 | `depth-pro` | 3% | 27% | 39% | 42% | 45% | 44% | 38% |
| `known_size` | 321 | `geometric` | 11% | 45% | 50% | 52% | 49% | 31% | 25% |

## Known limitations

- UniDepth is not included: it takes the camera as a network input, so its sensitivity is not
  a simple scaling and needs its own runs (including its mode that estimates the camera itself).
- Ground plane is not included: it depends on the focal length non-linearly.
