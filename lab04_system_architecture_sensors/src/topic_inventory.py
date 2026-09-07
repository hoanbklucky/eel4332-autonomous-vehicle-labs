"""List ROS 2 topics and message types for Lab 4.

Run after sourcing ROS 2 and starting the simulation.
"""

import subprocess


def main():
    """Print the live ROS 2 topic names and message types.

    Returns:
      None. Exits with the ROS command's nonzero status if topic discovery fails.

    Notes:
      ROS 2 must be sourced and the course simulation must be running.
    """
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
