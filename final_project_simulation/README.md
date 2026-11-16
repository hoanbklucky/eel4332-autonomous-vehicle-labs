# Final Project — Goosebot SLAM and Delivery in Simulation

> [!IMPORTANT]
> **Stop Gazebo with Ctrl+C in its launch terminal—not just the window's × button.** Closing the GUI can leave the simulation server and ROS nodes running, causing duplicate simulations or a GUI that does not match the robot/world queried from the terminal.
>
> **Before relaunching, switching worlds, or finishing:**
> 1. Stop robot motion; save any map/results you need.
> 2. Press **Ctrl+C** in each teleop, SLAM and Nav2 terminal that is running.
> 3. Press **Ctrl+C in the simulator launch terminal** (usually Terminal 1).
> 4. Wait for shutdown messages to finish and the shell prompt to return before launching again.
>
> If you already closed the window, return to its launch terminal and press Ctrl+C there. If shutdown seems incomplete, check `pgrep -af 'gz sim|gz-sim'` and identify leftover simulation processes before restarting.

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

Use the **provided Goosebot model with its configured 2-D LiDAR**, build your own SLAM map, and use **AMCL + Nav2** to reach three delivery locations and return home. Choose the supplied **IST interior** or **Florida Poly campus** world. Physical Goosebot SLAM/Nav2 is not required; your lane-following work is the hardware component.

## Learning objectives

Connect a robot model, sensors, bridges, TF, odometry, SLAM, localization, and navigation. Explain your own changes and diagnose problems rather than only repeating TurtleBot commands.

## AI assistance is allowed

You may use AI tools to help write or modify code, add sensors, configure ROS 2, and debug errors for this **final project**. You are responsible for testing the resulting code/configuration and must be able to explain your submitted changes and how the system works. Write the short final explanation in your own words. AI assistance does not replace the required simulation demonstration or your understanding.

## Prerequisites and background

Complete Labs 4–5, then the required Goosebot warm-up in Step 1b below. Keep your existing Ubuntu 24.04/WSL, ROS 2 Jazzy, and Gazebo Harmonic installation. Use VS Code's **WSL: Ubuntu integrated terminal** or a separate **Ubuntu/WSL terminal**; both work. Each long-running launch needs its own terminal. Commands have no leading `$` prompt. **The course instructions use native WSL/Jazzy for both the warm-up and final. Docker is an optional alternative, not an additional requirement.**

The Goosebot source is [hoanbklucky/goose, nav2 branch](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation). It already supplies the body/wheels, drive plugin, stereo cameras, IMU, forward ToF, command-derived odometry, and EKF. **The narrow forward ToF is not a 360° mapping LiDAR.** The course build helper supplies the 360° LiDAR and bridge automatically. Start with those defaults; inspect/change one LiDAR setting only after completing mapping and saved-map navigation.

The original Goosebot default mode uses a pre-baked map and Gazebo ground-truth localization. **Do not use that mode as your final demonstration.** This project instead uses LiDAR SLAM Toolbox for mapping, then a saved map with AMCL. This differs from the TurtleBot/Cartographer preparation in Lab 4. Stereo RTAB-Map is optional. Do not launch the original `nav2_bringup.launch.py` or `stereo_slam.launch.py` alongside the commands below.

AMCL estimates the robot's pose on a saved map by matching live scans. Nav2's supplied starting configuration uses **NavFn with Dijkstra** for the global path and **DWB** to choose local motion commands. The global costmap follows the full saved map, rather than the original Goosebot's 20 m rolling window. Use the supplied footprint and sensor defaults first; tuning comes after baseline mapping/localization/navigation.

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
  ros-jazzy-teleop-twist-keyboard python3-yaml
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

The helper also supplies the LiDAR link/sensor, `/scan` bridge, and wheel joint-state publisher automatically. If the source was copied already, skip the clone/copy commands and run the helper from the repository root. It preserves model edits, creates the workspace source link only when absent, and refuses a link/source pointing to another checkout. Inspect and preserve files before changing such a link. The helper does not fetch a missing model; complete the full source-copy step first.


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

### 1b. Required Goosebot warm-up — before the main project

Use **native Ubuntu/WSL + ROS 2 Jazzy**, the package built in Step 1, and the **same `~/goosebot_ws` workspace** as your final. No second installation, Docker setup, or robot-model modification is required for this warm-up. If you already completed Step 1, reuse your package/workspace and preserve your edits.

The required warm-up uses a **10 × 8 m open arena with low walls and three obstacles**, so Goosebot remains visible and there is room to steer. The original tall-wall maze is optional below. Pull the latest course repo to obtain these assets; rebuilding Goosebot is unnecessary for a world/map change.

<details>
<summary>Preview — simple practice arena</summary>

![Low-wall arena, spawn and example goal](warmup/warmup_plan.svg)

</details>

The practice arena's **perfect-map mode** provides both a pre-generated map and Gazebo ground-truth global localization. This checks Goosebot operation and Nav2 integration; **it is not SLAM and does not use AMCL**. This mode is allowed for this warm-up only; the final still requires the supplied LiDAR, your SLAM map, and AMCL.

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

Use Fixed Frame `map`; set the Map display's topic to **`/projected_map`**. Enable RobotModel with `/robot_description` and TF. The forward ToF, if displayed as LaserScan, is **`/tof_front/scan`** and gives only a narrow beam. The supplied LiDAR also publishes `/scan`; the warm-up still uses perfect-map localization. Do not initialize AMCL with 2D Pose Estimate: the ground-truth bridge supplies `map → odom` in this mode.

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

**Stereo RTAB-Map is an optional extension**, not a prerequisite. Its [upstream live-stereo mode](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation#32-mode-b--live-stereo-slam) must run separately from perfect-map localization and the final's LiDAR SLAM/AMCL. Running stereo SLAM does not replace the final mapping/AMCL/Nav2 demonstration.

</details>

### 2. Use the supplied robot — no sensor editing yet

The Step 1 build helper automatically configures the copied Goosebot source with a **360° LiDAR on `/scan`**, its ROS bridge, and the wheel joint-state publisher/bridge for RViz. No manual Xacro or bridge editing is required before mapping.

**Already completed the old setup?** Save/commit your work, pull the course updates, and run the Step 1 build helper again. It adds missing baseline components, preserves complete existing LiDAR settings, and stops on conflicting/partial edits rather than overwriting them. Then source the workspace and restart the simulator. Do not repeat the upstream clone/copy.

Use the defaults first: 720 samples, ±π horizontal coverage, one scan plane, 10 Hz, 0.12–12 m range, and a level mount 0.18 m above `base_link`. Finish Steps 3–7 before changing these settings. Your work is to build a map, localize, navigate and evaluate the delivery mission; a short LiDAR experiment comes last in Step 8.

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

#### Find Goosebot in the large world

The supplied IST opening camera looks inward from **+x (south)**, so the south entrance is in the foreground. Restart the simulator after pulling camera/world changes; an explicit custom `--gui-config` can override the world's GUI settings. Orbiting the camera changes which entrance is nearest.

**To inspect Goosebot:**

1. Collapse `ist_building` in the Entity Tree.
2. Right-click the separate **`goosebot`** entry.
3. Click **Move To**, the first item at the top of the menu. This moves the **camera**, not the robot; it is not inside the `View >` submenu.
4. Put the pointer in the 3-D scene and scroll the mouse wheel upward to zoom closer. Scroll downward to zoom out.

At whole-building zoom, the roughly 20 cm Goosebot can be only a few pixels wide. Selecting a tree entry highlights it but does not by itself move the camera.

IST starts Goosebot at **(24.85, 0)** in the centre of the **south entrance passage**, facing inward toward −x (yaw π).

<details>
<summary>Troubleshooting — robot missing, too small, or absent from the Entity Tree</summary>

**1. Check the model and actual pose.** Keep Terminal 1 running and open another Ubuntu/WSL terminal:

```bash
source /opt/ros/jazzy/setup.bash
gz model --list
gz model -m goosebot --pose
```

Use the exact name printed by the list if your local launch differs, such as `custom_bot`. The course wrapper requests the entity name `goosebot`; `custom_bot` can still appear as the URDF model name in conversion warnings. See [Gazebo's model-command reference](https://gazebosim.org/api/sim/8/model_command.html).

| Observation | What to check next |
| --- | --- |
| `goosebot` is listed at approximately (24.85, 0) with a small positive Z | It exists near home. Collapse `ist_building`, select the separate `goosebot` entry, and focus/zoom on the robot. |
| Pose has a large negative Z | It may have fallen through the floor. Save the pose and simulator log for troubleshooting. |
| Pose has different XY | Compare with the launch's printed spawn line; the robot may have moved, or a different launch/mission file is in use. |
| Terminal lists the robot but the GUI does not | Check whether the GUI is stale or connected to another running server; use the clean restart below. A GUI label such as `default` alone does not establish which server it displays. |
| No robot is listed | Inspect the full `[create-...]` log for creation errors/timeouts and check that only the intended server is running. |

**2. Restart cleanly if the GUI and terminal disagree.** Stop all old simulator launches, including the maze/warm-up, with Ctrl+C in their launch terminals. Close all Gazebo windows. Check for remaining processes:

```bash
pgrep -af 'gz sim|gz-sim'
```

No output means this check found no matching processes. If it lists processes, identify and stop the leftover course simulation before relaunching; ask the instructor if unsure. Closing a window alone may leave its server running. Then launch Step 3 **once**. Do not repeatedly spawn extra robots to solve a camera problem.

**3. Read the messages correctly.** `Entity creation successful` confirms creation was accepted, not that the robot stayed at its initial pose or is visible at the current zoom. The `gz_frame_id ... not defined in SDF. Copying ...` warning alone is not a spawn failure; retain that field and verify the ROS scan frame in Step 4.

If the problem remains, share the launch's printed spawn line, full create log, model list, robot pose, and remaining-process output. These distinguish visibility, wrong-pose, and multiple-server problems.

</details>

### 4. Check the sensor and TF — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 topic echo /scan --once --field header.frame_id
ros2 topic hz /scan
```


<details>
<summary>Troubleshooting — /scan does not appear to be published yet</summary>

This warning means ROS has not discovered a publisher/type for `/scan`; it is different from a TF warning. Press Ctrl+C to stop a waiting echo/hz command before running another check. Keep Gazebo playing and allow sensor/bridge startup time.

**First check which installed model you are using:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 pkg prefix goosebot_0
ros2 run xacro xacro "$(ros2 pkg prefix goosebot_0)/share/goosebot_0/urdf/robot.urdf.xacro" -o /tmp/goosebot_loaded.urdf
python3 - <<'PY'
import xml.etree.ElementTree as ET
r = ET.parse('/tmp/goosebot_loaded.urdf').getroot()
print('LiDAR link present:', r.find("link[@name='lidar_link']") is not None)
for s in r.findall("gazebo/sensor"):
    print('sensor:', s.get('name'), 'topic:', s.findtext('topic'))
PY
```

Expect your intended workspace prefix, `LiDAR link present: True`, and `lidar_sensor` on `scan`. If absent, the source edit was incomplete or the wrong package is installed/sourced. Rerun the Step 1 build helper, rebuild, source the correct workspace, and restart Terminal 1. A robot already in Gazebo will not acquire a new sensor merely because you saved the file.

**Then separate Gazebo output from ROS bridging:**

```bash
gz topic -l
ros2 topic list -t
ros2 topic info /scan --verbose
```

Find the new LiDAR's Gazebo scan topic in the list, distinct from `/tof_front/scan`. If it is `/scan`, inspect it with `gz topic -i -t /scan` and `gz topic -e -t /scan` (Ctrl+C after messages arrive). If Gazebo lists a different fully qualified scan topic, use that exact name when inspecting it and in the bridge's `gz_topic_name`; the ROS topic should remain `/scan`.

| Result | Next step |
| --- | --- |
| Installed description has no new LiDAR | Fix/source the correct model and respawn. |
| LiDAR is in the description but no Gazebo scan messages | Check the sensor block is attached to `lidar_link`, `always_on=true`, simulation is playing, and Terminal 1 has no sensor/render errors. Both supplied IST worlds include the Sensors system. |
| Gazebo scan messages arrive but ROS `/scan` is absent | Check the installed `config/ros_gz_bridge.yaml` has the new top-level bridge entry supplied by the Step 1 helper, with the exact Gazebo topic. Restart the launch to reload it and check Terminal 1 for bridge errors. |
| ROS scan messages arrive but RViz cannot display them | Continue with the TF/frame checks below; this is now a different problem. |

Do not change `gz_frame_id` or add another odometry publisher to fix a missing ROS topic. Share the installed-description check, topic lists and bridge errors if it remains unresolved.

</details>

Expect `lidar_link`. A 10 Hz simulated sensor may measure only about 1.3 Hz in wall-clock time when Gazebo runs at 13% real time. Stop `hz` with Ctrl+C, then run these one at a time (Ctrl+C after each check):

```bash
ros2 run tf2_ros tf2_echo base_footprint lidar_link
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 topic echo /odometry/filtered --once
```

Expect numerical transforms and odometry. A brief startup warning can resolve when TF arrives; persistent warnings need fixing. If the reported scan frame differs, correct the sensor frame/TF configuration. For a sensor-only RViz check, open `rviz2 --ros-args -p use_sim_time:=true` in a separate sourced terminal, use Fixed Frame `odom`, and add LaserScan `/scan` and RobotModel `/robot_description` using the click-by-click RViz setup in Step 5 below. Leave Map disabled until SLAM starts. Verify walls appear in the correct direction as you drive.

### 5. Build and save your map

**Terminal 2 — mapping** (after the checks):

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true \
  slam_params_file:="$PWD/final_project_simulation/goosebot/slam_goosebot.yaml"
```

**Set up visualization before driving:** open Terminal 4 and configure RViz first, then use Terminal 3 to drive while watching the map grow. Terminal numbers identify their roles; they do not require starting driving before RViz.

**Terminal 4 — visualization:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
rviz2 --ros-args -p use_sim_time:=true
```

#### RViz setup — add displays and select their topics

If RViz is already open with `use_sim_time:=true`, reuse it. Otherwise run the Terminal 4 command above. Keep Gazebo and the Step 5 SLAM launch running.

**1. Show the Displays panel and choose the fixed frame.**

- If the left panel is missing, select **Panels → Displays**.
- Expand **Global Options** at the top. Click the value beside **Fixed Frame**, type `map`, and press Enter.
- Use `map` during SLAM and saved-map navigation. For the earlier Step 4 sensor-only check, use `odom` and leave Map disabled: no map is being built yet.
- RViz displays ROS messages, not the Gazebo building automatically. A blank grid does not mean the Gazebo world is missing.

**2. Add Map and set its Topic.**

1. Click **Add** at the bottom of the Displays panel.
2. Select the **By display type** tab, expand **rviz_default_plugins** if needed, choose **Map**, and click **OK**.
3. In the Displays panel, expand the new **Map** row with its small triangle.
4. Find the editable **Topic** property below Status. Click the blank value cell to its right, select/type **`/map`**, and press Enter. Adding a display by type does **not** necessarily choose its topic.
5. Keep its checkbox enabled. Once SLAM publishes, expect **Status: Ok** and a grey/white/black occupancy map that grows as you drive.

**“Error subscribing: Empty topic name” means the Topic cell is blank.** Set the editable Topic property; the red `Status → Topic` line reports an error and is not the field to edit. “No map received” after setting `/map` means no map message has arrived yet; check that Step 5 SLAM is running and `ros2 topic list -t` contains `/map`. Changing RViz settings alone does not create a map.

For saved-map navigation, use `/map` as well. The earlier perfect-map warm-up uses **`/projected_map`** instead; do not carry that warm-up topic into final-project SLAM. If a running map publisher exists but no map arrives, inspect the Map Topic's QoS settings; the supplied map workflows use **Reliable / Transient Local**. Allow startup time and check the display's expanded Status.

**3. Add LaserScan and select the LiDAR topic.**

1. Click **Add → By display type → rviz_default_plugins → LaserScan → OK**.
2. Expand **LaserScan**, click its editable **Topic** value, choose/type **`/scan`**, and press Enter.
3. Keep its checkbox enabled. Expand Topic if needed to see QoS settings; **Best Effort** reliability is suitable for receiving sensor scans, including a Reliable publisher.
4. If points are too small, set **Style** to **Points** and increase **Size (Pixels)**, for example to `3`, if those properties are shown.
5. Expect points outlining nearby walls, not an image of the building. Do not choose `/tof_front/scan`, which is only the original narrow forward beam.

**4. Add RobotModel — it is a display type, not a topic name.**

1. Click **Add**, then select **By display type** (not **By topic**).
2. Under **rviz_default_plugins**, scroll to **RobotModel**: it is written as one word. Select it and click **OK**. If a filter/search box is shown, clear it or type `RobotModel`.
3. Expand the new **RobotModel** row in Displays.
4. Set **Description Source → Topic**.
5. Set **Description Topic → `/robot_description`**, then press Enter. This uses the expanded robot description published by `robot_state_publisher`; do not enter the Xacro filename here.
6. Keep the display enabled and **Visual Enabled** checked. If Description Topic exposes QoS settings, use **Reliable / Transient Local** to receive the retained description.
7. Expect Goosebot's chassis, wheels and added sensor, with Status Ok once its transforms are available. This does not add another robot to Gazebo.

If RobotModel is absent from the By topic tab, that is not evidence the robot description is missing: use **By display type** as above. If the display reports a transform error, return to Step 4; a valid description still needs TF to position every link.

**5. Add TF and choose an easy view.**

- Use **Add → By display type → rviz_default_plugins → TF → OK** to show coordinate frames. Toggle TF off if its axes/text clutter the map.
- In the **Views** panel, select **TopDownOrtho** for a flat overhead map, or keep Orbit. Use **Panels → Views** if the panel is hidden.
- Zoom with the mouse wheel over the 3-D view. Goosebot can be very small compared with IST; during sensor inspection you can set the view's **Target Frame** to `base_footprint` to keep the robot centred.
- Confirm scan points follow the mapped wall edges rather than forming a shifted/rotated duplicate. Save your RViz configuration with **File → Save Config As…** if you want to reuse it.

<details>
<summary>RViz quick check — blank map, missing robot, or red display status</summary>

| Symptom | Check |
| --- | --- |
| Map: Empty topic name | Edit Map's Topic property to `/map`, not the Status error row. |
| Map: No map received | Start SLAM in Step 5, or the saved-map navigation launch in Step 6; confirm `/map` is published. |
| Fixed Frame `map` does not exist | Before SLAM use `odom`; during SLAM check the SLAM node and its `map → odom` transform. |
| Cannot find RobotModel | Add → **By display type**, expand rviz_default_plugins, select **RobotModel**. |
| RobotModel has no description | Set Description Source Topic and Description Topic `/robot_description`; verify robot_state_publisher remains running. |
| Scan exists but is not visible | Select `/scan`, check TF/status and reliability, then increase point size or zoom closer. |
| RobotModel/scan transform errors | Use simulation time in RViz and complete Step 4 TF checks; adding displays does not repair missing transforms. |

</details>



**Terminal 3 — driving:**

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Click inside Terminal 3 and follow **its printed key layout** (different from TurtleBot teleop). Start slowly. Map all mission routes and revisit an earlier area. For IST, cover both halves of the oval, both end cross-passages, the north/south entrance lobbies, and the central passage through both side exits; classroom interiors are optional. For campus, cover the delivery routes and alternative crossings; every remote corner is unnecessary.

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
ros2 launch nav2_bringup bringup_launch.py slam:=False use_sim_time:=True \
  use_composition:=False autostart:=True \
  map:="$PWD/final_project_simulation/results/final_map.yaml" \
  params_file:="$PWD/final_project_simulation/goosebot/nav2_goosebot.yaml"
```

**Use the capitalized launch values exactly as shown.** Jazzy's standard Nav2 bringup evaluates `slam` and `use_composition` in Python expressions; lowercase `false` can cause **`name 'false' is not defined`** before nodes start. These command-line values differ from lowercase `true/false` in YAML configuration files. If you see this error, rerun the corrected command; no robot rebuild or remapping is needed. See the [Jazzy bringup launch source](https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/launch/bringup_launch.py).

Leave Terminal 2 running after successful startup. Nav2 prints logs there and opens no window; expect **Managed nodes are active**. Check that you saved `results/final_map.yaml` and its image in Step 5 and restarted the same world before continuing.

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

### 8. Explore LiDAR settings — after mapping and localization/navigation

**Do this last**, after you have saved your baseline map and demonstrated AMCL/Nav2. You do not need to build a sensor from scratch.

1. Save/commit your working baseline. Open `final_project_simulation/src/goosebot_0/urdf/robot.urdf.xacro` in VS Code.
2. Find `<sensor type="gpu_lidar" name="lidar_sensor">` and inspect its settings:

   | Setting inside the LiDAR block | Baseline | Meaning |
   | --- | --- | --- |
   | `update_rate` | 10 | Scans per simulated second. |
   | `horizontal/samples` | 720 | Number of directions measured per scan. |
   | `horizontal/min_angle`, `max_angle` | −3.14159, +3.14159 | Horizontal field of view in radians. |
   | `vertical/samples` | 1 | A single plane for 2-D SLAM. |
   | `range/min`, `max` | 0.12, 12.0 | Measurement limits in metres. |

3. Change **one setting only**: for example horizontal samples **720 → 360**, or update rate **10 → 5**. Keep the original ToF and the `scan` topic/`lidar_link` frame unchanged. Do not globally replace values throughout the file.
4. Save, stop launches with Ctrl+C, rebuild using the Step 1 helper, source your workspace and relaunch Step 3. The helper preserves your complete LiDAR's edited settings.
5. Inspect `/scan` in RViz and compare with the baseline. Fewer samples give wider angular spacing; a lower update rate gives fewer scans per simulated second. With a slow Gazebo real-time factor, wall-clock `ros2 topic hz /scan` is lower than the sensor's configured rate.
6. Restore the baseline setting before your final delivery demonstration. Add **two or three sentences** about your change and observation to the existing short explanation; no additional report or video is required.

<details>
<summary>Optional — how the LiDAR link, joint, sensor and bridge are constructed</summary>

See [the beginner Xacro reference](goosebot/LIDAR_REFERENCE.md) for the complete annotated XML and field-by-field explanation. Building another sensor or changing its mount is optional, not a prerequisite for this project.

</details>

## What to submit

- **One video, about 3–5 minutes:** show your LiDAR/scan display, mapping and a revisit, saved-map localization, successful navigation to three deliveries and home, and a brief blocked-route attempt. Clips may be joined; do not record the entire setup.
- **Your fork/code:** the configured Goosebot source, SLAM/Nav2 configuration, saved map YAML/image, and the commands you used. Include the single-setting LiDAR experiment or note its restored baseline. Commit source/configuration; exclude `build/`, `install/`, `log/`, databases, and bags.
- **A short explanation in your own words, about one page:** what you changed; how scans, TF, odometry, SLAM, AMCL, planning and control fit together; one problem/fix; the blocked-route result; and why simulation success does not prove physical Goosebot readiness. List each member's contribution.

No long report, custom planner implementation, or mandatory mission-client implementation is required. Assessment: mapping/localization 40%, navigation/obstacle test 35%, explanation/reproducibility 20%, end-of-project LiDAR settings observation 5%. Diagnose and retain failed attempts rather than presenting ground-truth localization as your solution.

<details>
<summary>Optional display troubleshooting — wheels or map rendering</summary>

The course helper supplies wheel joint states for RViz. If only wheel links show transform errors while chassis/LiDAR TF works, first inspect `ros2 topic echo /joint_states --once`; do not add another odometry publisher. Wheel appearance is not a mapping/localization completion requirement.

If RViz reports the shader error `active samplers with a different type refer to the same texture image unit`, save its configuration and stop only RViz. You may try `LIBGL_ALWAYS_SOFTWARE=1 rviz2 --ros-args -p use_sim_time:=true` for that process. This is a rendering diagnostic, may be slower, and is not guaranteed to fix the driver problem. Keep Gazebo/SLAM running and verify map messages independently; do not rebuild the robot to fix a graphics error.

</details>

## Troubleshooting and references

- **No `/scan`:** check Gazebo playing, sensor enabled, topic spelling, bridge entry, and sensor-rendering plugins. A bridge does not create sensor data by itself.
- **No motion:** focus the teleop terminal; check `/cmd_vel` type with `ros2 topic info /cmd_vel --verbose` against the supplied bridge. This model expects `geometry_msgs/msg/Twist`; do not enable stamped commands on only one end.
- **TF problems:** inspect the actual scan frame; exactly one mapper/localizer owns `map → odom`. Never run the original Goosebot perfect-map bridge alongside SLAM or AMCL.
- **Far goals fail:** verify map coverage and the full-map global costmap. Do not navigate into unmapped space. Sparse outdoor structure and open-loop odometry can make campus mapping harder; IST is the shorter starting option.
- **Robot invisible / duplicate clocks:** stop all old simulator launches; inspect leftover Gazebo processes before terminating only the stale processes you identify. Launch one world/server at a time.

References: [Goosebot source](https://github.com/hoanbklucky/goose/tree/nav2/11_simulation), [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox), [Nav2 configuration](https://docs.nav2.org/configuration/index.html), [Gazebo sensors](https://gazebosim.org/docs/harmonic/sensors/). All required commands are above.

**INSTRUCTOR VALIDATION REQUIRED:** the new Goosebot integration and image-derived IST world have offline syntax/geometry checks, not an end-to-end Gazebo run. Pilot the required open-arena warm-up, sensor rendering/TF, mapping, saved-map localization, all deliveries, and both blocked variants on the course WSL installation before release. Starting configurations require local verification and may need tuning.
