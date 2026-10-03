"""Kalman filter for one tracked object's distance and closing speed.

The camera gives a noisy distance every frame, never a speed. The filter keeps
a best guess of two numbers, distance d (metres) and its rate of change r
(metres per second; negative = the gap is shrinking), and updates it each frame:

    predict:  d <- d + r * dt   (assume the speed stays the same)
    correct:  move the guess towards the new reading, by how much the filter
              trusts the reading compared with its own prediction.

Two settings decide that trust:
    accel_noise   how suddenly the real speed may change (m/s^2): braking,
                  accelerating. Higher = follows changes faster, but noisier.
    meas_noise    how shaky a distance reading is, as a share of the distance
                  (0.02 = 2%). Higher = smoother, but reacts later.

Time To Collision (TTC) = distance / closing speed, if the gap is shrinking:
"if nothing changes, we hit in this many seconds".
"""

from __future__ import annotations

import math

import numpy as np


class DistanceKalman:
    def __init__(self, accel_noise: float, meas_noise: float, initial_speed_sigma: float = 10.0,
                 min_meas_sigma_m: float = 0.05) -> None:
        self.accel_noise = accel_noise
        self.meas_noise = meas_noise
        self.initial_speed_sigma = initial_speed_sigma
        self.min_meas_sigma_m = min_meas_sigma_m
        self.x: np.ndarray | None = None   # [distance, rate]
        self.P: np.ndarray | None = None   # uncertainty of x
        self.updates = 0

    def _meas_var(self, z: float) -> float:
        return max(self.meas_noise * z, self.min_meas_sigma_m) ** 2

    def predict(self, dt: float) -> None:
        if self.x is None:
            return
        F = np.array([[1.0, dt], [0.0, 1.0]])
        q = self.accel_noise ** 2
        Q = q * np.array([[dt ** 4 / 4, dt ** 3 / 2], [dt ** 3 / 2, dt ** 2]])
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def update(self, z: float) -> None:
        if self.x is None:
            self.x = np.array([z, 0.0])
            self.P = np.diag([self._meas_var(z), self.initial_speed_sigma ** 2])
            self.updates = 1
            return
        H = np.array([1.0, 0.0])
        S = H @ self.P @ H + self._meas_var(z)
        K = self.P @ H / S
        self.x = self.x + K * (z - H @ self.x)
        self.P = (np.eye(2) - np.outer(K, H)) @ self.P
        self.updates += 1

    @property
    def distance(self) -> float | None:
        return None if self.x is None else float(self.x[0])

    @property
    def speed_sigma(self) -> float | None:
        """How unsure the filter is about the speed (one standard deviation, m/s)."""
        return None if self.P is None else float(np.sqrt(self.P[1, 1]))

    @property
    def closing_speed(self) -> float | None:
        """Metres per second the gap shrinks by (positive = getting closer)."""
        return None if self.x is None else float(-self.x[1])


class LogSizeKalman(DistanceKalman):
    """Kalman filter on the LOG of an object's image size ("looming").

    An object's image size is proportional to 1 / distance, so the growth rate
    of log(size) is closing speed / distance = 1 / TTC. This needs no distance
    at all, so a depth model's slow drift does not affect it.

    State: [log size, growth rate g (1/s)]. TTC = 1 / g while g > 0.
        accel_noise   how suddenly g may change (1/s^2).
        meas_noise    noise of log(size) per reading (0.011 = 1.1% size wobble).
    """

    def __init__(self, accel_noise: float, meas_noise: float, initial_rate_sigma: float = 1.0) -> None:
        super().__init__(accel_noise, meas_noise, initial_speed_sigma=initial_rate_sigma, min_meas_sigma_m=0.0)

    def _meas_var(self, z: float) -> float:
        return self.meas_noise ** 2

    @property
    def growth_rate(self) -> float | None:
        return None if self.x is None else float(self.x[1])

    @property
    def growth_rate_sigma(self) -> float | None:
        return self.speed_sigma


def time_to_collision(distance: float | None, closing_speed: float | None) -> float:
    """Seconds until contact at constant speed; infinity if not closing."""
    if distance is None or closing_speed is None or closing_speed <= 0:
        return math.inf
    return max(distance, 0.0) / closing_speed
