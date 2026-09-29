# Distance stage: summary of all benchmarks

Generated automatically by `summarize_distance.py` from each benchmark's `results.json`
(the exact source file of every number is listed in `summary.json`). Do not edit by hand.
Generated at git commit `a44a1a5`, 2026-09-29T15:35:52+00:00 UTC.

All accuracy figures are the share of objects whose estimated distance is within 10% of the
true distance to their nearest surface (laser ground truth; stereo for Lost and Found).

## Accuracy

| Candidate | KITTI road users, in path | Lost and Found obstacles, under 20 m | nuScenes in path | nuScenes day | nuScenes night | nuScenes cones and barriers |
| --- | --- | --- | --- | --- | --- | --- |
| Metric3D v2 Small FP16 | 88% | 76% | 76% | 85% | 55% | 33% |
| Metric3D v2 Large FP16 | 92% | 84% | 69% | 81% | 39% | 57% |
| UniDepth v2 Base | 90% | 31% | 83% | 87% | 71% | 64% |
| UniDepth v2 Large | 90% | 66% | 85% | 86% | 81% | 62% |
| UniDepth v2 Base, camera not given | - | - | - | - | - | - |
| UniDepth v2 Large, camera not given | - | - | - | - | - | - |
| min(Metric3D v2 Large, UniDepth v2 Large) | 90% | 89% | 90% | 94% | 81% | 54% |
| Known size (geometric) | 77% | - | 52% | 51% | 55% | - |
| Ground plane (geometric) | 46% | 41% | 24% | 13% | 47% | 47% |

## Stability, speed, robustness, licence

Stability: KITTI tracking, in path. Speed: median per frame on an RTX 4060 in PyTorch at
nuScenes 1600x900 (sum of both models for a combination). Focal: KITTI in path, within 10% when
the focal length given is 10% too low / too high.

| Candidate | Jitter, median | Speed error p90, 0.5 s | Speed error p90, 2 s | ms per frame | Focal -10% | Focal +10% | Estimated focal (px), nuScenes | Licence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Metric3D v2 Small FP16 | 1.4% | 4.18 m/s | 1.42 m/s | 82.1 | 39% | 59% | - | BSD-2-Clause |
| Metric3D v2 Large FP16 | 1.1% | 3.05 m/s | 1.02 m/s | 356.5 | 71% | 29% | - | BSD-2-Clause |
| UniDepth v2 Base | 1.1% | 3.15 m/s | 1.12 m/s | 111.2 | - | - | - | CC BY-NC 4.0 (non-commercial) |
| UniDepth v2 Large | 1.0% | 3.25 m/s | 1.16 m/s | 214.1 | - | - | - | CC BY-NC 4.0 (non-commercial) |
| UniDepth v2 Base, camera not given | - | - | - | 111.2 | - | - | - | CC BY-NC 4.0 (non-commercial) |
| UniDepth v2 Large, camera not given | - | - | - | 214.1 | - | - | - | CC BY-NC 4.0 (non-commercial) |
| min(Metric3D v2 Large, UniDepth v2 Large) | - | - | - | 570.6 | - | - | - | CC BY-NC 4.0 (UniDepth part) |
| Known size (geometric) | 1.1% | 3.95 m/s | 0.97 m/s | 0.0 | 46% | 46% | - | own code |
| Ground plane (geometric) | 1.6% | 15.37 m/s | 7.31 m/s | 0.0 | - | - | - | own code |

## Where each benchmark is

- KITTI accuracy: `src/distance/benchmarks/kitti/COMPARISON.md`
- Lost and Found obstacles: `src/distance/benchmarks/lost_and_found/COMPARISON.md`
- nuScenes: `src/distance/benchmarks/nuscenes/COMPARISON.md` and `COMPARISON_OBSTACLES.md`
- Stability: `src/distance/benchmarks/kitti_tracking/COMPARISON.md`
- Speed: `src/distance/benchmarks/speed/results/`
- Focal length sensitivity: `src/distance/benchmarks/focal_sensitivity/results/`
