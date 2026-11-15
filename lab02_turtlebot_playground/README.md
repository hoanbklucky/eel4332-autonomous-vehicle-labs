# Lab 2 — TurtleBot Playground

> **Copying ROBOTIS commands:** A leading `$` is a terminal-prompt symbol, not part of the command. Some copy buttons include it. Copy only the command after `$ `, or paste into the editor first and remove that prefix from each command line. For example, `$ sudo apt update` must be entered as:
>
> ```bash
> sudo apt update
> ```
>
> If you see `$: command not found`, remove the leading `$ ` and rerun. **Keep dollar signs inside commands**, such as `$HOME`, `$PWD`, `${TURTLEBOT3_MODEL}`, and `$(...)`; those have a different meaning.

## Mission

Drive TurtleBot3 manually in Gazebo before studying modeling, SLAM, and navigation. Allow about 45–60 minutes.

## Prerequisites

Complete [Lab 00](../lab00_setup/README.md), including the official TurtleBot3 setup, and Lab 1. Select **Jazzy** on the ROBOTIS pages.

### After building: refresh the terminal environment

The ROBOTIS simulation installation section ends with a build, but the current terminal may still have the environment from **before** the new packages were installed. After a successful build, and in every new Ubuntu/WSL terminal used for TurtleBot3, run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 pkg prefix turtlebot3_gazebo
```

The last command must print an installation path before you launch Gazebo. Sourcing makes already-built packages discoverable; it does not install them. If `turtlebot3_gazebo` is still missing, confirm that you installed **`turtlebot3_simulations` separately from PC Setup** and that its build succeeded. If `install/setup.bash` is missing, complete the build first. Use your actual workspace path if different. Even if you added sourcing to `~/.bashrc`, rerun it in the current terminal after building new packages.


## Procedure

Run commands in **VS Code's integrated terminal connected to WSL** or a separate **Ubuntu/WSL terminal**. Both work; do not use PowerShell. “Remote PC” in the ROBOTIS instructions means your Ubuntu/WSL computer, not a physical robot.

In each new terminal, after completing the official setup:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
```

Use the same model (**Burger**) and environment (**TurtleBot3 World**) throughout Labs 2, 4, 5, and the final.

1. Stop any previous simulation. Follow [ROBOTIS Gazebo Simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy) to launch **TurtleBot3 World**.
2. Use the keyboard teleoperation instructions on that page. If needed, the [official SLAM tutorial](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy) also lists the teleoperation node; use only its teleoperation section in this lab, not the SLAM node.
3. Keep the keyboard terminal focused. Follow its printed key map: practice forward/reverse motion, turning, and stopping at low speed. These keys differ from the older `teleop_twist_keyboard` exercise.
4. Drive around two obstacles without contact and return near your start. Observe the difference between rotating in place and following a curve.
5. In another sourced terminal, inspect motion feedback:

```bash
ros2 topic echo /odom --once
ros2 topic info /cmd_vel
```

Record the actual command message type; do not assume it is `Twist` rather than `TwistStamped`.

6. Stop using the teleoperation node's printed stop key, confirm no motion, and terminate teleoperation and simulation with **Ctrl+C**. Relaunch once to practice a clean reset.

This lab uses the ROBOTIS simulation, not `nav2_bringup tb3_simulation_launch.py`. The older images retained in `images/` show the previous simulator and are not current expected output.

## What to Submit

A short driving video, a Gazebo screenshot, and `answers.md` describing the commands, message type, stopping/reset procedure, and your observations.

## Questions

1. What does a velocity command specify, compared with a destination?
2. How does the robot turn in place?
3. What does odometry report?
4. What additional capabilities are needed for autonomous navigation?
