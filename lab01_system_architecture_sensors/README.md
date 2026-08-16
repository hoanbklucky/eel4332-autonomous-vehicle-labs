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
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

Keep this terminal open. The launch file starts modern Gazebo, RViz2, the robot-state publisher, the simulated TurtleBot 3, and the Nav2 stack. The robot starts stationary; launching the simulation does not automatically command it to move.

Wait until the robot is visible in both Gazebo and RViz2 before continuing.

### 3. Localize the robot and send a navigation goal

In RViz2:

1. Select **2D Pose Estimate** from the toolbar.
2. Click near the robot's location on the map and drag in the direction the robot is facing.
3. Wait a few seconds for the particle cloud around the robot to settle.
4. Select **Nav2 Goal** or **2D Goal Pose** from the toolbar.
5. Click an open location on the map and drag to specify the desired final heading.

The global and local paths should appear in RViz2, and the robot should begin moving in both RViz2 and Gazebo.

### 4. Verify the simulator can move the robot directly

If the robot does not respond to an RViz2 goal, first test the Gazebo velocity interface without relying on localization or planning. Open **Terminal 2** and run:

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

### 5. Inspect the ROS graph and sensor topics

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
