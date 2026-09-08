"""Validation and experiment driver for Lab 3.

Use --model differential to validate differential_drive.py before completing
bicycle_model.py. Use --model bicycle or --model all after completing the
corresponding model functions.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes

from bicycle_model import BicycleState, simulate, wheel_speed_to_twist
from differential_drive import DifferentialDriveState, simulate_differential_drive


RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"

# TODO(student): Add one motion-design case selected from Part 3 of the README.
# Each tuple has the form (case_name, left_speed, right_speed), with wheel
# angular velocities in rad/s. Do not change the robot geometry to meet the
# motion target.
STUDENT_MOTION_CASES: list[tuple[str, float, float]] = []


def add_trajectory_playback(
    axis: Axes,
    trajectories: list[tuple[np.ndarray, str]],
    interval_ms: float,
    heading_length: float,
) -> FuncAnimation:
    """Animate position and heading markers over completed planar paths.

    Parameters:
      axis: Matplotlib axis containing the static planar paths
      trajectories: pairs of N x 3 [x, y, yaw] arrays and path colors
      interval_ms: delay between displayed trajectory samples in milliseconds
      heading_length: displayed length of each heading indicator in plot units

    Returns:
      FuncAnimation: animation object that must remain alive until plt.show

    This is provided visualization utility code, not a student TODO.
    """
    animated_artists = []
    position_markers = []
    heading_indicators = []

    for _, color in trajectories:
        marker, = axis.plot([], [], marker="o", color=color, markersize=7, zorder=4)
        heading, = axis.plot([], [], color=color, linewidth=2.5, zorder=4)
        position_markers.append(marker)
        heading_indicators.append(heading)
        animated_artists.extend((marker, heading))

    def update(frame_index: int):
        """Move every marker to the requested trajectory sample."""
        for (trajectory, _), marker, heading in zip(
            trajectories, position_markers, heading_indicators
        ):
            sample_index = min(frame_index, len(trajectory) - 1)
            x, y, yaw = trajectory[sample_index]
            marker.set_data([x], [y])
            heading.set_data(
                [x, x + heading_length * np.cos(yaw)],
                [y, y + heading_length * np.sin(yaw)],
            )
        return animated_artists

    return FuncAnimation(
        axis.figure,
        update,
        init_func=lambda: update(0),
        frames=max(len(trajectory) for trajectory, _ in trajectories),
        interval=interval_ms,
        blit=True,
        repeat=True,
        cache_frame_data=False,
    )


def run_differential_drive_experiments(
    animate: bool = False,
) -> FuncAnimation | None:
    """Run and save the validation checks and student-designed motion cases.

    Parameters:
      animate: add moving position and heading markers when True

    Returns:
      FuncAnimation when animation is enabled; otherwise None. Also prints
      final poses and saves path and yaw plots in the Lab 3 results directory.
    """
    initial = DifferentialDriveState(0.0, 0.0, 0.0)
    wheel_radius = 0.033
    track_width = 0.16
    dt = 0.02
    duration = 8.0

    validation_experiments = [
        ("equal positive", 5.0, 5.0),
        ("left wheel stationary", 0.0, 5.0),
        ("equal and opposite", -3.0, 3.0),
        ("slight mismatch", 5.0, 4.8),
    ]
    experiments = validation_experiments + STUDENT_MOTION_CASES

    if not STUDENT_MOTION_CASES:
        print(
            "\nA student motion-design case has not been added. "
            "Complete STUDENT_MOTION_CASES in run_experiments.py."
        )

    fig, (path_ax, yaw_ax) = plt.subplots(1, 2, figsize=(11, 4.5))
    final_poses = []
    plotted_trajectories = []

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
        path_line, = path_ax.plot(trajectory[:, 0], trajectory[:, 1], label=name)
        yaw_ax.plot(time_s, trajectory[:, 2], label=name)
        final_poses.append((name, *trajectory[-1]))
        plotted_trajectories.append((trajectory, path_line.get_color()))

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
    if animate:
        return add_trajectory_playback(
            path_ax,
            plotted_trajectories,
            interval_ms=dt * 1000.0,
            heading_length=0.08,
        )
    return None


def run_bicycle_experiments(animate: bool = False) -> FuncAnimation | None:
    """Run and save a compact set of bicycle-model cases.

    Parameters:
      animate: add moving position and heading markers when True

    Returns:
      FuncAnimation when animation is enabled; otherwise None. Also prints
      the input-to-twist conversion and saves a labeled trajectory figure.
    """
    initial = BicycleState(0.0, 0.0, 0.0)
    wheel_radius = 0.30
    wheelbase = 2.8
    dt = 0.02
    duration = 8.0

    experiments = [
        ("straight", 5.0, 0.0),
        ("gentle_turn", 5.0, 0.12),
        ("tighter_turn", 5.0, 0.25),
    ]

    fig, ax = plt.subplots()
    body_velocities = []
    plotted_trajectories = []
    for name, wheel_speed, steering in experiments:
        speed, yaw_rate = wheel_speed_to_twist(
            wheel_speed, wheel_radius, steering, wheelbase
        )
        trajectory = simulate(
            initial,
            wheel_speed,
            wheel_radius,
            steering,
            wheelbase,
            dt,
            duration,
        )
        path_line, = ax.plot(trajectory[:, 0], trajectory[:, 1], label=name)
        body_velocities.append((name, wheel_speed, steering, speed, yaw_rate))
        plotted_trajectories.append((trajectory, path_line.get_color()))

    print("\nBicycle-model wheel-to-body conversion")
    print(
        f"{'case':<18} {'wheel [rad/s]':>14} {'steer [rad]':>13} "
        f"{'speed [m/s]':>13} {'yaw rate [rad/s]':>17}"
    )
    print("-" * 79)
    for name, wheel_speed, steering, speed, yaw_rate in body_velocities:
        print(
            f"{name:<18} {wheel_speed:>14.3f} {steering:>13.3f} "
            f"{speed:>13.3f} {yaw_rate:>17.3f}"
        )

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Kinematic bicycle trajectories")
    ax.set_aspect("equal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "bicycle_trajectories.png", dpi=150)
    if animate:
        return add_trajectory_playback(
            ax,
            plotted_trajectories,
            interval_ms=dt * 1000.0,
            heading_length=0.5,
        )
    return None


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
    parser.add_argument(
        "--animate",
        action="store_true",
        help="replay each calculated planar trajectory in its plot window",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    animations = []
    if args.model in ("differential", "all"):
        animation = run_differential_drive_experiments(animate=args.animate)
        if animation is not None:
            animations.append(animation)
    if args.model in ("bicycle", "all"):
        animation = run_bicycle_experiments(animate=args.animate)
        if animation is not None:
            animations.append(animation)
    plt.show()


if __name__ == "__main__":
    main()
