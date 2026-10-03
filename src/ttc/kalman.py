"""Filters that turn noisy per-frame camera readings into closing speed and
Time To Collision (TTC) for ONE tracked object.

Why a filter: the camera gives a distance (and a box size) every frame, but
never a speed. Speed from two raw readings is far too noisy, because each
reading wobbles a little. A Kalman filter keeps a best guess and, every frame:
    1. predict:  "if the speed stays the same, where is the object now?"
    2. correct:  move the guess part of the way towards the new reading.
How far it moves depends on how much it trusts the reading vs its prediction.

Words used below:
    closing speed   metres per second the gap to the object shrinks
                    (positive = getting closer).
    TTC             seconds until contact if nothing changes:
                    distance / closing speed.
    sigma           the filter's own uncertainty (one standard deviation).

Three filters:
    DistanceKalman  fed with the depth model's distance.
    LogSizeKalman   fed with the box size; TTC from how fast the box grows.
    FusedKalman     fed with both.
"""

from __future__ import annotations

import math

import numpy as np


class DistanceKalman:
    """Filter on the distance. Keeps 2 numbers: distance d (m) and its rate of
    change r (m/s, negative = gap shrinking).

    Settings:
        accel_noise   how suddenly the real speed may change (m/s^2), e.g. hard
                      braking. Higher = reacts faster, but jumpier.
        meas_noise    how much a distance reading wobbles, as a share of the
                      distance (0.015 = 1.5%). Higher = smoother, but slower.
    """

    def __init__(self, accel_noise: float, meas_noise: float, initial_speed_sigma: float = 10.0,
                 min_meas_sigma_m: float = 0.05) -> None:
        self.accel_noise = accel_noise
        self.meas_noise = meas_noise
        self.initial_speed_sigma = initial_speed_sigma  # speed unknown at first: large uncertainty
        self.min_meas_sigma_m = min_meas_sigma_m        # never trust a reading more than +-5 cm
        self.x: np.ndarray | None = None   # the best guess: [distance, rate]
        self.P: np.ndarray | None = None   # how unsure the guess is (2x2 covariance)
        self.updates = 0                   # readings used so far

    def _meas_var(self, z: float) -> float:
        """Expected wobble of a reading at distance z (squared)."""
        return max(self.meas_noise * z, self.min_meas_sigma_m) ** 2

    def predict(self, dt: float) -> None:
        """Step 1: move the guess dt seconds forward at constant speed, and grow
        the uncertainty (the speed may have changed meanwhile)."""
        if self.x is None:
            return
        F = np.array([[1.0, dt], [0.0, 1.0]])   # distance += rate * dt; rate unchanged
        q = self.accel_noise ** 2
        Q = q * np.array([[dt ** 4 / 4, dt ** 3 / 2], [dt ** 3 / 2, dt ** 2]])  # uncertainty added
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def update(self, z: float) -> None:
        """Step 2: correct the guess with a new distance reading z (metres)."""
        if self.x is None:   # first reading: start here, speed unknown
            self.x = np.array([z, 0.0])
            self.P = np.diag([self._meas_var(z), self.initial_speed_sigma ** 2])
            self.updates = 1
            return
        H = np.array([1.0, 0.0])                  # a reading measures the distance only
        S = H @ self.P @ H + self._meas_var(z)    # total uncertainty of (reading - guess)
        K = self.P @ H / S                        # how far to move towards the reading
        self.x = self.x + K * (z - H @ self.x)
        self.P = (np.eye(2) - np.outer(K, H)) @ self.P
        self.updates += 1

    @property
    def distance(self) -> float | None:
        return None if self.x is None else float(self.x[0])

    @property
    def speed_sigma(self) -> float | None:
        """How unsure the filter is about the speed (m/s). Used as a gate: only
        trust its speed once this is small."""
        return None if self.P is None else float(np.sqrt(self.P[1, 1]))

    @property
    def closing_speed(self) -> float | None:
        """Metres per second the gap shrinks by (positive = getting closer)."""
        return None if self.x is None else float(-self.x[1])


class LogSizeKalman(DistanceKalman):
    """Filter on the box size ("looming"): TTC without any distance.

    An object twice as close looks twice as big, so its box grows as it
    approaches. The growth rate of log(size) equals 1 / TTC: a box growing 25%
    per second means about 4 s to contact. A depth model's slow drift does not
    affect it, because it never uses the distance.

    Same filter as DistanceKalman, fed with log(size) instead of distance.
    Keeps 2 numbers: log(size) and its growth rate g (1/s). TTC = 1 / g.
    Settings:
        accel_noise   how suddenly g may change (1/s^2).
        meas_noise    wobble of the size per reading (0.011 = 1.1%).
    """

    def __init__(self, accel_noise: float, meas_noise: float, initial_rate_sigma: float = 1.0) -> None:
        super().__init__(accel_noise, meas_noise, initial_speed_sigma=initial_rate_sigma, min_meas_sigma_m=0.0)

    def _meas_var(self, z: float) -> float:
        # In log space a 1.1% wobble is the same for big and small boxes.
        return self.meas_noise ** 2

    @property
    def growth_rate(self) -> float | None:
        """1 / TTC, per second (positive = getting closer)."""
        return None if self.x is None else float(self.x[1])

    @property
    def growth_rate_sigma(self) -> float | None:
        return self.speed_sigma


class FusedKalman:
    """One filter fed with BOTH the distance and the box size.

    The distance tells HOW FAR the object is; the box growth tells HOW FAST it
    approaches, without the depth model's drift. Each covers the other's weakness.

    Keeps 3 numbers, all in log space (where both readings become simple sums):
        log d   log of the distance
        u       rate of change of log d, per second (-u = 1 / TTC)
        log K   the object's "size factor": box size = K / distance, so K is
                fixed for one object (a truck has a bigger K than a car). It is
                unknown at first and learned from the two readings together.
    Each reading as the filter sees it:
        log(distance reading) = log d          + depth wobble
        log(box size)         = log K - log d  + size wobble

    Settings:
        accel_noise        how suddenly u may change (1/s^2).
        depth_noise        distance wobble per reading (0.015 = 1.5%). Raising it
                           trusts the distance less for motion (less drift, but
                           the box size alone must show the approach).
        size_noise         box size wobble per reading.
        size_factor_drift  how much log K may wander per second (a box partly
                           hidden, the object turning); small.
    """

    def __init__(self, accel_noise: float, depth_noise: float, size_noise: float,
                 size_factor_drift: float = 0.02, initial_rate_sigma: float = 1.0) -> None:
        self.accel_noise = accel_noise
        self.depth_noise = depth_noise
        self.size_noise = size_noise
        self.size_factor_drift = size_factor_drift
        self.initial_rate_sigma = initial_rate_sigma
        self.x: np.ndarray | None = None   # the best guess: [log d, u, log K]
        self.P: np.ndarray | None = None   # how unsure the guess is (3x3 covariance)
        self.updates = 0                   # frames used so far
        self.size_updates = 0              # frames that had a box size

    def predict(self, dt: float) -> None:
        """Step 1: move dt seconds forward at constant u; K stays the same."""
        if self.x is None:
            return
        F = np.array([[1.0, dt, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        q = self.accel_noise ** 2
        Q = np.zeros((3, 3))
        Q[:2, :2] = q * np.array([[dt ** 4 / 4, dt ** 3 / 2], [dt ** 3 / 2, dt ** 2]])
        Q[2, 2] = self.size_factor_drift ** 2 * dt
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def _update(self, H: np.ndarray, z: float, var: float) -> None:
        """Correct the guess with one reading z; H says which mix of the 3
        numbers that reading measures, var how much it wobbles (squared)."""
        S = H @ self.P @ H + var
        K = self.P @ H / S
        self.x = self.x + K * (z - H @ self.x)
        self.P = (np.eye(3) - np.outer(K, H)) @ self.P

    def update(self, distance: float | None, size: float | None) -> None:
        """Step 2: correct with this frame's distance (m) and box size (px).
        Either may be missing (None), e.g. no size when the box touches the
        image edge."""
        if self.x is None:   # first frame: start from the readings, speed unknown
            if distance is None:
                return
            log_k = math.log(size) + math.log(distance) if size else 0.0
            self.x = np.array([math.log(distance), 0.0, log_k])
            self.P = np.diag([self.depth_noise ** 2, self.initial_rate_sigma ** 2,
                              (self.depth_noise ** 2 + self.size_noise ** 2) if size else 100.0])
            self.updates, self.size_updates = 1, int(bool(size))
            return
        if distance is not None:   # the distance reading measures log d
            self._update(np.array([1.0, 0.0, 0.0]), math.log(distance), self.depth_noise ** 2)
        if size:                   # the box size measures log K - log d
            self._update(np.array([-1.0, 0.0, 1.0]), math.log(size), self.size_noise ** 2)
            self.size_updates += 1
        self.updates += 1

    @property
    def distance(self) -> float | None:
        return None if self.x is None else float(math.exp(self.x[0]))

    @property
    def closing_speed(self) -> float | None:
        """Metres per second the gap shrinks by: -distance * u."""
        return None if self.x is None else float(-math.exp(self.x[0]) * self.x[1])

    @property
    def closing_sigma(self) -> float | None:
        """How unsure the closing speed is (m/s). Used as a gate."""
        return None if self.x is None else float(math.exp(self.x[0]) * math.sqrt(self.P[1, 1]))


def time_to_collision(distance: float | None, closing_speed: float | None) -> float:
    """Seconds until contact if the speed stays the same; infinity if the gap is
    not shrinking. Example: 20 m at 5 m/s closing = 4 s."""
    if distance is None or closing_speed is None or closing_speed <= 0:
        return math.inf
    return max(distance, 0.0) / closing_speed
