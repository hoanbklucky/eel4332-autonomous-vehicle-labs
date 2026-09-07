"""Starter code for the EEL 4332 kinematic bicycle model."""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class BicycleState:
    """Planar bicycle-model pose; x and y are in m and yaw is in rad."""

    x: float
    y: float
    yaw: float


def step_bicycle(
    state: BicycleState,
    speed: float,
    steering: float,
    wheelbase: float,
    dt: float,
) -> BicycleState:
    """Advance the planar kinematic bicycle model by one time step.

    Parameters are SI units:
      state: current planar pose; x and y in m, yaw in rad
      speed: constant body-forward speed in m/s during this step
      steering: front-wheel steering angle in rad
      wheelbase: distance between equivalent front and rear axles in m
      dt: integration time step in s

    Returns:
      BicycleState: new pose after one time step; x and y in m, yaw in rad

    TODO:
      1. Compute x_dot, y_dot, and yaw_dot.
      2. Integrate one step.
      3. Return the new state.
    """
    raise NotImplementedError("Implement the bicycle-model propagation")


def simulate(
    initial_state: BicycleState,
    speed: float,
    steering: float,
    wheelbase: float,
    dt: float,
    duration: float,
) -> np.ndarray:
    """Return an N x 3 trajectory for a constant-input experiment.

    Parameters are SI units:
      initial_state: pose at time zero; x and y in m, yaw in rad
      speed: constant body-forward speed in m/s
      steering: constant front-wheel steering angle in rad
      wheelbase: distance between equivalent front and rear axles in m
      dt: fixed integration time step in s
      duration: requested simulation duration in s

    Returns:
      np.ndarray: trajectory with one pose per row and columns [x, y, yaw];
      x and y are in m and yaw is in rad

    TODO: repeatedly call step_bicycle and store the trajectory.
    """
    raise NotImplementedError("Implement trajectory simulation")
