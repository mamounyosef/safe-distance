# KITTI road-user benchmark: `yoloe-11s-seg_prompts-v2`

Generated automatically from `results.json` by `benchmark_kitti.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Model weights | `weights/yoloe-11s-seg.pt` |
| Vocabulary | open vocabulary, 17 prompts: `car`, `van`, `truck`, `bus`, `motorcycle`, `bicycle`, `person`, `traffic cone`, `construction barrier`, `traffic barricade`, `animal`, `dog`, `cat`, `ball`, `obstacle`, `box`, `bucket` |
| Input size | 1280 |
| Dataset | [KITTI Object Detection](https://www.cvlibs.net/datasets/kitti/eval_object.php), training (the only split with public labels; models were not trained on KITTI) |
| Images | 1500, data/kitti/subset.txt (random, fixed seed, see scripts/download_kitti.py) |
| Objects evaluated (recall) | 8049 |
| Ground-truth distance | laser-measured 3D position, ground distance sqrt(x^2 + z^2) |
| Recall match rule | IoU >= 0.5, any predicted class counts |
| AP method | KITTI-style AP|R40, greedy matching |
| Class conversion | car and van -> Car; person -> Pedestrian; bicycle merged with its rider (person box >= 30% inside the bicycle box) -> Cyclist; rider-less bicycles dropped (parked bikes are unlabelled in KITTI) |
| Hardware | NVIDIA GeForce RTX 4060, FP16 |
| Software | Python 3.12.0, torch 2.6.0+cu124, ultralytics 8.4.155 |
| Git commit | `992ab92` (with uncommitted changes) |
| Created (UTC) | 2026-09-23T07:10:41+00:00 |

## Metrics

- **Recall**: fraction of real objects detected, any predicted class. A miss is what causes a collision.
- **AP** (Average Precision): KITTI's official class-aware score, precision averaged over 40 recall levels.
  IoU 0.7 for Car, 0.5 for Pedestrian and Cyclist.
- **Difficulty**: Easy = fully visible, box at least 40 px tall; Moderate = partly hidden, at least 25 px;
  Hard = largely hidden, at least 25 px. Moderate is the standard headline number.
- **False alarms**: vehicle or person detections that match nothing labelled.
- **Latency**: model inference time per image; p95 is the slowest 5%.

## Average Precision (official metric)

| Class | Easy | Moderate | Hard | Objects (Easy) | Objects (Moderate) | Objects (Hard) |
| --- | --- | --- | --- | --- | --- | --- |
| Car | 89.2% | 71.3% | 55.3% | 1186 | 3234 | 4497 |
| Pedestrian | 63.4% | 51.0% | 43.5% | 416 | 648 | 785 |
| Cyclist | 34.3% | 24.5% | 24.2% | 125 | 219 | 238 |

## Recall by class

| Class | Objects | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| car | 5946 | 80% | 70% | 48% |
| pedestrian | 869 | 61% | 47% | 18% |
| van | 548 | 77% | 69% | 49% |
| cyclist | 324 | 60% | 50% | 21% |
| truck | 235 | 82% | 75% | 59% |
| tram | 127 | 51% | 47% | 32% |

## Recall by distance, all classes

| Distance | Objects | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| 0-10 m | 982 | 89% | 86% | 75% |
| 10-20 m | 1933 | 85% | 80% | 60% |
| 20-30 m | 1795 | 75% | 65% | 40% |
| 30-50 m | 2315 | 71% | 58% | 32% |
| 50+ m | 1024 | 65% | 47% | 20% |

## Recall by class and distance (@0.05)

| Distance | car | pedestrian | van | cyclist | truck | tram |
| --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 91% (n=657) | 82% (n=246) | 94% (n=34) | 88% (n=24) | 81% (n=16) | 80% (n=5) |
| 10-20 m | 89% (n=1382) | 65% (n=335) | 92% (n=103) | 82% (n=89) | 77% (n=13) | 91% (n=11) |
| 20-30 m | 80% (n=1367) | 50% (n=153) | 84% (n=116) | 55% (n=88) | 77% (n=35) | 25% (n=36) |
| 30-50 m | 75% (n=1841) | 25% (n=110) | 73% (n=150) | 52% (n=104) | 84% (n=73) | 32% (n=37) |
| 50+ m | 67% (n=699) | 12% (n=25) | 59% (n=145) | 0% (n=19) | 83% (n=98) | 79% (n=38) |

## False alarms

| Threshold | Total | Per image |
| --- | --- | --- |
| 0.05 | 1394 | 0.93 |
| 0.1 | 662 | 0.44 |
| 0.25 | 112 | 0.07 |

## Latency

| Median (ms) | p95 (ms) |
| --- | --- |
| 24.8 | 33.5 |

## Known limitations

- **False alarms are overstated.** KITTI does not label every vehicle: far or partly visible
  ones are often left out, and parked bicycles are never labelled. A correct detection of such
  an object counts as a false alarm. A model that sees more (higher recall far away) is
  penalised more. Compare false alarms between runs, not as an absolute rate.
- **Cyclist AP is approximate.** Our detector outputs separate person and bicycle boxes; they
  are merged into one box to match KITTI's rider-plus-bicycle label, which only roughly
  matches how KITTI draws it.
- **AP is KITTI-style, not the official devkit.** Same IoU thresholds, difficulty levels and
  ignore rules, but greedy matching; expect small differences from officially reported numbers.
- **Daytime only**, Karlsruhe, 2011. No night, rain or snow.
