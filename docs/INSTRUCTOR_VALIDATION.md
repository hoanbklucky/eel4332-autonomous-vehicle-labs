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
- [ ] `ros2 bag`, `teleop_twist_keyboard`, and `rqt_image_view` are installed and discoverable
- [ ] Lab 00 verification script passes before the Lab 1 practice workspace is built

## Lab 01

- [ ] `demo_nodes_py`, turtlesim, `rqt_graph`, colcon, and rosdep tested
- [ ] `eel4332_ros_practice` builds from a clean `~/eel4332_ws`
- [ ] replace the practice package's placeholder maintainer email and confirm its license metadata
- [ ] practice launch argument changes the measured `/practice/count` rate
- [ ] publisher/topic/subscriber relationship appears correctly in `rqt_graph`
- [ ] `gazebo_practice.sdf` validates and runs with physics, reset, and entity inspection
- [ ] `/clock` appears in Gazebo Transport and the documented one-way bridge produces a ROS `/clock` message
- [ ] complete both fundamentals practices once as a new student and confirm the expected duration

## Lab 02

- [ ] verify `tb3_simulation_launch.py` accepts `headless:=False use_rviz:=False autostart:=False` on the course image
- [ ] confirm Gazebo opens without RViz2 and the robot begins in a usable obstacle-course location
- [ ] confirm `teleop_twist_keyboard` publishes the expected `/cmd_vel` type and moves the simulated robot
- [ ] confirm the documented stop and speed-reduction keys match the installed teleoperation package
- [ ] confirm `/odom` remains available without starting localization or navigation
- [ ] complete every required challenge as a new student and confirm a 45–60 minute duration

## Lab 03

- [ ] verify differential-drive forward-kinematics and odometry starter flow
- [ ] verify straight, pivot, curved, and in-place wheel-speed cases
- [ ] verify the odometry-sensitivity experiment and expected metrics
- [ ] verify pure-Python bicycle starter flow
- [ ] verify the differential-drive-versus-bicycle-versus-skid-steer comparison prompt
- [ ] pin F1TENTH/RoboRacer Gym commit or environment only if the optional extension is assigned
- [ ] verify example trajectory comparison

## Lab 04 - SLAM

- [ ] Validate the shared [simulation runbook](SIMULATION_WORKFLOW.md) on the final course image and record package versions.
- [ ] Confirm exact scan/odometry topics, sensor/base frames, command message type, and one TF owner per edge.
- [ ] Confirm the simulator can run with localization/navigation inactive while standalone SLAM Toolbox maps.
- [ ] Verify the copied asynchronous SLAM config, simulation clock, node activation, and map publication.
- [ ] Verify the required seeded Kalman dataset, independent one-step check, three Q/R runs, and dropout evaluation without reference leakage.
- [ ] Run two planned routes from fresh simulator and mapper states.
- [ ] Provide independent reference geometry for two wall segments, or explicitly use the documented consistency alternative.
- [ ] Save both maps and verify YAML/image copies load correctly in Lab 5.

## Lab 05 - Nav2 Navigation

- [ ] Validate the saved-map AMCL startup and initial-pose sequence with no running mapper.
- [ ] Confirm installed Jazzy Simple Commander methods, goal acceptance/results, timeout, and cancellation behavior.
- [ ] Confirm the recorder receives odometry with its sensor-data QoS and rejects time resets.
- [ ] Select conservative inflation radii, verify actual parameter paths, and confirm both full configurations load.
- [ ] Complete three matched trials per configuration with the same map, goals, initial pose, and success criteria.
- [ ] Verify cancellation reaches a terminal result and actual motion stops; validate the manual pause/shutdown fallback.
- [ ] Verify the recovery run and that telemetry supports goal-time/distance analysis.
- [ ] Validate required A* grid/path checks, Pure Pursuit circle-tracking experiments using the student Lab 3 model, and safety-policy boundary tests.
- [ ] Verify the implemented monitor's injected STOP cancels the live goal and inhibits automatic mission continuation.
- [ ] Confirm required implementation TODOs remain unsolved and that workload is scheduled over enough sessions.

## Optional legacy exercises

The previous Labs 04-09 are archived under `optional_legacy/previous_lab_sequence/`. If assigning them, separately validate their datasets, algorithm harnesses, and any old simulation commands. Their original numbering does not extend the new required sequence.

## Final Project

- [ ] verify the TurtleBot Gazebo/Nav2 final simulation
- [ ] verify Goosebot ROS 2 branch/package
- [ ] document Goosebot fixed-axis geometry and four-motor skid-steer command mapping
- [ ] verify Goosebot LiDAR, odometry, TF, motor command interface, and safe stop
- [ ] measure/freeze Goosebot footprint, speed limits, and motion-controller parameters
- [ ] verify SLAM and Nav2 on Goosebot
- [ ] publish hardware-failure fallback policy
