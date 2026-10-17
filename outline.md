# safe-distance: what was tried and done, in order

A camera-only collision warning system for a car, meant to run on an edge device (Jetson Orin Nano). Two approaches
were built and measured: first a **hand-built pipeline** (detect, track, measure distance, compute time to collision,
warn), then a **learned risk model** (BADAS-Open, fine-tuned). Every number below comes from a results file in the
repo; the file is named next to it.

---

## Part 1: the hand-built pipeline (September 2026)

### 1.1 Detection (`src/detection/`)
- **Goal:** find road users and unusual obstacles in each frame.
- **Tried:** YOLO26-seg (80 COCO classes) and YOLOE-11-seg with open-vocabulary text prompts for hazards (prompt
  sets v1, v2, v3; v3 rejected).
- **Benchmarks:** KITTI road users (1,500 images) and Lost and Found small obstacles.

  | | YOLO26-seg (COCO) | YOLOE-11-seg (prompts v2) |
  | --- | --- | --- |
  | KITTI recall, all objects | **87%** | 77% |
  | KITTI false alarms per image | 6.44 | **0.93** |
  | Lost and Found recall, all obstacles | 30% | **42%** |
  | Lost and Found recall, 0-10 m | 49% | **99%** |
  | Median latency (RTX 4060) | 30 ms | 25-31 ms |

- **Decision:** YOLO26-seg by default (road users), YOLOE prompts for odd obstacles.
  (`src/detection/benchmarks/*/COMPARISON.md`)

### 1.2 Tracking (`src/tracking/`)
- **Tried:** ByteTrack and BoT-SORT on KITTI tracking (8,008 frames).
- **Result:** BoT-SORT better: car IDF1 79.5% vs 77.0%, MOTA 72.0% vs 64.8%, fewer ID switches (228 vs 301).
- **Decision:** BoT-SORT. (`src/tracking/benchmarks/kitti_tracking/COMPARISON.md`)

### 1.3 Distance (`src/distance/`)
- **Goal:** distance to each object's nearest surface, from one camera.
- **Tried:** geometric methods (known object size, ground plane, a fallback of both) and monocular depth models:
  Metric3D v2 (Small / Large, FP32 / FP16), UniDepth v2 (Small / Base / Large, with and without the camera given),
  Depth Anything v2 / v3 metric, Depth Pro, a YOLO depth head, and combinations (e.g. the minimum of two models).
- **Benchmarks:** KITTI (laser ground truth), Lost and Found (obstacles, also with real detector masks), nuScenes
  (day / night, cones and barriers), KITTI tracking (stability, closing-speed error), speed on the RTX 4060, focal
  length sensitivity. Share of objects within 10% of the true distance:

  | Candidate | KITTI in path | Lost and Found < 20 m | nuScenes in path | nuScenes night | ms per frame |
  | --- | --- | --- | --- | --- | --- |
  | **Metric3D v2 Small FP16** | 88% | 76% | 76% | 55% | 82 |
  | Metric3D v2 Large FP16 | 92% | 84% | 69% | 39% | 357 |
  | UniDepth v2 Large | 90% | 66% | 85% | 81% | 214 (non-commercial licence) |
  | Known size (geometric) | 77% | - | 52% | 55% | 0 |
  | Ground plane (geometric) | 46% | 41% | 24% | 47% | 0 |

- **Night enhancement:** CLAHE contrast boost before the depth model, confirmed on 82 never-seen nuScenes night
  scenes: in-path accuracy **51% to 68%** (45 scenes better, 12 worse).
- **Decision:** Metric3D v2 Small FP16 (accuracy, speed, BSD licence), CLAHE at night.
  (`src/distance/benchmarks/SUMMARY.md`, `nuscenes/COMPARISON_NIGHT_CONFIRM.md`)

### 1.4 Time to collision (`src/ttc/`)
- **Goal:** time until contact from the distance track, plus a warning rule.
- **Tried:** sliding-window speed fits, a distance Kalman filter with a speed gate, "looming" (growth of the
  object's image size), and a fused distance + size filter; warnings confirmed over N frames.
- **Benchmark:** KITTI tracking with real readings, plus a braking test that replays the real measurement errors.
  Best trade-offs: braking warning delay 0.10-0.30 s, false warnings before braking 0-4%.
- **Demo:** a live visual replay on KITTI and a simulated braking (`src/ttc/scripts/ttc_demo.py`).
  (`src/ttc/benchmarks/kitti_tracking/results/`)

### 1.5 The full pipeline on real crashes (Nexar)
- **Data:** the Nexar collision dataset (dashcam crashes and near-misses), downloaded to Modal.
- **Rule:** warn when TTC < 2.5 s for 2 frames, for an object in our path (1.2 m corridor).
- **Run v2 (300 crash + 50 normal clips):** **52%** of crashes warned in the 4 s before the event, but **187 false
  warnings per hour**; stricter rules cut false warnings only by also losing crashes (e.g. 24% warned at 43/h).
  A diagnosis compared false vs true warning objects (distance, closing speed, lateral gap, box size).
  (`src/ttc/benchmarks/nexar/results/v2/`)
- **Nexar test set, official metric (mAP):** our pipeline's best score **0.669** (0.5 = random).
  (`nexar/results/test1/RESULTS.md`)

---

## Part 2: comparing with learned models (October 2026)

### 2.1 BADAS-Open and openpilot on the Nexar test set
| System | Nexar mAP Public | Private |
| --- | --- | --- |
| Our pipeline (1 / TTC) | 0.669 | 0.663 |
| openpilot's driving model (forward collision warning) | 0.504 | 0.509 |
| **BADAS-Open** (V-JEPA 2 video model, trained on Nexar) | **0.909** | **0.900** |
| BADAS-Open + ours (rank combination) | 0.857 | 0.844 |

- **Live warnings** (a reading every 0.5 s): BADAS warned far more crashes than our rule (75% vs 34% at a comparable
  false-warning level), but still beeped often in normal driving.
- **Fusion test** (logistic fusion of BADAS + our TTC features, and "physical gates" like "only if something is in
  our path"): **none beat BADAS alone** (e.g. 47% vs 41% crashes warned at 100 false warnings per hour).
- **Decision:** move to a learned risk model: fine-tune BADAS-Open (the teacher), later distil it into a small
  student. The hand-built pipeline stays for "where / how far" (stage 2) and the braking decision.
  (`nexar/results/test1/LIVE_WARNINGS.md`, `FUSION_PUBLIC.md`)

### 2.2 BADAS's real problem: false warnings in normal driving
- First on 608 BDD100K clips (6.4 h): at risk > 0.9, **208 false warnings per hour** for 78% of crashes warned.
  (`src/ttc/benchmarks/bdd100k/results/FALSE_WARNINGS.md`)

---

## Part 3: the learned risk model (`src/risk/`)

### 3.1 Data
- **Nexar train:** 750 crash + 750 normal clips (~40 s, alert and crash times by 10 annotators).
  **Nexar test:** Public half = our validation, Private half = the final score only.
- **BDD100K** normal driving: 3,000 train / 500 val / 1,000 test clips drawn (seed 20261012), extracted on Modal.
- **Looked at and rejected for crashes:** MM-AU, CCD, ROL (footage / timing quality), DoTA (videos offline),
  DAD (hindsight labels). **NVIDIA PhysicalAI-AV:** scanned 239,027 clips for hard braking, then not used (its
  licence keeps results confidential and use internal).
- **Frame caches on Modal:** first 224 × 224 squashed; now **256 × 448, true 16:9** (6,243 clips).

### 3.2 Evaluation tool (`src/risk/eval_risk.py`)
- Live readings every 0.5 s on BDD100K val + Nexar Public; false warnings per hour, crashes warned, crashes warned
  at a false-warning budget, official mAP. Made fast (GPU preprocessing, torch.compile, 4 A100s) and checked
  against the exact original (readings 0.0012 off on average).
- **Baseline BADAS-Open:** Nexar Public mAP **0.903**; 51% of crashes warned at 30 false warnings per hour.

### 3.3 Cleaning BDD100K (removing real near-misses from "normal" data)
- BADAS's riskiest BDD100K clips were often **real near-misses**, which would teach the model "danger = safe".
  Ranked every clip by BADAS's peak risk, then reviewed and hand-labelled (desktop and shared web tools).
- **Train: 2,576 of 3,000 kept**; **val: 434 of 500 kept**; tilted-camera clips removed too. Test: spot-checked,
  cleaned at the end.
- **Baseline re-scored on the clean val:** 47% of crashes warned at 10 false warnings per hour (was 26%), 61% at
  30/h. (`src/risk/data/bdd100k_ids/`, `runs/baseline_badas_open/results/eval_val_clean/`)

### 3.4 Stage 1 design (`src/risk/runs/stage1_lora/`)
- **Label rule** (`stage1_labels.py`): each 2 s window labelled by where it ends vs Nexar's alert and crash times:
  1 in the last 2.4 s, a ramp from 0.25 for early alerts, a 0.4 s skip after late alerts, safe only more than 4 s
  before the crash; 706 crash clips usable. Shown in demo videos per case.
- **LoRA on all 219 layers** of BADAS-Open (14.2 M of 345.6 M trainable), coverage checked: nothing left out.
- **One window per source per epoch** (4,738 windows, 15% danger), augmentations with independent chances,
  validation on 2,202 fixed windows with many logged scores.
- **Training script** `stage1_train.py` on the shared `ml_utils.py` engine, with start-up checks (LoRA coverage,
  batched predictor equal to BADAS's loop, step-0 model equal to BADAS-Open, every weight gets a gradient).

### 3.5 Input shape: from squashed to true 16:9
- **Found:** the squashed 224 × 224 input stretched everything 1.8× and cut every edge (demo video in
  `Downloads/safe-distance-testing/preprocessing/`).
- **Changed to 256 × 448** (shape kept, whole width). V-JEPA 2's position code assumed a square, so it was patched
  for the 16 × 28 grid (`src/risk/wide_input.py`); CPU check passed (identical on the square grid, all positions
  right).
- **Plain BADAS-Open on 100 Nexar Public clips:** mAP 0.917 at 16:9 vs 0.940 squashed (no collapse; it was only
  fine-tuned on squashed input). (`runs/stage1_lora/results/wide_vs_square_100.json`)

---

## Where things stand
1. 16:9 frame cache built; 16:9 baseline evaluation being fixed (the compiled model crashed; patch rewritten).
2. Then: the 16:9 baseline on the clean validation, the stage 1 smoke test, the stage 1 run.
3. Later: stage 2 (time to crash, where, what, type), stage 3 (small student for the Jetson), the final score once
   on Nexar Private + clean BDD100K test. Full plan: `plan.md`.
