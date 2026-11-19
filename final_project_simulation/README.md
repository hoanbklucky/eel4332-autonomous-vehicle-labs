# Final Project — Indoor and Outdoor Goosebot Navigation

Use **`final-project-indoor-outdoor`**. Complete IST first, then campus. In each world: build your own SLAM map, restart with AMCL/Nav2, reach **two destinations and return Home**. Also complete one IST blocked-route attempt, one indoor LiDAR comparison, and the campus GPS position check below. Physical SLAM/Nav2 and mission-client coding are optional; lane following remains the hardware component.

## Before you start

Complete Labs 4–5. Use your existing Ubuntu/WSL, ROS 2 Jazzy and Gazebo Harmonic installation. Work in your course fork; `origin` is your fork and `upstream` is the public course repository. Save your edits before updating; do not discard model or map changes.

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git branch --show-current
git status --short
```

The branch should be `final-project-indoor-outdoor`. If it differs or files are modified, follow [the update guide](../docs/UPDATING_COURSE_REPOSITORY.md) first. With the correct branch and a clean working tree:

```bash
git fetch upstream &&
git merge --no-edit upstream/final-project-indoor-outdoor &&
git merge-base --is-ancestor upstream/final-project-indoor-outdoor HEAD &&
echo "Current checkout includes the latest fetched final-project-indoor-outdoor course commits"
git log -1 --oneline
```

**Command breakdown:** `fetch` downloads course updates; `merge` incorporates them; `merge-base --is-ancestor` checks they are included; `&&` continues only after success. Updating Git files does not rebuild your robot.

## Terminal conventions

Use four Ubuntu/WSL terminals: **1 Gazebo**, **2 SLAM or AMCL/Nav2**, **3 RViz**, **4 teleop/checks**. Open VS Code with `code .` from this checkout and confirm **WSL: Ubuntu**.

| Syntax | Meaning |
|---|---|
| `source /opt/ros/jazzy/setup.bash` then `source ~/goosebot_ws/install/setup.bash` | Enable ROS, then this built workspace in each new ROS terminal. |
| `ros2 run PACKAGE PROGRAM` / `ros2 launch PACKAGE FILE` | Run one program / a launch description. Local launch files may use an absolute path. |
| `name:=value` / `--ros-args -p name:=value` | A launch argument / a ROS parameter. `use_sim_time:=true` uses Gazebo's clock. |
| `~`, `$PWD`, `$(...)` | Home directory, current directory, and command output. Quotes keep a path together. |
| Trailing `\` | Continue the same command on the next line; copy all lines. |
| Ctrl+C | Stop the foreground program in its launch terminal. Closing only a GUI can leave processes running. |

**Before switching worlds or modes:** stop motion, save maps, then Ctrl+C teleop, SLAM/Nav2, RViz and Gazebo. Wait for prompts. Run only one simulator and one owner of `map → odom` (SLAM while mapping, AMCL while navigating). The perfect-map/ground-truth mode is optional practice only.

## 1. Setup — once, then rebuild when needed

Install missing packages:

```bash
sudo apt update
sudo apt install -y git python3-colcon-common-extensions python3-rosdep \
  ros-jazzy-ros-gz ros-jazzy-xacro ros-jazzy-robot-state-publisher \
  ros-jazzy-robot-localization ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-teleop-twist-keyboard python3-yaml
source /opt/ros/jazzy/setup.bash
```

**First setup only:** copy the complete pinned Goosebot package and build it. Existing users keep their edited package and rerun only the build helper.

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
mkdir -p final_project_simulation/src
# Run this clone/copy only once. Keep your existing edited package on later updates.
git clone --filter=blob:none --sparse --single-branch --branch nav2 \
  https://github.com/hoanbklucky/goose.git /tmp/eel4332-goose-source
git -C /tmp/eel4332-goose-source sparse-checkout set 11_simulation/ros2_ws/src/goosebot_0
git -C /tmp/eel4332-goose-source checkout bffaf3cdf2b38f3b5a53a977064e0c787e046ff7
cp -r --update=none /tmp/eel4332-goose-source/11_simulation/ros2_ws/src/goosebot_0 final_project_simulation/src/
# Omit the redundant packaged snapshot; the extracted source is already copied.
rm -f final_project_simulation/src/goosebot_0/goosebot-simulation.zip
# Link, fix script permissions, install dependencies, and build this source copy.
bash final_project_simulation/goosebot/build_student_workspace.sh
```

**Command breakdown:** the sparse clone selects the complete `goosebot_0` package; the pinned commit fixes its starting version; `cp -r --update=none` preserves existing destination files. The helper links this source into `~/goosebot_ws`, configures LiDAR/bridges, fixes executable permissions and the legacy GPS noise, installs dependencies, and builds.

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 pkg prefix goosebot_0
ros2 pkg executables goosebot_0
```

Expect the prefix inside `~/goosebot_ws` and executables `cmd_vel_to_odom.py`, `ground_truth_map_odom_bridge.py`, `stereo_camera_info_fixer.py`. Do not copy old build/install/log directories. 

## 2. Use the supplied robot

LiDAR, `/scan` bridge, wheel visualization and GPS already exist after setup. **No sensor XML needs to be pasted.** Keep defaults for baseline mapping/navigation. After source/configuration changes, stop launches, rerun the Step 1 helper, source the workspace and relaunch; saving a file does not change a spawned robot.

## 3. Launch the current part’s world — Terminal 1

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/world.launch.py" \
  world:="$PWD/final_project_simulation/ist/ist.sdf"
```

**Command breakdown:** `world.launch.py` starts Gazebo, spawns Goosebot and starts its ROS interfaces; `world:=` selects the SDF file. **Part B:** change only the world path to `campus/campus.sdf`. Expect `GOOSEBOT SPAWNED`. If a server is already running, stop its launch before retrying.

To find the robot: collapse the building in Gazebo's Entity Tree, right-click **goosebot → Move To**, then zoom. This moves the camera.

<a id="goosebot-readiness-check"></a>

## 4. Short readiness check — before mapping

With Gazebo playing, check in Terminal 2:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 topic echo /scan --once --field header.frame_id
ros2 topic hz /scan
```

Expect `lidar_link` and arriving scans. Ctrl+C the rate check, then run these one at a time:

```bash
ros2 run tf2_ros tf2_echo base_footprint lidar_link
ros2 run tf2_ros tf2_echo odom base_footprint
```

**Command breakdown:** `echo --once --field` prints one selected message field; `hz` measures wall-clock arrival rate; `tf2_echo A B` reports frame B relative to A. Numerical TF should appear after discovery; Ctrl+C each continuous check. Slow simulation produces less than the configured 10 Hz wall-clock scan rate.

Open RViz in Terminal 3:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
rviz2 --ros-args -p use_sim_time:=true
```

For your first run, add these yourself using **Add → By display type → rviz_default_plugins**:

| Display | Setting |
|---|---|
| LaserScan | Topic `/scan`; Best Effort reliability |
| RobotModel | Description Source: Topic; Description Topic: `/robot_description` |
| TF | Enable for frame checks; hide later if cluttered |
| Map — after SLAM starts | Topic `/map`; Reliable / Transient Local if needed |

Before SLAM, use **Fixed Frame: odom** and disable Map. Choose **Views → TopDownOrtho** for an overhead view. Expect the robot and scan points without persistent TF errors.

Drive briefly in Terminal 4:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.1 -p turn:=0.5
```

**Command breakdown:** `speed` and `turn` set 0.1 m/s and 0.5 rad/s. Focus this terminal: lowercase **i** forward, **j/l** turn, **k** stop. Speed-setting keys alone do not move the robot. Stop with k, then Ctrl+C. Keep Gazebo/RViz open; no separate readiness submission is required.

## 5. Map and save

**Terminal 2 — start SLAM:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true \
  slam_params_file:="$PWD/final_project_simulation/goosebot/slam_goosebot.yaml"
```

**Command breakdown:** `online_async_launch.py` starts LiDAR SLAM; `slam_params_file:=` loads course settings. In RViz change **Fixed Frame to map**, enable Map and set its **Topic to /map**. A blank topic causes “Empty topic name”; a red Status row is not the editable Topic field.

Restart teleop in Terminal 4. Explore a connected route to your two destinations, revisit an earlier area, and cover an alternative IST route. Full-building/full-campus exploration is unnecessary.

<details>
<summary>Expected mapping views</summary>

![IST mapping in progress](images/ist_mapping.png)

![Campus mapping in progress](images/campus_mapping.png)

The occupancy map grows as you drive. Scans should align with nearby boundaries; unexplored space remains unknown.

</details>

**Save the RViz layout:** `mkdir -p ~/rviz_configs`, then **File → Save Config As** → `~/rviz_configs/goosebot_mapping.rviz`. Next time load it with `rviz2 -d ~/rviz_configs/goosebot_mapping.rviz --ros-args -p use_sim_time:=true`. Configure displays once; reuse afterward. This saves the display layout, not the SLAM map.

Stop robot motion and save the map in another sourced terminal while SLAM and Gazebo stay running:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs/final_project_simulation
mkdir -p results
MAP_NAME=ist_map  # Part B: change this to campus_map
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/$MAP_NAME" \
  --ros-args -p use_sim_time:=true
```

**Command breakdown:** `MAP_NAME` chooses `ist_map` or `campus_map`; `-f` sets the output basename. The saver writes YAML plus an image. Keep both together and save each world separately.

## 6. Restart and navigate

Stop all launches as described above. Relaunch **the same world** in Terminal 1; leave SLAM stopped.

**Terminal 2 — AMCL/Nav2:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/navigation.launch.py" \
  map:="$PWD/final_project_simulation/results/ist_map.yaml"
```

**Command breakdown:** the wrapper loads your map automatically and starts AMCL/Nav2. For campus use `results/campus_map.yaml`. Do not manually call a load-map service during normal startup.

**Terminal 3 — navigation RViz:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
rviz2 -d "$(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz" \
  --ros-args -p use_sim_time:=true
```

**Command breakdown:** `$(ros2 pkg prefix ...)` finds Nav2's installed package; `-d` loads its layout. Expect **Nav2 Goal**, **2D Pose Estimate**, and the **Navigation 2** panel.

1. Set **2D Pose Estimate** at the robot's starting position and heading.
2. Confirm `/scan` points overlap saved-map walls. Brief missing-map/TF warnings before initialization can occur.
3. Send a nearby **Nav2 Goal**, then visit **two chosen destinations and Home**; wait 3 seconds at each destination. Keep teleop stopped.
4. Select coordinates on **your SLAM map**; do not blindly use Gazebo/`mission.json` coordinates.

Save this layout separately as `~/rviz_configs/goosebot_navigation.rviz`; load it with `rviz2 -d ...` next time. Initialize AMCL again each session. **Navigation/Localization: active** indicates readiness; **reached/succeeded** indicates completion.

## 7. IST blocked route

Restart with `ist/ist_blocked.sdf`, keeping your baseline **IST map**, robot settings and goals. Restart AMCL/Nav2 and set the initial pose; do not remap the barrier. Show whether the robot detours, stops, recovers or fails. Campus blocked-route testing is optional.

## 8. Indoor LiDAR comparison

After IST baseline navigation, open `final_project_simulation/src/goosebot_0/urdf/robot.urdf.xacro`. Inside **lidar_sensor**, change only **horizontal/samples: 720 → 360** or **update_rate: 10 → 5**.

Stop launches, run the Step 1 helper, source and relaunch IST. Compare scans under similar conditions. Save **one baseline and one changed screenshot**, plus two sentences describing the observed effect. Restore the baseline and rebuild before campus.

### 9. Part B — inspect GPS outdoors

**Purpose:** use GPS as an independent geographic position reference and compare its stationary noise with the apparent drift of local odometry after a loop. GPS already exists; add no XML. **This activity does not fuse GPS into SLAM or AMCL/Nav2.**

After campus mapping/navigation, stop all launches. Start a fresh campus world using Step 3 with `campus/campus.sdf`. Leave SLAM/Nav2 stopped; use Terminal 4 teleop for this short measurement run.

**Terminal 2 — GPS and odometry readings:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 topic echo /gps/fix --once
ros2 topic echo /odometry/filtered --once
```

**Command breakdown:** the first prints one geographic fix; the second prints the local odometry estimate. For odometry record **pose.pose.position.x/y**, not twist/velocity. To collect several GPS messages, omit `--once` and Ctrl+C after at least five.

**Do these three stops in the same uninterrupted run:**

| Stop | What to do | What to record |
|---|---|---|
| A — Home | Stop on a clearly identifiable Home marker; note robot heading | At least 5 GPS fixes; mean latitude/longitude; one odometry x/y |
| B — nearby landmark | Drive a short safe route, stop several meters away | Same readings; a screenshot identifying the landmark |
| C — Home again | Complete a loop and return as closely as possible to A's position and heading using the visible Gazebo marker | Same readings; a screenshot showing the return |

Use the means to estimate displacement from A near this campus latitude:

- **North (m) ≈ 111,000 × (latitude − latitude at A)**.
- **East (m) ≈ 98,000 × (longitude − longitude at A)**.
- **Odometry change:** subtract A's odometry x/y from B or C's odometry x/y. Compare the **distance** `sqrt(dx² + dy²)`; odometry axes need not align with geographic north/east.

**Submit one small A/B/C table and three sentences:**

1. How much did GPS vary while stationary, and was A → B movement distinguishable from that noise?
2. At the return to Home, what were the GPS and odometry distances from their starting readings? Describe visible residual drift or the absence of a clear difference. The physical return and GPS mean are approximate; neither is an exact error measurement.
3. How could an independent global position reference help an outdoor robot when local odometry drifts or LiDAR has few landmarks? GPS fusion could constrain position, while LiDAR still detects obstacles. **Do not claim that GPS improved this run's map or navigation: it was measured, not fused.**

Expected readings stay near **28.1485°, −81.8495°**, with meter-scale variation. `status: 0` means a fix; `position_covariance_type: 0` means unknown uncertainty, not perfect accuracy. Noisy altitude may be negative. The arena is scaled; these are synthetic coordinates, not real campus navigation data.

<details>
<summary>If GPS jumps by degrees, or no messages arrive</summary>

Horizontal GPS noise must be **0.000015 degrees** in `gps_sensor → navsat → position_sensing → horizontal → noise → stddev`; vertical noise stays **3.0 m**. Gazebo Sensors 8 applies horizontal noise in degrees. Update this branch, stop launches, rerun the Step 1 helper, source and respawn the robot. Existing readings from the old `1.5` setting must be recollected. Check `ros2 topic info /gps/fix --verbose` for the bridge and `ros2 topic hz /gps/fix` for arrivals; 5 Hz simulated becomes lower wall-clock Hz in slow simulation. World NavSat settings already reside in `campus/campus.sdf`, not Xacro.

</details>

### 10. Explain the system

Submit one shared **2–3 page explanation plus a topic table/diagram**, using [the system worksheet](SYSTEM_EXPLANATION.md). Explain sensor roles, actual EKF inputs, TF, SLAM versus AMCL, and goal → planning → control → motion. Include your LiDAR/GPS observations and indoor/outdoor comparison. GPS fusion is not a required implementation.

## What to submit

- **Two videos, about 2–3 minutes each:** IST and campus; mapping/revisit, AMCL alignment, two reached destinations and Home. Include the IST blocked attempt and brief sensor evidence.
- **Fork/code and evidence:** model/configuration, separate IST/campus YAML+image maps, commands/goals, two LiDAR screenshots, GPS A/B/C table and return-to-Home evidence. Exclude build/install/log, databases and bags.
- **Shared system explanation:** include each member's contribution and one problem/fix. AI assistance is allowed; test its output and explain your work in your own words.

| Assessment | Weight |
|---|---:|
| Mapping and AMCL in both worlds | 25% |
| Navigation in both worlds and IST blocked-route evidence | 25% |
| Indoor LiDAR comparison and outdoor GPS activity | 15% |
| System understanding and evidence-based explanation | 30% |
| Reproducibility and contributions | 5% |

<a id="goosebot-warm-up"></a>

## Optional reference

The practice-arena/perfect-map warm-up has **no required submission**. See the [detailed command and troubleshooting reference](COMMAND_REFERENCE.md) for that exercise, extra output examples, model diagnostics and full command breakdowns. All required steps are above. A live demonstration of **improved mapping/navigation from GPS fusion** would require a separately configured and tested comparison; this baseline does not consume GPS.

**Instructor validation:** the GPS noise fix has source-level checks and instructor-observed reasonable samples. The new return-to-Home comparison still needs a course-machine pilot. No improvement in mapping/navigation from GPS fusion has been demonstrated by this assignment.
