"""A* starter code for a 2-D occupancy grid."""

from __future__ import annotations
from typing import Iterable


def astar(grid, start, goal):
    """Return a collision-free sequence of grid cells from start to goal.

    Parameters:
      grid: 2-D array-like occupancy grid; 0 is free and nonzero is occupied
      start: start cell represented using the documented (row, column) or
      (x, y) convention
      goal: goal cell using the same convention as start

    Returns:
      list: ordered cells beginning at start and ending at goal, or a clearly
      documented empty/failure result when no valid path exists

    TODO:
      - maintain open/closed sets
      - track g costs and parents
      - use an admissible heuristic
      - reconstruct the final path
    """
    raise NotImplementedError("Implement A* search")
