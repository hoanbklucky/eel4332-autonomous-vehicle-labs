# Lab 4 - Build a Map with SLAM

## Mission

**Build, evaluate, and save a map that another team could use for navigation.** You will implement and evaluate a Kalman filter, configure SLAM Toolbox, drive two planned exploration routes, measure map quality, and select a map for Lab 5.

## Learning Objectives

- implement Kalman prediction/correction and evaluate uncertainty and dropout behavior;
- connect LiDAR, odometry, TF, and simulation time to a working mapper;
- edit and run a reproducible SLAM configuration;
- compare two exploration strategies using measured evidence;
- export a map and verify that its image and metadata can be reused.

## Prerequisites

Complete [setup](../lab00_setup/README.md) and Labs [1](../lab01_ros2_gazebo_fundamentals/README.md), [2](../lab02_turtlebot_playground/README.md), and [3](../lab03_vehicle_modeling/README.md). You must be able to teleoperate and stop TurtleBot. Update course files using [the repository update guide](../docs/UPDATING_COURSE_REPOSITORY.md).

## Background

SLAM estimates robot pose and a map together. Odometry connects observations over motion; LiDAR provides evidence about nearby geometry. TF supplies the coordinate relationships needed to place each scan at its measurement time.

The required work combines student algorithm implementation with configuring, building, testing, and evaluating the mapping system. Derivations, detailed sensor theory, TF examples, and reading checks with collapsed answers are in [OPTIONAL_BACKGROUND.md](OPTIONAL_BACKGROUND.md). They are supporting references, not extra submissions.

## Provided Files

- `src/kalman_filter.py`: required student predict/update starter.
- `src/make_estimation_data.py` and `src/localization_metrics.py`: provided data/metric utilities.
- [Required Kalman experiment](ALGORITHM_EXPERIMENT.md): implementation, verification, tuning, and dropout tasks.
- `answers.md`: experiment plans and evidence tables.
- `config/`: your saved SLAM parameter file.
- `results/`: your maps, measurements, and screenshots.
- [Simulation runbook](../docs/SIMULATION_WORKFLOW.md): launch, TF bridge, stop, and restart commands.

## Step-by-Step Procedure

### 0. Implement and evaluate your estimator

Complete the [required Kalman-filter experiment](ALGORITHM_EXPERIMENT.md), including your experiment runner, independent one-step verification, three Q/R configurations, and dropout comparison. This is a required part of Lab 4. It studies estimation independently; SLAM Toolbox continues to use its own estimator in the mapping steps below.

### 1. Prepare your SLAM configuration

Use WSL/Ubuntu terminals for all commands. From this lab directory:

```bash
source /opt/ros/jazzy/setup.bash
cp "$(ros2 pkg prefix --share slam_toolbox)/config/mapper_params_online_async.yaml" config/slam.yaml
```

`cp` creates your editable copy of the installed SLAM defaults. Inspect `scan_topic`, `odom_frame`, `map_frame`, and `base_frame`; match them to the running robot in the next step. Record their values and the map `resolution` in `answers.md`. Keep the other defaults for the baseline and submit the full configuration.

### 2. Bring up the robot and verify the inputs

Follow [Mapping mode](../docs/SIMULATION_WORKFLOW.md#mapping-mode). Start the simulator and verify motion-to-base TF before starting the standalone SLAM Toolbox node. Keep AMCL and Nav2 navigation inactive during mapping; do not send navigation goals.

Inspect the actual interfaces:

```bash
ros2 topic list -t
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 topic hz /scan
```

`list -t` shows names and types; `echo --once` captures one message; `hz` measures arrival rate. Stop `hz` with `Ctrl+C` after at least 10 seconds. Check two scan timestamps while Gazebo is playing and record the sensor frame, rate, and timestamp progression. Check odometry changes during a short drive. Use RViz2's TF display to trace `odom` through the base to the scan frame.

Record the simulated sensor, bridge/publisher, and one observed ROS consumer using `ros2 topic info /scan --verbose`. This is an input check for your map, not a separate architecture report. Resolve missing data or disconnected TF before mapping.

### 3. Build map A

Plan a route before driving. Define the starting pose, regions to cover, approximate duration, low-speed driving policy, and places you will revisit. Sketch the route in `answers.md` and predict its strengths and weaknesses.

Start SLAM using your configuration as shown in the runbook. In RViz2, set **Fixed Frame** to `map` and display `/map`, the robot, and the laser scan. Use keyboard teleoperation from Lab 2 to explore. Stop at turns when needed, observe map growth, and revisit a distinctive area. Save comparable screenshots before and after revisiting; report whether a correction is actually visible rather than assuming loop closure occurred.

Stop the robot, then save the map from this lab directory:

```bash
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/map_a" --ros-args -p use_sim_time:=true
```

`-f` sets the output basename. Keep both the generated YAML metadata and its referenced image. Inspect the YAML's `image`, `resolution`, `origin`, `negate`, and occupancy thresholds. Open the image and verify that it contains the explored world.

### 4. Build map B with one deliberate change

Plan a second route that changes one exploration factor, such as revisiting a distinctive area versus making a single pass. Keep world, initial pose, SLAM configuration, speed policy, and approximate duration matched. Do not use an aggressive or collision-seeking route.

Stop teleoperation and SLAM, shut down the simulator, and repeat Mapping mode from a fresh launch. This clears both the robot pose and the mapper's previous state. Reuse the same configuration. Execute route B, document deviations, and save `results/map_b` using the same command with a different basename.

### 5. Select and hand off a map

Complete the comparison below. Select a map using your evidence. Copy the selected YAML and image together into `results/selected/`; keep the YAML's relative `image` reference valid. Record the selected YAML's absolute WSL path for Lab 5.

Verify that the image named by the copied YAML exists and opens. The final reuse check is loading this exact YAML in Lab 5 and localizing on it. Do not substitute the simulator's supplied map for your map.

## Experiment / Quantitative Analysis

Before collecting data, select two identifiable wall segments in the shared region explored by both routes. Obtain reference lengths from the instructor-validated world geometry or another documented independent source; measurements from your SLAM map are not ground truth.

Measure the corresponding wall endpoint coordinates on each map using RViz2's **Publish Point** tool and inspect `/clicked_point`. Record endpoints in metres and compute segment lengths and absolute reference errors. Use the same endpoints and method for both maps. Report map resolution, reference source, and endpoint-selection uncertainty; do not claim accuracy finer than the measurement method supports.

If no independent reference is available, report the difference in each wall length between maps as a consistency measure, explicitly labeled **not accuracy**. Also record route duration, visible missing regions, wall duplication, collisions, and whether a revisit visibly changed the map. Choose your map based on these results, not visual attractiveness alone.

## Engineering Questions

1. Why does a valid scan topic still need TF and timestamps for mapping?

   <details>
   <summary>Show answer</summary>

   Scan coordinates are expressed in the sensor frame. The mapper needs the sensor-to-base relationship and robot motion at the scan time to place them consistently. A high arrival rate cannot compensate for a missing transform or incorrect clock.

   </details>

2. Why can revisiting an area help, and why is a visible correction not guaranteed?

   <details>
   <summary>Show answer</summary>

   Matching a revisited area can constrain accumulated drift. A useful correction depends on recognizable geometry and successful data association; a revisit alone does not prove a loop-closure constraint was accepted.

   </details>

3. Which map would you hand to the navigation team, and what evidence supports that choice?

   <details>
   <summary>Show answer guidance</summary>

   Use your measured geometry errors or consistency differences, coverage, and observed artifacts. Identify a limitation of the selected map and the YAML/image pair needed to reproduce your choice. The answer depends on your runs.

   </details>

## Success Criteria

- [ ] Your Kalman predict/update implementation passes your one-step check and produces tuning/dropout results.
- [ ] SLAM runs with your saved configuration and verified sensor/time/TF inputs.
- [ ] Two maps come from fresh runs with planned, comparable routes.
- [ ] Both maps include an image and matching YAML metadata.
- [ ] Two wall measurements per map are compared using a documented method.
- [ ] A selected map and its limitations are ready for Lab 5.

## What to Submit

- completed Kalman-filter code, your estimation runner, one-step check, Q/R table, and normal/dropout metrics/plots;
- `config/slam.yaml`;
- both YAML/image pairs and the selected map pair;
- route plans, input checks, and quantitative tables in `answers.md`;
- comparable screenshots and a short mapping demonstration;
- answers to the three engineering questions.

The Kalman implementation and SLAM map experiments are both required. The former standalone sensor-statistics exercise remains an optional extension in the [legacy archive](../optional_legacy/previous_lab_sequence/README.md).

## Troubleshooting

- Missing scans or frozen timestamps: check Gazebo play state, bridge, and simulation clock.
- Detached scans: compare message frame IDs with TF and the configured base frame.
- Doubled walls: check time/TF first, then investigate speed, odometry, and scan alignment.
- Competing `map -> odom` publishers: stop AMCL; mapping uses SLAM as that transform's owner.
- Empty saved map: confirm `/map` is updating and read the map-saver error before continuing.

**INSTRUCTOR VALIDATION REQUIRED:** run both mapping trials and the Lab 5 handoff on the course image, confirming exact frames, installed launch arguments, teleoperation type, and reference wall geometry. See the [validation checklist](../docs/INSTRUCTOR_VALIDATION.md).

Continue to [Lab 5 - Navigation with Nav2](../lab05_navigation/README.md).
