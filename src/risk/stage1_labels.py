"""Stage 1 risk label of one 2 s window, decided by WHERE THE WINDOW ENDS (the one rule, shared by training and demos).

BADAS reads the 2 s of video before a moment and answers "is a crash coming?". So every training window is
labelled by its end time t, measured against two Nexar labels of the crash clip:
    alert = the moment a person could first see the danger (median of 10 annotators)
    event = the collision / near-collision itself

The rule (agreed with the person; times as "seconds before the crash" = event - t):

    window ends ...                                                       label
    after the crash                                                       never used
    in the clip's first 2 s (no full 2 s of history)                      never used
    before the alert                                                      0
    EARLY alert (more than 2.4 s before the crash, also more than 4 s):
        between the alert and 2.4 s before the crash                      ramp: 0.25 at the alert -> 1 at -2.4 s
        in the last 2.4 s                                                 1
    LATE alert (2.4 s or less before the crash):
        less than 0.5 s after the alert                                   not used (window is mostly normal driving)
        0.5 s or more after the alert                                     1

Why: a window ending just after the alert still shows mostly normal driving, so it must not get a full 1.
For early alerts the ramp starts low (0.25) and does that job; for late alerts the label would jump straight to 1,
so the first 0.5 s after the alert is skipped instead. Alerts more than 4 s early follow the same ramp from the
alert (decided 2026-10-16: no window after the alert is ever labelled 0, since the danger is already visible).
Alerts less than 0.5 s before the crash give no danger windows (alert + 0.5 s is after the crash).
Normal clips (no crash) are 0 everywhere, except their first 2 s (no full history).
Clips listed in src/risk/data/nexar_excluded.json are never used at all (checked by the sampler, not here).
"""

from __future__ import annotations

# ---- CONFIG ----
WINDOW_S = 2.0          # length of video BADAS reads (16 frames at 8 fps)
HARD_S = 2.4            # label is 1 in the last 2.4 s before the crash
VERY_EARLY_S = 4.0      # only names a case for the demos (alerts this early); the label rule does not use it
RAMP_START = 0.25       # early alerts: label at the alert, rising linearly to 1 at HARD_S before the crash
MARGIN_S = 0.5          # late alerts: windows ending less than this after the alert are not used
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
    if t_end < alert:                          # before the danger was visible
        return 0.0, ZERO
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
