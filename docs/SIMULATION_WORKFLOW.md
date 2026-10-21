# Course Simulation Runbook - Labs 4 and 5

Use ROS 2 Jazzy and modern Gazebo in WSL/Ubuntu. This runbook extends the TurtleBot workflow used in Lab 2. Run only one simulator and one command source at a time. Each new terminal needs `source /opt/ros/jazzy/setup.bash`.

**INSTRUCTOR VALIDATION REQUIRED:** these are candidate commands based on the installed-package workflow and upstream Jazzy launch interfaces. The new mapping-to-navigation sequence has not been tested in this workspace. Validate it on the course image before student release, including package versions, command type, base/sensor frames, SLAM startup, lifecycle transitions, and stop behavior.

## Packages

Verify availability with `ros2 pkg prefix PACKAGE`. If missing, install in Ubuntu:

```bash
sudo apt update
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-minimal-tb3-sim ros-jazzy-slam-toolbox \
  ros-jazzy-teleop-twist-keyboard ros-jazzy-nav2-simple-commander
```

These packages provide the simulator, mapping, map saving, navigation, and Python client API. Do not install or launch Gazebo Classic.

## Mapping mode

In Terminal 1, from the repository root:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch nav2_bringup tb3_simulation_launch.py \
  headless:=False autostart:=False slam:=False use_sim_time:=True
```

This opens Gazebo and RViz2 with localization/navigation inactive. `slam:=False` avoids starting a second mapper: you will start SLAM Toolbox separately with your own file. Do not activate the AMCL/localization lifecycle manager in this mode.

In Terminal 2, check motion TF:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Stop the diagnostic with `Ctrl+C` after it prints transforms. If the transform is absent, start the dedicated bridge previously required by the course environment:

```bash
ros2 run ros_gz_bridge parameter_bridge \
  '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
```

The `[` requests Gazebo-to-ROS translation. Keep the bridge running, then repeat the TF check in another terminal. If the installed simulation already supplies this transform, do not add a duplicate bridge. Verify `odom -> base_footprint -> base_link -> scan frame` before proceeding.

In Terminal 3, from `lab04_slam/`:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch slam_toolbox online_async_launch.py \
  use_sim_time:=True slam_params_file:="$PWD/config/slam.yaml"
```

This runs the mapper with the saved configuration. Confirm `/map` updates, the mapper uses simulation time, and the map-to-robot TF chain exists. If the installed SLAM release exposes lifecycle states and remains inactive, follow its validated activation procedure; do not start another mapper to work around it.

```bash
ros2 param get /slam_toolbox use_sim_time
ros2 run tf2_ros tf2_echo map base_link
```

Stop `tf2_echo` with `Ctrl+C`. In RViz2, display `/map`, laser scan, robot model, and TF with Fixed Frame `map`. In Terminal 4, run the keyboard node used in Lab 2:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic info /cmd_vel
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

The expected course command type is `geometry_msgs/msg/Twist`. If inspection reports another type, stop and use the instructor-validated teleoperation configuration; do not silently remap topics or mix message types. Reduce keyboard speeds as practiced in Lab 2. Use its stop key before map saving or shutting down.

Between independent maps, stop teleoperation, SLAM, the optional dedicated bridge, and the simulator with `Ctrl+C` in their terminals. Relaunch from the same starting pose. Resetting Gazebo alone does not clear the mapper's accumulated map.

## Navigation mode

Stop every mapping-mode process first, especially SLAM Toolbox. From the repository root in Terminal 1, set paths to your own map and configuration:

```bash
source /opt/ros/jazzy/setup.bash
selected_map="$PWD/lab04_slam/results/selected/map_a.yaml"
nav_parameters="$PWD/lab05_navigation/config/nav2_a.yaml"
ros2 launch nav2_bringup tb3_simulation_launch.py \
  headless:=False autostart:=False slam:=False use_sim_time:=True \
  map:="$selected_map" params_file:="$nav_parameters"
```

Change the selected filename to your actual selected map; for configuration B change the parameter-file path. The map's referenced image must remain beside its metadata as specified in YAML. `map` and `params_file` pass your artifacts into the existing launch command.

Repeat the motion-TF check and start the dedicated bridge only if needed, as in Mapping mode. Then in a new sourced terminal:

```bash
ros2 service call /lifecycle_manager_localization/manage_nodes \
  nav2_msgs/srv/ManageLifecycleNodes "{command: 0}"
```

This requests startup of localization. Continue only after `success: true`; run it once. In RViz2 click **2D Pose Estimate**, place the pose at the known simulator start (default `x = -2.0 m`, `y = -0.5 m`, heading along positive map x), and check scan alignment. Your map's coordinates may differ from simulator world coordinates: use the start pose expressed in the saved map, not an assumed world-to-map identity.

```bash
ros2 run tf2_ros tf2_echo map base_link
```

Wait for transforms and stop this diagnostic with `Ctrl+C`. Check RViz2 scan/map alignment, then activate navigation once:

```bash
ros2 service call /lifecycle_manager_navigation/manage_nodes \
  nav2_msgs/srv/ManageLifecycleNodes "{command: 0}"
```

After `success: true`, send a nearby open-space goal using **Nav2 Goal**. Do not repeatedly call startup after success; check lifecycle state if a later call reports failure. For the student mission, run the client and recorder from the Lab 5 README. Keep teleoperation stopped during navigation.

## Stop and restart

For normal navigation stopping, cancel the active goal through the mission client or RViz2 and verify zero motion in Gazebo and odometry. A cancellation request is not proof of a stop. If motion continues unexpectedly, pause Gazebo immediately, terminate the client and launch processes, and investigate before a fresh launch. Do not resume an unsafe command after pausing.

For an independent trial, shut down all involved processes and relaunch. Reinitialize localization at the documented starting pose. Do not record a trajectory across a simulator clock reset. These instructions are for simulation; Goosebot requires instructor-validated command arbitration and physical stop procedures.

## References

- [Jazzy TurtleBot simulation launch source](https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/launch/tb3_simulation_launch.py): supported launch arguments.
- [Jazzy Nav2 bringup source](https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/launch/bringup_launch.py): mapping versus localization selection.
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox): parameters and installed launch behavior.
- [Nav2 Simple Commander](https://docs.nav2.org/commander_api/index.html): mission-client API. Use the installed Jazzy API where newer documentation differs.
