"""Starter safety-monitor state machine."""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class SafetyState(Enum):
    NORMAL = auto()
    DEGRADED = auto()
    STOP = auto()


@dataclass
class HealthInputs:
    sensor_age_s: float
    localization_ok: bool
    path_available: bool
    obstacle_distance_m: float


def evaluate_health(h: HealthInputs) -> SafetyState:
    """Return NORMAL, DEGRADED, or STOP.

    TODO:
      Define a small, defensible rule set based on the lab requirements.
      Document thresholds in your report.
    """
    raise NotImplementedError("Implement safety-monitor logic")
