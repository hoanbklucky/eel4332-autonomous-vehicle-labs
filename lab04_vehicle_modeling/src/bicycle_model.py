"""Starter code for the EEL 4332 kinematic bicycle model."""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class BicycleState:
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
      speed: m/s
      steering: rad
      wheelbase: m
      dt: s

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
    """Return an N x 3 array [x, y, yaw] for a constant-input experiment."""
    # TODO: repeatedly call step_bicycle and store the trajectory.
    raise NotImplementedError("Implement trajectory simulation")
