# KITTI distance benchmark: comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_kitti_distance.py`. Do not edit by hand. Best value per row in bold.

## vs nearest surface

|  | yolo26s-seg_geometric-v1 / ground_plane | yolo26s-seg_geometric-v1 / known_size |
| --- | --- | --- |
| Coverage | 99% | **100%** |
| Median error (m), all | 2.61 | **1.68** |
| Within 10%, all | 39% | **63%** |
| |Bias|, all | +13.4% | **+12.7%** |
| Median error (m), 0-10 m | 1.42 | **1.14** |
| Median error (m), 10-20 m | 1.37 | **1.09** |
| Median error (m), 20-30 m | 2.64 | **1.64** |
| Median error (m), 30-50 m | 5.40 | **2.37** |
| Median error (m), 50+ m | 10.20 | **4.42** |
| Within 10%, 0-10 m | 24% | **36%** |
| Within 10%, 10-20 m | 52% | **65%** |
| Within 10%, 20-30 m | 46% | **71%** |
| Within 10%, 30-50 m | 37% | **72%** |
| Within 10%, 50+ m | 28% | **62%** |

## vs centre

|  | yolo26s-seg_geometric-v1 / ground_plane | yolo26s-seg_geometric-v1 / known_size |
| --- | --- | --- |
| Coverage | 99% | **100%** |
| Median error (m), all | 2.75 | **1.79** |
| Within 10%, all | 37% | **58%** |
| |Bias|, all | **+0.6%** | **+0.6%** |
| Median error (m), 0-10 m | **1.00** | 1.16 |
| Median error (m), 10-20 m | 1.58 | **1.31** |
| Median error (m), 20-30 m | 3.00 | **1.86** |
| Median error (m), 30-50 m | 6.06 | **2.41** |
| Median error (m), 50+ m | 11.23 | **4.31** |
| Within 10%, 0-10 m | **37%** | 34% |
| Within 10%, 10-20 m | 44% | **54%** |
| Within 10%, 20-30 m | 42% | **61%** |
| Within 10%, 30-50 m | 32% | **67%** |
| Within 10%, 50+ m | 25% | **62%** |
