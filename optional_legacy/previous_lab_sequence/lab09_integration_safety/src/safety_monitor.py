"""Starter safety-monitor state machine."""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class SafetyState(Enum):
    """Discrete operating states selected by the safety monitor."""

    NORMAL = auto()
    DEGRADED = auto()
    STOP = auto()


@dataclass
class HealthInputs:
    """Health measurements used for one safety decision.

    Fields:
      sensor_age_s: elapsed time since the latest sensor measurement in s
      localization_ok: whether the localization health check currently passes
      path_available: whether a valid path is currently available
      obstacle_distance_m: nearest relevant obstacle distance in m
      forward_speed_mps: current body-forward speed in m/s
    """

    sensor_age_s: float
    localization_ok: bool
    path_available: bool
    obstacle_distance_m: float
    forward_speed_mps: float


def evaluate_health(h: HealthInputs) -> SafetyState:
    """Select NORMAL, DEGRADED, or STOP from one health snapshot.

    Parameters:
      h: current timing, localization, path, obstacle, and motion health inputs

    Returns:
      SafetyState: selected operating state for the current snapshot

    TODO:
      Define a small, defensible rule set based on the lab requirements.
      Use both obstacle distance and forward speed when evaluating
      collision urgency. Handle stale or invalid inputs explicitly.
      Document thresholds in your report.
    """
    raise NotImplementedError("Implement safety-monitor logic")
