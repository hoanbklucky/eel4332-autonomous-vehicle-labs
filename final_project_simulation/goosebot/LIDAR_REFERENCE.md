# Optional reference — constructing the supplied LiDAR

The main project supplies this configuration automatically. Read this reference after the main mapping/localization/navigation workflow if you want to understand or build a sensor. Do not paste duplicate blocks into an already configured robot.

#### 2a. Open the source file and understand the syntax

In VS Code's WSL window, open `final_project_simulation/src/goosebot_0/urdf/robot.urdf.xacro`. Edit this source file, not a copy inside `install/`. Save with Ctrl+S. Xacro is XML with reusable values: `<xacro:property name="..." value="..."/>` defines a value, and `${property_name}` uses it. `${base_height/2 + 0.02}` is an expression evaluated when Xacro generates URDF.

| Element | Purpose |
| --- | --- |
| `<link>` | A robot part and its coordinate frame. |
| `<visual>` | Its visible shape. A shape alone does not generate sensor data. |
| `<collision>` | Its physical collision shape. |
| `<inertial>` | Its mass and inertia. |
| `<joint type="fixed">` | Attaches the child link to the parent at a fixed position/orientation. |
| `<gazebo reference="...">` | Adds simulation settings or a sensor to the named link. |
| `<sensor type="gpu_lidar">` | Generates simulated range measurements. |

Tags must close: `<link>...</link>`, or use a self-closing tag such as `<mass value="0.05"/>`. XML names are case-sensitive. All new code goes **inside the existing `<robot>...</robot>`**, outside other links/joints/macros. Do not add another `<robot>` element. Paste XML into the editor, not into a terminal.

#### 2b. Create the LiDAR properties, link and joint

**Do not change the original `tof_x_offset` or `tof_z_offset`.** They position the original ToF. In the duplicated LiDAR section shown in the screenshot, rename the properties and every use of them to `lidar_x_offset` and `lidar_z_offset`; also rename the link and joint. Keeping the ToF names in your duplicate creates conflicting definitions or references the wrong part.

Coordinates follow the robot frame: **x forward, y left, z up**, in metres. Joint `xyz` is measured from the parent `base_link` origin (the chassis centre), not from the floor. `rpy` is roll, pitch, yaw in radians. Keep `rpy="0 0 0"` for a level horizontal scan.

For a first trial, use `x=0`, `y=0`, `z=0.18`: centred above the chassis, 18 cm above `base_link`. In the supplied unmodified model, `base_link` is about 3 cm above `base_footprint`, so the scan plane is about 21 cm above that frame. This is a starting mount, not a measured hardware location. Inspect clearance from the camera/bracket and ensure the scan plane is below the walls you want to detect. Change **`lidar_z_offset`**, not the ToF height, when adjusting the LiDAR.

Find the original `tof_front_joint` and its closing `</joint>`. Immediately after it, paste the following. If you already made a duplicate LiDAR link/joint, **replace that duplicate with this example**; keep the original ToF block and add only one LiDAR block.

```xml
<!-- Separate 2-D LiDAR mount: positions relative to base_link, in metres. -->
<xacro:property name="lidar_x_offset" value="0.0"/>
<xacro:property name="lidar_z_offset" value="0.18"/>

<link name="lidar_link">
  <visual>
    <geometry><cylinder radius="0.025" length="0.03"/></geometry>
    <material name="sensor_black"/>
  </visual>
  <collision>
    <geometry><cylinder radius="0.025" length="0.03"/></geometry>
  </collision>
  <inertial>
    <mass value="0.05"/>
    <inertia ixx="0.0000115625" ixy="0" ixz="0"
             iyy="0.0000115625" iyz="0" izz="0.000015625"/>
  </inertial>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="${lidar_x_offset} 0 ${lidar_z_offset}" rpy="0 0 0"/>
</joint>
```

The cylinder is 5 cm wide and 3 cm tall, centred on `lidar_link`. Its inertia values describe this 0.05 kg cylinder. If you change its size/mass, update the inertia consistently. `sensor_black` is an existing material in this model. A fixed joint attaches the sensor without needing a second movable joint or a separate TF broadcaster. The example omits a support mast; any support you add must stay out of the scan plane and be included in the footprint where appropriate.

#### 2c. Add the Gazebo sensor — a separate block later in the file

Search for `<gazebo reference="tof_front_link">`. **Yes, this original ToF already has `type="gpu_lidar"`.** Gazebo simulates its narrow forward beam using two rays only `0.000001` radians apart. Your 360° scanner uses the same sensor type; the angles and sample count change its coverage.

Find the matching closing `</gazebo>` for that ToF block. Immediately after it, paste this **new sibling block**, not inside the original ToF block. If you already copied a sensor block for LiDAR, replace only that copy. Keep the original ToF sensor unchanged.

```xml
<gazebo reference="lidar_link">
  <sensor type="gpu_lidar" name="lidar_sensor">
    <update_rate>10</update_rate>
    <always_on>true</always_on>
    <visualize>true</visualize>
    <topic>scan</topic>
    <gz_frame_id>lidar_link</gz_frame_id>
    <lidar>
      <scan>
        <horizontal>
          <samples>720</samples>
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
        <vertical>
          <samples>1</samples>
          <resolution>1</resolution>
          <min_angle>0</min_angle>
          <max_angle>0</max_angle>
        </vertical>
      </scan>
      <range>
        <min>0.12</min>
        <max>12.0</max>
        <resolution>0.001</resolution>
      </range>
    </lidar>
  </sensor>
</gazebo>
```

| Setting | Meaning |
| --- | --- |
| `reference="lidar_link"` and `gz_frame_id=lidar_link` | Attach the simulated sensor to your new mount and label its measurements with that frame. |
| `name="lidar_sensor"` | Unique sensor name; do not reuse `tof_front_sensor`. |
| `topic=scan` | Gazebo scan output, bridged to ROS `/scan` below. |
| Horizontal angles ±3.14159, 720 samples | Approximately 360° coverage with about 0.5° angular spacing. |
| One vertical sample at angle zero | One horizontal plane, suitable for 2-D SLAM. |
| Scan `resolution=1` | Keep one output sample per requested scan sample. |
| Range 0.12–12 m, range resolution 0.001 m | Distance limits and distance resolution; this is different from scan resolution. |
| Update rate 10 | Target 10 scans per simulated second; wall-clock rate may be lower if simulation runs slowly. |

These examples intentionally keep the original ToF on `tof_front/scan`. Do not globally replace `tof` across the file. Do not copy the old “single-beam ToF” comments into your LiDAR section.

#### 2d. Bridge the new scan to ROS

Open `final_project_simulation/src/goosebot_0/config/ros_gz_bridge.yaml`. If a `/scan` entry is already present from your earlier edits, update that entry rather than adding it again. Otherwise append the following as a new top-level list item, aligned with the existing leading `-` entries. Use spaces, not tabs; do not put it inside another entry or a Markdown code fence in the YAML file. Preserve all existing bridges, including ToF.

```yaml
- ros_topic_name: /scan
  gz_topic_name: /scan
  ros_type_name: sensor_msgs/msg/LaserScan
  gz_type_name: gz.msgs.LaserScan
  direction: GZ_TO_ROS
```

Gazebo's sensor produces measurements, the bridge transfers them into ROS, and TF tells SLAM where the sensor is on the robot. All three are needed. Do not add another EKF or `odom → base_footprint` publisher. The existing odometry is command-derived, not measured wheel-encoder odometry. Check that the robot footprint includes your sensor mount; update **both** costmaps if necessary.

#### 2e. Check syntax before launching

Save both files. Run the following from the course repo root in Ubuntu/WSL. This expands your actual Xacro and checks that the new link/joint and sensor references exist; errors must be fixed before building. It checks the description, not Gazebo runtime behavior.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 run xacro xacro final_project_simulation/src/goosebot_0/urdf/robot.urdf.xacro -o /tmp/goosebot_lidar.urdf
```

If expansion fails, stop here. Read the line number and check closing tags, quotes, spelling and `${...}` property names. After successful expansion, run:

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
r = ET.parse('/tmp/goosebot_lidar.urdf').getroot()
for tag in ('link', 'joint'):
    names = [e.get('name') for e in r.findall(tag)]
    assert len(names) == len(set(names)), f'Duplicate {tag} names'
assert r.find("link[@name='lidar_link']") is not None, 'Missing lidar_link'
j = r.find("joint[@name='lidar_joint']")
assert j is not None and j.get('type') == 'fixed', 'Missing fixed lidar_joint'
assert j.find('parent').get('link') == 'base_link'
assert j.find('child').get('link') == 'lidar_link'
sensors = r.findall("gazebo[@reference='lidar_link']/sensor")
assert len(sensors) == 1, 'Expected one LiDAR sensor on lidar_link'
s = sensors[0]
assert s.get('type') == 'gpu_lidar'
assert s.findtext('topic') == 'scan'
assert s.findtext('gz_frame_id') == 'lidar_link'
print('LiDAR description checks passed; runtime checks are next.')
PY
```

#### 2f. Rebuild, relaunch and inspect the scan

Stop the simulator, warm-up perfect-map navigation, and other related launches first. In Ubuntu/WSL:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/goosebot_ws
colcon build --symlink-install --packages-select goosebot_0
source install/setup.bash
```

Continue with **Step 3** to spawn the updated robot in IST or campus, then **Step 4** for `/scan`, TF and RViz checks. Existing Gazebo robots do not update when you save the Xacro: you must respawn/relaunch. Even with `--symlink-install`, rebuilding is useful to ensure the installed package/configuration is current.

In RViz, expect the small cylinder above Goosebot and scan returns from surrounding walls on `/scan`, rather than only a narrow forward beam. Expect about 720 range values with this configuration. Rays with no hit within range may have infinite values; you do not need a visible circular outline. If returns hit Goosebot's camera/body, adjust `lidar_x_offset` or `lidar_z_offset`, rebuild, relaunch and repeat. If low walls disappear, the scan may be too high. Verify the mount in a side view as well as from above.

<details>
<summary>Common first-time Xacro mistakes</summary>

| Symptom | Check |
| --- | --- |
| Duplicate link/joint error | Keep only one new `lidar_link` and `lidar_joint`; original ToF names stay unique. |
| Unknown property | Define `lidar_x_offset` / `lidar_z_offset` before use; use exactly the same spelling in `${...}`. |
| Visible sensor but no `/scan` | Add the Gazebo sensor as well as the link, preserve the world sensor plugin, and check the new bridge entry. |
| `/scan` exists but RViz reports a transform error | Check `gz_frame_id`, link/joint names and Step 4 TF commands. |
| Changes do not appear | Check that you edited the source used by this workspace, then rebuild/source and respawn the robot. |
| Only a forward beam | Confirm RViz is showing `/scan`, not `/tof_front/scan`; check horizontal angles and samples in the new sensor. |

</details>

Record the mounting position, sensor settings, footprint and what you verified in your own words. Additional sensors are optional; GPS/stereo cameras are not required for this LiDAR workflow.


