# Lab 1 — Autonomous-System Architecture and Sensors

## Mission

**Inspect a running autonomous-robot simulation and trace how sensor data flows through the ROS 2 system.**

## Learning Objectives

By the end of this lab, you should be able to:

- distinguish ROS 2 nodes, topics, messages, and coordinate frames;
- identify the roles of camera, LiDAR, IMU, and odometry-like data;
- measure topic update rates;
- explain how sensing feeds localization, planning, and control;
- draw a basic autonomy software/data-flow architecture.

## Prerequisites

- Complete `Lab00_setup/README.md`.
- ROS 2 Jazzy and Gazebo must launch.
- Review course material on autonomous-driving architecture and sensor roles.

## Background

A practical autonomous system is not one monolithic program. Sensor drivers, state estimation, mapping, planning, and control are commonly separated into components that exchange typed messages.

The purpose of this lab is **not** to master ROS 2. ROS 2 is the instrumentation layer that lets you inspect the autonomy pipeline.

## Provided Files

```text
lab01_system_architecture_sensors/
├── README.md
├── src/
│   └── topic_inventory.py
├── results/
└── answers.md
```

## Part 1 — Launch a Known-Good Simulation

For Lab 1, use the official Nav2 TurtleBot 3 simulation. It provides an integrated ROS 2 system with a simulated mobile robot, sensor data, odometry, coordinate transforms, RViz2, and navigation components.

Two graphical applications open during this activity:

- **Gazebo** is the physics simulator. It shows the robot and its environment as a 3D world. Use Gazebo to confirm that the simulated robot physically moves.
- **RViz2** visualizes ROS data. It shows the map, robot model, laser scan, coordinate frames, localization particles, planned path, and navigation controls. Use RViz2 to estimate the robot's starting pose and choose a destination.

The two windows display the same simulated robot in different ways. Moving the robot in Gazebo changes the sensor and odometry data displayed in RViz2.

### 1. Verify the required packages

Run:

```bash
source /opt/ros/jazzy/setup.bash
ros2 pkg prefix nav2_bringup
ros2 pkg prefix nav2_minimal_tb3_sim
```

Both commands should print `/opt/ros/jazzy`. If either package is missing, install the simulation packages:

```bash
sudo apt update
sudo apt install \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-minimal-tb3-sim
```

### 2. Launch the simulation

In **Terminal 1**, run:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch nav2_bringup tb3_simulation_launch.py \
  headless:=False autostart:=False
```

Keep this terminal open. The launch file starts modern Gazebo, RViz2, the robot-state publisher, the simulated TurtleBot 3, and the Nav2 stack. The `autostart:=False` argument prevents navigation from starting before localization has created the complete transform tree. The robot starts stationary; launching the simulation does not automatically command it to move.

Wait until both graphical windows open. At this stage:

- Gazebo should show a TurtleBot inside a small indoor world.
- RViz2 should open, but some displays may be blank or show warnings until localization starts and an initial pose is provided.
- Terminal 1 should remain running and continue printing status messages.

Make sure Gazebo is not paused. If its toolbar shows a **play** triangle, click it to start simulation time. Do not close Gazebo, RViz2, or Terminal 1 while completing the lab.

### 3. Start localization

In **Terminal 2**, start only the localization lifecycle nodes:

```bash
source /opt/ros/jazzy/setup.bash
ros2 service call /lifecycle_manager_localization/manage_nodes \
  nav2_msgs/srv/ManageLifecycleNodes "{command: 0}"
```

Run this command **once**. Wait for it to report `success: true` and for the map to appear in RViz2. Do not run it again: a second startup request reports `success: false` because the localization nodes are already active. That second response does not mean the first startup failed.

In RViz2, look for these signs that localization is ready for an initial pose:

- the **Map** display is checked in the left **Displays** panel;
- a black-and-white occupancy-grid map is visible in the center view;
- the **Navigation 2** panel reports **Localization: active**;
- **Navigation: inactive** is expected at this point.

Confirm the localization state:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

Both nodes should report `active` before continuing.

### 4. Set the initial pose and start navigation

In RViz2:

1. Find **2D Pose Estimate** in the toolbar at the top of the RViz2 window. Its icon is a green arrow.
2. Click **2D Pose Estimate** once. The mouse pointer is now used to place the robot, not to move the camera.
3. Move the pointer to the robot's starting location on the map. With the default launch settings, this is approximately `x = -2.0 m, y = -0.5 m`.
4. Press and hold the left mouse button at that location.
5. While holding the button, drag the arrow in the direction the robot is facing. The default yaw is approximately `0 rad`, toward the positive x-direction.
6. Release the mouse button. This publishes an initial-pose estimate; it does not command the robot to drive.
7. Wait several seconds for the purple **Amcl Particle Swarm** points to gather around the robot.

A reasonable pose estimate should make the robot model and red laser-scan points line up with the walls on the map. If they are clearly misaligned, repeat the **2D Pose Estimate** action with a corrected position or direction.

Return to Terminal 2 and start only the navigation lifecycle nodes:

```bash
ros2 service call /lifecycle_manager_navigation/manage_nodes \
  nav2_msgs/srv/ManageLifecycleNodes "{command: 0}"
```

Run this command **once**. Wait for `success: true`. The RViz2 panel should now report **Localization: active** and **Navigation: active**. Confirm the navigation state if needed:

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
```

Both nodes should report `active`. Then:

1. Find **Nav2 Goal** in the toolbar at the top of RViz2. Its icon is another green arrow.
2. Click **Nav2 Goal** once.
3. Choose a nearby open white area on the map; do not click a black wall or an occupied costmap cell.
4. Press and hold the left mouse button at the destination.
5. Drag in the direction the robot should face when it arrives, then release.
6. Watch for a path in RViz2 and wheel motion in Gazebo.

Start with a short goal in clear space. A long or obstructed goal makes troubleshooting harder.

Do not use the RViz2 **Startup** button for this procedure because it attempts to start both lifecycle managers together. Do not send a goal while the Navigation panel reports **inactive**. When navigation is active, the global and local paths should appear in RViz2, and the robot should begin moving in both RViz2 and Gazebo.

If Terminal 1 previously displayed an error similar to:

```text
Failed to activate global_costmap because transform from base_link to map
did not become available before timeout
```

Nav2 attempted to activate before the initial pose created the complete `map → odom → base_link` transform chain. Restart the simulation with `autostart:=False`, then follow the sequential lifecycle procedure above. A brief "extrapolation into the future" warning while setting the initial pose can occur because the sensor and transform timestamps differ by a few milliseconds; wait one second and set the initial pose again if localization does not become active.

If an error says that no transition is registered for a node in the `active` state, a lifecycle manager was asked to start an already-active node. Stop the complete launch with `Ctrl+C`, close its Gazebo and RViz2 windows, launch again with `autostart:=False`, and use the two service commands above exactly once each.

If RViz repeatedly reports that messages are older than the transform cache, stop the entire launch with `Ctrl+C`, close any remaining Gazebo and RViz2 windows, and start one fresh simulation. Do not leave an older simulation running when launching another one because resetting simulation time can invalidate cached transforms.

If navigation is active but nothing changes after sending a goal, check whether simulation time is advancing:

```bash
ros2 topic hz /clock
```

The command should continuously report a rate. If it prints nothing, return to Gazebo and click the **play** control.

### 5. Verify the simulator can move the robot directly

If the robot does not respond to an RViz2 goal, first test the Gazebo velocity interface without relying on localization or planning. In Terminal 2, run:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic type /cmd_vel
ros2 topic info /cmd_vel --verbose
```

The topic type should be `geometry_msgs/msg/Twist`, and the topic should have a subscriber from the ROS–Gazebo bridge. Command a slow forward motion:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.1}, angular: {z: 0.0}}"
```

Let the robot move for only a few seconds, then press `Ctrl+C` and send an explicit stop command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

If this direct test moves the robot, the simulator and command bridge work; return to RViz2 and check the initial pose and navigation goal. If it does not move, check Terminal 1 for bridge or Gazebo errors and confirm that `/cmd_vel` has a subscriber.

### 6. Inspect the ROS graph and sensor topics

After the simulation starts, confirm that ROS topics and transforms are available:

```bash
ros2 topic list
ros2 node list
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 topic echo /imu --once
ros2 topic echo /joint_states --once
ros2 topic echo /tf --once
```

Topic names may differ slightly with the installed Jazzy package version. Use `ros2 topic list` to identify the exact names before continuing.

To observe motion numerically while the robot moves, run:

```bash
ros2 topic echo /odom
```

Stop the command with `Ctrl+C` after confirming that position or orientation changes.

### Fallback sensor demonstration

If the primary simulation does not launch, use an official `ros_gz_sim_demos` sensor example as a fallback:

```bash
ros2 launch ros_gz_sim_demos imu.launch.py
```

Other available fallback demonstrations include `camera.launch.py` and the Gazebo LiDAR examples.

**INSTRUCTOR VALIDATION REQUIRED:** Test the primary launch command and record the final topic and frame names on the Fall 2026 course image before releasing the lab.

## Part 2 — Inspect the ROS Graph

Run:

```bash
ros2 node list
ros2 topic list
```

Choose at least four relevant topics and inspect them:

```bash
ros2 topic info /TOPIC
ros2 interface show MESSAGE_TYPE
ros2 topic echo /TOPIC --once
ros2 topic hz /TOPIC
```

Record:

- topic name;
- message type;
- approximate rate;
- physical quantity represented;
- likely downstream consumer.

## Part 3 — Inspect Coordinate Frames

Examine TF:

```bash
ros2 topic echo /tf --once
ros2 topic echo /tf_static --once
```

Use RViz2 to identify the base frame and at least two sensor frames.

Explain why the pose of a sensor relative to the vehicle matters.

## Part 4 — Run the Topic Inventory Helper

```bash
python3 src/topic_inventory.py
```

The helper prints available topics and their message types. It is intentionally a utility; you are still responsible for interpreting the topics.

## Part 5 — Sensor-to-Function Mapping

Create a table containing at least:

- camera;
- LiDAR;
- IMU;
- wheel odometry / encoder-derived motion.

For each, identify:

1. what is measured;
2. common limitation/failure mode;
3. which autonomy function uses it;
4. another sensor that complements it.

## Engineering Questions

Answer in `answers.md`.

1. Why is a high-rate sensor not automatically a high-quality sensor?
2. Why must sensor timestamps and frames be correct before sensor fusion?
3. Which sensor(s) would you trust for short-term motion? Which for long-term global position?
4. If the LiDAR topic continues publishing but its timestamps are delayed by 500 ms, what parts of the autonomy stack could be affected?
5. Draw a block diagram from sensing to actuation for the simulated system.

## Success Criteria

- [ ] simulation launches;
- [ ] ROS nodes/topics can be inspected;
- [ ] at least four sensor/state topics are characterized;
- [ ] TF frames are identified;
- [ ] a sensor-to-function table is completed;
- [ ] an autonomy architecture diagram is produced.

## What to Submit

- completed `answers.md`;
- sensor/topic characterization table;
- architecture diagram;
- one screenshot of RViz2 showing the robot and sensor frames;
- optional short screen recording.

## Troubleshooting

If no topics appear, confirm that the simulation is running and that your ROS environment is sourced.

See [`../docs/TROUBLESHOOTING.md`](../docs/TROUBLESHOOTING.md).
