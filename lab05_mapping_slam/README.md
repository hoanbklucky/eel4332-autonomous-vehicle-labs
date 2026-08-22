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

## Background

### Why map in Gazebo?

Gazebo provides a fixed world that can be explored repeatedly with controlled trajectories. SLAM does not receive the world file as a map: it must infer occupancy from bridged range measurements, odometry, and coordinate transforms. This separation lets you compare the map produced by the autonomy stack with the known simulated environment.

A clean Gazebo world does not guarantee a clean map. Fast turns, sparse observations, odometry drift, timestamp mismatch, poor sensor frames, and missed loop closures can all distort the result. Simulation makes these causes easier to reproduce, but it usually underrepresents physical vibration, wheel slip, reflective surfaces, and calibration error.

### Occupancy grids and SLAM

An occupancy grid divides the planar environment into cells representing free, occupied, or unknown space. Resolution trades spatial detail against memory and computation. Mapping estimates the environment when pose is known; localization estimates pose in a known map; SLAM estimates pose and map together, coupling errors in the two results.

LiDAR observations constrain nearby geometry while odometry connects observations over motion. Reobserving a distinctive area can create a loop-closure constraint that reduces accumulated drift. It can also produce a bad correction when data association or transforms are wrong, so inspect both the map and the robot trajectory.

### Frame and time contract

A typical mapping chain connects `map`, `odom`, the robot base, and the LiDAR frame. Each transform has a specific owner; publishing competing versions of the same transform can make the tree unstable. Sensor timestamps must be transformable at the time of each scan, and all simulation nodes must use a consistent clock.

## Provided Files

```text
lab05_mapping_slam/
├── README.md
├── results/
└── answers.md
```

## Part 1 — Verify Inputs

### Mapping interface contract

Verify these interfaces before launching SLAM. Names shown are the expected TurtleBot defaults; record any instructor-validated replacement used by the course image.

| Interface | Expected type/frame | Role | Required evidence |
|---|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan`, sensor frame such as `base_scan` | range observations | nonzero rate and one valid message |
| `/odom` | `nav_msgs/msg/Odometry`, `odom` to base frame | local motion estimate | changing pose while teleoperating |
| `/tf` and `/tf_static` | ROS TF tree | connects map, odometry, base, and LiDAR | connected tree in RViz2 or `tf2_echo` |
| `/map` | `nav_msgs/msg/OccupancyGrid`, `map` frame | map produced by SLAM | grid grows or updates during mapping |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | teleoperation command | subscriber present before driving |

SLAM and the simulator must use simulation time consistently. Check a SLAM node after it starts:

```bash
ros2 param get /slam_toolbox use_sim_time
```

**INSTRUCTOR VALIDATION REQUIRED:** confirm the final SLAM Toolbox node name, topic names, and frames on the Fall 2026 course image.

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

Keep the simulator world, initial pose, approximate driving duration, and map-saving procedure the same between runs. Change only the driving strategy being studied. Record the duration and approximate distance traveled so that the comparison is reproducible.

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

Define the chosen measure before comparing the runs. Report its units, calculation method, and value for both maps. Include one RViz2 screenshot from each run using comparable zoom and display settings; if a loop closure is visible, include before-and-after images.

## Engineering Questions

1. Why are odometry and range sensing both important for SLAM?
2. What evidence indicates accumulated drift?
3. Why can loop closure improve a map?
4. Why can a poor TF calibration distort the map even when the SLAM algorithm is correct?
5. Which driving strategy produced the better map and why?

## Success Criteria

- [ ] `/scan` and `/odom` have measured nonzero update rates;
- [ ] the sensor-to-base-to-odometry TF chain is connected before SLAM starts;
- [ ] an occupancy map is generated and changes as new space is observed;
- [ ] each saved map includes the course-required image and metadata files;
- [ ] two mapping strategies are compared under documented, approximately matched conditions;
- [ ] one quantitative quality measure with units and method is reported for both maps.

## What to Submit

- two map images;
- one short mapping video/screenshot sequence;
- quality comparison;
- completed `answers.md`.

## Troubleshooting

- Validate `/scan`, `/odom`, TF, and simulation time in that order before launching SLAM.
- If scans appear detached from the robot, inspect frame IDs and the LiDAR-to-base transform.
- If the map doubles or smears during turns, reduce speed and check odometry and timestamps.
- If a saved map is empty, verify that `/map` is updating and use the instructor-approved map-saving command.
