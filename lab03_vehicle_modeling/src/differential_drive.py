"""Starter code for Lab 3 differential-drive kinematics and odometry."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _student_todo(description: str):
    """Mark one expression that students must replace in the starter code."""
    raise NotImplementedError(f"Replace this _student_todo expression: {description}")


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

    TODO: replace the two _student_todo expressions below with the
    differential-drive forward-kinematics equations.

    Hints:
      - The average of the two wheel-edge speeds determines forward motion.
      - Their right-minus-left difference determines the yaw direction.
      - Equal wheel speeds are a useful zero-yaw check.
    """
    linear_speed = _student_todo("average the left and right wheel-edge speeds")
    yaw_rate = _student_todo("use the right-minus-left wheel-speed difference")
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

    TODO: replace the three _student_todo expressions below. The function
    call, Euler updates, and return statement are provided as scaffolding.

    Hint: the cosine and sine of the current yaw project body-forward speed
    onto the world x and y axes. Multiply each rate by dt only when updating
    its corresponding state value.
    """
    linear_speed, yaw_rate = wheel_speeds_to_twist(
        left_speed, right_speed, wheel_radius, track_width
    )
    x_rate = _student_todo("project forward speed onto the world x-axis")
    y_rate = _student_todo("project forward speed onto the world y-axis")

    new_x = state.x + x_rate * dt
    new_y = state.y + y_rate * dt
    new_yaw = _student_todo("integrate yaw_rate for one time step")
    return DifferentialDriveState(x=new_x, y=new_y, yaw=new_yaw)


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

    TODO: replace the one _student_todo expression below. Array creation,
    initial-state storage, the model call, loop structure, and sample storage
    are provided.

    Hint: each update must start from the state returned by the previous
    update. For a duration divided into fixed steps, the initial sample makes
    the trajectory contain one more row than the number of updates.
    """
    num_steps = _student_todo("calculate the number of fixed Euler updates")
    trajectory = np.zeros((num_steps + 1, 3))
    trajectory[0] = [initial_state.x, initial_state.y, initial_state.yaw]

    state = initial_state
    for step_index in range(num_steps):
        state = step_differential_drive(
            state,
            left_speed,
            right_speed,
            wheel_radius,
            track_width,
            dt,
        )
        trajectory[step_index + 1] = [state.x, state.y, state.yaw]

    return trajectory
