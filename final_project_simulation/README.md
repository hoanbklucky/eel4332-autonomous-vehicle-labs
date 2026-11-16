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

## AI assistance is allowed

You may use AI tools to help write or modify code, add sensors, configure ROS 2, and debug errors for this **final project**. You are responsible for testing the resulting code/configuration and must be able to explain your submitted changes and how the system works. Write the short final explanation in your own words. AI assistance does not replace the required simulation demonstration or your understanding.

## Prerequisites and background

Complete Labs 4–5, then the required Goosebot warm-up in Step 1b below. Keep your existing Ubuntu 24.04/WSL, ROS 2 Jazzy, and Gazebo Harmonic installation. Use VS Code's **WSL: Ubuntu integrated terminal** or a separate **Ubuntu/WSL terminal**; both work. Each long-running launch needs its own terminal. Commands have no leading `$` prompt. **The course instructions use native WSL/Jazzy for both the warm-up and final. Docker is an optional alternative, not an additional requirement.**

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
<summary>Preview — campus layout</summary>

![Geographic campus layout](campus/campus_plan.png)

The campus is uniformly scaled to a 73 × 80 m teaching arena; some newer footprints and all building heights are approximate. Blue water has solid collision geometry. Grass remains traversable.

</details>

Other supplied files: `goosebot/world.launch.py` (world/spawn wrapper), `goosebot/slam_goosebot.yaml`, and `goosebot/nav2_goosebot.yaml` (starting configurations). The worlds' `reference.yaml` files are geometric instructor references, **not student SLAM results**. The existing [mission-client scaffold](../lab05_navigation/src/mission_client.py) remains available as an optional programming extension; its TODOs are not completed for you.

## Step-by-step procedure

### 1. Install dependencies, copy Goosebot source, and build

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
cp -r --update=none /tmp/eel4332-goose-source/11_simulation/ros2_ws/src/goosebot_0 final_project_simulation/src/
# Omit the redundant packaged snapshot; the extracted source is already copied.
rm -f final_project_simulation/src/goosebot_0/goosebot-simulation.zip
# Link, fix script permissions, install dependencies, and build this source copy.
bash final_project_simulation/goosebot/build_student_workspace.sh
```

**After the helper reports a successful build**, configure this terminal and check the installed package:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 pkg prefix goosebot_0
ros2 pkg executables goosebot_0
```

Expected prefix: `$HOME/goosebot_ws/install/goosebot_0`. The helper builds/verifies in its own process; it does not configure the parent terminal. Source this workspace again in every launch terminal. Do not run the install/prefix checks before the build succeeds.

If the source was copied already, skip the clone/copy commands and run the helper from the repository root. It preserves model edits, creates the workspace source link only when absent, and refuses a link/source pointing to another checkout. Inspect and preserve files before changing such a link. The helper does not fetch a missing model; complete the full source-copy step first.


The executable list must include `cmd_vel_to_odom.py`, `ground_truth_map_odom_bridge.py`, and `stereo_camera_info_fixer.py` before launching. The full source package is needed: `CMakeLists.txt`, `package.xml`, `scripts/`, `launch/`, `urdf/`, `config/`, `maps/`, and `worlds/`. The recursive copy above already includes these; copying only the xacro/launch files is insufficient. Keep scripts in `scripts/`; CMake installs them into ROS's libexec directory.

The package lives in your course fork so your model edits can be committed/pushed; the workspace points to it. If the temporary clone already exists, reuse/check it instead of cloning again; the helper checks an existing workspace source link. If rosdep reports its database is uninitialized, run `sudo rosdep init` once and `rosdep update`, then retry. Do not copy old Docker build output. Rebuild after adding files or changing installation rules.

### 1a. Troubleshooting — only if an executable is not found

**If the build and executable checks in Step 1 pass, skip this section and continue to Step 1b.**

<details>
<summary>Only if you see “executable cmd_vel_to_odom.py not found” — expand repair steps</summary>

This message can mean a missing installed script **or a script without executable permission**. The supplied source revision stores its Python scripts as non-executable files, while the launch expects installed executables. With a symlink install, executable permission on the source matters.

Stop the failed launch. In Ubuntu/WSL, repair permissions, reconfigure/build the existing package, then source it again:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/goosebot_ws
ls src/goosebot_0/scripts/cmd_vel_to_odom.py
chmod +x src/goosebot_0/scripts/*.py
colcon build --symlink-install --packages-select goosebot_0 --cmake-force-configure
source install/setup.bash
ros2 pkg prefix goosebot_0
ros2 pkg executables goosebot_0
ls -l "$(ros2 pkg prefix goosebot_0)/lib/goosebot_0/cmd_vel_to_odom.py"
test -x "$(ros2 pkg prefix goosebot_0)/lib/goosebot_0/cmd_vel_to_odom.py" && echo "Executable is ready"
```

Expect all three executable names listed above and **Executable is ready**. Retry the warm-up launch only after a successful build/check. The package prefix must belong to **~/goosebot_ws**; if it names another workspace, open a fresh terminal and source the correct one.

If the first `ls` reports no such file, the source copy is incomplete. Repeat Step 1's **whole-package recursive copy from the pinned source** into `final_project_simulation/src/`, preserving your existing edits. Do not copy old build/install/log directories or place Python files manually inside `install/`.

The package's `CMakeLists.txt` must contain `install(PROGRAMS ... DESTINATION lib/${PROJECT_NAME})` for the three launch scripts. The provided revision already does. If your local copy differs, compare/restore that install declaration and rebuild; preserve your modified model/configuration.

</details>

<a id="goosebot-warm-up"></a>

### 1b. Required Goosebot warm-up — before adding LiDAR

Use **native Ubuntu/WSL + ROS 2 Jazzy**, the package built in Step 1, and the **same `~/goosebot_ws` workspace** as your final. No second installation, Docker setup, or robot-model modification is required for this warm-up. If you already completed Step 1, reuse your package/workspace and preserve your edits.

The required warm-up uses a **10 × 8 m open arena with low walls and three obstacles**, so Goosebot remains visible and there is room to steer. The original tall-wall maze is optional below. Pull the latest course repo to obtain these assets; rebuilding Goosebot is unnecessary for a world/map change.

<details>
<summary>Preview — simple practice arena</summary>

![Low-wall arena, spawn and example goal](warmup/warmup_plan.svg)

</details>

The practice arena's **perfect-map mode** provides both a pre-generated map and Gazebo ground-truth global localization. This checks Goosebot operation and Nav2 integration; **it is not SLAM and does not use AMCL**. This mode is allowed for this warm-up only; the final still requires your added LiDAR, your SLAM map, and AMCL.

**Terminal 1 — low-wall practice arena and Goosebot:** stop other simulator/SLAM/navigation launches first.

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch goosebot_0 spawn_robot.launch.py \
  world:="$PWD/final_project_simulation/warmup/warmup.sdf" x:=-3.5 y:=-2.5 yaw:=0.0
```

**Terminal 2 — manual driving:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.1 -p turn:=0.5
```

Click inside Terminal 2 and use **lowercase keys**, with Shift and Caps Lock off. Goosebot uses different keys from TurtleBot teleop:

| Key | Effect |
| --- | --- |
| `i` | Drive forward |
| `,` | Drive backward |
| `j` / `l` | Turn left / right |
| `k` | Stop |
| `w` / `x` | Increase / decrease the linear speed setting |
| `q` / `z` | Increase / decrease both speed settings |

**A changed “speed/turn” number only changes the settings; it does not command movement.** Press `i` to move. Start at 0.1 m/s; restarting the command above resets these settings. Keep Gazebo playing and stop Nav2 while driving manually. Drive a short distance, then press `k`. Stop the robot and quit teleop with Ctrl+C. For a repeatable navigation check, stop Terminal 1 too and relaunch the practice arena at the original spawn pose.

**Terminal 2 — supplied perfect-map Nav2:** run this after teleop has stopped. Keep its original model-specific configuration; the final's LiDAR configuration is used later.

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch goosebot_0 nav2_bringup.launch.py slam:=false use_sim_time:=true \
  map:="$PWD/final_project_simulation/warmup/reference.yaml"
```

Use this arena's `reference.yaml` with `warmup.sdf`; **do not use the maze map with the practice arena**. The supplied map is generated from obstacle geometry and is not a student SLAM result.

**Expected behavior:** Nav2 runs its navigation nodes in Terminal 2 and prints log messages; **no new window opens**. When the log says **`Managed nodes are active`**, the navigation nodes are ready. Leave Terminal 2 running and continue to Terminal 3, which opens RViz. Do not press Ctrl+C in Terminal 2 until you want to stop Nav2.

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
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 3.0, y: -2.5}, orientation: {w: 1.0}}}}" --feedback
```

Expect odometry/sensor messages, robot movement in Gazebo, and a **SUCCEEDED** action result. You may instead select one reachable free-space Nav2 Goal in RViz. If TF is missing, inspect `ros2 run tf2_ros tf2_echo odom base_footprint` in a sourced terminal; stop the check with Ctrl+C. Resolve warm-up startup/motion problems before modifying the model.

**Evidence:** one screenshot showing successful navigation and **two sentences in your own words** explaining where the map and localization come from, and why this does not demonstrate SLAM/AMCL. An instructor-observed in-class demonstration can replace the submission. No separate video or long report is needed.

**Finish:** stop Nav2, RViz and the practice arena with Ctrl+C. Continue with Step 2 in this same source/workspace. Keep the warm-up's perfect-map/ground-truth launches stopped while running final-project SLAM or AMCL; each mode must have only one `map → odom` publisher.

<details>
<summary>Troubleshooting — keyboard input but no motion</summary>

Check terminal focus, lowercase movement keys, and that Gazebo is playing. Stop other teleop/Nav2 processes that may also publish velocity commands. In a separate sourced terminal, run `ros2 topic echo /cmd_vel`, then press `i` in teleop: expect nonzero `linear.x`. A bridge message saying it passed a Twist confirms receipt, not physical movement. If nonzero commands arrive but Goosebot stays still, save the full simulator/bridge log for troubleshooting. Press `k` to stop and Ctrl+C to end the topic check.

</details>

<details>
<summary>Optional challenge — original tall-wall maze</summary>

The original maze has narrow passages and tall textured walls that obstruct the camera. It is not required for warm-up credit. Stop all practice-arena launches first. In Terminal 1 use:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 launch goosebot_0 spawn_robot.launch.py \
  world:="$(ros2 pkg prefix goosebot_0)/share/goosebot_0/worlds/maze.world" x:=-0.5
```

For perfect-map navigation, Terminal 2 must use its matching map:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 launch goosebot_0 nav2_bringup.launch.py slam:=false use_sim_time:=true \
  map:="$(ros2 pkg prefix goosebot_0)/share/goosebot_0/maps/maze.yaml"
```

Reuse the slow manual-driving command and RViz setup above, but select a reachable free-space goal on the maze map instead of using the arena's example coordinates.

</details>

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


#### What to change when copying the ToF sensor

**Keep the original ToF sensor. Edit only your new copy.** There are two separate parts in this file: the URDF link/joint defines the mount and TF; the later `<gazebo reference="tof_front_link">…</gazebo>` block creates the simulated measurements. Copy **both parts**. Copying only the link/joint shown in the screenshot creates a visible mount, not a working LiDAR.

Use the following checklist to edit your copy; these are XML fields, not terminal commands.

| Location in your new copy | Change |
| --- | --- |
| Xacro properties | Rename `tof_x_offset` / `tof_z_offset` to unique LiDAR property names, such as `lidar_x_offset` / `lidar_z_offset`. Update their uses in the new joint. Do not redefine the original ToF properties. |
| `<link name="…">` | `tof_front_link` → `lidar_link`. |
| Link visual/inertial | Choose a visible sensor shape and sensible mass/inertia for your mount. The visual shape does not set the scan coverage. |
| `<joint name="…">` | `tof_front_joint` → `lidar_joint`; retain `type="fixed"` and parent `base_link`; change child to `lidar_link`. |
| Joint `<origin xyz="…" rpy="…">` | Choose a clear mounting position. Values are relative to `base_link`, not the ground. Start with a level sensor, `rpy="0 0 0"`; choose height after inspecting the chassis, camera and nearby obstacles. The scan plane must avoid the robot itself and intersect walls. |
| `<gazebo reference="…">` | `tof_front_link` → `lidar_link`. This must match your new link name. |
| `<sensor type="…" name="…">` | Keep `type="gpu_lidar"`; rename `tof_front_sensor` to a unique name such as `lidar_sensor`. |
| `<topic>` and `<gz_frame_id>` | Set to `scan` and `lidar_link`, respectively. Keep the original ToF on `tof_front/scan`. |
| `<update_rate>` / `<always_on>` | Set to `10` / `true`. Keep `<visualize>true</visualize>` while debugging. |
| `<lidar><scan><horizontal>` | `samples=720`, `resolution=1`, `min_angle=-3.14159`, `max_angle=3.14159`. The ToF's two nearly identical rays must be replaced with a full horizontal sweep. |
| `<lidar><scan><vertical>` | `samples=1`, `resolution=1`, `min_angle=0`, `max_angle=0`. This keeps the scan in one plane. |
| `<lidar><range>` | Set `min=0.12`, `max=12.0`; retain `resolution=0.001` as a starting value. Range resolution is in metres; it is different from scan resolution above. |
| Copied comments | Replace “single-beam ToF” comments with a description of your 360° LiDAR. |
| `config/ros_gz_bridge.yaml` | Add the separate `/scan` entry shown above; preserve the existing ToF bridge. |

Do not globally replace `tof` throughout the file: that would also change the original sensor. Ensure all link, joint and sensor names are unique, and put the new blocks inside the existing `<robot>…</robot>` element.

**Reload after editing:** stop the simulator and related launches first. In Ubuntu/WSL, rebuild and source your existing workspace:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/goosebot_ws
colcon build --symlink-install --packages-select goosebot_0
source install/setup.bash
```

Continue with Step 3 to launch the edited model, then Step 4 to check the sensor and TF. `/scan` should contain about 720 ranges, its frame should be `lidar_link`, and TF must connect the robot to that frame. In RViz, add a LaserScan display on `/scan`: expect returns around the robot from surrounding walls, rather than just the original narrow forward ToF beam. A full circle of visible returns is not guaranteed where rays see no obstacle within range. If returns hit Goosebot's own body, adjust the mount before mapping.

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
