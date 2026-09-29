# Depth model speed: `rtx4060_pytorch_fp16`

Generated automatically from `results.json` by `benchmark_depth_speed.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| GPU | NVIDIA GeForce RTX 4060 |
| Precision | per model, see each model's precision (PyTorch, no TensorRT) |
| Detector precision | fp16 |
| Batch size | 1 |
| Timing covers | camera image in, full-resolution depth map in metres out |
| Passes | 5 warm-up (untimed), then 40 timed, distinct real frames |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `8cff289` (with uncommitted changes) |
| Created (UTC) | 2026-09-29T13:06:51+00:00 |

## Depth models (median / p95 ms per frame)

Verdict uses the nuScenes 1600x900 median against a 30 fps budget of 33.3 ms per frame for the
whole pipeline: `fits` = under half the budget, `tight` = under the budget, `too slow` = over.

| Model | Precision | KITTI 1242x375 | nuScenes 1600x900 | Lost and Found 2048x1024 | Peak GPU memory (GB) | Verdict | GPU at start |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `yolo26s-depth` | fp16 | 10.8 / 15.8 | 13.0 / 19.9 | 13.7 / 17.0 | 0.1 | fits | 59% busy, 1157 MB used |
| `da2-metric-small` | fp16 | 48.4 / 51.2 | 32.0 / 34.8 | 37.9 / 39.7 | 0.27 | tight | 100% busy, 1160 MB used |
| `da2-metric-base` | fp16 | 98.3 / 102.4 | 56.2 / 59.0 | 68.1 / 72.0 | 0.71 | too slow | 63% busy, 1160 MB used |
| `unidepth-v2-small` | fp16 (library autocast) | 57.6 / 59.6 | 61.4 / 63.1 | 64.1 / 65.5 | 0.82 | too slow | 99% busy, 1109 MB used |
| `da3-metric-large` | bf16 or fp16 (library autocast) | 51.6 / 53.9 | 79.1 / 81.1 | 83.6 / 86.8 | 2.15 | too slow | 98% busy, 1141 MB used |
| `metric3d-v2-small-fp16` | fp16 (autocast) | 78.8 / 81.6 | 82.1 / 85.9 | 84.0 / 86.0 | 0.65 | too slow | 100% busy, 1107 MB used |
| `unidepth-v2-base` | fp16 (library autocast) | 108.0 / 109.4 | 111.2 / 113.0 | 115.3 / 116.7 | 1.59 | too slow | 34% busy, 1141 MB used |
| `da2-metric-large` | fp16 | 264.5 / 269.2 | 135.6 / 140.0 | 156.5 / 159.8 | 1.52 | too slow | 73% busy, 1165 MB used |
| `metric3d-v2-small` | fp32 | 150.5 / 153.3 | 153.6 / 155.8 | 157.0 / 158.9 | 0.67 | too slow | 40% busy, 1113 MB used |
| `unidepth-v2-large` | fp16 (library autocast) | 209.5 / 211.8 | 214.1 / 216.4 | 218.1 / 220.4 | 3.41 | too slow | 93% busy, 1141 MB used |
| `metric3d-v2-large-fp16` | fp16 (autocast) | 353.2 / 358.0 | 356.5 / 359.8 | 358.7 / 362.4 | 3.17 | too slow | 82% busy, 1109 MB used |
| `depth-pro` | fp16 | 852.5 / 858.3 | 858.1 / 863.4 | 862.7 / 867.8 | 3.97 | too slow | 60% busy, 1149 MB used |
| `metric3d-v2-large` | fp32 | 886.9 / 893.1 | 890.7 / 900.9 | 891.9 / 897.1 | 2.54 | too slow | 97% busy, 1116 MB used |

## Detector, for the full per-frame budget

| Detector | KITTI 1242x375 | nuScenes 1600x900 | Lost and Found 2048x1024 |
| --- | --- | --- | --- |
| `weights/yolo26s-seg.pt` at 1280 | 19.2 / 28.8 | 29.3 / 40.0 | 19.9 / 24.1 |

## Known limitations

- PyTorch on an RTX 4060, not TensorRT on a Jetson Orin Nano: ranks the models and shows the
  distance to a real-time budget; edge timings need their own measurement.
- Includes pre- and post-processing done on the CPU, which differs per model's library.
