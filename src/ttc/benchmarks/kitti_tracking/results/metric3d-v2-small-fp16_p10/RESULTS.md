# Time To Collision benchmark (KITTI tracking): `metric3d-v2-small-fp16_p10`

Generated automatically from `results.json` by `benchmark_ttc_kitti.py`. Do not edit by hand.

## Setup

|  |  |
| --- | --- |
| Input | src/distance/benchmarks/kitti_tracking/results/metric3d-v2-small-fp16_f150/observations.csv, column metric3d-v2-small-fp16_p10 |
| Data | 14444 readings of 422 tracked objects, 10 fps |
| Ground truth | laser 3D box labels; closing speed = centred linear fit over +-0.5 s of the true nearest-surface distance |
| In path | footprint within 1.2 m of our centre line: 2682 readings with a true speed |
| Settled | 1931 readings of 70 objects with 2 s of history (where the longest window answers) |
| Early | 599 readings in the first 2 s |
| TTC scored | true TTC under 10 s, gap shrinking by at least 0.5 m/s: 535 settled readings of 46 objects |
| Phantom warning | true TTC over 6 s (or not closing) but estimated under 2.5 s; 1657 settled readings |
| Git commit | `f972a1a` (with uncommitted changes) |
| Created (UTC) | 2026-10-01T16:18:57+00:00 |

## How noisy the input is (in path)

|  |  |
| --- | --- |
| Change of the reading's error between consecutive frames, median / p90 | 1.5% / 4.5% |
| Equivalent independent noise per reading (used in the braking test) | 1.5% |
| True closing speed (absolute), median / p90 (m/s) | 1.55 / 6.54 |

## Summary: the trade-off per method

Real readings (part 1) and the braking test with real errors replayed (part 2, all scenarios).
Ranked: false warnings before braking (worst scenario) of 5% or less first, then by average delay.

| Method | Settled: answers | Settled speed error p90 (m/s) | Early: answers | Early phantom warnings | Braking: average warning delay (s) | Braking: false warning, worst scenario |
| --- | --- | --- | --- | --- | --- | --- |
| `window_5` | 96.4% | 3.86 | 73.5% | 3.0% | 0.10 | 3.6% |
| `kalman_a4_r0.015_g1.5` | 99.2% | 2.79 | 75.8% | 2.5% | 0.17 | 4.2% |
| `kalman_a4_r0.015_g1` | 94.7% | 2.35 | 61.9% | 1.4% | 0.17 | 3.6% |
| `kalman_a2_r0.015_g1.5` | 99.2% | 2.74 | 77.0% | 2.5% | 0.27 | 4.2% |
| `kalman_a2_r0.015_g1` | 98.9% | 2.68 | 69.3% | 2.4% | 0.27 | 3.6% |
| `kalman_a2_r0.015_g0.5` | 68.9% | 1.25 | 31.7% | 1.8% | 0.27 | 3.0% |
| `window_10` | 96.4% | 2.52 | 50.9% | 1.7% | 0.30 | 2.4% |
| `kalman_a1_r0.015_g1.5` | 99.2% | 2.84 | 77.3% | 3.1% | 0.43 | 3.6% |
| `kalman_a1_r0.015_g1` | 98.9% | 2.80 | 70.0% | 3.2% | 0.43 | 3.0% |
| `kalman_a1_r0.015_g0.5` | 97.7% | 2.68 | 52.8% | 3.4% | 0.43 | 2.4% |
| `window_20` | 100.0% | 2.47 | 0.0% | - | 0.53 | 0.8% |
| `kalman_a0.5_r0.015_g1.5` | 99.2% | 3.16 | 77.3% | 3.5% | 0.60 | 3.6% |
| `kalman_a0.5_r0.015_g1` | 98.9% | 3.11 | 70.0% | 3.6% | 0.60 | 3.0% |
| `kalman_a0.5_r0.015_g0.5` | 97.7% | 3.01 | 54.6% | 3.8% | 0.60 | 2.4% |
| `kalman_a8_r0.015_g1` | 18.8% | 1.32 | 10.8% | 1.7% | 0.80 | 1.8% |
| `kalman_a4_r0.015_g0.5` | 3.4% | 0.96 | 6.2% | 0.0% | 1.30 | 0.0% |
| `kalman_a8_r0.015_g0.5` | 0.0% | - | 0.0% | - | - | 0.0% |
| `window_1` | 97.9% | 11.89 | 93.3% | 13.8% | -0.68 | 62.4% |
| `kalman_a8_r0.015` | 99.7% | 3.06 | 95.7% | 2.7% | 0.07 | 10.3% |
| `kalman_a8_r0.015_g1.5` | 83.4% | 2.16 | 57.8% | 2.0% | 0.07 | 7.3% |
| `kalman_a4_r0.015` | 99.7% | 2.83 | 95.7% | 2.7% | 0.17 | 7.3% |
| `kalman_a2_r0.015` | 99.7% | 2.78 | 95.7% | 2.7% | 0.27 | 7.3% |
| `kalman_a1_r0.015` | 99.7% | 2.87 | 95.7% | 3.3% | 0.43 | 6.7% |
| `kalman_a0.5_r0.015` | 99.7% | 3.19 | 95.7% | 3.5% | 0.60 | 6.7% |

## Part 1: real readings, ranked by settled speed error p90

| Rank | Method | Settled speed error median (m/s) | Settled p90 | TTC within 20% | TTC median error | Phantom warnings (objects) | Early: answers | Early median | Early p90 | Early phantom warnings (objects) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `kalman_a4_r0.015_g0.5` | 0.32 | 0.96 | 44.8% | 31.5% | 2.7% (1) | 6.2% | 0.43 | 0.96 | 0.0% (0) |
| 2 | `kalman_a2_r0.015_g0.5` | 0.35 | 1.25 | 48.8% | 20.6% | 0.4% (4) | 31.7% | 0.54 | 5.24 | 1.8% (1) |
| 3 | `kalman_a8_r0.015_g1` | 0.53 | 1.32 | 28.1% | 36.9% | 2.8% (5) | 10.8% | 0.59 | 1.22 | 1.7% (1) |
| 4 | `kalman_a8_r0.015_g1.5` | 0.71 | 2.16 | 34.8% | 31.7% | 1.2% (10) | 57.8% | 0.98 | 5.24 | 2.0% (3) |
| 5 | `kalman_a4_r0.015_g1` | 0.56 | 2.35 | 44.5% | 23.2% | 0.7% (7) | 61.9% | 0.92 | 4.80 | 1.4% (3) |
| 6 | `window_20` | 0.44 | 2.47 | 49.6% | 20.1% | 0.5% (4) | 0.0% | - | - | - (0) |
| 7 | `window_10` | 0.50 | 2.52 | 46.6% | 21.9% | 0.5% (4) | 50.9% | 0.98 | 5.10 | 1.7% (2) |
| 8 | `kalman_a2_r0.015_g1` | 0.45 | 2.68 | 47.6% | 21.2% | 0.5% (5) | 69.3% | 1.06 | 5.79 | 2.4% (3) |
| 9 | `kalman_a1_r0.015_g0.5` | 0.44 | 2.68 | 47.7% | 21.2% | 0.4% (2) | 52.8% | 0.80 | 5.13 | 3.4% (1) |
| 10 | `kalman_a2_r0.015_g1.5` | 0.45 | 2.74 | 47.6% | 21.2% | 0.5% (5) | 77.0% | 1.16 | 5.80 | 2.5% (3) |
| 11 | `kalman_a2_r0.015` | 0.45 | 2.78 | 47.7% | 21.1% | 0.5% (5) | 95.7% | 1.49 | 8.64 | 2.7% (5) |
| 12 | `kalman_a4_r0.015_g1.5` | 0.58 | 2.79 | 44.3% | 23.6% | 0.7% (7) | 75.8% | 1.18 | 6.01 | 2.5% (3) |
| 13 | `kalman_a1_r0.015_g1` | 0.44 | 2.80 | 48.0% | 21.1% | 0.4% (2) | 70.0% | 1.15 | 5.15 | 3.2% (3) |
| 14 | `kalman_a4_r0.015` | 0.59 | 2.83 | 44.4% | 23.6% | 0.7% (7) | 95.7% | 1.43 | 9.45 | 2.7% (5) |
| 15 | `kalman_a1_r0.015_g1.5` | 0.44 | 2.84 | 48.0% | 21.1% | 0.4% (2) | 77.3% | 1.21 | 5.16 | 3.1% (3) |
| 16 | `kalman_a1_r0.015` | 0.44 | 2.87 | 48.1% | 21.0% | 0.4% (2) | 95.7% | 1.57 | 7.51 | 3.3% (5) |
| 17 | `kalman_a0.5_r0.015_g0.5` | 0.48 | 3.01 | 47.5% | 21.2% | 0.4% (2) | 54.6% | 0.85 | 5.14 | 3.8% (1) |
| 18 | `kalman_a8_r0.015` | 0.80 | 3.06 | 34.7% | 31.9% | 1.0% (10) | 95.7% | 1.50 | 9.29 | 2.7% (6) |
| 19 | `kalman_a0.5_r0.015_g1` | 0.49 | 3.11 | 47.8% | 21.1% | 0.4% (2) | 70.0% | 1.08 | 5.20 | 3.6% (3) |
| 20 | `kalman_a0.5_r0.015_g1.5` | 0.49 | 3.16 | 47.8% | 21.1% | 0.4% (2) | 77.3% | 1.21 | 5.22 | 3.5% (3) |
| 21 | `kalman_a0.5_r0.015` | 0.50 | 3.19 | 47.9% | 21.0% | 0.4% (2) | 95.7% | 1.58 | 7.04 | 3.5% (5) |
| 22 | `window_5` | 0.79 | 3.86 | 37.7% | 29.1% | 0.7% (7) | 73.5% | 1.43 | 7.18 | 3.0% (6) |
| 23 | `window_1` | 2.58 | 11.89 | 16.6% | 62.3% | 7.8% (36) | 93.3% | 4.35 | 23.23 | 13.8% (22) |
| 24 | `kalman_a8_r0.015_g0.5` | - | - | - | - | - (0) | 0.0% | - | - | - (0) |

## Part 2: braking test, hard braking, 30 m, real error sequences replayed

Car ahead 30 m away at our speed, then brakes at 6 m/s^2. Impact 3.16 s after it brakes. A perfect sensor warns 1.6 s after the brake, leaving 1.56 s. 126 noise draws. Ranked: never warned, then more than 5% false warnings, then delay.

| Method | Warning delay median (s) | Delay p90 (s) | Time left median (s) | Time left p10 (s) | False warning before braking | Never warned |
| --- | --- | --- | --- | --- | --- | --- |
| `window_5` | 0.10 | 0.30 | 1.46 | 1.26 | 2.4% | 0.0% |
| `kalman_a8_r0.015` | 0.10 | 0.30 | 1.46 | 1.26 | 4.8% | 0.0% |
| `kalman_a8_r0.015_g1.5` | 0.10 | 0.30 | 1.46 | 1.26 | 2.4% | 0.0% |
| `kalman_a4_r0.015` | 0.20 | 0.30 | 1.36 | 1.26 | 4.0% | 0.0% |
| `kalman_a4_r0.015_g1.5` | 0.20 | 0.30 | 1.36 | 1.26 | 2.4% | 0.0% |
| `kalman_a4_r0.015_g1` | 0.20 | 0.30 | 1.36 | 1.26 | 2.4% | 0.0% |
| `window_10` | 0.30 | 0.40 | 1.26 | 1.16 | 1.6% | 0.0% |
| `kalman_a2_r0.015` | 0.30 | 0.40 | 1.26 | 1.16 | 4.0% | 0.0% |
| `kalman_a2_r0.015_g1.5` | 0.30 | 0.40 | 1.26 | 1.16 | 2.4% | 0.0% |
| `kalman_a2_r0.015_g1` | 0.30 | 0.40 | 1.26 | 1.16 | 2.4% | 0.0% |
| `kalman_a2_r0.015_g0.5` | 0.30 | 0.40 | 1.26 | 1.16 | 0.8% | 0.0% |
| `kalman_a1_r0.015` | 0.50 | 0.60 | 1.06 | 0.96 | 4.0% | 0.0% |
| `kalman_a1_r0.015_g1.5` | 0.50 | 0.60 | 1.06 | 0.96 | 2.4% | 0.0% |
| `kalman_a1_r0.015_g1` | 0.50 | 0.60 | 1.06 | 0.96 | 2.4% | 0.0% |
| `kalman_a1_r0.015_g0.5` | 0.50 | 0.60 | 1.06 | 0.96 | 1.6% | 0.0% |
| `window_20` | 0.60 | 0.60 | 0.96 | 0.96 | 0.8% | 0.0% |
| `kalman_a0.5_r0.015` | 0.70 | 0.75 | 0.86 | 0.81 | 4.0% | 0.0% |
| `kalman_a0.5_r0.015_g1.5` | 0.70 | 0.75 | 0.86 | 0.81 | 1.6% | 0.0% |
| `kalman_a0.5_r0.015_g1` | 0.70 | 0.75 | 0.86 | 0.81 | 1.6% | 0.0% |
| `kalman_a0.5_r0.015_g0.5` | 0.70 | 0.75 | 0.86 | 0.81 | 0.8% | 0.0% |
| `kalman_a8_r0.015_g1` | 1.00 | 1.10 | 0.56 | 0.46 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g0.5` | 1.40 | 1.40 | 0.16 | 0.16 | 0.0% | 0.0% |
| `window_1` | -0.55 | -0.10 | 2.11 | 1.66 | 60.3% | 0.0% |
| `kalman_a8_r0.015_g0.5` | - | - | - | - | 0.0% | 100.0% |

## Part 2: braking test, moderate braking, 30 m, real error sequences replayed

Car ahead 30 m away at our speed, then brakes at 3 m/s^2. Impact 4.47 s after it brakes. A perfect sensor warns 2.7 s after the brake, leaving 1.77 s. 93 noise draws. Ranked: never warned, then more than 5% false warnings, then delay.

| Method | Warning delay median (s) | Delay p90 (s) | Time left median (s) | Time left p10 (s) | False warning before braking | Never warned |
| --- | --- | --- | --- | --- | --- | --- |
| `window_5` | 0.00 | 0.20 | 1.77 | 1.57 | 2.1% | 0.0% |
| `kalman_a8_r0.015` | 0.00 | 0.20 | 1.77 | 1.57 | 3.2% | 0.0% |
| `kalman_a8_r0.015_g1.5` | 0.00 | 0.20 | 1.77 | 1.57 | 2.1% | 0.0% |
| `kalman_a4_r0.015` | 0.10 | 0.30 | 1.67 | 1.47 | 3.2% | 0.0% |
| `kalman_a4_r0.015_g1.5` | 0.10 | 0.30 | 1.67 | 1.47 | 2.1% | 0.0% |
| `kalman_a4_r0.015_g1` | 0.10 | 0.30 | 1.67 | 1.47 | 2.1% | 0.0% |
| `window_10` | 0.20 | 0.30 | 1.57 | 1.47 | 1.1% | 0.0% |
| `kalman_a2_r0.015` | 0.20 | 0.30 | 1.57 | 1.47 | 3.2% | 0.0% |
| `kalman_a2_r0.015_g1.5` | 0.20 | 0.30 | 1.57 | 1.47 | 2.1% | 0.0% |
| `kalman_a2_r0.015_g1` | 0.20 | 0.30 | 1.57 | 1.47 | 2.1% | 0.0% |
| `kalman_a2_r0.015_g0.5` | 0.20 | 0.30 | 1.57 | 1.47 | 0.0% | 0.0% |
| `window_20` | 0.40 | 0.58 | 1.37 | 1.19 | 0.0% | 0.0% |
| `kalman_a1_r0.015` | 0.40 | 0.40 | 1.37 | 1.37 | 3.2% | 0.0% |
| `kalman_a1_r0.015_g1.5` | 0.40 | 0.40 | 1.37 | 1.37 | 2.1% | 0.0% |
| `kalman_a1_r0.015_g1` | 0.40 | 0.40 | 1.37 | 1.37 | 2.1% | 0.0% |
| `kalman_a1_r0.015_g0.5` | 0.40 | 0.40 | 1.37 | 1.37 | 1.1% | 0.0% |
| `kalman_a0.5_r0.015` | 0.50 | 0.60 | 1.27 | 1.17 | 3.2% | 0.0% |
| `kalman_a0.5_r0.015_g1.5` | 0.50 | 0.60 | 1.27 | 1.17 | 2.1% | 0.0% |
| `kalman_a0.5_r0.015_g1` | 0.50 | 0.60 | 1.27 | 1.17 | 2.1% | 0.0% |
| `kalman_a0.5_r0.015_g0.5` | 0.50 | 0.60 | 1.27 | 1.17 | 1.1% | 0.0% |
| `kalman_a8_r0.015_g1` | 1.00 | 1.00 | 0.77 | 0.77 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g0.5` | 1.50 | 1.50 | 0.27 | 0.27 | 0.0% | 0.0% |
| `window_1` | -1.30 | -0.22 | 3.07 | 1.99 | 55.9% | 0.0% |
| `kalman_a8_r0.015_g0.5` | - | - | - | - | 0.0% | 100.0% |

## Part 2: braking test, hard braking, 15 m, real error sequences replayed

Car ahead 15 m away at our speed, then brakes at 6 m/s^2. Impact 2.24 s after it brakes. A perfect sensor warns 0.9 s after the brake, leaving 1.34 s. 165 noise draws. Ranked: never warned, then more than 5% false warnings, then delay.

| Method | Warning delay median (s) | Delay p90 (s) | Time left median (s) | Time left p10 (s) | False warning before braking | Never warned |
| --- | --- | --- | --- | --- | --- | --- |
| `window_5` | 0.20 | 0.30 | 1.14 | 1.04 | 3.6% | 0.0% |
| `kalman_a4_r0.015_g1.5` | 0.20 | 0.30 | 1.14 | 1.04 | 4.2% | 0.0% |
| `kalman_a4_r0.015_g1` | 0.20 | 0.30 | 1.14 | 1.04 | 3.6% | 0.0% |
| `kalman_a2_r0.015_g1.5` | 0.30 | 0.40 | 1.04 | 0.94 | 4.2% | 0.0% |
| `kalman_a2_r0.015_g1` | 0.30 | 0.40 | 1.04 | 0.94 | 3.6% | 0.0% |
| `kalman_a2_r0.015_g0.5` | 0.30 | 0.40 | 1.04 | 0.94 | 3.0% | 0.0% |
| `window_10` | 0.40 | 0.40 | 0.94 | 0.94 | 2.4% | 0.0% |
| `kalman_a1_r0.015_g1.5` | 0.40 | 0.50 | 0.94 | 0.84 | 3.6% | 0.0% |
| `kalman_a1_r0.015_g1` | 0.40 | 0.50 | 0.94 | 0.84 | 3.0% | 0.0% |
| `kalman_a1_r0.015_g0.5` | 0.40 | 0.50 | 0.94 | 0.84 | 2.4% | 0.0% |
| `kalman_a8_r0.015_g1` | 0.40 | 0.50 | 0.94 | 0.84 | 1.8% | 0.0% |
| `window_20` | 0.60 | 0.70 | 0.74 | 0.64 | 0.6% | 0.0% |
| `kalman_a0.5_r0.015_g1.5` | 0.60 | 0.60 | 0.74 | 0.74 | 3.6% | 0.0% |
| `kalman_a0.5_r0.015_g1` | 0.60 | 0.60 | 0.74 | 0.74 | 3.0% | 0.0% |
| `kalman_a0.5_r0.015_g0.5` | 0.60 | 0.60 | 0.74 | 0.74 | 2.4% | 0.0% |
| `kalman_a4_r0.015_g0.5` | 1.00 | 1.00 | 0.34 | 0.34 | 0.0% | 0.0% |
| `window_1` | -0.20 | 0.06 | 1.54 | 1.28 | 62.4% | 0.0% |
| `kalman_a8_r0.015` | 0.10 | 0.20 | 1.24 | 1.14 | 10.3% | 0.0% |
| `kalman_a8_r0.015_g1.5` | 0.10 | 0.20 | 1.24 | 1.14 | 7.3% | 0.0% |
| `kalman_a4_r0.015` | 0.20 | 0.30 | 1.14 | 1.04 | 7.3% | 0.0% |
| `kalman_a2_r0.015` | 0.30 | 0.40 | 1.04 | 0.94 | 7.3% | 0.0% |
| `kalman_a1_r0.015` | 0.40 | 0.50 | 0.94 | 0.84 | 6.7% | 0.0% |
| `kalman_a0.5_r0.015` | 0.60 | 0.60 | 0.74 | 0.74 | 6.7% | 0.0% |
| `kalman_a8_r0.015_g0.5` | - | - | - | - | 0.0% | 100.0% |

## Part 2: braking test, hard braking, 30 m, independent noise

Car ahead 30 m away at our speed, then brakes at 6 m/s^2. Impact 3.16 s after it brakes. A perfect sensor warns 1.6 s after the brake, leaving 1.56 s. 300 noise draws. Ranked: never warned, then more than 5% false warnings, then delay.

| Method | Warning delay median (s) | Delay p90 (s) | Time left median (s) | Time left p10 (s) | False warning before braking | Never warned |
| --- | --- | --- | --- | --- | --- | --- |
| `window_5` | 0.10 | 0.20 | 1.46 | 1.36 | 0.0% | 0.0% |
| `kalman_a8_r0.015` | 0.10 | 0.20 | 1.46 | 1.36 | 0.7% | 0.0% |
| `kalman_a8_r0.015_g1.5` | 0.10 | 0.20 | 1.46 | 1.36 | 0.0% | 0.0% |
| `kalman_a4_r0.015` | 0.20 | 0.30 | 1.36 | 1.26 | 0.7% | 0.0% |
| `kalman_a4_r0.015_g1.5` | 0.20 | 0.30 | 1.36 | 1.26 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g1` | 0.20 | 0.30 | 1.36 | 1.26 | 0.0% | 0.0% |
| `window_10` | 0.30 | 0.30 | 1.26 | 1.26 | 0.0% | 0.0% |
| `kalman_a2_r0.015` | 0.30 | 0.40 | 1.26 | 1.16 | 0.7% | 0.0% |
| `kalman_a2_r0.015_g1.5` | 0.30 | 0.40 | 1.26 | 1.16 | 0.0% | 0.0% |
| `kalman_a2_r0.015_g1` | 0.30 | 0.40 | 1.26 | 1.16 | 0.0% | 0.0% |
| `kalman_a2_r0.015_g0.5` | 0.30 | 0.40 | 1.26 | 1.16 | 0.0% | 0.0% |
| `kalman_a1_r0.015` | 0.50 | 0.50 | 1.06 | 1.06 | 0.7% | 0.0% |
| `kalman_a1_r0.015_g1.5` | 0.50 | 0.50 | 1.06 | 1.06 | 0.0% | 0.0% |
| `kalman_a1_r0.015_g1` | 0.50 | 0.50 | 1.06 | 1.06 | 0.0% | 0.0% |
| `kalman_a1_r0.015_g0.5` | 0.50 | 0.50 | 1.06 | 1.06 | 0.0% | 0.0% |
| `window_20` | 0.60 | 0.60 | 0.96 | 0.96 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015` | 0.70 | 0.70 | 0.86 | 0.86 | 0.7% | 0.0% |
| `kalman_a0.5_r0.015_g1.5` | 0.70 | 0.70 | 0.86 | 0.86 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015_g1` | 0.70 | 0.70 | 0.86 | 0.86 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015_g0.5` | 0.70 | 0.70 | 0.86 | 0.86 | 0.0% | 0.0% |
| `kalman_a8_r0.015_g1` | 1.10 | 1.10 | 0.46 | 0.46 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g0.5` | 1.40 | 1.40 | 0.16 | 0.16 | 0.0% | 0.0% |
| `window_1` | -0.80 | -0.30 | 2.36 | 1.86 | 79.7% | 0.0% |
| `kalman_a8_r0.015_g0.5` | - | - | - | - | 0.0% | 100.0% |

## Part 2: braking test, moderate braking, 30 m, independent noise

Car ahead 30 m away at our speed, then brakes at 3 m/s^2. Impact 4.47 s after it brakes. A perfect sensor warns 2.7 s after the brake, leaving 1.77 s. 300 noise draws. Ranked: never warned, then more than 5% false warnings, then delay.

| Method | Warning delay median (s) | Delay p90 (s) | Time left median (s) | Time left p10 (s) | False warning before braking | Never warned |
| --- | --- | --- | --- | --- | --- | --- |
| `window_5` | 0.00 | 0.20 | 1.77 | 1.57 | 0.0% | 0.0% |
| `kalman_a4_r0.015` | 0.10 | 0.20 | 1.67 | 1.57 | 0.3% | 0.0% |
| `kalman_a4_r0.015_g1.5` | 0.10 | 0.20 | 1.67 | 1.57 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g1` | 0.10 | 0.20 | 1.67 | 1.57 | 0.0% | 0.0% |
| `kalman_a8_r0.015` | 0.10 | 0.20 | 1.67 | 1.57 | 0.3% | 0.0% |
| `kalman_a8_r0.015_g1.5` | 0.10 | 0.20 | 1.67 | 1.57 | 0.0% | 0.0% |
| `window_10` | 0.20 | 0.30 | 1.57 | 1.47 | 0.0% | 0.0% |
| `kalman_a2_r0.015` | 0.20 | 0.30 | 1.57 | 1.47 | 0.3% | 0.0% |
| `kalman_a2_r0.015_g1.5` | 0.20 | 0.30 | 1.57 | 1.47 | 0.0% | 0.0% |
| `kalman_a2_r0.015_g1` | 0.20 | 0.30 | 1.57 | 1.47 | 0.0% | 0.0% |
| `kalman_a2_r0.015_g0.5` | 0.20 | 0.30 | 1.57 | 1.47 | 0.0% | 0.0% |
| `window_20` | 0.40 | 0.50 | 1.37 | 1.27 | 0.0% | 0.0% |
| `kalman_a1_r0.015` | 0.40 | 0.40 | 1.37 | 1.37 | 0.3% | 0.0% |
| `kalman_a1_r0.015_g1.5` | 0.40 | 0.40 | 1.37 | 1.37 | 0.0% | 0.0% |
| `kalman_a1_r0.015_g1` | 0.40 | 0.40 | 1.37 | 1.37 | 0.0% | 0.0% |
| `kalman_a1_r0.015_g0.5` | 0.40 | 0.40 | 1.37 | 1.37 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015` | 0.50 | 0.60 | 1.27 | 1.17 | 0.3% | 0.0% |
| `kalman_a0.5_r0.015_g1.5` | 0.50 | 0.60 | 1.27 | 1.17 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015_g1` | 0.50 | 0.60 | 1.27 | 1.17 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015_g0.5` | 0.50 | 0.60 | 1.27 | 1.17 | 0.0% | 0.0% |
| `kalman_a8_r0.015_g1` | 1.00 | 1.00 | 0.77 | 0.77 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g0.5` | 1.50 | 1.50 | 0.27 | 0.27 | 0.0% | 0.0% |
| `window_1` | -1.70 | -0.80 | 3.47 | 2.57 | 77.0% | 0.0% |
| `kalman_a8_r0.015_g0.5` | - | - | - | - | 0.0% | 100.0% |

## Part 2: braking test, hard braking, 15 m, independent noise

Car ahead 15 m away at our speed, then brakes at 6 m/s^2. Impact 2.24 s after it brakes. A perfect sensor warns 0.9 s after the brake, leaving 1.34 s. 300 noise draws. Ranked: never warned, then more than 5% false warnings, then delay.

| Method | Warning delay median (s) | Delay p90 (s) | Time left median (s) | Time left p10 (s) | False warning before braking | Never warned |
| --- | --- | --- | --- | --- | --- | --- |
| `kalman_a8_r0.015` | 0.10 | 0.20 | 1.24 | 1.14 | 1.7% | 0.0% |
| `kalman_a8_r0.015_g1.5` | 0.10 | 0.20 | 1.24 | 1.14 | 0.0% | 0.0% |
| `window_5` | 0.20 | 0.30 | 1.14 | 1.04 | 0.0% | 0.0% |
| `kalman_a4_r0.015` | 0.20 | 0.30 | 1.14 | 1.04 | 1.7% | 0.0% |
| `kalman_a4_r0.015_g1.5` | 0.20 | 0.30 | 1.14 | 1.04 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g1` | 0.20 | 0.30 | 1.14 | 1.04 | 0.0% | 0.0% |
| `kalman_a2_r0.015` | 0.30 | 0.30 | 1.04 | 1.04 | 1.7% | 0.0% |
| `kalman_a2_r0.015_g1.5` | 0.30 | 0.30 | 1.04 | 1.04 | 0.0% | 0.0% |
| `kalman_a2_r0.015_g1` | 0.30 | 0.30 | 1.04 | 1.04 | 0.0% | 0.0% |
| `kalman_a2_r0.015_g0.5` | 0.30 | 0.30 | 1.04 | 1.04 | 0.0% | 0.0% |
| `window_10` | 0.40 | 0.40 | 0.94 | 0.94 | 0.0% | 0.0% |
| `kalman_a1_r0.015` | 0.40 | 0.50 | 0.94 | 0.84 | 1.7% | 0.0% |
| `kalman_a1_r0.015_g1.5` | 0.40 | 0.50 | 0.94 | 0.84 | 0.0% | 0.0% |
| `kalman_a1_r0.015_g1` | 0.40 | 0.50 | 0.94 | 0.84 | 0.0% | 0.0% |
| `kalman_a1_r0.015_g0.5` | 0.40 | 0.50 | 0.94 | 0.84 | 0.0% | 0.0% |
| `kalman_a8_r0.015_g1` | 0.40 | 0.40 | 0.94 | 0.94 | 0.0% | 0.0% |
| `window_20` | 0.60 | 0.70 | 0.74 | 0.64 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015` | 0.60 | 0.60 | 0.74 | 0.74 | 1.7% | 0.0% |
| `kalman_a0.5_r0.015_g1.5` | 0.60 | 0.60 | 0.74 | 0.74 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015_g1` | 0.60 | 0.60 | 0.74 | 0.74 | 0.0% | 0.0% |
| `kalman_a0.5_r0.015_g0.5` | 0.60 | 0.60 | 0.74 | 0.74 | 0.0% | 0.0% |
| `kalman_a4_r0.015_g0.5` | 1.00 | 1.00 | 0.34 | 0.34 | 0.0% | 0.0% |
| `window_1` | -0.30 | 0.00 | 1.64 | 1.34 | 75.0% | 0.0% |
| `kalman_a8_r0.015_g0.5` | - | - | - | - | 0.0% | 100.0% |

## Known limitations

- KITTI is calm driving: few objects truly approach fast, so TTC is scored on few objects.
- The true speed comes from laser boxes fitted frame by frame; their own wobble is a floor.
- Objects are followed by their labelled ID, so tracker ID switches are not included.
- Braking test, independent noise: real depth errors drift slowly and jump now and then, so
  this version is optimistic. The replayed version uses real error sequences, but from calm
  KITTI driving, not from a braking car.
- Daytime only; first 150 frames of each sequence.
