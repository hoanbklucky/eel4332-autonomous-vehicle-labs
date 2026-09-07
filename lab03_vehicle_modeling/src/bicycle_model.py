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

    TODO:
      1. Convert driven-wheel angular velocity to body-forward speed using
         ideal rolling without slip.
      2. Use the bicycle-model steering geometry to compute vehicle yaw rate.
      3. Return body-forward speed and vehicle yaw rate.

    Hints:
      - Start with the tangential speed at the driven wheel's rim.
      - Zero steering must give zero yaw rate.
      - For fixed speed and wheelbase, increasing steering magnitude should
        increase yaw-rate magnitude.
    """
    linear_speed = wheel_speed * wheel_radius
    yaw_rate = linear_speed * np.tan(steering) / wheelbase
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

    TODO:
      1. Call wheel_speed_to_twist.
      2. Express body-forward speed in the world frame using state.yaw.
      3. Integrate one step.
      4. Return the new state.

    Hint: use the current yaw, not the newly updated yaw, when computing this
    explicit Euler step's world-frame position rates.
    """
    speed, yaw_dot = wheel_speed_to_twist(
        wheel_speed, wheel_radius, steering, wheelbase
    )
    x_dot = speed * np.cos(state.yaw)
    y_dot = speed * np.sin(state.yaw)

    x = state.x + x_dot * dt
    y = state.y + y_dot * dt
    yaw = state.yaw + yaw_dot * dt

    return BicycleState(x, y, yaw)


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

    TODO: repeatedly call step_bicycle and store the trajectory.

    Hint: store initial_state first, then repeatedly advance from the most
    recently returned BicycleState until all fixed time steps are complete.
    """
    num_steps = int(duration / dt)
    trajectory = np.zeros((num_steps + 1, 3))
    trajectory[0] = [initial_state.x, initial_state.y, initial_state.yaw]

    state = initial_state
    for i in range(1, num_steps + 1):
        state = step_bicycle(
            state, wheel_speed, wheel_radius, steering, wheelbase, dt
        )
        trajectory[i] = [state.x, state.y, state.yaw]

    return trajectory
