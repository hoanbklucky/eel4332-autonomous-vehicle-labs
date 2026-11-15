# Lab 5 — Navigate on Your Map

## Mission

Load your Lab 4 map, localize Waffle with AMCL, and reach three destinations with Nav2.

Use **VS Code's integrated terminal with the WSL: Ubuntu indicator**, or a separate **Ubuntu/WSL terminal**. Both work. Open additional VS Code terminals with **Terminal → New Terminal** or **+**. Run each long-running node in its own terminal.

Commands below are ready to copy: no leading `$` prompt is included. Keep dollar signs *inside* commands, such as `$PWD` and `$(...)`.

Use **Waffle in TurtleBot3 World** throughout. Before switching worlds, stop motion, stop teleoperation/SLAM/navigation, and press **Ctrl+C in the simulator launch terminal**. Wait for the processes to exit; closing the Gazebo window alone may leave the server running.


## 1. Install and check packages

Lab 4 must be complete, including the core TurtleBot3 and simulation workspace build. Keep its `map.yaml` and image together. Install navigation and the final-project Python API:

```bash
sudo apt update
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-nav2-simple-commander
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 pkg prefix turtlebot3_gazebo
ros2 pkg prefix turtlebot3_navigation2
ros2 pkg prefix nav2_bringup
ros2 pkg prefix nav2_map_server
ros2 pkg prefix nav2_simple_commander
```

Each check must print a path. If `turtlebot3_navigation2` is missing, verify that the official `turtlebot3` source is in `~/turtlebot3_ws/src` on branch `jazzy`. Reinstall dependencies/build it:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/turtlebot3_ws
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install
source install/setup.bash
ros2 pkg prefix turtlebot3_navigation2
```

Continue only after success. If the source workspace itself is missing, complete Lab 4's installation section first; Ubuntu/ROS do not need reinstalling.

## 2. Start a fresh world — Terminal 1

Stop all previous simulator, Cartographer, and teleoperation processes with Ctrl+C.

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Use the same world and model used to build the map. Leave this terminal running.

## 3. Start navigation — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:="$HOME/courses/eel4332-autonomous-vehicle-labs/lab04_slam/results/map.yaml"
```

Replace the quoted map path if your saved map is elsewhere. Keep this terminal running. This launch starts the model-specific Nav2 configuration and RViz2; do not start Cartographer/SLAM Toolbox or the previous manual lifecycle sequence.

## 4. Initialize localization

In RViz2, click **2D Pose Estimate**, click where the robot actually starts on the saved map, and drag toward its heading. Check that laser returns overlap mapped walls.

If needed, refine localization with small motions in **Terminal 3**:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```

Click that terminal before driving slowly. Press `s` to stop, then **Ctrl+C to terminate teleop before sending navigation goals**. Confirm scan/map alignment. Exporting the model in Terminal 1 does not configure Terminal 3.

## 5. Reach three goals

Click **Navigation2 Goal / Nav2 Goal** in RViz2, click a reachable location, and drag toward the desired final heading. Wait for completion before sending the next goal.

Visit three open-space destinations. Record map-frame x/y (metres), yaw (radians), outcome, and approximate simulation-time duration in `answers.md`; put the poses in `config/goals.csv`. Capture the map, robot, scan, and planned path. Record the home/start pose and launch commands for the final.

To stop early, use RViz2's navigation cancellation control if available and confirm actual stopping. If unexpected motion continues, pause Gazebo and end the launch processes before restarting. Do not treat a new goal at the current pose as a guaranteed stop.

After finishing, stop navigation (Terminal 2), then simulation (Terminal 1) with Ctrl+C.

## What to Submit

- `answers.md`, `config/goals.csv`, map identity/path, and home pose.
- Navigation configuration path/version; copy the full file if modified.
- Screenshot and short demonstration of three successful goals.

## Questions

1. How does localization differ from building a map?
2. How does the planned path differ from actual robot motion?
3. What would need validation before using this system on Goosebot?

## Final Handoff and Optional Background

Reuse the map, goals, and launch sequence in the [delivery final](../final_project_simulation/README.md). Its mission-client scaffold and recorder are in `src/`. [Navigation background](OPTIONAL_BACKGROUND.md) and [algorithm exercises](ALGORITHM_EXPERIMENTS.md) are optional.

## Troubleshooting

Package errors: check the build and sourcing. Misaligned scans: check map, initial pose, and world/model. Conflicting motion: stop all teleoperation publishers. Record the exact command and full error when requesting help.

The instructor must test saved-map navigation and cancellation on the course WSL image.

## References

These procedures adapt the official **Jazzy** workflow, with explicit per-terminal environment setup:
- [ROBOTIS PC Setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup/?ros=jazzy)
- [ROBOTIS Gazebo Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy)
- [ROBOTIS SLAM Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy)
- [ROBOTIS Navigation Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/navigation_simulation/?ros=jazzy)

