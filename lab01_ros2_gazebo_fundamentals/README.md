# Lab 1 — ROS 2 and Gazebo Fundamentals

## Mission

Build a working mental model of ROS 2 and Gazebo before using the complete TurtleBot/Nav2 simulation in Lab 2. You will inspect small ROS systems, compare communication patterns, build and launch a ROS package, inspect a Gazebo world, and create one explicit Gazebo-to-ROS bridge.

## Learning Objectives

By the end of this lab, you should be able to:

- distinguish nodes, topics, messages, services, actions, and parameters;
- inspect a live ROS graph with command-line tools and `rqt_graph`;
- explain packages, colcon workspaces, underlays, overlays, and launch files;
- distinguish the roles of Gazebo, ROS 2, and RViz2;
- inspect and modify an SDF world;
- distinguish Gazebo Transport from the ROS graph;
- explain why selected Gazebo data requires a ROS–Gazebo bridge.

## Prerequisites

- Complete [Lab 00 — Software Setup](../lab00_setup/README.md).
- Run `./lab00_setup/verify_installation.sh` successfully from the repository root.
- Use WSL/Ubuntu Terminals for all Linux, ROS 2, and Gazebo commands.

## Background

ROS 2 and Gazebo solve different parts of the robotics problem:

```mermaid
flowchart LR
    world["SDF world and models"] --> gazebo["Gazebo physics and sensors"]
    gazebo --> transport["Gazebo Transport topics"]
    transport --> bridge["ros_gz bridge"]
    bridge --> graph["ROS 2 nodes and typed interfaces"]
    graph --> tools["ROS CLI and rqt_graph"]
    graph --> rviz["RViz2 visualization"]
```

Gazebo simulates the world. ROS 2 connects autonomy software. A bridge translates only the selected data that must cross between their communication systems. This lab begins with small examples so each layer can be understood before they are combined in a full robot simulation.

## Provided Files

```text
lab01_ros2_gazebo_fundamentals/
├── README.md
├── answers.md
├── ros2_fundamentals.md
├── ros2_fundamentals_part1.md
├── ros2_fundamentals_part2.md
├── gazebo_fundamentals.md
├── eel4332_ros_practice/
├── worlds/gazebo_practice.sdf
├── images/
└── results/
```

## Step-by-Step Procedure

Complete the following guides in order. Do not skip directly to the larger Gazebo exercise.

1. [ROS 2 Fundamentals — Part 1: Graph and Communication](ros2_fundamentals_part1.md)
2. [ROS 2 Fundamentals — Part 2: Packages, Workspaces, and Launch](ros2_fundamentals_part2.md)
3. [Gazebo Fundamentals Practice](gazebo_fundamentals.md)

The short [ROS 2 fundamentals landing page](ros2_fundamentals.md) also links the two ROS parts.

## Experiment / Quantitative Analysis

Record the following in `answers.md`:

- the measured publication rate of `/chatter`;
- the measured `/practice/count` rates for `rate_hz:=5.0` and `rate_hz:=2.0`;
- the original and modified red-box poses from the SDF experiment;
- what happens to Gazebo simulation time when the world is paused.

Small differences in measured rates are expected. Explain whether each measured value is reasonably consistent with its configured value.

## Engineering Questions

Answer the questions in [answers.md](answers.md) using evidence from your commands and observations.

## Success Criteria

- [ ] ROS topic, service, action, and parameter interactions demonstrated.
- [ ] Publisher/topic/subscriber relationship observed in `rqt_graph`.
- [ ] Course practice package built and discovered from the workspace overlay.
- [ ] Launch argument changed and its effect measured.
- [ ] Gazebo world played, paused, reset, and inspected.
- [ ] One SDF pose changed and verified.
- [ ] Gazebo and ROS topic graphs compared.
- [ ] Gazebo `/clock` bridged to ROS 2 and echoed successfully.
- [ ] Required evidence and `answers.md` completed.

## What to Submit

- completed `answers.md`;
- one screenshot of `/talker → /chatter → /listener` in `rqt_graph`;
- one screenshot of the Gazebo practice world with the Entity Tree visible;
- terminal output showing the ROS `/clock` message while the bridge is running;
- any additional evidence requested by the instructor.

Store locally generated evidence in `lab01_ros2_gazebo_fundamentals/results/` unless the instructor specifies another submission method.

## Troubleshooting

- Run commands in WSL/Ubuntu, not PowerShell.
- Source `/opt/ros/jazzy/setup.bash` in every new WSL/Ubuntu Terminal.
- For the practice package, source `~/eel4332_ws/install/setup.bash` after sourcing Jazzy.
- Close older Gazebo instances before relaunching the practice world.
- Use the repository [troubleshooting guide](../docs/TROUBLESHOOTING.md) for installation, workspace, bridge, and graphics problems.

After completing this lab, continue to [Lab 2 — Autonomous-System Architecture and Sensors](../lab02_system_architecture_sensors/README.md).
