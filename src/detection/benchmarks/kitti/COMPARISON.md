# KITTI road-user benchmark: run comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_kitti.py`. Do not edit by hand. Each run's full setup and results are in its own `results/<run>/RESULTS.md`.

Recall and false alarms at confidence threshold 0.05. Best value per row in bold.

## Runs

| Run | Weights | Vocabulary | Input size | Images | Git commit |
| --- | --- | --- | --- | --- | --- |
| `yolo26s-seg_coco` | `weights/yolo26s-seg.pt` | COCO 80 | 1280 | 1500 | `992ab92` |
| `yoloe-11s-seg_prompts-v2` | `weights/yoloe-11s-seg.pt` | 17 prompts | 1280 | 1500 | `992ab92` |
| `yoloe-11s-seg_prompts-v3` | `weights/yoloe-11s-seg.pt` | 19 prompts | 1280 | 1500 | `a0e55b3` |

## Summary

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v2 | yoloe-11s-seg_prompts-v3 |
| --- | --- | --- | --- |
| Recall, all objects | **87%** | 77% | 77% |
| False alarms per image | 6.44 | **0.93** | 0.94 |
| Latency median (ms) | 30.2 | 24.8 | **24.3** |
| Latency p95 (ms) | 55.9 | **33.5** | 33.7 |

## Average Precision (official metric)

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v2 | yoloe-11s-seg_prompts-v3 |
| --- | --- | --- | --- |
| Car, easy | 83.4% | **89.2%** | **89.2%** |
| Car, moderate | **73.6%** | 71.3% | 71.3% |
| Car, hard | **59.9%** | 55.3% | 55.3% |
| Pedestrian, easy | **74.3%** | 63.4% | 65.7% |
| Pedestrian, moderate | **63.9%** | 51.0% | 52.5% |
| Pedestrian, hard | **54.5%** | 43.5% | 44.6% |
| Cyclist, easy | **34.9%** | 34.3% | 20.4% |
| Cyclist, moderate | **25.7%** | 24.5% | 15.9% |
| Cyclist, hard | **24.4%** | 24.2% | 16.2% |

## Recall by class

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v2 | yoloe-11s-seg_prompts-v3 |
| --- | --- | --- | --- |
| car (n=5946) | **90%** | 80% | 80% |
| pedestrian (n=869) | **77%** | 61% | 61% |
| van (n=548) | **85%** | 77% | 77% |
| cyclist (n=324) | **68%** | 60% | 58% |
| truck (n=235) | **85%** | 82% | 82% |
| tram (n=127) | **51%** | **51%** | **51%** |

## Recall by distance, all classes

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v2 | yoloe-11s-seg_prompts-v3 |
| --- | --- | --- | --- |
| 0-10 m (n=982) | **90%** | 89% | 89% |
| 10-20 m (n=1933) | **89%** | 85% | 84% |
| 20-30 m (n=1795) | **85%** | 75% | 75% |
| 30-50 m (n=2315) | **85%** | 71% | 71% |
| 50+ m (n=1024) | **87%** | 65% | 65% |
