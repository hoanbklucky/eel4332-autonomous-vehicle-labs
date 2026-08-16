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

- Complete `setup/README.md`.
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

Use the instructor-provided Gazebo/ROS launch command.

**INSTRUCTOR VALIDATION REQUIRED:** insert the final Fall 2026 launch command here after the course simulation image is frozen.

If no course vehicle is yet available, the instructor may use an official `ros_gz_sim_demos` sensor demo for this lab.

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
