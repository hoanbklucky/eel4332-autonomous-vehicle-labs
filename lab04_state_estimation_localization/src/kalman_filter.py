"""Minimal linear Kalman-filter starter for EEL 4332."""

from __future__ import annotations
import numpy as np


class LinearKalmanFilter:
    def __init__(self, x, P, F, H, Q, R):
        self.x = np.asarray(x, dtype=float)
        self.P = np.asarray(P, dtype=float)
        self.F = np.asarray(F, dtype=float)
        self.H = np.asarray(H, dtype=float)
        self.Q = np.asarray(Q, dtype=float)
        self.R = np.asarray(R, dtype=float)

    def predict(self):
        """Perform the linear Kalman prediction step."""
        # TODO: update self.x and self.P.
        raise NotImplementedError

    def update(self, z):
        """Perform the linear Kalman correction step."""
        # TODO: innovation, innovation covariance, Kalman gain,
        # state correction, covariance correction.
        raise NotImplementedError
