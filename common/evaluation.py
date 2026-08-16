"""Generic evaluation utilities that do not implement course algorithms."""

from __future__ import annotations
import numpy as np


def rmse(reference, estimate) -> float:
    """Return root-mean-square error between equal-shaped arrays."""
    reference = np.asarray(reference, dtype=float)
    estimate = np.asarray(estimate, dtype=float)
    if reference.shape != estimate.shape:
        raise ValueError("reference and estimate must have the same shape")
    return float(np.sqrt(np.mean((reference - estimate) ** 2)))


def mae(reference, estimate) -> float:
    """Return mean absolute error."""
    reference = np.asarray(reference, dtype=float)
    estimate = np.asarray(estimate, dtype=float)
    if reference.shape != estimate.shape:
        raise ValueError("reference and estimate must have the same shape")
    return float(np.mean(np.abs(reference - estimate)))
