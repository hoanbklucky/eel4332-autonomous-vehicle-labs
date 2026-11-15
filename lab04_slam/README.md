# Lab 4 - Build a Map with SLAM

## Mission

**Build, evaluate, and save a map that another team could use for navigation.** You will configure SLAM Toolbox, drive two planned exploration routes, measure map quality, and select a map for Lab 5.

## Learning Objectives

- connect LiDAR, odometry, TF, and simulation time to a working mapper;
- edit and run a reproducible SLAM configuration;
- compare two exploration strategies using measured evidence;
- export a map and verify that its image and metadata can be reused.

## Prerequisites

Complete [setup](../lab00_setup/README.md) and Labs [1](../lab01_ros2_gazebo_fundamentals/README.md), [2](../lab02_turtlebot_playground/README.md), and [3](../lab03_vehicle_modeling/README.md). You must be able to teleoperate and stop TurtleBot. Update course files using [the repository update guide](../docs/UPDATING_COURSE_REPOSITORY.md).

## Background

SLAM estimates robot pose and a map together. Odometry connects observations over motion; LiDAR provides evidence about nearby geometry. TF supplies the coordinate relationships needed to place each scan at its measurement time.

The required work focuses on configuring, building, testing, and evaluating the mapping system. The separate Kalman-filter implementation is an optional extension. Derivations, detailed sensor theory, TF examples, and reading checks with collapsed answers are in [OPTIONAL_BACKGROUND.md](OPTIONAL_BACKGROUND.md). They are supporting references, not extra submissions.

## Provided Files

- `src/kalman_filter.py`: optional student predict/update starter.
- `src/make_estimation_data.py` and `src/localization_metrics.py`: provided data/metric utilities.
- [Optional Kalman experiment](ALGORITHM_EXPERIMENT.md): optional implementation, verification, tuning, and dropout tasks.
- `answers.md`: experiment plans and evidence tables.
- `config/`: your saved SLAM parameter file.
- `results/`: your maps, measurements, and screenshots.

## Step-by-Step Procedure

### 1. Open terminals and prepare the configuration

Use **VS Code's integrated terminal while connected to WSL** (recommended), or a separate **Ubuntu/WSL terminal**. Both work. In VS Code, confirm **WSL: Ubuntu** at the lower left and choose **Terminal → New Terminal**. Use the **+** button to open additional terminals. Do not use PowerShell.

In **every new terminal**, run:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs/lab04_slam
```

Use your actual repository path if different. Save all files before updating. For a clean working tree on course `main`, `git pull --ff-only origin main` gets the latest instructions; preserve any local work before pulling.

In **Terminal 1**, prepare the configuration once:

```bash
mkdir -p config results
cp -n "$(ros2 pkg prefix --share slam_toolbox)/config/mapper_params_online_async.yaml" config/slam.yaml
code config/slam.yaml
```

`cp -n` preserves an existing configuration. In the YAML, check `scan_topic: /scan`, `odom_frame: odom`, `map_frame: map`, and `base_frame: base_footprint` against the frames checked below. Record these values and `resolution` in `answers.md`. Keep the other defaults.

### 2. Start Gazebo, check TF, and start SLAM

First stop previous simulator, teleoperation, SLAM, and navigation launch processes with **Ctrl+C** in their terminals.

**Terminal 1 — simulator (leave running):**

```bash
ros2 launch nav2_bringup tb3_simulation_launch.py \
  headless:=False autostart:=False slam:=False use_sim_time:=True
```

Gazebo and RViz2 should open. Ensure Gazebo is playing. `autostart:=False` leaves AMCL and Nav2 lifecycle nodes unconfigured rather than starting navigation. `slam:=False` prevents this launch from starting a mapper; you will start one separately. Do not click **Startup**, call the navigation/localization lifecycle managers, or send **Nav2 Goal** commands during mapping.

**Terminal 2 — input checks:** run the common source/`cd` commands from Step 1, then:

```bash
ros2 lifecycle get /amcl
ros2 lifecycle get /controller_server
ros2 topic echo /scan --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_footprint
```

AMCL and the controller should report **unconfigured** (neither may be active). Scans and odometry should print messages. The last command checks the robot's odometry-to-base transform: wait for repeated translation/rotation output, then press **Ctrl+C** to stop only this diagnostic.

If `odom -> base_footprint` remains missing after the robot loads, run the course's Gazebo-to-ROS TF bridge in **Terminal 2** and leave it running:

```bash
ros2 run ros_gz_bridge parameter_bridge \
  '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
```

Use another sourced terminal for the remaining checks. Do not add this bridge if TF already works. If it still fails, stop and check the simulator/bridge output before continuing.

Check the base transform, then press **Ctrl+C** after it prints translation/rotation output:

```bash
ros2 run tf2_ros tf2_echo base_footprint base_link
```

Read the LiDAR's actual frame name:

```bash
ros2 topic echo /scan --once --field header.frame_id
```

The course TurtleBot reports **`base_scan`**. Check its transform with:

```bash
ros2 run tf2_ros tf2_echo base_link base_scan
```

Expect repeated translation/rotation output; the tested setup reports approximately `[-0.064, 0.000, 0.122]` m and zero rotation. An initial “frame does not exist” message can appear while the listener receives TF; if transforms follow, the check succeeded. `At time 0.0` is normal for this static sensor mounting transform. Press **Ctrl+C** after confirming output.

This verifies `odom -> base_footprint -> base_link -> base_scan`. If your scan reports another frame, replace only `base_scan` in the command with that exact name. If errors persist without transform output, check the simulator and robot-state publisher before continuing.

**Terminal 3 — standalone mapper:** run the common source/`cd` commands, then leave this running:

```bash
ros2 launch slam_toolbox online_async_launch.py \
  use_sim_time:=True slam_params_file:="$PWD/config/slam.yaml"
```

**Terminal 4 — verify mapping:** run the common source/`cd` commands, then:

```bash
ros2 param get /slam_toolbox use_sim_time
ros2 topic echo /map --once --qos-durability transient_local
ros2 run tf2_ros tf2_echo map base_link
```

Expect `True`, a map message, and repeated transforms. Stop `tf2_echo` with **Ctrl+C**. If the mapper exposes lifecycle states and produces no map, run `ros2 lifecycle get /slam_toolbox`; it should be **active**. If **unconfigured**, run `ros2 lifecycle set /slam_toolbox configure`, then `ros2 lifecycle set /slam_toolbox activate`; if already **inactive**, run only `activate`. Do not start a second mapper.

In RViz2, set **Global Options → Fixed Frame** to `map`. Enable/add **Map** (topic `/map`), **LaserScan** (topic `/scan`), **RobotModel**, and **TF**. The scan should align with nearby mapped walls. Navigation status warnings are expected because navigation is not running.

Before driving, record the scan frame, two advancing scan timestamps, and its rate:

```bash
ros2 topic echo /scan --once
ros2 topic echo /scan --once
ros2 topic info /scan --verbose
ros2 topic hz /scan
```

Stop `hz` after about 10 seconds with **Ctrl+C**. Record the publisher/bridge and a consumer in `answers.md`.

**Terminal 4 — keyboard driving:** after the checks finish:

```bash
ros2 topic info /cmd_vel
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

The course expects `geometry_msgs/msg/Twist`. If the topic instead uses `TwistStamped`, run the keyboard node with `--ros-args -p stamped:=true -p use_sim_time:=true` appended, provided your installed keyboard package supports `stamped`; otherwise stop and ask the instructor. Do not mix message types.

Keep keyboard focus in Terminal 4. Use **i** forward, **j/l** turn, **k** stop, and **z** repeatedly to reduce speed. Drive slowly, stop before switching windows, and verify odometry changes during a short drive.

### 3. Build map A

Plan a route before driving. Define the starting pose, regions to cover, approximate duration, low-speed driving policy, and places you will revisit. Sketch the route in `answers.md` and predict its strengths and weaknesses.

With the simulator, SLAM, and keyboard nodes from Step 2 running, use keyboard teleoperation to explore. Stop at turns when needed, observe map growth, and revisit a distinctive area. Save comparable screenshots before and after revisiting; report whether a correction is actually visible rather than assuming loop closure occurred.

Press **k** in the keyboard terminal to stop the robot. Open **Terminal 5**, run the common source/`cd` commands from Step 1, and save the map:

```bash
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/map_a" --ros-args -p use_sim_time:=true
```

`-f` sets the output basename. Keep both the generated YAML metadata and its referenced image. Inspect the YAML's `image`, `resolution`, `origin`, `negate`, and occupancy thresholds. Open the image and verify that it contains the explored world.

### 4. Build map B with one deliberate change

Plan a second route that changes one exploration factor, such as revisiting a distinctive area versus making a single pass. Keep world, initial pose, SLAM configuration, speed policy, and approximate duration matched. Do not use an aggressive or collision-seeking route.

Press **k** to stop motion, then **Ctrl+C** in the keyboard, mapper, optional TF-bridge, and simulator terminals. Repeat Step 2 from a fresh launch at the same starting pose. This clears both the robot pose and the mapper's previous state. Reuse the same configuration. Execute route B, document deviations, and save it in Terminal 5:

```bash
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/map_b" --ros-args -p use_sim_time:=true
```

### 5. Select and hand off a map

Complete the comparison below. Select a map using your evidence. Copy the selected YAML and image together into `results/selected/`; keep the YAML's relative `image` reference valid. For example, if choosing map A and the generated image is `map_a.pgm`:

```bash
mkdir -p results/selected
cp results/map_a.yaml results/map_a.pgm results/selected/
realpath results/selected/map_a.yaml
```

Use map B's filenames if selected; use the actual image extension named by the YAML. Record the printed absolute YAML path for Lab 5.

Verify that the image named by the copied YAML exists and opens. The final reuse check is loading this exact YAML in Lab 5 and localizing on it. Do not substitute the simulator's supplied map for your map.

## Experiment / Quantitative Analysis

Before collecting data, select two identifiable wall segments in the shared region explored by both routes. Obtain reference lengths from the instructor-validated world geometry or another documented independent source; measurements from your SLAM map are not ground truth.

Measure the corresponding wall endpoint coordinates on each map using RViz2's **Publish Point** tool and inspect `/clicked_point` in Terminal 5 with `ros2 topic echo /clicked_point`. Stop the command with **Ctrl+C** after recording the endpoints. Record endpoints in metres and compute segment lengths and absolute reference errors. Use the same endpoints and method for both maps. Report map resolution, reference source, and endpoint-selection uncertainty; do not claim accuracy finer than the measurement method supports.

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

- [ ] SLAM runs with your saved configuration and verified sensor/time/TF inputs.
- [ ] Two maps come from fresh runs with planned, comparable routes.
- [ ] Both maps include an image and matching YAML metadata.
- [ ] Two wall measurements per map are compared using a documented method.
- [ ] A selected map and its limitations are ready for Lab 5.

## What to Submit

- `config/slam.yaml`;
- both YAML/image pairs and the selected map pair;
- route plans, input checks, and quantitative tables in `answers.md`;
- comparable screenshots and a short mapping demonstration;
- answers to the three engineering questions.

Only the SLAM map experiments above are required; the Kalman implementation is optional. The former standalone sensor-statistics exercise remains an optional extension in the [legacy archive](../optional_legacy/previous_lab_sequence/README.md).

## Troubleshooting

- Missing scans or frozen timestamps: check Gazebo play state, bridge, and simulation clock.
- Detached scans: compare message frame IDs with TF and the configured base frame.
- Doubled walls: check time/TF first, then investigate speed, odometry, and scan alignment.
- Competing `map -> odom` publishers: stop AMCL; mapping uses SLAM as that transform's owner.
- Empty saved map: confirm `/map` is updating and read the map-saver error before continuing.

**INSTRUCTOR VALIDATION REQUIRED:** run both mapping trials and the Lab 5 handoff on the course image, confirming exact frames, installed launch arguments, teleoperation type, and reference wall geometry. See the [validation checklist](../docs/INSTRUCTOR_VALIDATION.md).

Continue to [Lab 5 - Navigation with Nav2](../lab05_navigation/README.md).
