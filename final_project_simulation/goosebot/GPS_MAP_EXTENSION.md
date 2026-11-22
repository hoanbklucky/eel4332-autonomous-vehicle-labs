# Required — GPS navigation using the full-scale campus map

**No new mapping or manual alignment is needed for this road-only mode.** The supplied `campus/reference.yaml` and `reference.png` were generated from the same obstacle geometry as the world. Their +x east / +y north coordinates match the GPS ENU frame already used by the live localizer. World and map now use 1:1 horizontal meters; Goosebot is unscaled. Do not apply the old 0.06 factor.

This is the required outdoor navigation activity in final-project Step 9B. **INSTRUCTOR VALIDATION REQUIRED:** map/world grid checks and launch/configuration tests pass offline; the full mode still needs a Gazebo pilot.

| Component | Role |
|---|---|
| RTK-like GPS + local odometry/IMU | Estimate position/heading; initialize at the known Home pose |
| Supplied map + layout road/path mask | Global obstacle knowledge plus no-grass routing beyond current LiDAR range |
| Live LiDAR | Detect new obstacles and update costmaps |
| Nav2 | Plan on the full map and control motion using the rolling local costmap |

No AMCL, SLAM or 2D Pose Estimate is used during GPS navigation. The map server supplies `/map`, **not robot localization or TF**; the GPS localizer alone supplies `map → odom`.

The launcher derives a **road-and-paved-path-only planning map** from the supplied layout. It intersects road/path rectangles with obstacle-free cells, marks **grass and all other off-route areas as lethal**, and applies this static mask to **both global and local costmaps**. LiDAR clearing cannot open a shortcut across grass. The controller retains footprint collision checks; goals outside the permitted grid are rejected rather than snapped onto a road.

The mask does not invent connections or widen paths. The 25 cm global raster includes a one-cell boundary margin; the rolling local grid is 2.5 cm. The 20 × 20 cm footprint is retained. Widths are explicit full-scale assumptions (6 m road, 3.5 m service road, 2 m walk, 3 m crossing), not surveyed measurements. Home/delivery markers are on mapped centerlines; read current coordinates from mission.json. Roads and paved pedestrian paths are permitted; parking areas are excluded unless a mapped road/path crosses them. This does not implement traffic rules.

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

**Command breakdown:** `reference_map:=` validates the supplied map, builds a temporary road-only grid and starts its map server plus a full, non-rolling global costmap. The local costmap still rolls but also includes the static road mask; live LiDAR remains enabled in both. The launcher defaults to this supplied map and rejects an empty map argument; short-range mode is retired. RTK-like GPS is required for this mode; the ordinary-GPS experiment stays separate.

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

1. At Home, verify scan/map alignment; stop if it is wrong rather than hiding it with a manual transform.
2. Use `gps_goal.py --waypoint A`, then `--waypoint B`, then `--home` as shown in the main guide. Wait for SUCCEEDED after each. These nearby goals avoid a campus-wide drive.
3. Inspect the global path staying on roads/paths beyond the current scan. An off-road goal must be rejected. Live LiDAR continues to detect new obstacles.
4. Save the required campus video. Existing screenshots show the older reduced campus and are not evidence of full-scale validation.

Navigation uses a 0.30 m/s autonomous speed limit; the 0.81 m/s teleop setting is separate. To return to known Home, run in another sourced terminal:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
python3 final_project_simulation/goosebot/gps_goal.py --home
```

**Pilot checks:** `/map_server` active; no AMCL/SLAM; GPS is the sole global TF publisher; scan/map alignment at Home and a second location; a longer path remaining on roads/paths around a known obstacle; an off-road goal rejected; a new obstacle visible in live costmaps; reached/succeeded at destination and Home. Save logs for failures. The prior map is obstacle knowledge, not perfect robot localization. Include this activity in the existing campus navigation video and navigation rubric; no extra rubric category is added.
