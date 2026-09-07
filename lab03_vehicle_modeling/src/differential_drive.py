"""Starter code for Lab 3 differential-drive kinematics and odometry."""

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
    """Return body-forward speed and vehicle yaw rate from wheel angular velocities.

    Parameters are SI units:
      left_speed, right_speed: wheel angular velocities in rad/s
      wheel_radius: effective wheel radius in m
      track_width: distance between left and right wheel contact lines in m

    Returns:
      linear_speed: body-forward speed in m/s
      yaw_rate: vehicle yaw rate in rad/s

    TODO: implement the differential-drive forward-kinematics equations.

    Hints:
      - The average of the two wheel-edge speeds determines forward motion.
      - Their right-minus-left difference determines the yaw direction.
      - Equal wheel speeds are a useful zero-yaw check.
    """
    linear_speed = wheel_radius * (left_speed + right_speed) / 2.0
    yaw_rate = wheel_radius * (right_speed - left_speed) / track_width
    return linear_speed, yaw_rate


def step_differential_drive(
    state: DifferentialDriveState,
    left_speed: float,
    right_speed: float,
    wheel_radius: float,
    track_width: float,
    dt: float,
) -> DifferentialDriveState:
    """Advance wheel-odometry pose by one fixed Euler time step.

    Parameters are SI units:
      state: current planar pose; x and y in m, yaw in rad
      left_speed, right_speed: wheel angular velocities in rad/s
      wheel_radius: effective wheel radius in m
      track_width: distance between left and right wheel contact lines in m
      dt: integration time step in s

    Returns:
      DifferentialDriveState: new pose after one time step; x and y in m,
      yaw in rad

    TODO:
      1. Call wheel_speeds_to_twist.
      2. Express body-forward speed in the world frame using state.yaw.
      3. Integrate x, y, and yaw for one time step.
      4. Return the new state.

    Hint: the cosine and sine of the current yaw project body-forward speed
    onto the world x and y axes. Multiply each rate by dt only when updating
    its corresponding state value.
    """
    linear_speed, yaw_rate = wheel_speeds_to_twist(
        left_speed, right_speed, wheel_radius, track_width
    )
    x_dot = linear_speed * np.cos(state.yaw)
    y_dot = linear_speed * np.sin(state.yaw)
    yaw_dot = yaw_rate

    new_x = state.x + x_dot * dt
    new_y = state.y + y_dot * dt
    new_yaw = state.yaw + yaw_dot * dt

    return DifferentialDriveState(new_x, new_y, new_yaw)


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

    Parameters are SI units:
      initial_state: pose at time zero; x and y in m, yaw in rad
      left_speed, right_speed: constant wheel angular velocities in rad/s
      wheel_radius: effective wheel radius in m
      track_width: distance between left and right wheel contact lines in m
      dt: fixed integration time step in s
      duration: requested simulation duration in s

    Returns:
      np.ndarray: trajectory with one pose per row and columns [x, y, yaw];
      x and y are in m, yaw is in rad, and the first row is initial_state

    TODO: repeatedly call step_differential_drive and store the trajectory.
    Include the initial state as the first row.

    Hint: each update must start from the state returned by the previous
    update. For a duration divided into fixed steps, the initial sample makes
    the trajectory contain one more row than the number of updates.
    """
    trajectory = [initial_state]
    current_state = initial_state

    for _ in range(int(duration / dt)):
        current_state = step_differential_drive(
            current_state,
            left_speed,
            right_speed,
            wheel_radius,
            track_width,
            dt
        )
        trajectory.append(current_state)

    return np.array([[state.x, state.y, state.yaw] for state in trajectory])
