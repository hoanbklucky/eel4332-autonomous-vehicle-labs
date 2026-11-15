# Florida Polytechnic campus world — geographic layout, version 2

> **For the current Goosebot final:** use the complete commands in [the final-project README](../README.md). The TurtleBot launch/mapping instructions below are retained as an optional reference and do not add the required Goosebot LiDAR.

This replaces the earlier arbitrary 24 × 30 m block layout. It uses **OpenStreetMap building, lake, road, parking, and path outlines**, checked against the supplied **2026 printable campus map**. The IST footprint is elongated/curved; BARC and the residence cluster retain their real shapes and relative positions; the lake chain and multiple causeways are preserved.

![North-up campus plan](campus_plan.svg)

## Accuracy and teaching adjustments

- Horizontal geometry uses a **uniform 0.06 scale** (about 1:16.7), retaining geographic proportions/angles. The teaching arena is 73 × 80 m. It is not a full-scale or surveyed digital twin.
- World +x is east; +y is north. The printable PDF is a perspective illustration, so its viewpoint differs from this north-up plan.
- Most footprints are OSM geometry. Purple buildings on the plan are approximate additions inferred from the 2026 PDF: Residence Hall III, Campus Store, The Phoenix, and administration buildings. Their shapes/positions are less certain. Heights and roof details are illustrative.
- Water is rendered as low, solid blue geometry to prevent robot traversal and provide LiDAR returns. This is a simulation safety abstraction, not water physics. Causeways are widened to 1.9 m for Waffle clearance.
- Roads/paths/parking are included visually. Grass remains traversable: this world does not enforce sidewalk-only navigation or traffic rules. FIPR is off campus in Bartow and is not placed inside this campus.

## Files

| File | Purpose |
|---|---|
| `layout.json` | Source footprints, path network, named locations, scale, provenance, and source IDs |
| `campus.sdf`, `campus_blocked.sdf` | Baseline/blocked worlds using matching visual and collision meshes |
| `meshes/` | Generated building/water/parking geometry; keep this directory beside the worlds |
| `campus.launch.py` | Uses installed ROBOTIS Waffle spawning, bridges, and robot-state publisher |
| `reference.yaml`, `reference.png` | Geometric reference occupancy map; **not a student SLAM result** |
| `mission.json`, `reference_goals.csv` | World/reference-frame home and delivery poses; the launch reads home from mission.json |
| `generate_campus.py` | Recreates assets from layout.json using Python's standard library |

Install Lab 4 dependencies first. Use a WSL/Ubuntu terminal. Stop existing Gazebo, SLAM, teleop, and Nav2 processes before switching worlds. After updating an earlier campus version, rebuild your SLAM map; its old map/goals do not match this layout.

## 1. Launch — Terminal 1

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/campus/campus.launch.py"
```

The robot spawns near IST at **(-15.025, 17.888) m**, yaw 0 (east), in world coordinates. Check `waffle` in the Entity Tree. The launch adds the campus resource directory for mesh lookup; do not copy the SDF alone into another folder.

## 2. Map with SLAM — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
```

Drive from **Terminal 3**, mapping the delivery routes, both sides of the lake, and the alternative causeways:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```

Keep keyboard focus in Terminal 3. `w/x` changes forward speed, `a/d` changes turn rate, and `s` or Space stops. You need enough mapped coverage for the delivery mission and its alternative route; mapping every remote corner is unnecessary.

Stop motion, then save from **Terminal 4** while mapping/simulation remain running:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
cd ~/courses/eel4332-autonomous-vehicle-labs/final_project_simulation
mkdir -p results
ros2 run nav2_map_server map_saver_cli -f "$PWD/results/campus_map" --ros-args -p use_sim_time:=true
```

Keep `campus_map.yaml` and its image together. Then stop keyboard, Cartographer, and simulator with Ctrl+C.

## 3. Navigate

Restart the baseline campus in Terminal 1. In another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:="$PWD/final_project_simulation/results/campus_map.yaml"
```

Use **2D Pose Estimate** at home in your map and check scan alignment as in Lab 5. Stop localization teleop before navigation. Test a nearby goal first.

| Yellow pad | World / reference-map x (m) | y (m) |
|---|---:|---:|
| 0 Home near IST | -15.025 | 17.888 |
| 1 IST delivery | -5.756 | 11.983 |
| 2 Residence delivery | -0.043 | 12.883 |
| 3 GCW delivery | -9.587 | 1.621 |

All example yaws are 0. **Your SLAM map may have a different origin/heading.** Select the yellow pads/home in RViz2 on your own saved map and record those map-frame coordinates. Use the table/CSV directly only with the supplied reference map.

For an instructor reference-map check, substitute `final_project_simulation/campus/reference.yaml` in the navigation command and initialize at the world/reference home pose above. The PNG map is accepted by Nav2. This map is generated from geometry and must not be presented as student SLAM output.

This world is larger than Lab 5's arena. Choose fixed mission/time limits based on a successful pilot run; a per-goal limit around **600 simulation seconds** is a starting example, not a guarantee.

## 4. Blocked-causeway trial

Stop all baseline processes. Restart with:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/campus/campus.launch.py" world_file:=campus_blocked.sdf
```

Use the **same baseline map**, goals, and configuration. Do not remap the added orange barrier. It blocks a mapped causeway at world **(-6.8685, 11.3297) m**, yaw **2.3159 rad**, dimensions **4.0 × 0.35 × 0.8 m**. Other crossings remain open. Verify live scan/costmap detection and record actual response; a detour alone does not prove global replanning.

## Regenerate and customize

```bash
python3 final_project_simulation/campus/generate_campus.py
```

The script overwrites generated worlds, meshes, reference map, plan, and mission files. Edit `layout.json` to change this geographic model. For a simpler beginner box-based world, use `create_simple_world.py` in a copied folder as described in [Create your own world](../CREATE_YOUR_OWN_WORLD.md); do not run that alternative in this campus directory.

**Checked offline:** polygon triangulation, closed mesh topology, map/world footprint agreement, XML/Python syntax, and baseline/blocked connectivity with 0.4 m grid clearance. **Not tested here:** Gazebo rendering/mesh loading, Waffle spawning/sensors/TF, AMCL, or Nav2 execution. The instructor must pilot both world variants on the course WSL installation. Geometry connectivity is not proof of successful navigation.

## Sources and attribution

- Map data **© OpenStreetMap contributors**, [ODbL 1.0](https://www.openstreetmap.org/copyright); the derivative footprint database is provided in `layout.json` under ODbL. Source way IDs, projection origin, and snapshot date are recorded there. No online map fetch is needed to run the world.
- User-supplied `2026_Printable_Campus_Map_JJ_digital.pdf`: building names and approximate additions checked against its legend. PDF-derived additions are identified individually in layout.json.
- The Google Maps short link could not be retrieved during authoring; no Google imagery or geometry is embedded. This model uses the geographic OSM outlines plus the supplied PDF, not a reproduction of Google's 3-D buildings.
