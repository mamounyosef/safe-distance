# KITTI road-user benchmark: `yolo26s-seg_coco`

Generated automatically from `results.json` by `benchmark_kitti.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Model weights | `weights/yolo26s-seg.pt` |
| Vocabulary | fixed 80 COCO (Common Objects in Context) classes |
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
| Created (UTC) | 2026-09-23T07:11:51+00:00 |

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
| Car | 83.4% | 73.6% | 59.9% | 1186 | 3234 | 4497 |
| Pedestrian | 74.3% | 63.9% | 54.5% | 416 | 648 | 785 |
| Cyclist | 34.9% | 25.7% | 24.4% | 125 | 219 | 238 |

## Recall by class

| Class | Objects | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| car | 5946 | 90% | 90% | 88% |
| pedestrian | 869 | 77% | 75% | 70% |
| van | 548 | 85% | 84% | 80% |
| cyclist | 324 | 68% | 66% | 61% |
| truck | 235 | 85% | 84% | 80% |
| tram | 127 | 51% | 48% | 46% |

## Recall by distance, all classes

| Distance | Objects | Recall @0.05 | Recall @0.1 | Recall @0.25 |
| --- | --- | --- | --- | --- |
| 0-10 m | 982 | 90% | 90% | 89% |
| 10-20 m | 1933 | 89% | 88% | 87% |
| 20-30 m | 1795 | 85% | 85% | 83% |
| 30-50 m | 2315 | 85% | 84% | 82% |
| 50+ m | 1024 | 87% | 85% | 79% |

## Recall by class and distance (@0.05)

| Distance | car | pedestrian | van | cyclist | truck | tram |
| --- | --- | --- | --- | --- | --- | --- |
| 0-10 m | 91% (n=657) | 87% (n=246) | 91% (n=34) | 88% (n=24) | 81% (n=16) | 80% (n=5) |
| 10-20 m | 92% (n=1382) | 77% (n=335) | 93% (n=103) | 80% (n=89) | 77% (n=13) | 91% (n=11) |
| 20-30 m | 89% (n=1367) | 76% (n=153) | 89% (n=116) | 60% (n=88) | 91% (n=35) | 22% (n=36) |
| 30-50 m | 90% (n=1841) | 58% (n=110) | 82% (n=150) | 62% (n=104) | 86% (n=73) | 35% (n=37) |
| 50+ m | 92% (n=699) | 52% (n=25) | 77% (n=145) | 58% (n=19) | 84% (n=98) | 79% (n=38) |

## False alarms

| Threshold | Total | Per image |
| --- | --- | --- |
| 0.05 | 9667 | 6.44 |
| 0.1 | 5585 | 3.72 |
| 0.25 | 2432 | 1.62 |

## Latency

| Median (ms) | p95 (ms) |
| --- | --- |
| 30.2 | 55.9 |

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
