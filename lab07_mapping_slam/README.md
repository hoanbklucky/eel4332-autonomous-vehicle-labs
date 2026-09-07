# Lab 7 — Mapping and SLAM

## Before You Begin — Update Course Files

In a **WSL/Ubuntu Terminal**, go to your local course repository and check for changes:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

**Command breakdown:** `cd` changes to the repository directory; `~` means your Ubuntu home directory. `git status --short` gives a compact list of local changes and prints nothing when the working tree is clean.

If the command prints nothing, run `git pull --rebase`. If it lists files, protect your work first by following [Updating the Course Repository](../docs/UPDATING_COURSE_REPOSITORY.md). Use your actual repository path if you cloned it elsewhere.

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
lab07_mapping_slam/
├── README.md
├── results/
└── answers.md
```

## Learning Path and Visible Checkpoints

| Stage | What you are learning | Visible checkpoint |
|---|---|---|
| Verify the baseline | Whether SLAM has valid sensor, odometry, time, and TF inputs | `/scan` and `/odom` update and the sensor-to-odometry frame chain is connected. |
| Observe map growth | How motion and LiDAR observations create an occupancy grid | Previously unknown space becomes free or occupied as TurtleBot explores. |
| Save the result | How a live map becomes a reusable navigation artifact | The saved image and metadata describe the same map seen in RViz2. |
| Compare strategies | How driving behavior changes SLAM quality | Comparable screenshots reveal differences in coverage, blur, duplication, or drift. |
| Test map usefulness | Why appearance alone is insufficient | One defined quality measure supports the visual comparison. |

Pause at each checkpoint and capture evidence before changing the driving strategy. A visually attractive map is not a passing result if its inputs were invalid or its saved files cannot be reused.

**Optional challenge after the two required maps:** Revisit one distinctive area slowly and watch for a loop-closure correction. Save before-and-after screenshots if the correction is visible; this is not an additional submission unless assigned.

## Part 1 — Verify Inputs

**Why this part matters:** SLAM depends on valid sensor, odometry, and transform data, so checking inputs first avoids blaming the mapper for upstream problems.

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

**Command breakdown:** `ros2 param get NODE PARAMETER` reads one parameter from a running node. Here it checks whether `/slam_toolbox` uses the simulation clock.

**INSTRUCTOR VALIDATION REQUIRED:** confirm the final SLAM Toolbox node name, topic names, and frames on the Fall 2026 course image.

Record:

```bash
ros2 topic list
ros2 topic hz /scan
ros2 topic hz /odom
```

**Command breakdown:** `ros2 topic list` checks that expected topics exist. Each `ros2 topic hz` command measures a topic's message rate; run the rate checks one at a time and stop each with `Ctrl+C`.

Inspect TF in RViz2.

Do not start debugging SLAM until `/scan`, `/odom`, and TF are valid.

## Part 2 — Build a Map

**Why this part matters:** Controlled exploration gives the mapper useful coverage while letting you observe how motion and revisiting areas affect the result.

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

**Why this part matters:** Saving converts the live SLAM result into a reusable artifact for later localization and navigation.

Save the occupancy map using the course-approved workflow.

Keep generated map files in `results/`.

## Part 4 — Compare Mapping Strategies

**Why this part matters:** Repeating the experiment with different trajectories reveals how coverage, speed, and loop closure influence drift and consistency.

Create two maps using different driving strategies, for example:

- slow/systematic;
- fast/aggressive;
- with/without revisiting a loop.

Before driving, design both routes and identify one intentional difference between them. Describe or sketch the planned order of regions, turn behavior, speed policy, and whether the route revisits a distinctive area. Predict which strategy will produce better coverage, lower distortion, and stronger loop-closure evidence, and explain why.

Keep the simulator world, initial pose, approximate driving duration, and map-saving procedure the same between runs. Change only the driving strategy being studied. Record the duration and approximate distance traveled so that the comparison is reproducible. If the actual route differs substantially from the plan, document the deviation instead of silently redefining the strategy afterward.

Compare:

- completeness;
- wall consistency;
- duplicated/blurred structures;
- obvious drift;
- loop-closure behavior.

## Part 5 — Map Quality

**Why this part matters:** Quantitative and task-based checks determine whether a map is usable, not merely visually appealing.

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
- [ ] both routes and their expected effects are recorded before mapping and compared with the resulting maps;
- [ ] one quantitative quality measure with units and method is reported for both maps.

## What to Submit

- two map images;
- one short mapping video/screenshot sequence;
- quality comparison;
- pre-run route plans, hypotheses, and post-run evidence table;
- completed `answers.md`.

## Troubleshooting

- Validate `/scan`, `/odom`, TF, and simulation time in that order before launching SLAM.
- If scans appear detached from the robot, inspect frame IDs and the LiDAR-to-base transform.
- If the map doubles or smears during turns, reduce speed and check odometry and timestamps.
- If a saved map is empty, verify that `/map` is updating and use the instructor-approved map-saving command.
