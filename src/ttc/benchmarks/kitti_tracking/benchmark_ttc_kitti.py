"""Benchmark closing speed and Time To Collision (TTC) on KITTI tracking. No GPU.

Question it answers: from the noisy per-frame camera distances, how well can we
estimate each object's CLOSING SPEED (how fast the gap shrinks) and its Time To
Collision (distance / closing speed), and which method does it best?

Input: the saved readings of the distance stability benchmark
(src/distance/benchmarks/kitti_tracking/results/<run>/observations.csv): every
labelled object followed by its labelled ID through the first 150 frames of all
21 KITTI tracking sequences (10 frames per second), with the depth model's
distance and the laser-measured true distance (nearest surface) per frame.

Ground truth:
    true distance        from the laser-measured 3D box labels.
    true closing speed   slope of the true distances, fitted over +-0.5 s around
                         each frame (centred, so it has no delay; this needs
                         future frames, which only an offline truth may use).
    true TTC             true distance / true closing speed.

Methods compared (all causal: they only use the current and past frames):
    window_W           closing speed from two readings W frames apart (W = 1 is raw).
    kalman_a{A}_r{R}   constant-velocity Kalman filter (src/ttc/kalman.py),
                       acceleration noise A m/s^2, measurement noise R (share of
                       the distance). Only the ratio A / R changes the result.

Part 1, real readings (in-path objects, footprint within 1.2 m of our centre line):
    settled          readings 2 s or more after an object is first seen, where
                     EVERY method has an answer, so all are judged on the same rows.
    early            readings in the first 2 s: which methods can answer at all,
                     and how well.
    speed error      |estimated - true closing speed|, m/s, median and p90.
    TTC error        where the true TTC is under 10 s and the gap is shrinking:
                     share within 20% of the true TTC.
    phantom TTC      where the true TTC is over 6 s (or not closing): share of
                     readings whose estimated TTC is under 2.5 s, a typical
                     warning threshold. These would be false warnings.

Part 2, braking test (simulated, so the truth is exact): the car ahead brakes
hard while we keep our speed. Readings get either real error sequences replayed
(Metric3D's actual relative error along unbroken stretches of real KITTI
tracks, with its real jumps and slow drift) or independent random noise of the
size measured in part 1. Per method: how late the warning (estimated TTC under
2.5 s) comes compared with a perfect sensor, how much time is left before
impact, and how often it warns falsely before the braking starts.

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
from src.ttc.kalman import DistanceKalman, time_to_collision  # noqa: E402

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

STABILITY = REPO / "src/distance/benchmarks/kitti_tracking/results"

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

# Kalman settings to compare: acceleration noise (m/s^2) x measurement noise
# (share of the distance; 0.015 is what part 1 measures for Metric3D) x speed
# gate: the filter outputs a speed only once its own speed uncertainty (one
# standard deviation) is below this many m/s (None = from the 2nd reading).
ACCEL_NOISES = [0.5, 1.0, 2.0, 4.0, 8.0]
MEAS_NOISES = [0.015]
SPEED_GATES = [None, 1.5, 1.0, 0.5]

# A track unseen for more than this many frames is restarted.
MAX_GAP_FRAMES = 5

# "Settled" = at least this many frames since first seen (the longest window,
# so every method has an answer there).
SETTLED_AFTER_FRAMES = max(WINDOWS)

# TTC scoring.
TTC_RELEVANT_S = 10.0       # score TTC error where the true TTC is below this
TTC_TOLERANCE = 0.20
MIN_TRUE_CLOSING_MPS = 0.5  # below this the true TTC is not meaningful
WARN_TTC_S = 2.5            # typical forward collision warning threshold
SAFE_TTC_S = 6.0            # true TTC above this: a warning would be false

# Braking test: (name, starting gap m, braking of the car ahead m/s^2). We keep
# our speed; the car ahead drives at our speed for BRAKE_AFTER_S, then brakes.
SCENARIOS = [
    ("hard braking, 30 m", 30.0, 6.0),
    ("moderate braking, 30 m", 30.0, 3.0),
    ("hard braking, 15 m", 15.0, 6.0),
]
BRAKE_AFTER_S = 4.0
NOISE_DRAWS = 300
# Replayed errors: pieces start every this many frames along each real stretch
# (pieces overlap, so draws are not independent; more of them cover more cases).
REPLAY_STEP_FRAMES = 10
SEED = 0

OUT_DIR = Path(__file__).resolve().parent / "results"

# ----------------------------------------------------------------------------


def load(run_folder: str, column: str) -> dict[tuple, list[dict]]:
    """Observations per track, in frame order, with the chosen distance column."""
    tracks = defaultdict(list)
    with (STABILITY / run_folder / "observations.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r[column] in ("", "None"):
                continue
            tracks[(r["sequence"], int(r["track_id"]))].append({
                "sequence": r["sequence"], "track_id": int(r["track_id"]), "frame": int(r["frame"]),
                "class": r["class"], "lateral_gap_m": float(r["lateral_gap_m"]),
                "true_m": float(r["true_nearest_surface_m"]), "measured_m": float(r[column]),
            })
    for obs in tracks.values():
        obs.sort(key=lambda o: o["frame"])
    return tracks


def add_truth(obs: list[dict]) -> None:
    """True closing speed: centred linear fit of the true distance over +-0.5 s."""
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


# ---- methods: each takes (frames, readings) of one track, returns per reading
# ---- (distance, closing speed or None, frames since the track started)

def window_method(w: int):
    def run(frames, readings):
        at = dict(zip(frames, readings))
        out = []
        for f, z in zip(frames, readings):
            before = at.get(f - w)
            out.append((z, None if before is None else -(z - before) / (w / FPS), f - frames[0]))
        return out
    return run


def kalman_method(accel: float, meas: float, gate: float | None):
    def run(frames, readings):
        out, kf, prev, start = [], None, None, None
        for f, z in zip(frames, readings):
            if kf is None or f - prev > MAX_GAP_FRAMES:
                kf, start = DistanceKalman(accel, meas), f
            else:
                kf.predict((f - prev) / FPS)
            kf.update(z)
            prev = f
            ready = kf.updates >= 2 and (gate is None or kf.speed_sigma <= gate)
            out.append((kf.distance, kf.closing_speed if ready else None, f - start))
        return out
    return run


def all_methods() -> dict:
    methods = {f"window_{w}": window_method(w) for w in WINDOWS}
    for a in ACCEL_NOISES:
        for r in MEAS_NOISES:
            for g in SPEED_GATES:
                methods[f"kalman_a{a:g}_r{r:g}" + ("" if g is None else f"_g{g:g}")] = kalman_method(a, r, g)
    return methods


def apply(tracks: dict, methods: dict) -> None:
    for obs in tracks.values():
        frames = [o["frame"] for o in obs]
        readings = [o["measured_m"] for o in obs]
        for name, method in methods.items():
            for o, (d, c, age) in zip(obs, method(frames, readings)):
                o[name] = {"distance": d, "closing": c, "age": age,
                           "ttc": None if c is None else time_to_collision(d, c)}


def pct(values: list[float], q: float) -> float | None:
    return round(float(np.percentile(values, q)), 3) if values else None


def speed_stats(rows: list[dict], name: str) -> dict:
    err = [abs(o[name]["closing"] - o["true_closing_mps"]) for o in rows]
    return {"rows": len(rows), "speed_error_median_mps": pct(err, 50), "speed_error_p90_mps": pct(err, 90)}


def ttc_stats(rows: list[dict], name: str) -> dict:
    relevant = [o for o in rows if o["true_ttc_s"] is not None and o["true_ttc_s"] <= TTC_RELEVANT_S]
    rel = [abs(o[name]["ttc"] - o["true_ttc_s"]) / o["true_ttc_s"] if math.isfinite(o[name]["ttc"]) else math.inf
           for o in relevant]
    safe = [o for o in rows if o["true_ttc_s"] is not None and o["true_ttc_s"] > SAFE_TTC_S]
    phantom = [o for o in safe if o[name]["ttc"] < WARN_TTC_S]
    return {
        "rows_true_ttc_under_10s": len(relevant),
        "objects_true_ttc_under_10s": len({(o["sequence"], o["track_id"]) for o in relevant}),
        "ttc_within_20pct": round(float(np.mean([r <= TTC_TOLERANCE for r in rel])), 4) if rel else None,
        "ttc_rel_error_median": pct([min(r, 10.0) for r in rel], 50),
        "safe_rows": len(safe),
        "phantom_warning_share": round(len(phantom) / len(safe), 5) if safe else None,
        "phantom_warning_objects": len({(o["sequence"], o["track_id"]) for o in phantom}),
    }


def score_real(tracks: dict, names: list[str]) -> dict:
    rows = [o for obs in tracks.values() for o in obs
            if o["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M and o["true_closing_mps"] is not None]
    # Settled rows: where the longest window answers (2 s of history). Each method
    # is scored on the settled rows it answers; a gated filter may skip some.
    longest = f"window_{max(WINDOWS)}"
    settled = [o for o in rows if o[longest]["closing"] is not None]
    early = [o for o in rows if o[names[0]]["age"] < SETTLED_AFTER_FRAMES]
    out = {"rows_in_path_with_true_speed": len(rows), "settled_rows": len(settled), "early_rows": len(early),
           "settled_objects": len({(o["sequence"], o["track_id"]) for o in settled}), "methods": {}}
    for n in names:
        early_ok = [o for o in early if o[n]["closing"] is not None]
        settled_ok = [o for o in settled if o[n]["closing"] is not None]
        dist = [o for o in settled if o["true_m"] > 0]
        out["methods"][n] = {
            "settled": {"answered_share": round(len(settled_ok) / len(settled), 4) if settled else None,
                        **speed_stats(settled_ok, n), **ttc_stats(settled_ok, n),
                        "distance_within_10pct": round(float(np.mean(
                            [abs(o[n]["distance"] - o["true_m"]) <= 0.1 * o["true_m"] for o in dist])), 4)},
            "early": {"answered_share": round(len(early_ok) / len(early), 4) if early else None,
                      **speed_stats(early_ok, n), **ttc_stats(early_ok, n)},
        }
    return out


def measured_noise(tracks: dict) -> dict:
    """How noisy the readings are: change of the reading's error between frames."""
    steps, speeds = [], []
    for obs in tracks.values():
        for a, b in zip(obs, obs[1:]):
            if b["frame"] - a["frame"] == 1 and b["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M:
                steps.append(((b["measured_m"] - b["true_m"]) - (a["measured_m"] - a["true_m"])) / b["true_m"])
        speeds += [abs(o["true_closing_mps"]) for o in obs
                   if o["true_closing_mps"] is not None and o["lateral_gap_m"] <= CORRIDOR_HALF_WIDTH_M]
    steps = np.abs(steps)
    # If each reading had independent noise of size s, the change between two
    # readings would have a median of 0.6745 * sqrt(2) * s.
    sigma = float(np.median(steps)) / (0.6745 * math.sqrt(2))
    return {
        "error_change_median": round(float(np.median(steps)), 4),
        "error_change_p90": round(float(np.percentile(steps, 90)), 4),
        "equivalent_per_reading_noise": round(sigma, 4),
        "true_closing_speed_median_mps": round(float(np.median(speeds)), 3),
        "true_closing_speed_p90_mps": round(float(np.percentile(speeds, 90)), 3),
    }


def real_error_runs(tracks: dict) -> list[np.ndarray]:
    """Relative errors (measured / true - 1) along every unbroken run of a real
    track, any lateral position. Replayed onto the simulated braking car, they
    carry the real error's size, jumps and slow drift."""
    runs = []
    for obs in tracks.values():
        cur = []
        for a, b in zip([None] + obs, obs):
            if a is not None and b["frame"] - a["frame"] != 1:
                runs.append(np.array(cur))
                cur = []
            if b["true_m"] > 1.0:
                cur.append(b["measured_m"] / b["true_m"] - 1.0)
        runs.append(np.array(cur))
    return [r for r in runs if len(r) > 0]


def braking_test(methods: dict, sigma: float, error_runs: list[np.ndarray], noise_kind: str) -> dict:
    """Simulated braking of the car ahead, with independent noise of the
    measured size ("independent"), or with real error sequences replayed
    ("replayed": every unbroken real stretch long enough, cut into pieces)."""
    rng = np.random.default_rng(SEED)
    out = {}
    for name, gap, decel in SCENARIOS:
        # Gap over time: constant until the brake, then shrinks as 0.5 * decel * t^2.
        t_impact = BRAKE_AFTER_S + math.sqrt(2 * gap / decel)
        frames = list(range(int(t_impact * FPS) + 1))
        t = np.array(frames) / FPS
        tb = np.clip(t - BRAKE_AFTER_S, 0, None)
        true_d = gap - 0.5 * decel * tb ** 2
        true_ttc = np.array([time_to_collision(d, decel * x) for d, x in zip(true_d, tb)])
        t_true_warn = float(t[np.argmax(true_ttc < WARN_TTC_S)])
        n = len(true_d)
        if noise_kind == "independent":
            draws = [sigma * rng.standard_normal(n) for _ in range(NOISE_DRAWS)]
        else:
            draws = [run[i:i + n] for run in error_runs for i in range(0, len(run) - n + 1, REPLAY_STEP_FRAMES)]
        res = {"gap_m": gap, "braking_mps2": decel, "impact_after_brake_s": round(t_impact - BRAKE_AFTER_S, 2),
               "perfect_warning_after_brake_s": round(t_true_warn - BRAKE_AFTER_S, 2),
               "perfect_warning_margin_s": round(t_impact - t_true_warn, 2), "noise": noise_kind,
               "draws": len(draws), "methods": {}}
        for mname, method in methods.items():
            delays, margins, early, missed = [], [], 0, 0
            for noise in draws:
                z = true_d * (1 + noise)
                est = method(frames, list(np.maximum(z, 0.1)))
                ttc = np.array([math.inf if c is None else time_to_collision(d, c) for d, c, _ in est])
                if (ttc[t < BRAKE_AFTER_S] < WARN_TTC_S).any():
                    early += 1
                after = (t >= BRAKE_AFTER_S) & (ttc < WARN_TTC_S)
                if not after.any():
                    missed += 1
                    continue
                t_warn = float(t[np.argmax(after)])
                delays.append(t_warn - t_true_warn)
                margins.append(t_impact - t_warn)
            res["methods"][mname] = {
                "delay_median_s": pct(delays, 50), "delay_p90_s": pct(delays, 90),
                "margin_median_s": pct(margins, 50), "margin_p10_s": pct(margins, 10),
                "false_warning_before_braking_share": round(early / len(draws), 4),
                "never_warned_share": round(missed / len(draws), 4),
            }
        out[name] = res
    return out


def main() -> None:
    methods = all_methods()
    names = list(methods)
    for run_name, folder, column in RUNS:
        tracks = load(folder, column)
        for obs in tracks.values():
            add_truth(obs)
        apply(tracks, methods)
        noise = measured_noise(tracks)
        results = {
            "benchmark": "kitti_tracking_ttc",
            "provenance": provenance(),
            "dataset": {
                "name": "KITTI Tracking", "source": "https://www.cvlibs.net/datasets/kitti/eval_tracking.php",
                "input": f"{STABILITY.relative_to(REPO).as_posix()}/{folder}/observations.csv, column {column}",
                "tracks": len(tracks), "observations": sum(len(o) for o in tracks.values()), "fps": FPS,
                "ground_truth": "laser 3D box labels; closing speed = centred linear fit over "
                                f"+-{TRUTH_HALF_WINDOW / FPS:g} s of the true nearest-surface distance",
            },
            "config": {
                "run_name": run_name, "corridor_half_width_m": CORRIDOR_HALF_WIDTH_M, "windows": WINDOWS,
                "accel_noises": ACCEL_NOISES, "meas_noises": MEAS_NOISES, "max_gap_frames": MAX_GAP_FRAMES,
                "settled_after_frames": SETTLED_AFTER_FRAMES, "ttc_relevant_s": TTC_RELEVANT_S,
                "ttc_tolerance": TTC_TOLERANCE, "min_true_closing_mps": MIN_TRUE_CLOSING_MPS,
                "warn_ttc_s": WARN_TTC_S, "safe_ttc_s": SAFE_TTC_S, "methods": names,
                "scenarios": SCENARIOS, "brake_after_s": BRAKE_AFTER_S, "noise_draws": NOISE_DRAWS, "seed": SEED,
                "speed_gates": SPEED_GATES, "replay_step_frames": REPLAY_STEP_FRAMES,
            },
            "input_noise": noise,
            "real": score_real(tracks, names),
            "braking_test": {
                kind: braking_test(methods, noise["equivalent_per_reading_noise"], real_error_runs(tracks), kind)
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
        w.writerow(base + [f"{m}_{k}" for m in names for k in ("distance", "closing", "ttc")])
        for obs in tracks.values():
            for o in obs:
                w.writerow([o[k] for k in base] + [
                    "" if o[m][k] is None else round(o[m][k], 3) for m in names for k in ("distance", "closing", "ttc")])


def summary_rows(r: dict, names: list[str], f) -> list[list]:
    replay = r["braking_test"]["replayed"]
    rows = []
    for m in names:
        delays = [s["methods"][m]["delay_median_s"] for s in replay.values()]
        false = max(s["methods"][m]["false_warning_before_braking_share"] for s in replay.values())
        avg = None if None in delays else sum(delays) / len(delays)
        real, early = r["real"]["methods"][m]["settled"], r["real"]["methods"][m]["early"]
        rows.append(((false > 0.05, 1e9 if avg is None else avg), [
            f"`{m}`", f(real["answered_share"], "pct"), f(real["speed_error_p90_mps"]),
            f(early["answered_share"], "pct"),
            f(early["phantom_warning_share"], "pct"), f(avg), f(false, "pct")]))
    return [row for _, row in sorted(rows, key=lambda x: x[0])]


def write_report(run_dir: Path) -> None:
    """Generate RESULTS.md entirely from results.json."""
    r = json.loads((run_dir / "results.json").read_text())
    cfg, ds, prov, noise, real = r["config"], r["dataset"], r["provenance"], r["input_noise"], r["real"]
    f = lambda v, k="": "-" if v is None else (f"{v:.1%}" if k == "pct" else f"{v:.2f}")  # noqa: E731
    names = cfg["methods"]
    ranked = sorted(names, key=lambda m: real["methods"][m]["settled"]["speed_error_p90_mps"] or 1e9)
    real_rows = []
    for i, m in enumerate(ranked, 1):
        s, e = real["methods"][m]["settled"], real["methods"][m]["early"]
        real_rows.append([i, f"`{m}`", f(s["speed_error_median_mps"]), f(s["speed_error_p90_mps"]),
                          f(s["ttc_within_20pct"], "pct"), f(s["ttc_rel_error_median"], "pct"),
                          f"{f(s['phantom_warning_share'], 'pct')} ({s['phantom_warning_objects']})",
                          f(e["answered_share"], "pct"), f(e["speed_error_median_mps"]), f(e["speed_error_p90_mps"]),
                          f"{f(e['phantom_warning_share'], 'pct')} ({e['phantom_warning_objects']})"])
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
            ["Phantom warning", f"true TTC over {cfg['safe_ttc_s']:g} s (or not closing) but estimated under "
                                f"{cfg['warn_ttc_s']:g} s; {any_s['safe_rows']} settled readings"],
            ["Git commit", f"`{prov['git_commit']}`" + (" (with uncommitted changes)" if prov.get("git_uncommitted_changes") else "")],
            ["Created (UTC)", prov["created_utc"]],
        ]),
        "## How noisy the input is (in path)", "",
        *md_table(["", ""], [
            ["Change of the reading's error between consecutive frames, median / p90",
             f"{f(noise['error_change_median'], 'pct')} / {f(noise['error_change_p90'], 'pct')}"],
            ["Equivalent independent noise per reading (used in the braking test)",
             f(noise["equivalent_per_reading_noise"], "pct")],
            ["True closing speed (absolute), median / p90 (m/s)",
             f"{f(noise['true_closing_speed_median_mps'])} / {f(noise['true_closing_speed_p90_mps'])}"],
        ]),
        "## Summary: the trade-off per method", "",
        "Real readings (part 1) and the braking test with real errors replayed (part 2, all scenarios).",
        "Ranked: false warnings before braking (worst scenario) of 5% or less first, then by average delay.", "",
        *md_table(["Method", "Settled: answers", "Settled speed error p90 (m/s)", "Early: answers",
                   "Early phantom warnings",
                   "Braking: average warning delay (s)", "Braking: false warning, worst scenario"],
                  summary_rows(r, names, f)),
        "## Part 1: real readings, ranked by settled speed error p90", "",
        *md_table(["Rank", "Method", "Settled speed error median (m/s)", "Settled p90", "TTC within 20%",
                   "TTC median error", "Phantom warnings (objects)", "Early: answers", "Early median", "Early p90",
                   "Early phantom warnings (objects)"],
                  real_rows),
    ]
    noise_titles = {"replayed": "real error sequences replayed", "independent": "independent noise"}
    for kind, scenarios in r["braking_test"].items():
        for scen, s in scenarios.items():
            rows = sorted(names, key=lambda m: (
                s["methods"][m]["never_warned_share"],
                s["methods"][m]["false_warning_before_braking_share"] > 0.05,
                1e9 if s["methods"][m]["delay_median_s"] is None else s["methods"][m]["delay_median_s"]))
            out += [f"## Part 2: braking test, {scen}, {noise_titles[kind]}", "",
                    f"Car ahead {s['gap_m']:g} m away at our speed, then brakes at {s['braking_mps2']:g} m/s^2. "
                    f"Impact {s['impact_after_brake_s']} s after it brakes. A perfect sensor warns "
                    f"{s['perfect_warning_after_brake_s']} s after the brake, leaving {s['perfect_warning_margin_s']} s. "
                    f"{s['draws']} noise draws. Ranked: never warned, then more than 5% false warnings, then delay.", "",
                *md_table(["Method", "Warning delay median (s)", "Delay p90 (s)", "Time left median (s)",
                           "Time left p10 (s)", "False warning before braking", "Never warned"],
                          [[f"`{m}`", f(v["delay_median_s"]), f(v["delay_p90_s"]), f(v["margin_median_s"]),
                            f(v["margin_p10_s"]), f(v["false_warning_before_braking_share"], "pct"),
                            f(v["never_warned_share"], "pct")]
                           for m in rows for v in [s["methods"][m]]])]
    out += [
        "## Known limitations", "",
        "- KITTI is calm driving: few objects truly approach fast, so TTC is scored on few objects.",
        "- The true speed comes from laser boxes fitted frame by frame; their own wobble is a floor.",
        "- Objects are followed by their labelled ID, so tracker ID switches are not included.",
        "- Braking test, independent noise: real depth errors drift slowly and jump now and then, so",
        "  this version is optimistic. The replayed version uses real error sequences, but from calm",
        "  KITTI driving, not from a braking car.",
        "- Daytime only; first 150 frames of each sequence.", "",
    ]
    (run_dir / "RESULTS.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
