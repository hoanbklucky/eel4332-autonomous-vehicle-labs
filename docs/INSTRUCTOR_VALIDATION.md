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

## Lab 01

- [ ] choose the exact simulation launch command
- [ ] confirm camera/LiDAR/IMU/odometry topic names
- [ ] confirm TF frame names

## Lab 02

- [ ] verify pure-Python bicycle starter flow
- [ ] verify the bicycle-versus-skid-steer comparison prompt
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

## Lab 07

- [ ] define supported fault-injection methods
- [ ] decide which safety state/command students can actually publish
- [ ] verify baseline mission

## Final Project

- [ ] verify the TurtleBot Gazebo/Nav2 final simulation
- [ ] verify Goosebot ROS 2 branch/package
- [ ] verify Goosebot LiDAR, odometry, TF, four-wheel skid-steer motor command interface, and safe stop
- [ ] measure/freeze Goosebot footprint, speed limits, and skid-steer controller parameters
- [ ] verify SLAM and Nav2 on Goosebot
- [ ] publish hardware-failure fallback policy
