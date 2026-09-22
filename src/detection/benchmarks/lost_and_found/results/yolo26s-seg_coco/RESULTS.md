# Lost and Found obstacle benchmark: `yolo26s-seg_coco`

Generated automatically from `results.json` by `benchmark_lost_and_found.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Model weights | `weights/yolo26s-seg.pt` |
| Vocabulary | fixed 80 COCO (Common Objects in Context) classes |
| Input size | 1280 |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 |
| Obstacles evaluated | 1724 |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground-truth distance | median stereo depth inside the obstacle polygon |
| Match rule | IoU >= 0.3, any predicted class counts |
| Hardware | NVIDIA GeForce RTX 4060, FP16 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `0573e63` (with uncommitted changes) |
| Created (UTC) | 2026-09-22T20:05:56+00:00 |

## Metrics

- **Recall**: fraction of real obstacles detected. A miss is what causes a collision.
- **False alarms per frame**: detections on free road where no obstacle exists.
- **IoU** (Intersection over Union): box overlap area divided by combined area.
- **Latency**: model inference time per frame; p95 is the slowest 5%.

## Recall overall

|  | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| All | 1724 | 30% | 23% | 17% |

## Recall by distance

| Distance | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| 0-10 m | 88 | 49% | 43% | 35% |
| 10-20 m | 265 | 57% | 47% | 37% |
| 20-30 m | 247 | 36% | 30% | 23% |
| 30-50 m | 584 | 22% | 17% | 13% |
| 50+ m | 540 | 20% | 12% | 6% |

## Recall by obstacle group

| Group | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| random hazards | 563 | 18% | 10% | 5% |
| standard objects | 535 | 7% | 4% | 1% |
| emotional hazards | 423 | 49% | 42% | 33% |
| humans | 203 | 85% | 72% | 61% |

## Recall by obstacle type

| Type | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| crate (gray, 2x stacked) | 133 | 17% | 7% | 1% |
| tire | 106 | 6% | 2% | 1% |
| cardboard box | 105 | 1% | 1% | 0% |
| dog (white) | 94 | 55% | 50% | 40% |
| crate (black, 2x stacked) | 93 | 2% | 1% | 0% |
| bobby car (red) | 91 | 46% | 40% | 30% |
| bobby car (gray) | 89 | 57% | 43% | 30% |
| crate (black, upright) | 89 | 9% | 7% | 1% |
| crate (gray) | 88 | 7% | 3% | 1% |
| dog (black) | 86 | 49% | 45% | 38% |
| kid (on a bobby car) | 79 | 76% | 63% | 48% |
| crate (black) | 74 | 0% | 0% | 0% |
| kid (walking) | 65 | 91% | 88% | 80% |
| crate (gray, upright) | 58 | 0% | 0% | 0% |
| exhaust pipe | 55 | 20% | 11% | 4% |
| bumper | 53 | 87% | 68% | 42% |
| styrofoam | 50 | 2% | 0% | 0% |
| kid (on a small bobby car) | 50 | 90% | 62% | 50% |
| pylon (white) | 46 | 33% | 13% | 4% |
| crate (green) | 35 | 23% | 9% | 0% |
| plastic bag (bloated) | 28 | 18% | 7% | 0% |
| bobby car (yellow) | 27 | 37% | 37% | 33% |
| euro pallet | 20 | 5% | 0% | 0% |
| ball | 20 | 25% | 25% | 20% |
| pylon | 20 | 0% | 0% | 0% |
| crate (blue) | 18 | 0% | 0% | 0% |
| kid dummy | 16 | 25% | 19% | 19% |
| crate (blue, small) | 15 | 20% | 13% | 13% |
| headlight | 12 | 17% | 8% | 0% |
| kid (crawling) | 9 | 100% | 100% | 100% |

## False alarms on free road

| Threshold | Total | Per frame |
| --- | --- | --- |
| 0.05 | 198 | 0.16 |
| 0.1 | 133 | 0.11 |
| 0.25 | 89 | 0.07 |

## Latency

| Median (ms) | p95 (ms) |
| --- | --- |
| 28.3 | 37.4 |
