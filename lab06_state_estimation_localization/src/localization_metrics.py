"""Localization metrics that students may use for Lab 6."""

from __future__ import annotations
import numpy as np


def position_rmse(reference_xy, estimate_xy) -> float:
    """Return planar position RMSE over corresponding trajectory samples.

    Parameters:
      reference_xy: N x 2 array-like reference positions [x, y]
      estimate_xy: N x 2 array-like estimated positions [x, y], in the same
      frame, units, and sample order as reference_xy

    Returns:
      float: root mean square of Euclidean position error, in the same length
      unit as the input coordinates

    Raises:
      ValueError: if reference_xy and estimate_xy have different shapes
    """
    reference_xy = np.asarray(reference_xy, dtype=float)
    estimate_xy = np.asarray(estimate_xy, dtype=float)
    if reference_xy.shape != estimate_xy.shape:
        raise ValueError("Shapes must match")
    error = reference_xy - estimate_xy
    squared_distance = np.sum(error**2, axis=1)
    return float(np.sqrt(np.mean(squared_distance)))
