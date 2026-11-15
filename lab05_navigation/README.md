# Lab 5 — Navigate on Your Map

> **Copying ROBOTIS commands:** A leading `$` is a terminal-prompt symbol, not part of the command. Some copy buttons include it. Copy only the command after `$ `, or paste into the editor first and remove that prefix from each command line. For example, `$ sudo apt update` must be entered as:
>
> ```bash
> sudo apt update
> ```
>
> If you see `$: command not found`, remove the leading `$ ` and rerun. **Keep dollar signs inside commands**, such as `$HOME`, `$PWD`, `${TURTLEBOT3_MODEL}`, and `$(...)`; those have a different meaning.

## Mission

Follow the official ROBOTIS navigation tutorial to localize on your Lab 4 map and reach three destinations.

## Prerequisites

Complete [Lab 4](../lab04_slam/README.md), including its **PC Setup and Simulation Package installation**, and retain its map YAML/image pair. Select **Jazzy** in the official tutorial.

### 0. Install/check navigation packages

If not already done, complete **Install Navigation2** and **Install TurtleBot3 Packages** in [ROBOTIS PC Setup — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup/?ros=jazzy). Ubuntu/ROS do not need reinstalling. The core TurtleBot3 workspace supplies the model-specific `turtlebot3_navigation2` launch package.

Install the Nav2 packages and the Python API needed for the final:

```bash
sudo apt update
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-nav2-simple-commander
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
ros2 pkg prefix turtlebot3_gazebo
ros2 pkg prefix turtlebot3_navigation2
ros2 pkg prefix nav2_bringup
ros2 pkg prefix nav2_map_server
ros2 pkg prefix nav2_simple_commander
```

Every package check must print a path. If the TurtleBot3 launch package is missing, complete/rebuild the official workspace and source it again before starting navigation.

### After building: refresh the terminal environment

The ROBOTIS simulation installation section ends with a build, but the current terminal may still have the environment from **before** the new packages were installed. After a successful build, and in every new Ubuntu/WSL terminal used for TurtleBot3, run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 pkg prefix turtlebot3_gazebo
```

The last command must print an installation path before you launch Gazebo. Sourcing makes already-built packages discoverable; it does not install them. If `turtlebot3_gazebo` is still missing, confirm that you installed **`turtlebot3_simulations` separately from PC Setup** and that its build succeeded. If `install/setup.bash` is missing, complete the build first. Use your actual workspace path if different. Even if you added sourcing to `~/.bashrc`, rerun it in the current terminal after building new packages.


### Choose one world at a time

The ROBOTIS page lists **alternative launch choices**, not commands to run together:

| Environment | Launch file |
|---|---|
| Empty World | `empty_world.launch.py` |
| TurtleBot3 World | `turtlebot3_world.launch.py` |
| TurtleBot3 House | `turtlebot3_house.launch.py` |

For this course, use **Waffle in TurtleBot3 World** unless instructed otherwise; Empty World is suitable for an initial installation test. Use `TURTLEBOT3_MODEL=waffle` in each terminal to match the course's TurtleBot3 World configuration.

To switch worlds: stop robot motion, stop teleoperation and any SLAM/navigation nodes with **Ctrl+C**, then press **Ctrl+C in the terminal running the current Gazebo launch**. Wait for its processes to exit before running the next world's launch command. Closing only the Gazebo window may leave the simulation server running. Start the required nodes again after the new world loads.

For saved-map navigation, use the same world/model that produced the map. A map from one environment does not describe another.


### New terminal for teleoperation

The ROBOTIS “Operate TurtleBot3” section shows only the teleop command. Before running it in a **new Ubuntu/WSL terminal**, run the complete sequence:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```

An `export` in the simulator terminal does not configure a separately opened terminal. Repeat the source commands and model setting in **every new terminal** used for teleoperation, SLAM, or navigation. `KeyError: 'TURTLEBOT3_MODEL'` means the model setting is missing in that terminal. Keep keyboard focus in the teleop terminal and use its printed stop key before switching windows.

Use **Waffle** for both the simulator and these nodes. If an existing simulator was launched as Burger, stop its launch and related nodes before relaunching as Waffle; exporting a new value alone does not change an already-running robot. Keep the same model/world for mapping and navigation; recheck any map, goals, and configuration reused from a different model.

## Procedure

Run commands in **VS Code's integrated terminal connected to WSL** or a separate **Ubuntu/WSL terminal**. Both work; do not use PowerShell. “Remote PC” in the ROBOTIS instructions means your Ubuntu/WSL computer, not a physical robot.

In each new terminal, after completing the official setup:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
```

Use the same model (**Waffle**) and environment (**TurtleBot3 World**) throughout Labs 2, 4, 5, and the final.

1. Stop all applications from mapping with **Ctrl+C**, including Cartographer and teleoperation.
2. Follow [ROBOTIS Navigation Simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/navigation_simulation/?ros=jazzy), in order: **Launch Simulation World → Run Navigation Node → Estimate Initial Pose → Set Navigation Goal**.
3. Use the same world/model as mapping. Replace the tutorial's example map path with the **absolute path to your Lab 4 `map.yaml`**. Keep the referenced map image beside the YAML.
4. Initialize the robot pose in RViz2 and check scan/wall alignment. If using teleoperation to refine localization as the tutorial describes, stop and terminate that keyboard node before sending navigation goals.
5. Reach three open-space destinations, one at a time. Record their map-frame x/y coordinates (metres), yaw (radians), outcomes, and approximate simulation-time durations in `answers.md`. Save destinations in `config/goals.csv`.
6. Capture a screenshot showing the map, robot, scan, and planned path. Save the home/start pose and exact launch commands for the final.

Keep the simulator and navigation terminals running while sending goals. Do not run Cartographer or SLAM Toolbox during saved-map navigation, or add the old custom lifecycle-startup/TF-bridge commands.

**Stopping:** use RViz2's navigation cancel control if available and confirm actual stopping in Gazebo. If motion continues unexpectedly, pause Gazebo and end the launch processes before a clean restart. Do not treat a new destination at the current pose as a guaranteed stop.

## What to Submit

- Completed `answers.md` and `config/goals.csv`.
- Map identity/path, home pose, and the navigation configuration path/version used (copy the full file if modified).
- A screenshot and short demonstration of three successful goals.

## Questions

1. How does localization differ from building a map?
2. How does the planned path differ from actual robot motion?
3. What would need validation before using this system on Goosebot?

## Final Handoff

Reuse your map, goals, and working official navigation setup in the [delivery final](../final_project_simulation/README.md). The mission-client scaffold and odometry recorder in `src/` support that project. Separate A*, Pure Pursuit, and safety-monitor exercises are optional.

## Optional Background

[Navigation background](OPTIONAL_BACKGROUND.md) and [algorithm exercises](ALGORITHM_EXPERIMENTS.md).

## Troubleshooting

Check the map path, initial pose, Jazzy tab, sourced workspace, model, and duplicate command publishers before changing parameters. The official tutorial supplies startup instructions; this README supplies the course tasks. The instructor must test the workflow on the course WSL image.
