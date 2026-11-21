# Optional — GPS navigation using the supplied campus map

**No new mapping or manual alignment is needed for this road-only mode.** The supplied `campus/reference.yaml` and `reference.png` were generated from the same obstacle geometry as the world. Their +x east / +y north coordinates match the GPS ENU frame already used by the live localizer. The 0.06 teaching scale has already been applied; do not scale the map again.

This is optional and ungraded. **INSTRUCTOR VALIDATION REQUIRED:** map/world grid checks and launch/configuration tests pass offline; the full mode still needs a Gazebo pilot.

| Component | Role |
|---|---|
| RTK-like GPS + local odometry/IMU | Estimate position/heading; initialize at the known Home pose |
| Supplied map + layout road/path mask | Global obstacle knowledge plus no-grass routing beyond current LiDAR range |
| Live LiDAR | Detect new obstacles and update costmaps |
| Nav2 | Plan on the full map and control motion using the rolling local costmap |

No AMCL, SLAM or 2D Pose Estimate is used during GPS navigation. The map server supplies `/map`, **not robot localization or TF**; the GPS localizer alone supplies `map → odom`.

The launcher derives a **road-and-paved-path-only planning map** from the supplied layout. It intersects road/path rectangles with obstacle-free cells, marks **grass and all other off-route areas as lethal**, and applies this static mask to **both global and local costmaps**. LiDAR clearing cannot open a shortcut across grass. The controller retains footprint collision checks; goals outside the permitted grid are rejected rather than snapped onto a road.

The mask does not invent connections or widen paths. A 5 cm raster with a one-cell boundary margin represents the scaled routes; very narrow or disconnected paths may be unusable. The Residence delivery pad has been moved onto a connected road at **(1.3612, 13.7061) m**; world, mission coordinates and plan agree. Roads and paved pedestrian paths are permitted; parking areas are excluded unless a mapped road/path crosses them. This does not implement traffic rules.

This is a known simulation prior, not a surveyed real-campus map, perfect localization or student SLAM evidence. The main project's campus SLAM activity remains separate; this extension needs no additional mapping.

## 1. Start fresh campus — Terminal 1

Stop old launches with Ctrl+C and wait for prompts. Install the map-image validation dependency once:

```bash
sudo apt install -y python3-pil
```

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/world.launch.py" \
  world:="$PWD/final_project_simulation/campus/campus.sdf" gps_profile:=rtk
```

Leave Goosebot stationary at fresh Home with the prescribed heading. Keep SLAM, AMCL and teleop stopped. No rebuild is needed for these local-file Python launch changes.

## 2. Start GPS localization and full-map Nav2 — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/gps_navigation.launch.py" \
  profile:=rtk reference_map:="$PWD/final_project_simulation/campus/reference.yaml"
```

**Command breakdown:** `reference_map:=` validates the supplied map, builds a temporary road-only grid and starts its map server plus a full, non-rolling global costmap. The local costmap still rolls but also includes the static road mask; live LiDAR remains enabled in both. Omitting `reference_map:=` restores the existing short-range rolling-costmap mode. RTK-like GPS is required for this optional mode; the ordinary-GPS experiment stays separate.

The launcher checks the map origin, datum, resolution and image pixels against `layout.json` and the generator before starting. It rejects unrelated or unaligned SLAM maps. Keep the complete campus directory together. Expect **GPS_LOCALIZATION_READY**, **road-only campus reference map + live LiDAR**, then map-server and Nav2 activation.

## 3. Open the full-map view — Terminal 3

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
rviz2 -d "$PWD/final_project_simulation/goosebot/gps_reference_navigation.rviz" \
  --ros-args -p use_sim_time:=true
```

Expect white permitted roads/paths and black forbidden grass/obstacles, plus the global costmap, scans and GPS pose. The display is the derived road-only planning map, not the unmasked reference image. Fixed Frame is `map`. **Localization: inactive** in the Nav2 panel refers to AMCL, which is intentionally absent; check Terminal 2's GPS-ready message. Do not send 2D Pose Estimate.

1. At Home, check scan points overlap nearby reference-map building edges. If they do not, stop and check the world, map and Home start; do not add a static TF or manually shift the pose to hide an error.
2. Send a nearby **Nav2 Goal** first and confirm **reached/succeeded**.
3. Click a more distant, free-space destination on the campus map. Nav2 can now plan around known buildings/water beyond the current scan. Inspect the full global path; it should remain on permitted roads/paths. Start with a 10–20 m route, then try a longer one after validation.
4. Live LiDAR still handles new obstacles. Cancel if the robot/localization behaves unexpectedly. A known map does not guarantee every route or recovery will succeed.

Navigation keeps the existing 0.12 m/s autonomous speed limit; the 0.81 m/s teleop setting is separate. To return to known Home, run in another sourced terminal:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
python3 final_project_simulation/goosebot/gps_goal.py --home
```

**Pilot checks:** `/map_server` active; no AMCL/SLAM; GPS is the sole global TF publisher; scan/map alignment at Home and a second location; a longer path remaining on roads/paths around a known obstacle; an off-road goal rejected; a new obstacle visible in live costmaps; reached/succeeded at destination and Home. Save logs for failures. The prior map is obstacle knowledge, not perfect robot localization. No extra required submission or rubric weight.
