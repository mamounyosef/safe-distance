# Lost and Found obstacle benchmark: run comparison

Generated automatically from every `results/<run>/results.json` by `benchmark_lost_and_found.py`. Do not edit by hand. Each run's full setup and results are in its own `results/<run>/RESULTS.md`.

Recall and false alarms at confidence threshold 0.05. Best value per row in bold.

## Runs

| Run | Weights | Vocabulary | Input size | Git commit |
| --- | --- | --- | --- | --- |
| `yolo26s-seg_coco` | `weights/yolo26s-seg.pt` | COCO 80 | 1280 | `0573e63` |
| `yoloe-11s-seg_prompts-v1` | `weights/yoloe-11s-seg.pt` | 14 prompts | 1280 | `0573e63` |
| `yoloe-11s-seg_prompts-v2` | `weights/yoloe-11s-seg.pt` | 17 prompts | 1280 | `0573e63` |

## Summary

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v1 | yoloe-11s-seg_prompts-v2 |
| --- | --- | --- | --- |
| Recall, all obstacles | 30% | 40% | **42%** |
| False alarms per frame | 0.16 | **0.11** | 0.12 |
| Latency median (ms) | **28.3** | 30.2 | 31.2 |
| Latency p95 (ms) | **37.4** | 40.1 | 42.0 |

## Recall by distance

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v1 | yoloe-11s-seg_prompts-v2 |
| --- | --- | --- | --- |
| 0-10 m (n=88) | 49% | 94% | **99%** |
| 10-20 m (n=265) | 57% | 82% | **84%** |
| 20-30 m (n=247) | 36% | 51% | **55%** |
| 30-50 m (n=584) | 22% | 26% | **27%** |
| 50+ m (n=540) | 20% | **22%** | **22%** |

## Recall by obstacle group

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v1 | yoloe-11s-seg_prompts-v2 |
| --- | --- | --- | --- |
| random hazards (n=563) | 18% | 35% | **36%** |
| standard objects (n=535) | 7% | **27%** | **27%** |
| emotional hazards (n=423) | **49%** | 43% | 48% |
| humans (n=203) | 85% | **86%** | **86%** |

## Recall by obstacle type

|  | yolo26s-seg_coco | yoloe-11s-seg_prompts-v1 | yoloe-11s-seg_prompts-v2 |
| --- | --- | --- | --- |
| crate (gray, 2x stacked) (n=133) | 17% | **34%** | **34%** |
| tire (n=106) | 6% | **34%** | **34%** |
| cardboard box (n=105) | 1% | **38%** | **38%** |
| dog (white) (n=94) | **55%** | 36% | 43% |
| crate (black, 2x stacked) (n=93) | 2% | **31%** | **31%** |
| bobby car (red) (n=91) | 46% | 52% | **54%** |
| bobby car (gray) (n=89) | 57% | **70%** | **70%** |
| crate (black, upright) (n=89) | 9% | **19%** | **19%** |
| crate (gray) (n=88) | 7% | **20%** | **20%** |
| dog (black) (n=86) | **49%** | 30% | 36% |
| kid (on a bobby car) (n=79) | **76%** | 73% | 73% |
| crate (black) (n=74) | 0% | **26%** | **26%** |
| kid (walking) (n=65) | 91% | **97%** | **97%** |
| crate (gray, upright) (n=58) | 0% | **24%** | **24%** |
| exhaust pipe (n=55) | **20%** | 4% | 5% |
| bumper (n=53) | **87%** | 83% | 83% |
| styrofoam (n=50) | 2% | **12%** | **12%** |
| kid (on a small bobby car) (n=50) | **90%** | **90%** | **90%** |
| pylon (white) (n=46) | 33% | 50% | **57%** |
| crate (green) (n=35) | 23% | **43%** | **43%** |
| plastic bag (bloated) (n=28) | **18%** | 11% | 11% |
| bobby car (yellow) (n=27) | 37% | 37% | **41%** |
| euro pallet (n=20) | 5% | **15%** | **15%** |
| ball (n=20) | 25% | 0% | **35%** |
| pylon (n=20) | 0% | **65%** | **65%** |
| crate (blue) (n=18) | 0% | **39%** | **39%** |
| kid dummy (n=16) | **25%** | 19% | 19% |
| crate (blue, small) (n=15) | 20% | **27%** | **27%** |
| headlight (n=12) | **17%** | 0% | **17%** |
| kid (crawling) (n=9) | **100%** | **100%** | **100%** |
