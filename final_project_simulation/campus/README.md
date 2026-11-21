# Florida Polytechnic campus world

This replaces the earlier arbitrary 24 × 30 m block layout. It uses **OpenStreetMap building, lake, road, parking, and path outlines**, checked against the supplied **2026 printable campus map**. The IST footprint is elongated/curved; BARC and the residence cluster retain their real shapes and relative positions; the lake chain and multiple causeways are preserved.

![North-up campus plan](campus_plan.svg)

## Accuracy and teaching adjustments

- Horizontal geometry uses a **uniform 0.06 scale** (about 1:16.7), retaining geographic proportions/angles. The teaching arena is 73 × 80 m. It is not a full-scale or surveyed digital twin.
- World +x is east; +y is north. The printable PDF is a perspective illustration, so its viewpoint differs from this north-up plan.
- Most footprints are OSM geometry. Purple buildings on the plan are approximate additions inferred from the 2026 PDF: Residence Hall III, Campus Store, The Phoenix, and administration buildings. Their shapes/positions are less certain. Heights and roof details are illustrative.
- Water is rendered as low, solid blue geometry to prevent robot traversal and provide LiDAR returns. This is a simulation safety abstraction, not water physics. Causeways are widened to 1.9 m for robot clearance.
- Roads/paths/parking are included visually. Grass remains traversable: this world does not enforce sidewalk-only navigation or traffic rules. FIPR is off campus in Bartow and is not placed inside this campus.

## Files

| File | Purpose |
|---|---|
| `layout.json` | Source footprints, path network, named locations, scale, provenance, and source IDs |
| `campus.sdf`, `campus_blocked.sdf` | Baseline/blocked worlds using matching visual and collision meshes |
| `meshes/` | Generated building/water/parking geometry; keep this directory beside the worlds |
| `campus.launch.py` | Legacy TurtleBot launcher; use the Goosebot wrapper below for this final |
| `reference.yaml`, `reference.png` | Geometric reference occupancy map; **not a student SLAM result** |
| `mission.json`, `reference_goals.csv` | World/reference-frame home and delivery poses; the launch reads home from mission.json |
| `generate_campus.py` | Recreates assets from layout.json using Python's standard library |

## Launch campus — Terminal 1

Complete the Goosebot setup in [the final-project guide](../README.md) first. Stop previous simulator, SLAM, teleop, RViz, and navigation launches with **Ctrl+C in their launching terminals**. Closing the Gazebo window alone can leave a server running. Check `pgrep -af 'gz sim|gz-sim'` before switching worlds; inspect and stop any leftover simulator server.

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/world.launch.py" \
  world:="$PWD/final_project_simulation/campus/campus.sdf"
```

Expect one collapsed **campus** scenery group and a separate **goosebot** in Gazebo's Entity Tree, at IST's south end at **(-8.500, 9.500) m**, yaw **1.180 rad** (toward IST). The opening camera is aimed at Goosebot here. Right-click its entry and choose **Move To** to focus the camera. Keep the entire campus folder together: the world needs its adjacent `meshes/` and `mission.json`. No `TURTLEBOT3_MODEL` setting is needed.

![Expected Gazebo campus view with Goosebot at IST south end and a collapsed campus scenery group](../images/campus_ist_south_start.png)

*Expected launch result: Goosebot is visible on the yellow Home marker at IST’s south end. Expand `campus` to inspect scenery; `goosebot` remains a separate Entity Tree entry.*

### Updating an existing installation

Pull the current course files after saving your local edits. The corrected meshes are committed; no mesh generation or ROS rebuild is required for the mesh repair itself. Re-run the Step 1 build/setup helper once to install the accompanying Python shutdown fix, then source the workspace again.

The earlier DART error, **“normal count [0] … does not match its vertex count”**, meant collision submeshes were being ignored. The supplied meshes now include explicit surface normals. Do not ignore that error if it persists with custom meshes. The later `rcl_shutdown already called` traceback is a separate cleanup issue; the setup helper now makes that cleanup idempotent.

## Mapping and GPS navigation

Use the current [final-project guide](../README.md): campus SLAM mapping is a separate activity; outdoor navigation uses the supplied GPS localizer instead of AMCL. Keep IST and campus maps under different names. During GPS navigation, SLAM/AMCL stay stopped and the known Home start replaces manual 2D Pose Estimate initialization.

For short-range navigation, use Step 9's rolling LiDAR-costmap mode. For longer routes, the [optional reference-map guide](../goosebot/GPS_MAP_EXTENSION.md) gives full commands to load the supplied `reference.yaml` using `reference_map:=`. No extra mapping or manual alignment is needed: reference geometry and GPS already use the same scaled east/north frame. GPS still supplies localization; the prior map supplies obstacles and live LiDAR detects new ones. A supplied map is not a student-built SLAM result.

The reference grid includes buildings, water barriers and boundaries. In the optional GPS reference-map mode, a derived road/path mask forbids grass in both costmaps. The underlying world still permits physical driving on grass; the navigation mask adds the route restriction. This is not traffic-rule enforcement.

## Optional blocked-causeway trial

Stop all baseline launches with Ctrl+C. Use the same launch command above, replacing `campus.sdf` with `campus_blocked.sdf`. Keep the **baseline campus map** and goals; do not remap the orange barrier. Other crossings remain open. Check live scan/costmap detection and record the response; a detour alone does not prove global replanning.

## Campus poses

These are **world/reference-map and GPS-ENU** coordinates for this teaching world. They can be used in the optional GPS reference-map mode. A student SLAM map may have a different origin/heading; do not copy these coordinates into an unaligned SLAM-map navigation session.

| Yellow pad | x (m) | y (m) |
|---|---:|---:|
| Home at IST south end | -8.500 | 9.500 |
| IST delivery | -5.756 | 11.983 |
| Residence delivery — on road | 1.3612 | 13.7061 |
| GCW delivery | -9.587 | 1.621 |

The home yaw is **1.180 rad**; delivery-pose example yaws remain 0. The supplied `reference.yaml` is a geometric instructor reference, not a student SLAM result. The Residence pad was moved onto its connected paved access road; restart the world after pulling to see the new position.

## Regenerate and customize

```bash
python3 final_project_simulation/campus/generate_campus.py
```

The script overwrites generated worlds, meshes, reference map, plan, and mission files. Edit `layout.json` to change this geographic model. For a simpler beginner box-based world, use `create_simple_world.py` in a copied folder as described in [Create your own world](../CREATE_YOUR_OWN_WORLD.md); do not run that alternative in this campus directory.

Generated OBJ files include a unit normal for every triangle corner, including collision meshes. Regeneration preserves this fix.

**Checked offline:** polygon triangulation, closed mesh topology, map/world footprint agreement, XML/Python syntax, and baseline/blocked connectivity with 0.4 m grid clearance. **Not tested here:** Gazebo rendering/mesh loading, Goosebot spawning/sensors/TF, AMCL, or Nav2 execution. The instructor must pilot both world variants on the course WSL installation. Geometry connectivity is not proof of successful navigation.

## Sources and attribution

- Map data **© OpenStreetMap contributors**, [ODbL 1.0](https://www.openstreetmap.org/copyright); the derivative footprint database is provided in `layout.json` under ODbL. Source way IDs, projection origin, and snapshot date are recorded there. No online map fetch is needed to run the world.
- User-supplied `2026_Printable_Campus_Map_JJ_digital.pdf`: building names and approximate additions checked against its legend. PDF-derived additions are identified individually in layout.json.
- The Google Maps short link could not be retrieved during authoring; no Google imagery or geometry is embedded. This model uses the geographic OSM outlines plus the supplied PDF, not a reproduction of Google's 3-D buildings.


### Flashing road/path surfaces

Overlapping decorative road segments previously shared the same height, causing z-fighting (flickering as the camera moves). The generator now assigns overlapping ground decorations distinct heights in 3 mm increments and lifts delivery markers above them. This changes visual surfaces only; ground/obstacle collisions, the reference map and mission poses are unchanged. Both world variants group scenery under the identity-pose static `campus` model; expand its arrow to inspect individual items. Goosebot and the sun remain separate. After pulling, stop the simulation with Ctrl+C and relaunch; no ROS rebuild is needed for these world changes. Rendering still requires a pilot check on the course WSL installation.

The yellow rectangle under Goosebot marks **Home (pad 0)**. It is visual-only, with no collision surface; the robot drives on the ground. Delivery pads use the same yellow style. Home and its marker now sit at IST's south end in both campus variants. These changes need a full Ctrl+C/relaunch after pulling, not Gazebo Reset; no ROS rebuild is needed. Existing campus obstacle maps still apply, but record the new home pose in your SLAM map's frame.

