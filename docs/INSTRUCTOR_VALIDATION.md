# Instructor Validation Checklist

Complete this checklist before publishing the repository to students.

## Core environment

- [ ] Ubuntu 24.04 WSL image tested
- [ ] ROS 2 Jazzy installation tested
- [ ] Gazebo Harmonic / modern Gazebo launches
- [ ] `ros_gz` integration tested
- [ ] RViz2 tested
- [ ] Nav2 demo tested
- [ ] SLAM Toolbox tested
- [ ] robot_localization tested

## Lab 00

- [ ] Git installs inside Ubuntu/WSL and the documented identity checks work
- [ ] Windows VS Code, Microsoft WSL extension, and `code .` open the Linux repository as a WSL workspace
- [ ] Microsoft Python extension can select `~/venvs/eel4332/bin/python` inside WSL
- [ ] `demo_nodes_py`, turtlesim, `rqt_graph`, colcon, and rosdep tested
- [ ] `ros2 bag`, `teleop_twist_keyboard`, and `rqt_image_view` tested
- [ ] `eel4332_ros_practice` builds from a clean `~/eel4332_ws`
- [ ] replace the practice package's placeholder maintainer email and confirm its license metadata
- [ ] practice launch argument changes the measured `/practice/count` rate
- [ ] publisher/topic/subscriber relationship appears correctly in `rqt_graph`
- [ ] `gazebo_practice.sdf` validates and runs with physics, reset, and entity inspection
- [ ] `/clock` appears in Gazebo Transport and the documented one-way bridge produces a ROS `/clock` message
- [ ] complete both fundamentals practices once as a new student and confirm the expected duration

## Lab 01

- [ ] choose the exact simulation launch command
- [ ] confirm camera/LiDAR/IMU/odometry topic names
- [ ] confirm TF frame names

## Lab 02

- [ ] verify pure-Python bicycle starter flow
- [ ] verify the bicycle-versus-differential-drive comparison prompt
- [ ] pin F1TENTH/RoboRacer Gym commit or environment only if the optional extension is assigned
- [ ] verify example trajectory comparison

## Lab 03

- [ ] define the exact sensor-recording/export workflow
- [ ] provide a reference dataset in case ROS bag collection fails

## Lab 04

- [ ] choose the warm-up KF dataset
- [ ] choose localization/fusion dataset or simulation topics
- [ ] confirm ground-truth source

## Lab 05

- [ ] pin simulation robot/world
- [ ] verify `/scan`, `/odom`, TF
- [ ] verify SLAM launch
- [ ] verify map-save command

## Lab 06

- [ ] provide occupancy grid/map input for A*
- [ ] verify the required bicycle-model tracking environment
- [ ] verify F1TENTH only if the optional extension is assigned
- [ ] define track/path file format
- [ ] validate the ROS/RViz2 planning-visualization wrapper if that extension is required

## Lab 07

- [ ] define supported fault-injection methods
- [ ] decide which safety state/command students can actually publish
- [ ] verify baseline mission
- [ ] validate Nav2 cancellation and command arbitration for simulated safe stop
- [ ] verify the two-speed collision-approach experiment remains simulation-only

## Final Project

- [ ] verify the TurtleBot Gazebo/Nav2 final simulation
- [ ] verify Goosebot ROS 2 branch/package
- [ ] document Goosebot fixed-axis geometry and four-motor skid-steer command mapping
- [ ] verify Goosebot LiDAR, odometry, TF, motor command interface, and safe stop
- [ ] measure/freeze Goosebot footprint, speed limits, and motion-controller parameters
- [ ] verify SLAM and Nav2 on Goosebot
- [ ] publish hardware-failure fallback policy
