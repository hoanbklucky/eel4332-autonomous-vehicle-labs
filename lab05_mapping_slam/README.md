# Lab 5 — Mapping and SLAM

## Mission

**Build a usable occupancy-grid map of an unknown environment and explain why some mapping trajectories produce better maps than others.**

## Learning Objectives

- explain occupancy-grid representation;
- distinguish mapping, localization, and SLAM;
- operate a SLAM workflow in ROS 2;
- identify loop-closure and drift behavior;
- evaluate map quality qualitatively and quantitatively.

## Prerequisites

Before starting, verify:

- robot/vehicle can be teleoperated;
- LiDAR data is available;
- odometry is available;
- TF is connected;
- SLAM Toolbox is installed.

## Part 1 — Verify Inputs

Record:

```bash
ros2 topic list
ros2 topic hz /scan
ros2 topic hz /odom
```

Inspect TF in RViz2.

Do not start debugging SLAM until `/scan`, `/odom`, and TF are valid.

## Part 2 — Build a Map

Launch the instructor-provided TurtleBot/Gazebo simulation and SLAM workflow.

The official [ROBOTIS TurtleBot 3 SLAM simulation guide for ROS 2 Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy) is a helpful visual reference for the overall workflow:

1. launch the simulated world;
2. launch the SLAM system with simulation time enabled;
3. teleoperate the robot through the environment;
4. save the completed occupancy map.

The ROBOTIS example uses Cartographer and the `turtlebot3_gazebo` packages. This course uses SLAM Toolbox and the course simulation workflow. Use the link to understand the process, but use the instructor-validated commands below for the lab rather than substituting the website's commands.

This lab establishes the ROS 2 mapping procedure later used on Goosebot. On hardware, repeat all input checks because Goosebot's LiDAR mounting, odometry drift, wheel slip, motion model, and TF frames will differ from TurtleBot.

**INSTRUCTOR VALIDATION REQUIRED:** insert the final launch commands for the Fall 2026 course simulation.

Teleoperate through the environment.

Use a deliberate trajectory:

- cover all major regions;
- avoid excessively fast turns;
- revisit distinctive regions;
- create opportunities for loop closure.

## Part 3 — Save the Map

Save the occupancy map using the course-approved workflow.

Keep generated map files in `results/`.

## Part 4 — Compare Mapping Strategies

Create two maps using different driving strategies, for example:

- slow/systematic;
- fast/aggressive;
- with/without revisiting a loop.

Compare:

- completeness;
- wall consistency;
- duplicated/blurred structures;
- obvious drift;
- loop-closure behavior.

## Part 5 — Map Quality

Use one simple quantitative measure in addition to visual assessment. Examples:

- map coverage;
- fraction of unknown cells;
- alignment error for a known wall;
- repeatability across two runs.

## Engineering Questions

1. Why are odometry and range sensing both important for SLAM?
2. What evidence indicates accumulated drift?
3. Why can loop closure improve a map?
4. Why can a poor TF calibration distort the map even when the SLAM algorithm is correct?
5. Which driving strategy produced the better map and why?

## Success Criteria

- [ ] valid sensor/odometry/TF inputs verified;
- [ ] occupancy map generated;
- [ ] map saved;
- [ ] two mapping strategies compared;
- [ ] one quantitative quality measure reported.

## What to Submit

- two map images;
- one short mapping video/screenshot sequence;
- quality comparison;
- completed `answers.md`.
