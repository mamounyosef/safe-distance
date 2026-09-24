# KITTI tracking benchmark: run comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_kitti_tracking.py`. Do not edit by hand. Each run's full setup and per-sequence results are in `results/<run>/RESULTS.md`.

Best value per row in bold.

## Runs

| Run | Detector | Tracker | Frames | Git commit |
| --- | --- | --- | --- | --- |
| `yolo26s-seg_botsort` | `weights/yolo26s-seg.pt` | botsort | 8008 | `4a31b54` |
| `yolo26s-seg_bytetrack` | `weights/yolo26s-seg.pt` | bytetrack | 8008 | `4a31b54` |

## Results

|  | yolo26s-seg_botsort | yolo26s-seg_bytetrack |
| --- | --- | --- |
| Car: IDF1 | **79.5%** | 77.0% |
| Car: MOTA | **72.0%** | 64.8% |
| Car: ID switches | **228** | 301 |
| Car: recall | **82.0%** | 77.1% |
| Car: precision | **90.1%** | 87.5% |
| Pedestrian: IDF1 | **66.3%** | 63.9% |
| Pedestrian: MOTA | **50.8%** | 49.9% |
| Pedestrian: ID switches | **188** | 250 |
| Pedestrian: recall | **71.5%** | 68.0% |
| Pedestrian: precision | 78.9% | **81.0%** |
| Latency median (ms) | 29.7 | **23.3** |
| Latency p95 (ms) | 39.0 | **32.9** |
