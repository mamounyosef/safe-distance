"""Benchmark closing speed and Time To Collision (TTC) on KITTI tracking. No GPU.

Question it answers: from the noisy per-frame camera measurements, how well can
we estimate each object's CLOSING SPEED (how fast the gap shrinks) and its Time
To Collision, which method does it best, and how should a warning be confirmed?

Inputs (both saved earlier, joined on sequence, frame and track ID):
    distances  src/distance/benchmarks/kitti_tracking/results/<run>/observations.csv:
               Metric3D's distance and the laser-measured true distance (nearest
               surface) of every labelled object matched to a detection, first
               150 frames of all 21 KITTI tracking sequences, 10 frames per second.
    sizes      results/sizes_f150/observations.csv (collect_sizes.py): the same
               objects' image sizes (box, mask outline) per frame.

Ground truth:
    true distance        from the laser-measured 3D box labels.
    true closing speed   slope of the true distances, fitted over +-0.5 s around
                         each frame (centred, so it has no delay; this needs
                         future frames, which only an offline truth may use).
    true TTC             true distance / true closing speed.

Methods compared (all causal: they only use the current and past frames):
    window_W                 closing speed from two distances W frames apart.
    kalman_a{A}_r{R}[_g{G}]  constant-velocity Kalman filter on the distance
                             (src/ttc/kalman.py): acceleration noise A m/s^2,
                             measurement noise R (share of the distance), speed
                             output only once its uncertainty is under G m/s.
    looming_{size}_a{A}[_g{G}]  Kalman filter on log(image size): its growth
                             rate is 1 / TTC, no distance needed ("looming").
                             Closing speed = filtered distance x growth rate.
                             Size = box height, mask outline height, or the
                             square root of the mask area. Measurement noise =
                             the wobble measured on the data. Objects touching
                             the image edge give no size reading that frame.
    fused_a{A}_d{D}[_g{G}]   ONE filter fed with both the distance and the box
                             height (src/ttc/kalman.py FusedKalman): the distance
                             sets how far, the box growth sets how fast. A =
                             growth-rate noise, D = depth noise (higher = trust
                             the distance less for motion), G = speed gate.

Warning confirmation (part A of step 3): a warning is raised when the estimated
TTC is under 2.5 s for N frames in a row (N = 1, 2, 3).

Part 1, real readings (in-path objects, footprint within 1.2 m of our centre line):
    settled          readings with 2 s of history (where the 20-frame window answers).
    early            readings in the first 2 s after an object is first seen.
    speed error      |estimated - true closing speed|, m/s, median and p90.
    TTC error        where the true TTC is under 10 s and the gap is shrinking:
                     share within 20% of the true TTC.
    phantom TTC      where the true TTC is over 6 s (or not closing): share of
                     readings with an active (confirmed) warning. False warnings.

Part 2, braking test (simulated, so the truth is exact): the car ahead brakes
while we keep our speed. Distance and size readings get either REAL error
sequences replayed (Metric3D's actual distance error and the detector's actual
size wobble along the same unbroken stretch of a real KITTI track) or
independent random noise of the measured size. Per method and confirmation N:
how late the warning comes compared with a perfect sensor, how much time is
left before impact, and how often it warns falsely before the braking starts.

Output: results/<run>/results.json (source of truth), series.csv (every
estimate per real reading) and a generated RESULTS.md.

RUN IT (from the repo root, D:\\My Projects\\safe-distance):

    .venv\\Scripts\\python.exe src\\ttc\\benchmarks\\kitti_tracking\\benchmark_ttc_kitti.py

Every setting lives in the CONFIG block below. Edit it there and re-run.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from src.detection.benchmarks.common import md_table, provenance  # noqa: E402
from src.ttc.kalman import DistanceKalman, FusedKalman, LogSizeKalman, time_to_collision  # noqa: E402

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

STABILITY = REPO / "src/distance/benchmarks/kitti_tracking/results"
SIZES = Path(__file__).resolve().parent / "results" / "sizes_f150" / "observations.csv"

# Runs, as (run name, stability run folder, distance column).
RUNS = [
    ("metric3d-v2-small-fp16_p10", "metric3d-v2-small-fp16_f150", "metric3d-v2-small-fp16_p10"),
]

FPS = 10.0
CORRIDOR_HALF_WIDTH_M = 1.2

# Truth: closing speed fitted over this many frames either side (5 = +-0.5 s).
TRUTH_HALF_WINDOW = 5
TRUTH_MIN_POINTS = 6

# Window baselines, in frames.
WINDOWS = [1, 5, 10, 20]

# Distance Kalman settings: acceleration noise (m/s^2) x measurement noise
# (share of the distance; 0.015 is what part 1 measures for Metric3D) x speed
# gate (m/s; None = speed from the 2nd reading).
ACCEL_NOISES = [0.5, 1.0, 2.0, 4.0, 8.0]
MEAS_NOISES = [0.015]
SPEED_GATES = [None, 1.5, 1.0, 0.5]

# Looming settings: size measures x growth-rate noise (1/s^2) x speed gate (m/s,
# on the closing speed = distance x growth rate). The size's measurement noise is
# measured on the data. The distance used for its closing speed comes from the
# distance Kalman filter below.
SIZE_KINDS = ["box_height", "mask_height", "sqrt_mask_area"]
LOOMING_ACCELS = [0.1, 0.2, 0.4, 0.8]
LOOMING_GATES = [None, 1.0]
LOOMING_DISTANCE_FILTER = (4.0, 0.015)   # (acceleration noise, measurement noise)

# Fused filter (distance + box size in one, src/ttc/kalman.py FusedKalman):
# growth-rate noise (1/s^2) x depth noise (share; 0.015 = measured, higher =
# trust the distance less for motion) x speed gate (m/s).
FUSED_SIZE_KIND = "box_height"
FUSED_ACCELS = [0.1, 0.2, 0.4]
FUSED_DEPTH_NOISES = [0.015, 0.03, 0.06]
FUSED_GATES = [None, 1.0]

# A track unseen for more than this many frames is restarted.
MAX_GAP_FRAMES = 5

# "Settled" = at least this many frames since first seen (the longest window).
SETTLED_AFTER_FRAMES = max(WINDOWS)

# TTC scoring.
TTC_RELEVANT_S = 10.0       # score TTC error where the true TTC is below this
TTC_TOLERANCE = 0.20
MIN_TRUE_CLOSING_MPS = 0.5  # below this the true TTC is not meaningful
WARN_TTC_S = 2.5            # typical forward collision warning threshold
SAFE_TTC_S = 6.0            # true TTC above this: a warning would be false
CONFIRM_FRAMES = [1, 2, 3]  # warning needs TTC under WARN_TTC_S this many frames in a row

# Braking test: (name, starting gap m, braking of the car ahead m/s^2). We keep
# our speed; the car ahead drives at our speed for BRAKE_AFTER_S, then brakes.
SCENARIOS = [
    ("hard braking, 30 m", 30.0, 6.0),
    ("moderate braking, 30 m", 30.0, 3.0),
    ("hard braking, 15 m", 15.0, 6.0),
]
BRAKE_AFTER_S = 4.0
# Simulated image size = this / distance (a 1.5 m tall car, focal length 720 px).
SIM_SIZE_PX_M = 1080.0
NOISE_DRAWS = 300
# Replayed errors: pieces start every this many frames along each real stretch
# (pieces overlap, so draws are not independent; more of them cover more cases).
REPLAY_STEP_FRAMES = 10
SEED = 0

OUT_DIR = Path(__file__).resolve().parent / "results"

# ----------------------------------------------------------------------------

# How to read each kind of image size (pixels) from a row of the sizes file.
SIZE_OF = {
    "box_height": lambda r: float(r["y2"]) - float(r["y1"]),
    "mask_height": lambda r: float(r["mask_height_px"]) if r["mask_height_px"] else None,
    "sqrt_mask_area": lambda r: math.sqrt(float(r["mask_area_px"])) if r["mask_area_px"] else None,
}


def load(run_folder: str, column: str) -> dict[tuple, list[dict]]:
    """Read both saved files and group them per object.

    Returns {(sequence, track ID): [one dict per frame, in time order]}, each
    with the depth model's distance, the true distance and the image sizes.
    A box touching the image edge gets no size (None): a cut-off object does
    not grow normally as it approaches."""
    sizes = {}
    with SIZES.open(newline="") as f:
        for r in csv.DictReader(f):
            edge = r["touches_edge"] == "1"
            sizes[(r["sequence"], int(r["track_id"]), int(r["frame"]))] = {
                k: (None if edge else SIZE_OF[k](r)) for k in SIZE_KINDS}
    tracks = defaultdict(list)
    with (STABILITY / run_folder / "observations.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r[column] in ("", "None"):
                continue
            key = (r["sequence"], int(r["track_id"]), int(r["frame"]))
            tracks[key[:2]].append({
                "sequence": r["sequence"], "track_id": key[1], "frame": key[2],
                "class": r["class"], "lateral_gap_m": float(r["lateral_gap_m"]),
                "true_m": float(r["true_nearest_surface_m"]), "measured_m": float(r[column]),
                "sizes": sizes.get(key, {k: None for k in SIZE_KINDS}),
            })
    for obs in tracks.values():
        obs.sort(key=lambda o: o["frame"])
    return tracks


def add_truth(obs: list[dict]) -> None:
    """Add the TRUE closing speed and TRUE TTC to each frame of one object.

    True closing speed = slope of a straight line fitted through the laser
    distances from 0.5 s before to 0.5 s after the frame (smooths the labels'
    own wobble). True TTC = true distance / true closing speed; infinity if the
    gap shrinks by less than MIN_TRUE_CLOSING_MPS."""
    frames = np.array([o["frame"] for o in obs])
    true = np.array([o["true_m"] for o in obs])
    for o in obs:
        near = np.abs(frames - o["frame"]) <= TRUTH_HALF_WINDOW
        if near.sum() >= TRUTH_MIN_POINTS and np.ptp(frames[near]) >= TRUTH_HALF_WINDOW:
            slope = np.polyfit(frames[near] / FPS, true[near], 1)[0]
            o["true_closing_mps"] = float(-slope)
            o["true_ttc_s"] = time_to_collision(o["true_m"], -slope) if -slope >= MIN_TRUE_CLOSING_MPS else math.inf
        else:
            o["true_closing_mps"] = None
            o["true_ttc_s"] = None


# ---- The methods being compared --------------------------------------------
# Each method is a function run(frames, readings, sizes) for ONE object:
#     frames    frame numbers (10 per second)
#     readings  depth model distance per frame (m)
#     sizes     image sizes per frame: {kind: pixels, or None if unknown}
# It returns, per frame: (distance, closing speed or None if not sure yet,
# frames since the object was first seen). TTC is computed from these later.
# The *_method(...) functions below build one such function per setting.

def window_method(w: int):
    """Simplest method: speed = change in distance over the last w frames."""
    def run(frames, readings, sizes):
        at = dict(zip(frames, readings))
        out = []
        for f, z in zip(frames, readings):
            before = at.get(f - w)
            out.append((z, None if before is None else -(z - before) / (w / FPS), f - frames[0]))
        return out
    return run


def kalman_method(accel: float, meas: float, gate: float | None):
    """Distance Kalman filter. Speed is reported only once the filter's own
    speed uncertainty is under `gate` m/s (None = from the 2nd reading)."""
    def run(frames, readings, sizes):
        out, kf, prev, start = [], None, None, None
        for f, z in zip(frames, readings):
            if kf is None or f - prev > MAX_GAP_FRAMES:   # new object, or lost too long: start over
                kf, start = DistanceKalman(accel, meas), f
            else:
                kf.predict((f - prev) / FPS)
            kf.update(z)
            prev = f
            ready = kf.updates >= 2 and (gate is None or kf.speed_sigma <= gate)
            out.append((kf.distance, kf.closing_speed if ready else None, f - start))
        return out
    return run


def looming_method(kind: str, accel: float, meas: float, gate: float | None):
    """Box-growth filter (TTC = 1 / growth rate). A separate distance filter
    runs alongside only to turn TTC into a closing speed (distance x growth)."""
    def run(frames, readings, sizes):
        out, kd, ks, prev, start = [], None, None, None, None
        for f, z, s in zip(frames, readings, sizes):
            if kd is None or f - prev > MAX_GAP_FRAMES:
                kd, ks, start = DistanceKalman(*LOOMING_DISTANCE_FILTER), LogSizeKalman(accel, meas), f
            else:
                kd.predict((f - prev) / FPS)
                ks.predict((f - prev) / FPS)
            kd.update(z)
            if s.get(kind):   # no size this frame (box at the image edge): predict only
                ks.update(math.log(s[kind]))
            prev = f
            closing = None
            if ks.updates >= 2:
                d, g = kd.distance, ks.growth_rate
                if gate is None or d * ks.growth_rate_sigma <= gate:
                    closing = d * g
            out.append((kd.distance, closing, f - start))
        return out
    return run


def fused_method(accel: float, depth_noise: float, size_noise: float, gate: float | None):
    """One filter fed with both the distance and the box height every frame."""
    def run(frames, readings, sizes):
        out, kf, prev, start = [], None, None, None
        for f, z, s in zip(frames, readings, sizes):
            if kf is None or f - prev > MAX_GAP_FRAMES:
                kf, start = FusedKalman(accel, depth_noise, size_noise), f
            else:
                kf.predict((f - prev) / FPS)
            kf.update(z, s.get(FUSED_SIZE_KIND))
            prev = f
            ready = kf.updates >= 2 and (gate is None or kf.closing_sigma <= gate)
            out.append((kf.distance, kf.closing_speed if ready else None, f - start))
        return out
    return run


def all_methods(size_noise: dict) -> dict:
    """Every method x setting listed in CONFIG, by name, e.g. "kalman_a4_r0.015_g1"
    = distance filter, acceleration noise 4, measurement noise 1.5%, gate 1 m/s."""
    methods = {f"window_{w}": window_method(w) for w in WINDOWS}
    for a in ACCEL_NOISES:
        for r in MEAS_NOISES:
            for g in SPEED_GATES:
                methods[f"kalman_a{a:g}_r{r:g}" + ("" if g is None else f"_g{g:g}")] = kalman_method(a, r, g)
    for kind in SIZE_KINDS:
        for a in LOOMING_ACCELS:
            for g in LOOMING_GATES:
                methods[f"looming_{kind}_a{a:g}" + ("" if g is None else f"_g{g:g}")] = \
                    looming_method(kind, a, size_noise[kind]["equivalent_per_reading_noise"], g)
    s_noise = size_noise[FUSED_SIZE_KIND]["equivalent_per_reading_noise"]
    for a in FUSED_ACCELS:
        for d in FUSED_DEPTH_NOISES:
            for g in FUSED_GATES:
                methods[f"fused_a{a:g}_d{d:g}" + ("" if g is None else f"_g{g:g}")] = fused_method(a, d, s_noise, g)
    return methods


def confirmed(frames: list[int], ttc: list[float | None], n: int) -> list[bool]:
    """Warning rule: is the warning on at each frame? On = TTC under WARN_TTC_S
    for the last n frames in a row. n = 1 warns at once; n = 2 or 3 ignores a
    single noisy frame, at the cost of 0.1 or 0.2 s. A missing frame resets it."""
    out, run, prev = [], 0, None
    for f, t in zip(frames, ttc):
        if prev is not None and f - prev != 1:
            run = 0
        run = run + 1 if (t is not None and t < WARN_TTC_S) else 0
        out.append(run >= n)
        prev = f
    return out


def apply(tracks: dict, methods: dict) -> None:
    """Run every method on every real object; store its distance, closing speed,
    TTC and warning state on each frame, under the method's name."""
    for obs in tracks.values():
        frames = [o["frame"] for o in obs]
        readings = [o["measured_m"] for o in obs]
        sizes = [o["sizes"] for o in obs]
        for name, method in methods.items():
            est = method(frames, readings, sizes)
            ttcs = [None if c is None else time_to_collision(d, c) for d, c, _ in est]
            warn = {n: confirmed(frames, ttcs, n) for n in CONFIRM_FRAMES}
            for i, (o, (d, c, age)) in enumerate(zip(obs, est)):
                o[name] = {"distance": d, "closing": c, "age": age, "ttc": ttcs[i],
                           "warn": {n: warn[n][i] for n in CONFIRM_FRAMES}}


def pct(values: list[float], q: float) -> float | None:
    return round(float(np.percentile(values, q)), 3) if values else None


def speed_stats(rows: list[dict], name: str) -> dict:
    err = [abs(o[name]["closing"] - o["true_closing_mps"]) for o in rows]
    return {"rows": len(rows), "speed_error_median_mps": pct(err, 50), "speed_error_p90_mps": pct(err, 90)}


def ttc_stats(rows: list[dict], name: str, all_rows: list[dict]) -> dict:
    """TTC accuracy on the answered rows; phantom warnings on ALL rows of the
    subset (an unanswered reading simply cannot warn)."""
    relevant = [o for o in rows if o["true_ttc_s"] is not None and o["true_ttc_s"] <= TTC_RELEVANT_S]
    rel = [abs(o[name]["ttc"] - o["true_ttc_s"]) / o["true_ttc_s"] if math.isfinite(o[name]["ttc"]) else math.inf
           for o in relevant]
    safe = [o for o in all_rows if o["true_ttc_s"] is not None and o["true_ttc_s"] > SAFE_TTC_S]
    out = {
        "rows_true_ttc_under_10s": len(relevant),
        "objects_true_ttc_under_10s": len({(o["sequence"], o["track_id"]) for o in relevant}),
        "ttc_within_20pct": round(float(np.mean([r <= TTC_TOLERANCE for r in rel])), 4) if rel else None,
        "ttc_rel_error_median": pct([min(r, 10.0) for r in rel], 50),
        "safe_rows": len(safe),
        "phantom": {},
    }
    for n in CONFIRM_FRAMES:
        hit = [o for o in safe if o[name]["warn"][n]]
        out["phantom"][str(n)] = {"share": round(len(hit) / len(safe), 5) if safe else None,
                                  "objects": len({(o["sequence"], o["track_id"]) for o in hit})}
    return out


def score_real(tracks: dict, names: list[str]) -> dict:
    """Part 1: score every method on the real in-path frames, in two groups:
    settled (object seen for 2 s or more) and early (its first 2 s)."""
    rows = [o for obs in tracks.values() for o in obs
            if o["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M and o["true_closing_mps"] is not None]
    longest = f"window_{max(WINDOWS)}"
    settled = [o for o in rows if o[longest]["closing"] is not None]
    early = [o for o in rows if o[names[0]]["age"] < SETTLED_AFTER_FRAMES]
    out = {"rows_in_path_with_true_speed": len(rows), "settled_rows": len(settled), "early_rows": len(early),
           "settled_objects": len({(o["sequence"], o["track_id"]) for o in settled}), "methods": {}}
    for n in names:
        early_ok = [o for o in early if o[n]["closing"] is not None]
        settled_ok = [o for o in settled if o[n]["closing"] is not None]
        out["methods"][n] = {
            "settled": {"answered_share": round(len(settled_ok) / len(settled), 4) if settled else None,
                        **speed_stats(settled_ok, n), **ttc_stats(settled_ok, n, settled)},
            "early": {"answered_share": round(len(early_ok) / len(early), 4) if early else None,
                      **speed_stats(early_ok, n), **ttc_stats(early_ok, n, early)},
        }
    return out


def noise_summary(steps: list[float]) -> dict:
    """Median and p90 of the frame-to-frame error changes, plus the equivalent
    per-reading noise (used as the filters' measurement noise)."""
    steps = np.abs(steps)
    # If each reading had independent noise of size s, the change between two
    # readings would have a median of 0.6745 * sqrt(2) * s.
    return {"error_change_median": round(float(np.median(steps)), 4),
            "error_change_p90": round(float(np.percentile(steps, 90)), 4),
            "equivalent_per_reading_noise": round(float(np.median(steps)) / (0.6745 * math.sqrt(2)), 4),
            "pairs": len(steps)}


def measured_noise(tracks: dict) -> dict:
    """How noisy the readings are, on in-path objects, consecutive frames:
    distance: change of (measured - true) / true;
    size:     change of log(size x true distance), which would be constant
              for a perfect size (size is proportional to 1 / distance)."""
    dist, size, speeds = [], {k: [] for k in SIZE_KINDS}, []
    for obs in tracks.values():
        for a, b in zip(obs, obs[1:]):
            if b["frame"] - a["frame"] != 1 or b["lateral_gap_m"] > CORRIDOR_HALF_WIDTH_M:
                continue
            dist.append(((b["measured_m"] - b["true_m"]) - (a["measured_m"] - a["true_m"])) / b["true_m"])
            for k in SIZE_KINDS:
                sa, sb = a["sizes"][k], b["sizes"][k]
                if sa and sb and a["true_m"] > 1 and b["true_m"] > 1:
                    size[k].append(math.log(sb * b["true_m"]) - math.log(sa * a["true_m"]))
        speeds += [abs(o["true_closing_mps"]) for o in obs
                   if o["true_closing_mps"] is not None and o["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M]
    return {
        "distance": noise_summary(dist),
        "size": {k: noise_summary(v) for k, v in size.items()},
        "true_closing_speed_median_mps": round(float(np.median(speeds)), 3),
        "true_closing_speed_p90_mps": round(float(np.percentile(speeds, 90)), 3),
    }


def real_error_runs(tracks: dict) -> list[dict]:
    """Error sequences along every unbroken stretch of a real track (any lateral
    position): distance error (measured / true - 1) and, per size kind, size
    wobble (size x true distance / its median along the stretch - 1; NaN where
    there is no size reading). Replayed onto the simulated braking car, they
    carry the real errors' size, jumps and slow drift."""
    runs = []
    for obs in tracks.values():
        stretch = []
        for a, b in zip([None] + obs, obs):
            if a is not None and b["frame"] - a["frame"] != 1:
                runs.append(stretch)
                stretch = []
            if b["true_m"] > 1.0:
                stretch.append(b)
        runs.append(stretch)
    out = []
    for stretch in runs:
        if not stretch:
            continue
        run = {"distance": np.array([o["measured_m"] / o["true_m"] - 1.0 for o in stretch])}
        for k in SIZE_KINDS:
            prod = np.array([o["sizes"][k] * o["true_m"] if o["sizes"][k] else np.nan for o in stretch])
            ref = np.nanmedian(prod) if np.isfinite(prod).any() else np.nan
            run[k] = prod / ref - 1.0
        out.append(run)
    return out


def braking_test(methods: dict, noise: dict, error_runs: list[dict], noise_kind: str) -> dict:
    """Part 2: a simulated car ahead brakes; how late does each method warn?

    The truth is exact because it is simulated: the gap stays constant for
    BRAKE_AFTER_S, then shrinks as the car ahead brakes. Noisy readings are
    made from it, either with real error sequences replayed from KITTI
    ("replayed") or with random noise of the measured size ("independent").
    Each noise draw is one simulated run; results are over all draws."""
    rng = np.random.default_rng(SEED)
    out = {}
    for name, gap, decel in SCENARIOS:
        # Gap over time: constant until the brake, then shrinks as 0.5 * decel * t^2.
        t_impact = BRAKE_AFTER_S + math.sqrt(2 * gap / decel)
        frames = list(range(int(t_impact * FPS) + 1))
        t = np.array(frames) / FPS
        tb = np.clip(t - BRAKE_AFTER_S, 0, None)
        true_d = np.maximum(gap - 0.5 * decel * tb ** 2, 0.1)
        true_ttc = np.array([time_to_collision(d, decel * x) for d, x in zip(true_d, tb)])
        t_true_warn = float(t[np.argmax(true_ttc < WARN_TTC_S)])   # when a perfect sensor would warn
        n = len(true_d)
        if noise_kind == "independent":
            draws = [{"distance": noise["distance"]["equivalent_per_reading_noise"] * rng.standard_normal(n),
                      **{k: noise["size"][k]["equivalent_per_reading_noise"] * rng.standard_normal(n)
                         for k in SIZE_KINDS}}
                     for _ in range(NOISE_DRAWS)]
        else:
            # Only pieces with a size reading in every frame, the same pieces for every
            # method: a car straight ahead does not touch the image edge, and a piece
            # without sizes would test the edge rule, not the method.
            draws = [piece for run in error_runs
                     for i in range(0, len(run["distance"]) - n + 1, REPLAY_STEP_FRAMES)
                     for piece in [{k: v[i:i + n] for k, v in run.items()}]
                     if all(np.isfinite(piece[k]).all() for k in SIZE_KINDS)]
        res = {"gap_m": gap, "braking_mps2": decel, "impact_after_brake_s": round(t_impact - BRAKE_AFTER_S, 2),
               "perfect_warning_after_brake_s": round(t_true_warn - BRAKE_AFTER_S, 2),
               "perfect_warning_margin_s": round(t_impact - t_true_warn, 2), "noise": noise_kind,
               "draws": len(draws), "methods": {}}
        # Turn each noise draw into noisy readings: distance = truth x (1 + error),
        # box size = SIM_SIZE_PX_M / true distance x (1 + size wobble).
        sims = []
        for dr in draws:
            z = list(np.maximum(true_d * (1 + dr["distance"]), 0.1))
            sizes = [{k: (None if not np.isfinite(dr[k][i]) else SIM_SIZE_PX_M / true_d[i] * (1 + dr[k][i]))
                      for k in SIZE_KINDS} for i in range(n)]
            sims.append((z, sizes))
        for mname, method in methods.items():
            stats = {c: {"delays": [], "margins": [], "early": 0, "missed": 0} for c in CONFIRM_FRAMES}
            for z, sizes in sims:
                est = method(frames, z, sizes)
                ttc = [None if c is None else time_to_collision(d, c) for d, c, _ in est]
                for c in CONFIRM_FRAMES:
                    warn = np.array(confirmed(frames, ttc, c))
                    s = stats[c]
                    if warn[t < BRAKE_AFTER_S].any():    # warned before the car even braked: false
                        s["early"] += 1
                    after = (t >= BRAKE_AFTER_S) & warn  # the real warning: first one after braking starts
                    if not after.any():
                        s["missed"] += 1
                        continue
                    t_warn = float(t[np.argmax(after)])
                    s["delays"].append(t_warn - t_true_warn)
                    s["margins"].append(t_impact - t_warn)
            res["methods"][mname] = {str(c): {
                "delay_median_s": pct(s["delays"], 50), "delay_p90_s": pct(s["delays"], 90),
                "margin_median_s": pct(s["margins"], 50), "margin_p10_s": pct(s["margins"], 10),
                "false_warning_before_braking_share": round(s["early"] / len(draws), 4),
                "never_warned_share": round(s["missed"] / len(draws), 4),
            } for c, s in stats.items()}
        out[name] = res
    return out


def main() -> None:
    for run_name, folder, column in RUNS:
        tracks = load(folder, column)
        for obs in tracks.values():
            add_truth(obs)
        noise = measured_noise(tracks)
        methods = all_methods(noise["size"])
        names = list(methods)
        apply(tracks, methods)
        error_runs = real_error_runs(tracks)
        results = {
            "benchmark": "kitti_tracking_ttc",
            "provenance": provenance(),
            "dataset": {
                "name": "KITTI Tracking", "source": "https://www.cvlibs.net/datasets/kitti/eval_tracking.php",
                "input": f"{STABILITY.relative_to(REPO).as_posix()}/{folder}/observations.csv, column {column}; "
                         f"sizes from {SIZES.relative_to(REPO).as_posix()}",
                "tracks": len(tracks), "observations": sum(len(o) for o in tracks.values()), "fps": FPS,
                "ground_truth": "laser 3D box labels; closing speed = centred linear fit over "
                                f"+-{TRUTH_HALF_WINDOW / FPS:g} s of the true nearest-surface distance",
            },
            "config": {
                "run_name": run_name, "corridor_half_width_m": CORRIDOR_HALF_WIDTH_M, "windows": WINDOWS,
                "accel_noises": ACCEL_NOISES, "meas_noises": MEAS_NOISES, "speed_gates": SPEED_GATES,
                "size_kinds": SIZE_KINDS, "looming_accels": LOOMING_ACCELS, "looming_gates": LOOMING_GATES,
                "looming_distance_filter": LOOMING_DISTANCE_FILTER, "fused_size_kind": FUSED_SIZE_KIND, "fused_accels": FUSED_ACCELS, "fused_depth_noises": FUSED_DEPTH_NOISES, "fused_gates": FUSED_GATES, "max_gap_frames": MAX_GAP_FRAMES,
                "settled_after_frames": SETTLED_AFTER_FRAMES, "ttc_relevant_s": TTC_RELEVANT_S,
                "ttc_tolerance": TTC_TOLERANCE, "min_true_closing_mps": MIN_TRUE_CLOSING_MPS,
                "warn_ttc_s": WARN_TTC_S, "safe_ttc_s": SAFE_TTC_S, "confirm_frames": CONFIRM_FRAMES,
                "scenarios": SCENARIOS, "brake_after_s": BRAKE_AFTER_S, "sim_size_px_m": SIM_SIZE_PX_M,
                "noise_draws": NOISE_DRAWS, "replay_step_frames": REPLAY_STEP_FRAMES, "seed": SEED,
                "methods": names,
            },
            "input_noise": noise,
            "real": score_real(tracks, names),
            "braking_test": {kind: braking_test(methods, noise, error_runs, kind)
                             for kind in ("replayed", "independent")},
        }
        run_dir = OUT_DIR / run_name
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "results.json").write_text(json.dumps(results, indent=2))
        write_series(run_dir, tracks, names)
        write_report(run_dir)
        print(f"wrote {run_dir}")


def write_series(run_dir: Path, tracks: dict, names: list[str]) -> None:
    base = ["sequence", "track_id", "frame", "class", "lateral_gap_m", "true_m", "measured_m",
            "true_closing_mps", "true_ttc_s"]
    with (run_dir / "series.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(base + [f"size_{k}" for k in SIZE_KINDS]
                   + [f"{m}_{k}" for m in names for k in ("distance", "closing", "ttc")])
        for obs in tracks.values():
            for o in obs:
                w.writerow([o[k] for k in base] + ["" if o["sizes"][k] is None else round(o["sizes"][k], 2)
                                                   for k in SIZE_KINDS] + [
                    "" if o[m][k] is None else round(o[m][k], 3) for m in names for k in ("distance", "closing", "ttc")])


def braking_summary(r: dict, m: str, c: int) -> tuple[float | None, float]:
    """Average warning delay and worst false-warning share over the replayed scenarios."""
    scen = r["braking_test"]["replayed"].values()
    delays = [s["methods"][m][str(c)]["delay_median_s"] for s in scen]
    false = max(s["methods"][m][str(c)]["false_warning_before_braking_share"] for s in scen)
    missed = max(s["methods"][m][str(c)]["never_warned_share"] for s in scen)
    return (None if None in delays else sum(delays) / len(delays)), false, missed


def summary_rows(r: dict, names: list[str], f) -> list[list]:
    rows = []
    for m in names:
        real, early = r["real"]["methods"][m]["settled"], r["real"]["methods"][m]["early"]
        b = {c: braking_summary(r, m, c) for c in CONFIRM_FRAMES}
        avg1, false1, _ = b[1]
        rank = (false1 > 0.05, 1e9 if avg1 is None else avg1)
        rows.append((rank, [
            f"`{m}`", f(real["answered_share"], "pct"), f(real["speed_error_p90_mps"]),
            f(real["ttc_within_20pct"], "pct"), f(early["answered_share"], "pct"),
            *[f(b[c][0]) for c in CONFIRM_FRAMES], *[f(b[c][1], "pct") for c in CONFIRM_FRAMES],
            f(max(b[c][2] for c in CONFIRM_FRAMES), "pct"),
            *[f(real["phantom"][str(c)]["share"], "pct") for c in (CONFIRM_FRAMES[0], CONFIRM_FRAMES[-1])],
        ]))
    return [row for _, row in sorted(rows, key=lambda x: x[0])]


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md entirely from results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov, noise, real = r["config"], r["dataset"], r["provenance"], r["input_noise"], r["real"]
    f = lambda v, k="": "-" if v is None else (f"{v:.1%}" if k == "pct" else f"{v:.2f}")  # noqa: E731
    names = cfg["methods"]
    confirms = cfg["confirm_frames"]
    ranked = sorted(names, key=lambda m: (real["methods"][m]["settled"]["speed_error_p90_mps"] is None,
                                          real["methods"][m]["settled"]["speed_error_p90_mps"] or 0))
    real_rows = []
    for i, m in enumerate(ranked, 1):
        s, e = real["methods"][m]["settled"], real["methods"][m]["early"]
        real_rows.append([i, f"`{m}`", f(s["answered_share"], "pct"), f(s["speed_error_median_mps"]),
                          f(s["speed_error_p90_mps"]), f(s["ttc_within_20pct"], "pct"),
                          f(s["ttc_rel_error_median"], "pct"),
                          *[f"{f(s['phantom'][str(c)]['share'], 'pct')} ({s['phantom'][str(c)]['objects']})"
                            for c in confirms],
                          f(e["answered_share"], "pct"), f(e["speed_error_p90_mps"]),
                          *[f"{f(e['phantom'][str(c)]['share'], 'pct')} ({e['phantom'][str(c)]['objects']})"
                            for c in confirms]])
    any_s = real["methods"][names[0]]["settled"]
    out = [
        f"# Time To Collision benchmark (KITTI tracking): `{cfg['run_name']}`", "",
        "Generated automatically from `results.json` by `benchmark_ttc_kitti.py`. Do not edit by hand.", "",
        "## Setup", "",
        *md_table(["", ""], [
            ["Input", ds["input"]],
            ["Data", f"{ds['observations']} readings of {ds['tracks']} tracked objects, {ds['fps']:.0f} fps"],
            ["Ground truth", ds["ground_truth"]],
            ["In path", f"footprint within {cfg['corridor_half_width_m']} m of our centre line: "
                        f"{real['rows_in_path_with_true_speed']} readings with a true speed"],
            ["Settled", f"{real['settled_rows']} readings of {real['settled_objects']} objects with "
                        f"{cfg['settled_after_frames'] / ds['fps']:g} s of history (where the longest window answers)"],
            ["Early", f"{real['early_rows']} readings in the first {cfg['settled_after_frames'] / ds['fps']:g} s"],
            ["TTC scored", f"true TTC under {cfg['ttc_relevant_s']:g} s, gap shrinking by at least "
                           f"{cfg['min_true_closing_mps']} m/s: {any_s['rows_true_ttc_under_10s']} settled readings of "
                           f"{any_s['objects_true_ttc_under_10s']} objects"],
            ["Warning", f"estimated TTC under {cfg['warn_ttc_s']:g} s for N readings in a row, N = "
                        f"{', '.join(map(str, confirms))}"],
            ["Phantom warning", f"warning active while the true TTC is over {cfg['safe_ttc_s']:g} s (or not "
                                f"closing); {any_s['safe_rows']} settled readings"],
            ["Git commit", f"`{prov['git_commit']}`" + (" (with uncommitted changes)" if prov.get("git_uncommitted_changes") else "")],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## How noisy the input is (in path, consecutive frames)", "",
        "Distance: change of the reading's relative error. Size: change of log(size x true distance),",
        "which is constant for a perfect size. Equivalent noise = the independent per-reading noise",
        "that would give the same median change (used as the filters' measurement noise and in the",
        "independent-noise braking test).", "",
        *md_table(["Measurement", "Change median", "Change p90", "Equivalent noise per reading", "Pairs"],
                  [["Metric3D distance", f(noise["distance"]["error_change_median"], "pct"),
                    f(noise["distance"]["error_change_p90"], "pct"),
                    f(noise["distance"]["equivalent_per_reading_noise"], "pct"), noise["distance"]["pairs"]]]
                  + [[f"Size: {k}", f(v["error_change_median"], "pct"), f(v["error_change_p90"], "pct"),
                      f(v["equivalent_per_reading_noise"], "pct"), v["pairs"]] for k, v in noise["size"].items()]),
        "## Summary: the trade-off per method", "",
        "Real readings (part 1) and the braking test with real errors replayed (part 2, average over",
        "its scenarios). Ranked: false warnings before braking (N = 1, worst scenario) of 5% or less",
        "first, then by average delay (N = 1).", "",
        *md_table(["Method", "Settled: answers", "Settled speed error p90 (m/s)", "TTC within 20%",
                   "Early: answers", *[f"Braking delay N={c} (s)" for c in confirms],
                   *[f"Braking false warning N={c}" for c in confirms], "Braking never warned (worst)",
                   f"Real phantom N={confirms[0]}", f"Real phantom N={confirms[-1]}"],
                  summary_rows(r, names, f)),
        "## Part 1: real readings, ranked by settled speed error p90", "",
        *md_table(["Rank", "Method", "Settled: answers", "Settled speed error median (m/s)", "Settled p90",
                   "TTC within 20%", "TTC median error",
                   *[f"Phantom N={c} (objects)" for c in confirms],
                   "Early: answers", "Early speed error p90",
                   *[f"Early phantom N={c} (objects)" for c in confirms]],
                  real_rows),
    ]
    noise_titles = {"replayed": "real error sequences replayed", "independent": "independent noise"}
    for kind, scenarios in r["braking_test"].items():
        for scen, s in scenarios.items():
            def key(m):
                v = s["methods"][m]["1"]
                return (v["never_warned_share"], v["false_warning_before_braking_share"] > 0.05,
                        1e9 if v["delay_median_s"] is None else v["delay_median_s"])
            out += [f"## Part 2: braking test, {scen}, {noise_titles[kind]}", "",
                    f"Car ahead {s['gap_m']:g} m away at our speed, then brakes at {s['braking_mps2']:g} m/s^2. "
                    f"Impact {s['impact_after_brake_s']} s after it brakes. A perfect sensor warns "
                    f"{s['perfect_warning_after_brake_s']} s after the brake, leaving {s['perfect_warning_margin_s']} s. "
                    f"{s['draws']} noise draws. Ranked (N = 1): never warned, then more than 5% false warnings, "
                    "then delay.", "",
                    *md_table(["Method", *[f"Delay N={c} (s)" for c in confirms],
                               *[f"Time left p10 N={c} (s)" for c in confirms],
                               *[f"False warning N={c}" for c in confirms],
                               *[f"Never warned N={c}" for c in confirms]],
                              [[f"`{m}`", *[f(s["methods"][m][str(c)]["delay_median_s"]) for c in confirms],
                                *[f(s["methods"][m][str(c)]["margin_p10_s"]) for c in confirms],
                                *[f(s["methods"][m][str(c)]["false_warning_before_braking_share"], "pct")
                                  for c in confirms],
                                *[f(s["methods"][m][str(c)]["never_warned_share"], "pct") for c in confirms]]
                               for m in sorted(names, key=key)])]
    out += [
        "## Known limitations", "",
        "- KITTI is calm driving: few objects truly approach fast, so TTC is scored on few objects.",
        "- The true speed comes from laser boxes fitted frame by frame; their own wobble is a floor.",
        "- Objects are followed by their labelled ID, so tracker ID switches are not included.",
        "- Braking test, independent noise: real errors drift slowly and jump now and then, so this",
        "  version is optimistic. The replayed version uses real error sequences, but from calm KITTI",
        "  driving, not from a braking car; size wobble is measured relative to its own median along",
        "  each stretch, so a constant size error (which looming ignores) is removed.",
        "- Daytime only; first 150 frames of each sequence.", "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
