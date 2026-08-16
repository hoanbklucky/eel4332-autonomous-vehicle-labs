"""Experiment driver for Lab 2.

Students should complete bicycle_model.py first.
"""

import matplotlib.pyplot as plt
from bicycle_model import BicycleState, simulate


def main():
    initial = BicycleState(0.0, 0.0, 0.0)
    wheelbase = 2.8
    dt = 0.02
    duration = 8.0

    experiments = [
        ("straight", 5.0, 0.0),
        ("gentle_turn", 5.0, 0.12),
        ("tighter_turn", 5.0, 0.25),
    ]

    for name, speed, steering in experiments:
        traj = simulate(initial, speed, steering, wheelbase, dt, duration)
        plt.plot(traj[:, 0], traj[:, 1], label=name)

    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.axis("equal")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
