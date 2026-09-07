"""Minimal linear Kalman-filter starter for EEL 4332."""

from __future__ import annotations
import numpy as np


class LinearKalmanFilter:
    """Store the state and covariance matrices for a linear Kalman filter.

    Matrix dimensions:
      x: state vector with shape (n,) or (n, 1)
      P: state covariance with shape (n, n)
      F: state-transition matrix with shape (n, n)
      H: measurement matrix with shape (m, n)
      Q: process-noise covariance with shape (n, n)
      R: measurement-noise covariance with shape (m, m)

    Units depend on the chosen state and measurement definitions. Each covariance
    entry has the product of the corresponding variables' units.
    """

    def __init__(self, x, P, F, H, Q, R):
        """Initialize the filter state, models, and covariance matrices.

        Parameters:
          x: initial state vector
          P: initial state covariance matrix
          F: linear state-transition matrix
          H: linear measurement matrix
          Q: process-noise covariance matrix
          R: measurement-noise covariance matrix

        Returns:
          None.
        """
        self.x = np.asarray(x, dtype=float)
        self.P = np.asarray(P, dtype=float)
        self.F = np.asarray(F, dtype=float)
        self.H = np.asarray(H, dtype=float)
        self.Q = np.asarray(Q, dtype=float)
        self.R = np.asarray(R, dtype=float)

    def predict(self):
        """Predict the state and covariance in place.

        Returns:
          None. Updates self.x and self.P using the stored model.

        TODO: implement the assigned linear Kalman prediction equations.
        """
        # TODO: update self.x and self.P.
        raise NotImplementedError

    def update(self, z):
        """Correct the predicted state and covariance using one measurement.

        Parameters:
          z: measurement vector with shape (m,) or (m, 1), using units that
          match the measurement model H and covariance R

        Returns:
          None. Updates self.x and self.P in place.

        TODO: implement the assigned innovation, gain, state-correction, and
        covariance-correction equations.
        """
        # TODO: innovation, innovation covariance, Kalman gain,
        # state correction, covariance correction.
        raise NotImplementedError
