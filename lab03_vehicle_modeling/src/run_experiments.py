"""Validation and experiment driver for Lab 3.

Use --model differential to validate differential_drive.py before completing
bicycle_model.py. Use --model bicycle or --model all after completing the
corresponding model functions.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from bicycle_model import BicycleState, simulate
from differential_drive import DifferentialDriveState, simulate_differential_drive


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def run_differential_drive_experiments() -> None:
    """Run and save the required constant-wheel-angular-velocity checks.

    Returns:
      None. Prints final poses and saves path and yaw plots in the Lab 3 results
      directory.
    """
    initial = DifferentialDriveState(0.0, 0.0, 0.0)
    wheel_radius = 0.033
    track_width = 0.16
    dt = 0.02
    duration = 8.0

    experiments = [
        ("equal positive", 5.0, 5.0),
        ("left wheel stationary", 0.0, 5.0),
        ("equal and opposite", -3.0, 3.0),
        ("slight mismatch", 5.0, 4.8),
    ]

    fig, (path_ax, yaw_ax) = plt.subplots(1, 2, figsize=(11, 4.5))
    final_poses = []

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
        time_s = [sample_index * dt for sample_index in range(len(trajectory))]
        path_ax.plot(trajectory[:, 0], trajectory[:, 1], label=name)
        yaw_ax.plot(time_s, trajectory[:, 2], label=name)
        final_poses.append((name, *trajectory[-1]))

    path_ax.set_xlabel("x [m]")
    path_ax.set_ylabel("y [m]")
    path_ax.set_title("Planar path")
    path_ax.set_aspect("equal")
    path_ax.legend()

    yaw_ax.set_xlabel("time [s]")
    yaw_ax.set_ylabel("yaw [rad]")
    yaw_ax.set_title("Heading over time")
    yaw_ax.legend()

    print("\nDifferential-drive final poses")
    print(f"{'case':<24} {'x [m]':>12} {'y [m]':>12} {'yaw [rad]':>12}")
    print("-" * 63)
    for name, final_x, final_y, final_yaw in final_poses:
        print(f"{name:<24} {final_x:>12.4f} {final_y:>12.4f} {final_yaw:>12.4f}")

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "differential_drive_trajectories.png", dpi=150)


def run_bicycle_experiments() -> None:
    """Run and save a compact set of bicycle-model cases.

    Returns:
      None. Saves a labeled trajectory figure in the Lab 3 results directory.
    """
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
    """Run the selected model experiments, save their figures, and show plots.

    Returns:
      None.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=("differential", "bicycle", "all"),
        default="all",
        help="model experiment set to run (default: all)",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    if args.model in ("differential", "all"):
        run_differential_drive_experiments()
    if args.model in ("bicycle", "all"):
        run_bicycle_experiments()
    plt.show()


if __name__ == "__main__":
    main()
