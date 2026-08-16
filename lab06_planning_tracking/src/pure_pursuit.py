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
    """Return steering angle in radians.

    TODO:
      1. Express the target point relative to the vehicle.
      2. Determine the target heading / lateral geometry.
      3. Apply the Pure Pursuit steering relationship.
    """
    raise NotImplementedError("Implement Pure Pursuit")
