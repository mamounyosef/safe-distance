# Lost and Found obstacle benchmark: `yoloe-11s-seg_prompts-v3`

Generated automatically from `results.json` by `benchmark_lost_and_found.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Model weights | `weights/yoloe-11s-seg.pt` |
| Vocabulary | open vocabulary, 19 prompts: `car`, `van`, `truck`, `bus`, `motorcycle`, `bicycle`, `person`, `pedestrian`, `cyclist`, `traffic cone`, `construction barrier`, `traffic barricade`, `animal`, `dog`, `cat`, `ball`, `obstacle`, `box`, `bucket` |
| Input size | 1280 |
| Dataset | [Lost and Found](https://huggingface.co/datasets/kumuji/lost_and_found), test split, 5 scenes |
| Frames | 1203 |
| Obstacles evaluated | 1724 |
| Excluded | random non-hazards (30, 32, 33, 35-38), per the dataset definition |
| Ground-truth distance | median stereo depth inside the obstacle polygon |
| Match rule | IoU >= 0.3, any predicted class counts |
| Hardware | NVIDIA GeForce RTX 4060, FP16 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `a0e55b3` (with uncommitted changes) |
| Created (UTC) | 2026-09-23T12:12:52+00:00 |

## Metrics

- **Recall**: fraction of real obstacles detected. A miss is what causes a collision.
- **False alarms per frame**: detections on free road where no obstacle exists.
- **IoU** (Intersection over Union): box overlap area divided by combined area.
- **Latency**: model inference time per frame; p95 is the slowest 5%.

## Recall overall

|  | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| All | 1724 | 42% | 32% | 21% |

## Recall by distance

| Distance | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| 0-10 m | 88 | 99% | 94% | 67% |
| 10-20 m | 265 | 84% | 69% | 46% |
| 20-30 m | 247 | 55% | 39% | 25% |
| 30-50 m | 584 | 27% | 19% | 13% |
| 50+ m | 540 | 22% | 16% | 9% |

## Recall by obstacle group

| Group | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| random hazards | 563 | 36% | 26% | 14% |
| standard objects | 535 | 27% | 14% | 5% |
| emotional hazards | 423 | 48% | 40% | 30% |
| humans | 203 | 86% | 81% | 66% |

## Recall by obstacle type

| Type | Obstacles | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| crate (gray, 2x stacked) | 133 | 34% | 21% | 8% |
| tire | 106 | 34% | 14% | 5% |
| cardboard box | 105 | 38% | 29% | 13% |
| dog (white) | 94 | 43% | 41% | 36% |
| crate (black, 2x stacked) | 93 | 31% | 14% | 5% |
| bobby car (red) | 91 | 54% | 47% | 31% |
| bobby car (gray) | 89 | 70% | 51% | 37% |
| crate (black, upright) | 89 | 19% | 10% | 4% |
| crate (gray) | 88 | 20% | 12% | 3% |
| dog (black) | 86 | 36% | 33% | 29% |
| kid (on a bobby car) | 79 | 73% | 66% | 47% |
| crate (black) | 74 | 26% | 15% | 4% |
| kid (walking) | 65 | 97% | 89% | 80% |
| crate (gray, upright) | 58 | 24% | 9% | 0% |
| exhaust pipe | 55 | 5% | 0% | 0% |
| bumper | 53 | 83% | 79% | 58% |
| styrofoam | 50 | 12% | 8% | 0% |
| kid (on a small bobby car) | 50 | 90% | 90% | 74% |
| pylon (white) | 46 | 57% | 46% | 24% |
| crate (green) | 35 | 43% | 34% | 20% |
| plastic bag (bloated) | 28 | 11% | 7% | 7% |
| bobby car (yellow) | 27 | 41% | 37% | 26% |
| euro pallet | 20 | 15% | 15% | 5% |
| ball | 20 | 35% | 20% | 5% |
| pylon | 20 | 65% | 40% | 20% |
| crate (blue) | 18 | 39% | 22% | 11% |
| kid dummy | 16 | 19% | 12% | 6% |
| crate (blue, small) | 15 | 27% | 20% | 7% |
| headlight | 12 | 17% | 8% | 0% |
| kid (crawling) | 9 | 100% | 100% | 100% |

## False alarms on free road

| Threshold | Total | Per frame |
| --- | --- | --- |
| 0.05 | 150 | 0.12 |
| 0.1 | 86 | 0.07 |
| 0.25 | 41 | 0.03 |

## Latency

| Median (ms) | p95 (ms) |
| --- | --- |
| 30.6 | 42.0 |
