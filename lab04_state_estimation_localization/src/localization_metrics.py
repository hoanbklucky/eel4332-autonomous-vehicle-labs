"""Localization metrics that students may use for Lab 4."""

from __future__ import annotations
import numpy as np


def position_rmse(reference_xy, estimate_xy) -> float:
    reference_xy = np.asarray(reference_xy, dtype=float)
    estimate_xy = np.asarray(estimate_xy, dtype=float)
    if reference_xy.shape != estimate_xy.shape:
        raise ValueError("Shapes must match")
    error = reference_xy - estimate_xy
    squared_distance = np.sum(error**2, axis=1)
    return float(np.sqrt(np.mean(squared_distance)))
