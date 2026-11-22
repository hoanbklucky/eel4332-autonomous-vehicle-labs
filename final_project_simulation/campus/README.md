# Florida Polytechnic campus — full-scale simulation

![North-up campus plan](campus_plan.svg)

Horizontal coordinates now use **1:1 meters**, restored from the previous 0.06 layout. The world covers about **1,217 × 1,333 m**. Goosebot, wheel radii, sensor ranges and GPS noise are unscaled. OSM/PDF-derived footprints, building heights and widths are approximate; this is not a surveyed digital twin.

**Measured width references:** narrow walk **3.12 m**, Home pedestrian crossing **11.31 m**, diagonal Residence-side route **7.22 m**. Unmeasured walks use the instructor-reported **3 m minimum**. The **21.87 m** Polytechnic Circle measurement includes median/sidewalk/verge and is not a drivable width. Read [width provenance and access rules](WIDTHS_AND_ACCESS.md).

**Robot access:** mapped pedestrian paths, separate sidewalks and reviewed interior non-asphalt paved corridors. Identified asphalt carriageways/parking access and grass remain forbidden in both navigation costmaps, including where a pedestrian centerline overlaps a motor road. The visible world still shows those roads.

## Required campus navigation — use final-project-indoor-outdoor

Follow [final-project Step 9B](https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs/blob/final-project-indoor-outdoor/final_project_simulation/README.md#gps-aided-outdoor-navigation). It includes every terminal command. Use the supplied `reference.yaml`, RTK-like GPS, the pedestrian-only global/local costmaps, live LiDAR, and goals **A → B → Home**. A/B are about 20 m from Home along mapped routes, avoiding a campus-wide drive. Short-range map-free navigation is retired. GPS provides pose; the prior map provides route knowledge. No AMCL, SLAM or 2D Pose Estimate runs during this activity.

Campus SLAM remains a separate, local mapping activity around Home; do not map the entire campus or use an unaligned student map for GPS navigation. The pedestrian mask forbids asphalt motor roads and grass in navigation; the underlying physical world does not model grass as an obstacle. Non-asphalt interior paved corridors, pedestrian paths and separate sidewalks are allowed; this does not implement traffic rules.

## Start campus — Terminal 1

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/world.launch.py" \
  world:="$PWD/final_project_simulation/campus/campus.sdf"
```

Leave still at known Home **(-138.269497, 157.530227) m**, yaw **1.338654 rad**. The opening camera stays a few meters from Goosebot; right-click its entity and choose Move To if needed. Keep the complete campus directory together for mesh lookup. Use the linked final-project-indoor-outdoor guide for Terminals 2–4; main does not include those GPS navigation tools.

## Updating from the reduced world

Stop all launches with Ctrl+C, save work, pull the matching branch and restart. Generated worlds, meshes and map are committed; this update needs no asset generation or ROS rebuild. **Old campus maps, goals, screenshots and recordings belong to the reduced world.** Preserve them as historical results, then collect new evidence with the matching full-scale assets. A Gazebo Reset does not load changed world files.

## Coordinates and files

Coordinates below are world/reference-map/GPS-ENU meters; student SLAM maps may have different origins/headings.

| Marker | x (m) | y (m) |
|---|---:|---:|
| Home | -138.269497 | 157.530227 |
| IST delivery | -95.902258 | 199.529632 |
| Residence delivery | 22.686100 | 228.434483 |
| GCW delivery | -158.764060 | 27.947684 |
| Campus goal A | -129.772204 | 174.716679 |
| Campus goal B | -142.870762 | 138.066713 |

`mission.json` supplies Home and A/B goals directly to the launch/goal helper. Named delivery pads remain landmarks, not additional required long drives. `reference_goals.csv` lists delivery-pad positions. `layout.json` is the geometry/width source; `generate_campus.py` regenerates both worlds, meshes, the obstacle map and plan. The 25 cm obstacle map limits memory for the full campus; the local Nav2 grid is 2.5 cm. The pedestrian-only map is derived temporarily at launch and has a conservative one-cell boundary margin.

Regenerate only when editing geometry:

```bash
python3 final_project_simulation/campus/generate_campus.py
```

This uses Python's standard library. Keep map, world, layout and mission from the same generation. Source attribution is in [SOURCES.md](SOURCES.md). Original PDF reference images are not committed.

The blocked world is an optional obstacle trial, not required evidence. It adds a 4 m barrier across the crossing; do not remap it. Water is solid collision geometry for simulation. Ground decorations are visual-only and layered to avoid flicker; all scenery is grouped beneath static `campus` with identity pose. Meshes include explicit normals for DART collision loading.

**INSTRUCTOR VALIDATION REQUIRED:** offline geometry, route-clearance and configuration checks do not establish successful live Gazebo navigation. Pilot A/B/Home before student release. Historical screenshots show the older reduced arena.
