"""Stage 1 risk label of one 2 s window, decided by WHERE THE WINDOW ENDS (the one rule, shared by training and demos).

BADAS reads the 2 s of video before a moment and answers "is a crash coming?". So every training window is
labelled by its end time t, measured against two Nexar labels of the crash clip:
    alert = the moment a person could first see the danger (median of 10 annotators)
    event = the collision / near-collision itself

The rule for CRASH clips (agreed with the person; "before" = seconds left until the crash = event - t):

    window ends ...                                                       label
    after the crash                                                       never used
    in the clip's first 2 s (no full 2 s of history)                      never used
    before the alert, more than 4 s before the crash                      0 (safe)
    before the alert, 4 s or less before the crash                        not used (maybe slight signs of danger)
    EARLY alert (more than 2.4 s before the crash, also more than 4 s):
        between the alert and 2.4 s before the crash                      ramp: 0.25 at the alert -> 1 at -2.4 s
        in the last 2.4 s                                                 1
    LATE alert (2.4 s or less before the crash):
        less than 0.4 s after the alert                                   not used (window is mostly normal driving)
        0.4 s or more after the alert                                     1

Training draws danger windows only where the label is at least DANGER_MIN_LABEL (0.7): the low start of the ramp
(0.25 to 0.7) is never drawn. A crash clip with no danger window at all (alert less than 0.4 s before the crash, or
a danger zone too short to hold one frame) is not used at all, not even its safe part: crash_clip_used() says so.

Why:
  - A window ending just after the alert still shows mostly normal driving, so it must not get a full 1. For
    early alerts the ramp starts low (0.25) and does that job; for late alerts the label would jump straight to 1,
    so the first 0.4 s after the alert is skipped instead (0.4 s: person, 2026-10-16, was 0.5).
  - Alerts more than 4 s early follow the same ramp from the alert: no window after the alert is ever labelled 0,
    since the danger is already visible (person, 2026-10-16).
  - Safe windows from crash clips must end more than 4 s before the crash: closer than that, the danger may
    already show slightly even before the annotators' alert (person, 2026-10-16).
Normal clips (no crash) are 0 everywhere, except their first 2 s (no full history).
Clips listed in src/risk/data/nexar_excluded.json are never used at all (checked by the sampler, not here).
"""

from __future__ import annotations

# ---- CONFIG ----
WINDOW_S = 2.0          # length of video BADAS reads (16 frames at 8 fps)
FRAME_S = 0.125         # window end points lie on the frame grid (8 fps cache)
HARD_S = 2.4            # label is 1 in the last 2.4 s before the crash
SAFE_BEFORE_S = 4.0     # crash clips: a safe (0) window must end more than this before the crash
VERY_EARLY_S = 4.0      # only names a case for the demos (alerts this early); the label rule does not use it
RAMP_START = 0.25       # early alerts: label at the alert, rising linearly to 1 at HARD_S before the crash
MARGIN_S = 0.4          # late alerts: windows ending less than this after the alert are not used
DANGER_MIN_LABEL = 0.7  # training draws danger windows only where the label is at least this (ramp values below
                        # 0.7 are too close to normal driving to stand for a crash; person, 2026-10-17)
# ----------------

# Zone names (what the demo draws, and what training counts)
ZERO, RAMP, ONE, SKIP, NO_HISTORY, AFTER = "zero", "ramp", "one", "skip", "no_history", "after_crash"


def window_label(t_end: float, alert: float | None = None, event: float | None = None) -> tuple[float | None, str]:
    """Label of the 2 s window ending at t_end (seconds from clip start).

    Returns (label, zone). label is None when the window must not be used for training.
    alert / event are None for normal clips (no crash): then the label is 0.
    """
    if t_end < WINDOW_S:                       # not enough video before t_end to fill a 2 s window
        return None, NO_HISTORY
    if event is None:                          # normal driving clip
        return 0.0, ZERO
    if t_end > event:                          # after the crash: never a training window
        return None, AFTER
    before = event - t_end                     # seconds left until the crash
    if t_end < alert:                          # before the danger was visible ...
        if before <= SAFE_BEFORE_S:            # ... but close to the crash: maybe slight signs already, skip
            return None, SKIP
        return 0.0, ZERO                       # ... and far from the crash: a safe window
    lead = event - alert                       # how early the danger was visible
    if lead > HARD_S:
        # EARLY alert: ramp from RAMP_START at the alert up to 1 at HARD_S before the crash, then 1.
        if before <= HARD_S:
            return 1.0, ONE
        frac = (t_end - alert) / (lead - HARD_S)          # 0 at the alert, 1 at HARD_S before the crash
        return RAMP_START + (1.0 - RAMP_START) * frac, RAMP
    # LATE alert: skip the first MARGIN_S after the alert (mostly normal driving), then 1.
    if t_end < alert + MARGIN_S:
        return None, SKIP
    return 1.0, ONE


def danger_ends(alert: float, event: float) -> list[float]:
    """The danger pool: every window end point (on the frame grid) of a crash clip whose label is at least
    DANGER_MIN_LABEL. Ramp points below it are not drawn at all (neither as danger nor as safe)."""
    n = int(event / FRAME_S + 1e-9)
    return [k * FRAME_S for k in range(n + 1)
            if (window_label(k * FRAME_S, alert, event)[0] or 0.0) >= DANGER_MIN_LABEL]


def crash_clip_used(alert: float, event: float) -> bool:
    """A crash clip is used only if it has at least one danger window; otherwise it is dropped entirely."""
    return bool(danger_ends(alert, event))
