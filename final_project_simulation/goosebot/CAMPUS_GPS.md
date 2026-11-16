# Part B — guided campus GPS activity

Complete campus mapping and AMCL/Nav2 first. Keep the baseline LiDAR settings. This activity adds **GPS observations** to the outdoor experiment; the required navigation remains LiDAR/AMCL-based. GPS fusion is optional.

## 1. Understand the three pieces

The pinned Goosebot already contains a `gps_link`, a `navsat` sensor named `gps_sensor`, and a `/gps/fix` bridge. Do not add a second GPS sensor or bridge. A sensor declaration alone is insufficient: the **world** must also run the NavSat system.

| Piece | Location | What to inspect |
|---|---|---|
| Robot sensor | `final_project_simulation/src/goosebot_0/urdf/robot.urdf.xacro` | `gps_link`, `gps_sensor`, topic `gps/fix`, frame `gps_link`, update rate and noise |
| ROS bridge | Copied package's `config/ros_gz_bridge.yaml` | `gps/fix`, `sensor_msgs/msg/NavSatFix`, `gz.msgs.NavSat`, `GZ_TO_ROS` |
| World support | `campus/campus.sdf` and `campus_blocked.sdf` | NavSat system and WGS84 spherical coordinates |

In VS Code search the Xacro for `gps_sensor`, then the bridge YAML for `gps/fix`. Record what your files actually contain. The supplied sensor uses **5 Hz in simulation**, horizontal Gaussian noise standard deviation **1.5 m**, and vertical standard deviation **3 m**. Existing custom models may differ; report your values.

The campus generator now supplies these world-level settings, alongside the other world plugins (not inside the robot or `campus` model):

```xml
<plugin filename="gz-sim-navsat-system" name="gz::sim::systems::NavSat"/>
<spherical_coordinates>
  <surface_model>EARTH_WGS84</surface_model>
  <world_frame_orientation>ENU</world_frame_orientation>
  <latitude_deg>28.1485</latitude_deg>
  <longitude_deg>-81.8495</longitude_deg>
  <elevation>0</elevation>
  <heading_deg>0</heading_deg>
</spherical_coordinates>
```

The files already include these blocks on this branch; **inspect them rather than pasting duplicates**. If using an older/custom world, add the missing blocks directly under `<world>`, then restart the simulation. World-only changes need no ROS rebuild. Changes to the robot/bridge require the Step 1 build helper, workspace sourcing, and a fresh robot launch.

This example follows [Gazebo Harmonic's spherical-coordinate/NavSat world](https://github.com/gazebosim/gz-sim/blob/gz-sim8/examples/worlds/spherical_coordinates.sdf). The model/bridge come from [the pinned Goosebot source](https://github.com/hoanbklucky/goose/tree/bffaf3cdf2b38f3b5a53a977064e0c787e046ff7/11_simulation/ros2_ws/src/goosebot_0).

## 2. Launch and inspect messages

Use the complete **campus Terminal 1 command in main Step 3**. Keep that simulator running. Stop SLAM/Nav2/teleop before this measurement-only session; use Terminal 4 for manual driving when needed. In **Terminal 2**, source the same workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 topic info /gps/fix --verbose
ros2 topic echo /gps/fix --once
ros2 topic hz /gps/fix
```

Stop `hz` with Ctrl+C before the next command. Expect `sensor_msgs/msg/NavSatFix` messages containing timestamp, frame, status, latitude/longitude in **degrees**, altitude in **meters**, and covariance/type fields. Inspect `status` and `position_covariance_type`; do not assume the bridge reports known uncertainty. Record the actual frame (expected `gps_link`).

```bash
ros2 run tf2_ros tf2_echo base_footprint gps_link
```

Stop after numerical TF appears. With a slow real-time factor, measured wall-clock Hz is lower than the 5 Hz simulated rate. The sensor frame is mounted on the robot; it is not the ROS `map` frame.

## 3. Record three stationary locations

1. At Home, stop motion and collect at least five consecutive fixes. Record latitude, longitude, altitude, stamp, status and covariance type. A short text excerpt is sufficient.
2. Drive safely to a second visible landmark, preferably several simulation meters away, stop, and repeat.
3. Repeat at a third location. Save a screenshot or description identifying each location. Note approximate displacement and direction using your map; compare **relative movement**, not raw map coordinates against latitude/longitude.

| Location | Landmark / approximate map XY | Latitude samples (deg) | Longitude samples (deg) | Altitude (m) | Status / covariance type |
|---|---|---|---|---|---|
| A | Home | Fill from messages | Fill | Fill | Fill |
| B | Your landmark | Fill | Fill | Fill | Fill |
| C | Your landmark | Fill | Fill | Fill | Fill |

Explain why readings vary while stationary and whether the differences between locations are clear compared with that variation. The simulation does not model realistic satellite visibility, building blockage or multipath merely because buildings are drawn. Do not claim real-world GPS accuracy from these trials.

## 4. Explain coordinates and actual fusion

World +x is east and +y is north (ENU). The datum anchors the simulation at the approximate campus origin, but the arena uses **0.06-scaled geography**. GPS follows distances in the simulation; it will not reproduce the real building coordinates from OSM. Noise remains in simulation meters and can be large relative to this teaching arena. Do not use these synthetic fixes for real campus navigation.

Your SLAM `map` has its own origin/heading. Latitude/longitude cannot be sent directly as a Nav2 `map`-frame XY goal or copied into an EKF's Cartesian odometry input. GPS requires geographic-to-local conversion, frame/heading alignment and covariance handling before fusion.

Inspect the installed `config/ekf.yaml`: does it subscribe to GPS at all? In the supplied baseline it does not; adding a bridge does not change filter inputs. Keep one owner of `map → odom` (AMCL during saved-map navigation) and one owner of `odom → base_footprint` (the local EKF). Do not add another TF publisher to make GPS appear connected.

**Required conclusion:** explain what GPS adds, what LiDAR still provides, why the required system does or does not fuse GPS, and what extra components would be needed. A working `/gps/fix` display is GPS integration/inspection evidence, not evidence of GPS-aided localization.

**Optional extension:** an instructor-validated `navsat_transform_node`/filter configuration may convert and fuse GPS. It needs consistent heading/datum, uncertainty and TF ownership; do not run a competing global filter alongside AMCL by copying an unrelated launch. See [robot_localization GPS integration](https://docs.ros.org/en/jazzy/p/robot_localization/doc/integrating_gps.html).

## If no GPS messages arrive

- Confirm campus is playing and uses the updated world. Inspect Terminal 1 for NavSat loading errors.
- Run `gz topic -l`; if `/gps/fix` exists, inspect `gz topic -i -t /gps/fix` and `gz topic -e -t /gps/fix` (Ctrl+C after receiving samples). Use the actual discovered name if different.
- No Gazebo messages: check sensor declaration, NavSat world plugin and spherical coordinates. A ROS topic publisher alone does not prove sensor samples exist.
- Gazebo messages but no ROS messages: check the installed bridge's type/direction/exact topic, correct sourced workspace, and bridge logs. Restart after configuration changes; avoid a duplicate bridge.

**INSTRUCTOR VALIDATION REQUIRED:** XML, bridge types and baseline sensor configuration were checked against source. Pilot message publication, TF, simulated rate and stationary/moving readings on course WSL before release. No Gazebo runtime test was available during authoring.
