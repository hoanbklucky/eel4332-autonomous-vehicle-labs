"""Starter code for Lab 4 differential-drive kinematics and odometry."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class DifferentialDriveState:
    """Planar pose in meters and radians."""

    x: float
    y: float
    yaw: float


def wheel_speeds_to_twist(
    left_speed: float,
    right_speed: float,
    wheel_radius: float,
    track_width: float,
) -> tuple[float, float]:
    """Return body linear speed and yaw rate from wheel angular speeds.

    Parameters are SI units:
      left_speed, right_speed: rad/s
      wheel_radius: m
      track_width: m between the left and right wheel contact lines

    Returns:
      linear_speed: m/s
      yaw_rate: rad/s

    TODO: implement the differential-drive forward-kinematics equations.
    """
    raise NotImplementedError("Implement wheel-speed forward kinematics")


def step_differential_drive(
    state: DifferentialDriveState,
    left_speed: float,
    right_speed: float,
    wheel_radius: float,
    track_width: float,
    dt: float,
) -> DifferentialDriveState:
    """Advance wheel-odometry pose by one fixed Euler time step.

    TODO:
      1. Call wheel_speeds_to_twist.
      2. Express body-forward speed in the world frame using state.yaw.
      3. Integrate x, y, and yaw for one time step.
      4. Return the new state.
    """
    raise NotImplementedError("Implement differential-drive odometry propagation")


def simulate_differential_drive(
    initial_state: DifferentialDriveState,
    left_speed: float,
    right_speed: float,
    wheel_radius: float,
    track_width: float,
    dt: float,
    duration: float,
) -> np.ndarray:
    """Return an N x 3 array [x, y, yaw] for constant wheel speeds.

    TODO: repeatedly call step_differential_drive and store the trajectory.
    Include the initial state as the first row.
    """
    raise NotImplementedError("Implement differential-drive trajectory simulation")
