# Final Project — Goosebot SLAM and Delivery in Simulation

## Open in VS Code through WSL

After cloning the repository, open **Windows Terminal / PowerShell**, run `wsl`, then run these commands in **Ubuntu/WSL**:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
code .
```

Confirm VS Code shows **WSL: Ubuntu** (or your Ubuntu distribution) in the lower-left corner. Open `final_project_simulation/README.md` in Explorer. Choose **Terminal → New Terminal**; when working from this lab directory, run:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs/final_project_simulation
```

Use that Ubuntu terminal for the commands below; follow any later `cd` commands as written. This assumes VS Code is installed on Windows with the **WSL extension**. If the repository is not cloned yet, complete Lab 00's clone step first.

## Mission

Use the **provided Goosebot model**, add a simulated **2-D LiDAR**, build your own SLAM map, and use **AMCL + Nav2** to reach three delivery locations and return home. Choose the supplied **IST interior** or **Florida Poly campus** world. Physical Goosebot SLAM/Nav2 is not required; your lane-following work is the hardware component.

## Learning objectives

Connect a robot model, sensors, bridges, TF, odometry, SLAM, localization, and navigation. Explain your own changes and diagnose problems rather than only repeating TurtleBot commands.

## Prerequisites and background

Complete Labs 4–5, then the required Goosebot warm-up in Step 1b below. Keep your existing Ubuntu 24.04/WSL, ROS 2 Jazzy, and Gazebo Harmonic installation. Use VS Code's **WSL: Ubuntu integrated terminal** or a separate **Ubuntu/WSL terminal**; both work. Each long-running launch needs its own terminal. Commands have no leading `# Final Project — Goosebot SLAM and Delivery in Simulation

## Mission

Use the **provided Goosebot model**, add a simulated **2-D LiDAR**, build your own SLAM map, and use **AMCL + Nav2** to reach three delivery locations and return home. Choose the supplied **IST interior** or **Florida Poly campus** world. Physical Goosebot SLAM/Nav2 is not required; your lane-following work is the hardware component.

## Learning objectives

Connect a robot model, sensors, bridges, TF, odometry, SLAM, localization, and navigation. Explain your own changes and diagnose problems rather than only repeating TurtleBot commands.

## Prerequisites and background

Complete Labs 4–5, then the required Goosebot warm-up in Step 1b below. Keep your existing Ubuntu 24.04/WSL, ROS 2 Jazzy, and Gazebo Harmonic installation. Use VS Code's **WSL: Ubuntu integrated terminal** or a separate **Ubuntu/WSL terminal**; both work.  prompt. **The course instructions use native WSL/Jazzy for both the warm-up and final. Docker is an optional alternative, not an additional requirement.**

The Goosebot source is [hoanbklucky/goose, nav2 branch](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation). It already supplies the body/wheels, drive plugin, stereo cameras, IMU, forward ToF, command-derived odometry, and EKF. **The narrow forward ToF is not a 360° mapping LiDAR.** Students add that sensor themselves; no completed LiDAR model is supplied here.

The original Goosebot default mode uses a pre-baked map and Gazebo ground-truth localization. **Do not use that mode as your final demonstration.** This project instead uses LiDAR SLAM Toolbox for mapping, then a saved map with AMCL. This differs from the TurtleBot/Cartographer preparation in Lab 4. Stereo RTAB-Map is optional. Do not launch the original `nav2_bringup.launch.py` or `stereo_slam.launch.py` alongside the commands below.

AMCL estimates the robot's pose on a saved map by matching live scans. Nav2's supplied starting configuration uses **NavFn with Dijkstra** for the global path and **DWB** to choose local motion commands. The global costmap follows the full saved map, rather than the original Goosebot's 20 m rolling window. Students must verify/tune the robot footprint and sensor settings.

## Provided files and environment choice

| Environment | Features | Baseline / blocked world |
|---|---|---|
| **IST interior — recommended for a shorter project** | Photo-traced classrooms, oval hallway, two end cross-passages, north/south entrance lobbies and central side exits | `ist/ist.sdf` / `ist/ist_blocked.sdf` |
| **Florida Poly campus** | Geographic footprints, lake chain, roads and causeways; larger mapping area | `campus/campus.sdf` / `campus/campus_blocked.sdf` |
| Optional custom world | Same mission; requires checking collision geometry and a feasible alternative route | See [optional builder guide](CREATE_YOUR_OWN_WORLD.md) |

<details>
<summary>Preview — IST oval hallway and classroom layout</summary>

![IST teaching interior](ist/ist_plan.png)

Classroom identities and relative positions come from the first image's labels/black partitions; the oval hallway, both end cross-passages and central through-passage come from the second image. **Evacuation arrows and colored zone boundaries are excluded from geometry.** Rooms 1045/1048 and 1002/1068 flank the north/south entrance lobbies. Dimensions and doors remain illustrative. Yellow is actual hallway floor, not evacuation routes. **Version 4 replaces earlier IST geometry: rebuild your SLAM map and reselect goals.**

</details>

<details>
<summary>Preview — supplied IST reference images</summary>

![Provided evacuation-plan photograph](ist/images/ist_evacuation_reference.png)
![Provided oval-hallway illustration](ist/images/ist_hallway_reference.png)

These references guide the teaching layout; colored evacuation routes are not walls or navigation maps. North is at the left in the photograph.

</details>

<details>
<summary>Preview — campus layout</summary>

![Geographic campus layout](campus/campus_plan.png)

The campus is uniformly scaled to a 73 × 80 m teaching arena; some newer footprints and all building heights are approximate. Blue water has solid collision geometry. Grass remains traversable.

</details>

Other supplied files: `goosebot/world.launch.py` (world/spawn wrapper), `goosebot/slam_goosebot.yaml`, and `goosebot/nav2_goosebot.yaml` (starting configurations). The worlds' `reference.yaml` files are geometric instructor references, **not student SLAM results**. The existing [mission-client scaffold](../lab05_navigation/src/mission_client.py) remains available as an optional programming extension; its TODOs are not completed for you.

## Step-by-step procedure

### 1. Install missing dependencies and copy the supplied Goosebot source

Run once in Ubuntu/WSL. This supplements your existing installation; no Ubuntu/ROS reinstall or Docker is needed.

```bash
sudo apt update
sudo apt install -y git python3-colcon-common-extensions python3-rosdep \
  ros-jazzy-ros-gz ros-jazzy-xacro ros-jazzy-robot-state-publisher \
  ros-jazzy-robot-localization ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-teleop-twist-keyboard ros-jazzy-rtabmap-ros
source /opt/ros/jazzy/setup.bash
```

In **your fork** of the course repository, copy only the provided source package (not its old build/install/virtual-environment directories). The pinned revision makes the starting model reproducible:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
mkdir -p final_project_simulation/src
# Run this clone/copy only once. Keep your existing edited package on later updates.
git clone --filter=blob:none --sparse --single-branch --branch nav2 \
  https://github.com/hoanbklucky/goose.git /tmp/eel4332-goose-source
git -C /tmp/eel4332-goose-source sparse-checkout set 11_simulation/ros2_ws/src/goosebot_0
git -C /tmp/eel4332-goose-source checkout bffaf3cdf2b38f3b5a53a977064e0c787e046ff7
cp -r -n /tmp/eel4332-goose-source/11_simulation/ros2_ws/src/goosebot_0 final_project_simulation/src/
# Omit the redundant packaged snapshot; the extracted source is already copied.
rm -f final_project_simulation/src/goosebot_0/goosebot-simulation.zip
mkdir -p ~/goosebot_ws/src
ln -s "$PWD/final_project_simulation/src/goosebot_0" ~/goosebot_ws/src/goosebot_0
cd ~/goosebot_ws
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install
source install/setup.bash
ros2 pkg prefix goosebot_0
```

The package lives in your course fork so your model edits can be committed/pushed; the workspace points to it. If the temporary clone or symlink already exists, reuse/check it instead of repeating those commands. If rosdep reports its database is uninitialized, run `sudo rosdep init` once and `rosdep update`, then retry. Do not copy old Docker build output. Rebuild after adding files or changing installation rules.

<a id="goosebot-warm-up"></a>

### 1b. Required Goosebot warm-up — before adding LiDAR

Use **native Ubuntu/WSL + ROS 2 Jazzy**, the package built in Step 1, and the **same `~/goosebot_ws` workspace** as your final. No second installation, Docker setup, or robot-model modification is required for this warm-up. If you already completed Step 1, reuse your package/workspace and preserve your edits.

The supplied maze's **perfect-map mode** provides both a pre-generated map and Gazebo ground-truth global localization. This checks Goosebot operation and Nav2 integration; **it is not SLAM and does not use AMCL**. This mode is allowed for this warm-up only; the final still requires your added LiDAR, your SLAM map, and AMCL.

**Terminal 1 — supplied maze and Goosebot:** stop other simulator/SLAM/navigation launches first.

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 launch goosebot_0 spawn_robot.launch.py \
  world:="$(ros2 pkg prefix goosebot_0)/share/goosebot_0/worlds/maze.world" x:=-0.5
```

**Terminal 2 — manual driving:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Focus Terminal 2, follow its printed keys, and drive a short distance. Stop the robot and quit teleop with Ctrl+C. For a repeatable navigation check, stop Terminal 1 too and relaunch the maze at the original spawn pose.

**Terminal 2 — supplied perfect-map Nav2:** run this after teleop has stopped. Keep its original model-specific configuration; the final's LiDAR configuration is used later.

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 launch goosebot_0 nav2_bringup.launch.py slam:=false use_sim_time:=true \
  map:="$(ros2 pkg prefix goosebot_0)/share/goosebot_0/maps/maze.yaml"
```

**Terminal 3 — RViz:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 launch nav2_bringup rviz_launch.py use_sim_time:=true
```

Use Fixed Frame `map`; set the Map display's topic to **`/projected_map`**. Enable RobotModel with `/robot_description` and TF. The forward ToF, if displayed as LaserScan, is **`/tof_front/scan`** and gives only a narrow beam. There is no student-added `/scan` yet. Do not initialize AMCL with 2D Pose Estimate: the ground-truth bridge supplies `map → odom` in this mode.

**Terminal 4 — check interfaces, then send one goal:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 topic echo /odometry/filtered --once
ros2 topic echo /tof_front/scan --once --field header.frame_id
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: -4.5}, orientation: {w: 1.0}}}}" --feedback
```

Expect odometry/sensor messages, robot movement in Gazebo, and a **SUCCEEDED** action result. You may instead select one reachable free-space Nav2 Goal in RViz. If TF is missing, inspect `ros2 run tf2_ros tf2_echo odom base_footprint` in a sourced terminal; stop the check with Ctrl+C. Resolve warm-up startup/motion problems before modifying the model.

**Evidence:** one screenshot showing successful navigation and **two sentences in your own words** explaining where the map and localization come from, and why this does not demonstrate SLAM/AMCL. An instructor-observed in-class demonstration can replace the submission. No separate video or long report is needed.

**Finish:** stop Nav2, RViz and the maze with Ctrl+C. Continue with Step 2 in this same source/workspace. Keep the warm-up's perfect-map/ground-truth launches stopped while running final-project SLAM or AMCL; each mode must have only one `map → odom` publisher.

<details>
<summary>Optional alternatives — Docker and stereo SLAM</summary>

**Docker is optional for both the warm-up and final.** The required course workflow stays native WSL/Jazzy. Students who already use Docker may follow the [upstream Docker setup](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation#2-docker-setup), use the same pinned source revision as Step 1, run ROS commands inside the container, and adapt paths to its filesystem. Keep source/configuration/maps in a persistent host-mounted workspace, retain changes when containers are recreated, and demonstrate the same required outcomes. Do not copy native or old Docker `build/install/log` directories between environments.

**Stereo RTAB-Map is an optional extension**, not a prerequisite. Its [upstream live-stereo mode](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation#32-mode-b--live-stereo-slam) must run separately from perfect-map localization and the final's LiDAR SLAM/AMCL. Running stereo SLAM does not replace the required final LiDAR integration.

</details>

### 2. Add your 2-D LiDAR — required student work

Open `final_project_simulation/src/goosebot_0/urdf/robot.urdf.xacro`. Use its existing front ToF sensor as a syntax example, but **add a separate sensor**:

1. Add a `lidar_link` and a fixed joint to `base_link`. Give the sensor a visual shape and a clear mounting position above the chassis. Document your chosen position; keep the laser plane above the robot and below obstacles.
2. Add a Gazebo `gpu_lidar` sensor on that link. Starting specifications: **360° horizontal field of view**, 720 horizontal samples, one vertical sample, 10 Hz, minimum range 0.12 m, maximum range 12 m. Angles are in radians (`-3.14159` to `3.14159`). Use the existing sensor's `<lidar><scan>…</scan><range>…</range></lidar>` structure. Set its topic to `scan`, enable it, and set `<gz_frame_id>lidar_link</gz_frame_id>`.
3. Add this entry to `config/ros_gz_bridge.yaml` in your copied package:

```yaml
- ros_topic_name: /scan
  gz_topic_name: /scan
  ros_type_name: sensor_msgs/msg/LaserScan
  gz_type_name: gz.msgs.LaserScan
  direction: GZ_TO_ROS
```

4. Retain the existing EKF and its `odom → base_footprint` transform. Do not add a second odometry TF publisher. Inspect the model/configuration to understand its command-derived odometry: it is not measured wheel-encoder odometry.
5. Verify the supplied footprint contains the complete robot and your sensor mount; update **both** costmaps if necessary. Record the sensor values, mounting position, and footprint in your short explanation.

Adding other sensors is optional: add a link/joint and Gazebo sensor, bridge its correct message type, and configure a consumer. A visible sensor shape alone does not produce measurements. GPS and stereo cameras are not required by this LiDAR workflow.

### 3. Launch your selected world — Terminal 1

Stop all previous Gazebo, TurtleBot, SLAM, teleop, and navigation launches with Ctrl+C before starting. Closing the Gazebo window alone can leave a server running. Use this Goosebot launch, **not** the old TurtleBot campus launch:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/world.launch.py" \
  world:="$PWD/final_project_simulation/ist/ist.sdf"
```

For campus, replace the final path with `final_project_simulation/campus/campus.sdf`. The wrapper reads the home pose from the world's adjacent `mission.json` and adds mesh lookup paths. Keep the entire world directory together. Goosebot does **not** need `TURTLEBOT3_MODEL`.

### 4. Check the sensor and TF — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 topic echo /scan --once --field header.frame_id
ros2 topic hz /scan
```

Expect `lidar_link` and approximately your configured rate while Gazebo is playing. Stop `hz` with Ctrl+C, then run these one at a time (Ctrl+C after each check):

```bash
ros2 run tf2_ros tf2_echo base_footprint lidar_link
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 topic echo /odometry/filtered --once
```

Expect numerical transforms and odometry. A brief startup warning can resolve when TF arrives; persistent warnings need fixing. If the reported scan frame differs, correct the sensor frame/TF configuration. In RViz2, use Fixed Frame `odom`, add LaserScan `/scan`, and verify walls appear in the correct direction as you drive.

### 5. Build and save your map

**Terminal 2 — mapping** (after the checks):

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true \
  slam_params_file:="$PWD/final_project_simulation/goosebot/slam_goosebot.yaml"
```

**Terminal 3 — driving:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Click inside Terminal 3 and follow **its printed key layout** (different from TurtleBot teleop). Start slowly. Map all mission routes and revisit an earlier area. For IST, cover both halves of the oval, both end cross-passages, the north/south entrance lobbies, and the central passage through both side exits; classroom interiors are optional. For campus, cover the delivery routes and alternative crossings; every remote corner is unnecessary.

**Terminal 4 — visualization:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
rviz2 --ros-args -p use_sim_time:=true
```

Set Fixed Frame `map`; add Map `/map`, LaserScan `/scan`, TF, and RobotModel `/robot_description`. The hallway outline should fill in as you explore. Confirm scans follow mapped walls, not a displaced/rotated duplicate.

Stop robot motion. In another sourced terminal, save while SLAM and Gazebo remain running:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs/final_project_simulation
mkdir -p results
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/final_map" \
  --ros-args -p use_sim_time:=true
```

Keep the YAML and image together. To view the image, use an Ubuntu image viewer, or `python3 -c "from PIL import Image; Image.open('results/final_map.pgm').save('results/final_map.png')"` from this directory and open the PNG in VS Code (install `python3-pil` if needed). The PNG is a viewing copy; keep the original map files.

### 6. Restart and navigate on your saved map

Stop teleop, SLAM, RViz, and simulator. Relaunch your baseline world using Step 3. **Do not restart SLAM.** In Terminal 2:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch nav2_bringup bringup_launch.py slam:=false use_sim_time:=true \
  use_composition:=false autostart:=true \
  map:="$PWD/final_project_simulation/results/final_map.yaml" \
  params_file:="$PWD/final_project_simulation/goosebot/nav2_goosebot.yaml"
```

In Terminal 4, use the standard Nav2 RViz layout:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 launch nav2_bringup rviz_launch.py use_sim_time:=true
```

Use **2D Pose Estimate** at the starting position, dragging in its heading direction. Enable Map and LaserScan `/scan`. **Alignment means live scan points overlap the saved map's wall edges** around several sides of the robot; they should not form a shifted/rotated outline. Costmap inflation colors are clearance margins, not the physical wall. If alignment is poor, correct the initial pose before sending goals. AMCL now owns `map → odom`; the EKF still owns `odom → base_footprint`.

Send a nearby **Nav2 Goal** first, then visit three chosen delivery locations and return home. Wait 3 seconds at each delivery. Clicking goals in RViz is sufficient; autonomous mission sequencing using the existing client scaffold is optional. Keep keyboard teleop stopped during navigation.

Select destinations and home on **your SLAM map**. The `mission.json` coordinates describe Gazebo/the geometric reference map, and may differ from your SLAM frame. Do not blindly copy them. IST example destinations are in the hallway near 1044, 1003, and 1066.

### 7. Test one blocked route

Stop all launches and restart Step 3 with `ist/ist_blocked.sdf` (or `campus/campus_blocked.sdf`). Keep your **baseline saved map**, robot, settings, and goals. Relaunch AMCL/Nav2 and initialize the pose again; do not remap the barrier.

For IST the barrier crosses the upper hallway near the central junction at (0.5, 8.2) m; the lower loop and connecting passages provide alternatives. For campus it blocks one causeway. Check that live scans/costmaps detect it. Describe the actual result: detour, changed global path, recovery, stopping, or failure. A detour alone does not establish which algorithm replanned.

## What to submit

- **One video, about 3–5 minutes:** show your LiDAR/scan display, mapping and a revisit, saved-map localization, successful navigation to three deliveries and home, and a brief blocked-route attempt. Clips may be joined; do not record the entire setup.
- **Your fork/code:** modified Goosebot xacro and bridge, full SLAM/Nav2 configuration, saved map YAML/image, and the commands you used. Commit source/configuration; exclude `build/`, `install/`, `log/`, databases, and bags.
- **A short explanation in your own words, about one page:** what you changed; how scans, TF, odometry, SLAM, AMCL, planning and control fit together; one problem/fix; the blocked-route result; and why simulation success does not prove physical Goosebot readiness. List each member's contribution.

No long report, custom planner implementation, or mandatory mission-client implementation is required. Assessment: model/sensor integration 30%, mapping/localization 25%, navigation/obstacle test 25%, explanation/reproducibility 20%. Diagnose and retain failed attempts rather than presenting ground-truth localization as your solution.

## Troubleshooting and references

- **No `/scan`:** check Gazebo playing, sensor enabled, topic spelling, bridge entry, and sensor-rendering plugins. A bridge does not create sensor data by itself.
- **No motion:** focus the teleop terminal; check `/cmd_vel` type with `ros2 topic info /cmd_vel --verbose` against the supplied bridge. This model expects `geometry_msgs/msg/Twist`; do not enable stamped commands on only one end.
- **TF problems:** inspect the actual scan frame; exactly one mapper/localizer owns `map → odom`. Never run the original Goosebot perfect-map bridge alongside SLAM or AMCL.
- **Far goals fail:** verify map coverage and the full-map global costmap. Do not navigate into unmapped space. Sparse outdoor structure and open-loop odometry can make campus mapping harder; IST is the shorter starting option.
- **Robot invisible / duplicate clocks:** stop all old simulator launches; inspect leftover Gazebo processes before terminating only the stale processes you identify. Launch one world/server at a time.

References: [Goosebot source](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation), [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox), [Nav2 configuration](https://docs.nav2.org/configuration/index.html), [Gazebo sensors](https://gazebosim.org/docs/harmonic/sensors/). All required commands are above.

**INSTRUCTOR VALIDATION REQUIRED:** the new Goosebot integration and image-derived IST world have offline syntax/geometry checks, not an end-to-end Gazebo run. Pilot the required maze warm-up, sensor rendering/TF, mapping, saved-map localization, all deliveries, and both blocked variants on the course WSL installation before release. Starting configurations require local verification and may need tuning.
