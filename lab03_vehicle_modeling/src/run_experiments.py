"""Experiment driver for Lab 3.

Complete differential_drive.py and bicycle_model.py before running this file.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from bicycle_model import BicycleState, simulate
from differential_drive import DifferentialDriveState, simulate_differential_drive


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def run_differential_drive_experiments() -> None:
    """Plot the required constant-wheel-speed sanity checks."""
    initial = DifferentialDriveState(0.0, 0.0, 0.0)
    wheel_radius = 0.033
    track_width = 0.16
    dt = 0.02
    duration = 8.0

    experiments = [
        ("equal speeds", 5.0, 5.0),
        ("left wheel stationary", 0.0, 5.0),
        ("opposite speeds", -3.0, 3.0),
        ("slight mismatch", 5.0, 4.8),
    ]

    fig, ax = plt.subplots()
    for name, left_speed, right_speed in experiments:
        trajectory = simulate_differential_drive(
            initial,
            left_speed,
            right_speed,
            wheel_radius,
            track_width,
            dt,
            duration,
        )
        ax.plot(trajectory[:, 0], trajectory[:, 1], label=name)

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Differential-drive trajectories")
    ax.set_aspect("equal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "differential_drive_trajectories.png", dpi=150)


def run_bicycle_experiments() -> None:
    """Plot a compact set of bicycle-model cases."""
    initial = BicycleState(0.0, 0.0, 0.0)
    wheelbase = 2.8
    dt = 0.02
    duration = 8.0

    experiments = [
        ("straight", 5.0, 0.0),
        ("gentle_turn", 5.0, 0.12),
        ("tighter_turn", 5.0, 0.25),
    ]

    fig, ax = plt.subplots()
    for name, speed, steering in experiments:
        trajectory = simulate(initial, speed, steering, wheelbase, dt, duration)
        ax.plot(trajectory[:, 0], trajectory[:, 1], label=name)

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Kinematic bicycle trajectories")
    ax.set_aspect("equal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "bicycle_trajectories.png", dpi=150)


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    run_differential_drive_experiments()
    run_bicycle_experiments()
    plt.show()


if __name__ == "__main__":
    main()
