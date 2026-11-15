# Lab 4 — Build a Map with SLAM

> **Copying ROBOTIS commands:** A leading `$` is a terminal-prompt symbol, not part of the command. Some copy buttons include it. Copy only the command after `$ `, or paste into the editor first and remove that prefix from each command line. For example, `$ sudo apt update` must be entered as:
>
> ```bash
> sudo apt update
> ```
>
> If you see `$: command not found`, remove the leading `$ ` and rerun. **Keep dollar signs inside commands**, such as `$HOME`, `$PWD`, `${TURTLEBOT3_MODEL}`, and `$(...)`; those have a different meaning.

## Mission

Follow the official ROBOTIS tutorial to create and save a map for navigation. The required mapper is **Cartographer**, as used in that tutorial. SLAM Toolbox and the separate Kalman-filter exercise are optional.

## Prerequisites

Complete [Lab 00](../lab00_setup/README.md). Earlier Lab 2 used a different simulator, so completing it does **not** prove that the ROBOTIS packages are installed.

### 0. Install/check packages before launching

Run in Ubuntu/WSL (including VS Code's WSL terminal). Select **Jazzy** on both official setup pages.

1. Follow [ROBOTIS PC Setup — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup/?ros=jazzy), specifically **Install Dependent ROS 2 Packages → Install TurtleBot3 Packages → Environment Configuration**. Keep your existing Ubuntu 24.04, ROS 2 Jazzy, and working Gazebo installation; install only missing dependencies. The PC setup supplies Cartographer, Nav2, and the core TurtleBot3 packages, including `turtlebot3_msgs`.
2. Follow **Install Simulation Package** in [ROBOTIS Gazebo Simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy), then build the workspace. The simulation package is additional to PC Setup; it does not replace it. Use the `jazzy` branch. If a source directory already exists, check it rather than cloning another copy.
3. Source the built workspace and check packages:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
ros2 pkg prefix turtlebot3_msgs
ros2 pkg prefix turtlebot3_description
ros2 pkg prefix turtlebot3_gazebo
ros2 pkg prefix turtlebot3_teleop
ros2 pkg prefix turtlebot3_cartographer
ros2 pkg prefix cartographer_ros
ros2 pkg prefix nav2_map_server
```

Every check must print an installation path. If a package is missing, complete its PC/simulation setup step and source the workspace again before continuing. Do not follow SBC/OpenCR hardware setup for this simulation.

Keep `~/turtlebot3_ws` (robot software) separate from your fork of the course repository (lab code/results).

## Procedure

Run commands in **VS Code's integrated terminal connected to WSL** or a separate **Ubuntu/WSL terminal**. Both work; do not use PowerShell. “Remote PC” in the ROBOTIS instructions means your Ubuntu/WSL computer, not a physical robot.

In each new terminal, after completing the official setup:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
```

Use the same model (**Burger**) and environment (**TurtleBot3 World**) throughout Labs 2, 4, 5, and the final.

1. Stop all previous simulator, mapper, teleoperation, and navigation processes with **Ctrl+C**.
2. Follow [ROBOTIS SLAM Simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy), in order: **Launch Simulation World → Run SLAM Node → Run Teleoperation Node → Save Map**. Keep each long-running node in its own terminal.
3. Explore slowly and revisit an area. Capture RViz2 screenshots before and after the revisit. Explain whether you actually observe a map correction.
4. Stop motion using the keyboard node's printed stop key. In a new sourced terminal, save directly into your course results folder:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs/lab04_slam
mkdir -p results
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/map" --ros-args -p use_sim_time:=true
```

Keep both `map.yaml` and its referenced image (normally `map.pgm`). Inspect the image, resolution, origin, and image filename in the YAML. Your path may differ if you cloned elsewhere.

5. Record the map's absolute YAML path with `realpath results/map.yaml`. Use this exact map in Lab 5. Stop motion before ending nodes; close the mapper, teleoperation, and simulator with **Ctrl+C** when finished.

**Use the official TurtleBot3 launch sequence throughout.** Do not combine it with the earlier `nav2_bringup tb3_simulation_launch.py` workflow, standalone SLAM Toolbox, custom TF bridges, or mesh-path workarounds. Old simulator screenshots are not reference output for this workflow.

## What to Submit

- Your map YAML/image pair.
- One Gazebo screenshot and two mapping screenshots showing the revisit.
- A brief `answers.md`: model/world, launch commands, saved-map path, map resolution, observed quality, and one limitation.
- A short mapping demonstration.

## Questions

1. Why does mapping need robot motion information as well as laser scans?
2. How might revisiting an area improve a map?
3. What parts of your map could cause navigation problems?

## Optional Background

[SLAM background](OPTIONAL_BACKGROUND.md) and [Kalman-filter extension](ALGORITHM_EXPERIMENT.md) are optional. The background's SLAM Toolbox configuration examples describe a different mapper; they are not required launch instructions.

## Troubleshooting

Confirm **Jazzy**, the sourced TurtleBot3 workspace, `TURTLEBOT3_MODEL=burger`, and that only one simulator/mapper is running. For an error, record the exact command and full terminal output. The instructor must check the official workflow once on the course WSL image before release.

Continue to [Lab 5 — Navigation](../lab05_navigation/README.md).
