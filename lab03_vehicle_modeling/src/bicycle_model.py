"""Starter code for the EEL 4332 kinematic bicycle model."""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def _student_todo(description: str):
    """Mark one expression that students must replace in the starter code."""
    raise NotImplementedError(f"Replace this _student_todo expression: {description}")


@dataclass
class BicycleState:
    """Planar bicycle-model pose; x and y are in m and yaw is in rad."""

    x: float
    y: float
    yaw: float


def wheel_speed_to_twist(
    wheel_speed: float,
    wheel_radius: float,
    steering: float,
    wheelbase: float,
) -> tuple[float, float]:
    """Return body-forward speed and yaw rate for the bicycle model.

    Parameters are SI units:
      wheel_speed: equivalent driven-wheel angular velocity in rad/s
      wheel_radius: effective driven-wheel radius in m
      steering: equivalent front-wheel steering angle in rad
      wheelbase: distance between equivalent front and rear axles in m

    Returns:
      linear_speed: body-forward speed in m/s
      yaw_rate: vehicle yaw rate in rad/s

    TODO: replace the two _student_todo expressions below. The return
    statement is provided as scaffolding.

    Hints:
      - Start with the tangential speed at the driven wheel's rim.
      - Zero steering must give zero yaw rate.
      - For fixed speed and wheelbase, increasing steering magnitude should
        increase yaw-rate magnitude.
    """
    linear_speed = _student_todo("convert wheel angular velocity to rim speed")
    yaw_rate = _student_todo("apply the bicycle-model steering relationship")
    return linear_speed, yaw_rate


def step_bicycle(
    state: BicycleState,
    wheel_speed: float,
    wheel_radius: float,
    steering: float,
    wheelbase: float,
    dt: float,
) -> BicycleState:
    """Advance the planar kinematic bicycle model by one time step.

    Parameters are SI units:
      state: current planar pose; x and y in m, yaw in rad
      wheel_speed: equivalent driven-wheel angular velocity in rad/s
      wheel_radius: effective driven-wheel radius in m
      steering: front-wheel steering angle in rad
      wheelbase: distance between equivalent front and rear axles in m
      dt: integration time step in s

    Returns:
      BicycleState: new pose after one time step; x and y in m, yaw in rad

    TODO: replace the three _student_todo expressions below. The function
    call, Euler updates, and return statement are provided as scaffolding.

    Hint: use the current yaw, not the newly updated yaw, when computing this
    explicit Euler step's world-frame position rates.
    """
    linear_speed, yaw_rate = wheel_speed_to_twist(
        wheel_speed, wheel_radius, steering, wheelbase
    )
    x_rate = _student_todo("project forward speed onto the world x-axis")
    y_rate = _student_todo("project forward speed onto the world y-axis")

    new_x = state.x + x_rate * dt
    new_y = state.y + y_rate * dt
    new_yaw = _student_todo("integrate yaw_rate for one time step")
    return BicycleState(x=new_x, y=new_y, yaw=new_yaw)


def simulate(
    initial_state: BicycleState,
    wheel_speed: float,
    wheel_radius: float,
    steering: float,
    wheelbase: float,
    dt: float,
    duration: float,
) -> np.ndarray:
    """Return an N x 3 trajectory for a constant-input experiment.

    Parameters are SI units:
      initial_state: pose at time zero; x and y in m, yaw in rad
      wheel_speed: constant equivalent driven-wheel angular velocity in rad/s
      wheel_radius: effective driven-wheel radius in m
      steering: constant front-wheel steering angle in rad
      wheelbase: distance between equivalent front and rear axles in m
      dt: fixed integration time step in s
      duration: requested simulation duration in s

    Returns:
      np.ndarray: trajectory with one pose per row and columns [x, y, yaw];
      x and y are in m and yaw is in rad

    TODO: replace the one _student_todo expression below. Array creation,
    initial-state storage, the model call, loop structure, and sample storage
    are provided.

    Hint: store initial_state first, then repeatedly advance from the most
    recently returned BicycleState until all fixed time steps are complete.
    """
    num_steps = _student_todo("calculate the number of fixed Euler updates")
    trajectory = np.zeros((num_steps + 1, 3))
    trajectory[0] = [initial_state.x, initial_state.y, initial_state.yaw]

    state = initial_state
    for step_index in range(num_steps):
        state = step_bicycle(
            state,
            wheel_speed,
            wheel_radius,
            steering,
            wheelbase,
            dt,
        )
        trajectory[step_index + 1] = [state.x, state.y, state.yaw]

    return trajectory
