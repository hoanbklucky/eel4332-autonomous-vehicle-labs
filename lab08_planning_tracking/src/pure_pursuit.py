"""Pure Pursuit steering starter."""

from __future__ import annotations


def steering_command(
    vehicle_x: float,
    vehicle_y: float,
    vehicle_yaw: float,
    target_x: float,
    target_y: float,
    wheelbase: float,
    lookahead: float,
) -> float:
    """Return the bicycle-model steering angle toward a look-ahead target.

    Parameters are SI units in one common fixed frame:
      vehicle_x, vehicle_y: current vehicle position in m
      vehicle_yaw: current vehicle heading in rad
      target_x, target_y: selected look-ahead point position in m
      wheelbase: distance between equivalent front and rear axles in m
      lookahead: distance used by the Pure Pursuit controller in m

    Returns:
      float: front-wheel steering angle in rad for the bicycle model

    TODO:
      1. Express the target point relative to the vehicle.
      2. Determine the target heading / lateral geometry.
      3. Apply the Pure Pursuit steering relationship.
    """
    raise NotImplementedError("Implement Pure Pursuit")
