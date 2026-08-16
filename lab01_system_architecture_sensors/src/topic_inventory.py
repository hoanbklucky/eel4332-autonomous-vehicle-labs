"""List ROS 2 topics and message types for Lab 1.

Run after sourcing ROS 2 and starting the simulation.
"""

import subprocess


def main():
    result = subprocess.run(
        ["ros2", "topic", "list", "-t"],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(result.returncode)
    print(result.stdout)


if __name__ == "__main__":
    main()
