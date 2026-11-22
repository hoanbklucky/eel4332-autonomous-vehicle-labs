# Instructor validation — course simulation

The instructor has exercised the core required indoor/outdoor simulation workflow. Keep this checklist for regression testing after software/configuration changes and for optional scenarios; unchecked items are not a blanket release gate or a claim that every extension has been tested.

## Labs 2/4/5 — TurtleBot preparation

- [ ] Verify Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, and the installed ROBOTIS Jazzy sources.
- [ ] Map World with Waffle and House with Waffle Pi in separate Cartographer sessions, saving distinct map pairs.
- [ ] Initialize AMCL on each matching map/model; reach one World goal and two House goals in different rooms, including doorway traversal.
- [ ] Verify the one-video/short-explanation submission can show both environments clearly.
- [ ] Check meshes, scans, clock, TF, cancellation, and actual stopping.

## Final — Goosebot with supplied LiDAR

Use [the final README](../final_project_simulation/README.md). The baseline LiDAR/bridge/wheel visualization is supplied by the build helper; pilot that baseline after relevant configuration changes. The sensor-settings activity comes after mapping/localization/navigation.

- [ ] Build the pinned Goosebot source natively in the course WSL installation.
- [ ] Verify the supplied 360° LiDAR, scan frame, bridge, mounting clearance and complete robot footprint.
- [ ] Confirm EKF-only odometry TF and exactly one SLAM/AMCL map-to-odom publisher; no ground-truth global localizer.
- [ ] Launch both IST and campus, check spawn/physics/rendering, and manually drive the mission routes.
- [ ] Build a LiDAR SLAM Toolbox map, revisit, save it, and restart cleanly with AMCL/Nav2.
- [ ] Verify scan alignment, three deliveries and home, and Twist command compatibility.
- [ ] Test each blocked variant on the original map, including actual obstacle detection and a feasible alternative.
- [ ] Pilot time/compute demands and starting configuration values before assigning the world.
- [ ] Verify students can follow the self-contained instructions and meet the simplified video/source/short-explanation submission.

Physical Goosebot SLAM/Nav2, stereo RTAB-Map, mission-client programming, and separate algorithm implementations remain optional.


## Goosebot open-arena warm-up pilot

After pulling, run final README Step 1b with `warmup/warmup.sdf` and its matching `reference.yaml`. Check low walls and visible robot, lowercase `i/j/l/k` motion at 0.1 m/s, `/cmd_vel`, odometry/TF, `/projected_map`, and the (3.0, -2.5) Nav2 goal. Stop teleop before Nav2. Generated geometry/map consistency and inflated-grid connectivity are offline checks only; Gazebo/Goosebot/Nav2 require a local runtime pilot. Keep the original maze optional and do not use perfect localization for final SLAM/AMCL evidence.

- [ ] Run the baseline helper twice: confirm no duplicates, preserve complete customized LiDAR settings, and refuse partial/conflicting edits.
- [ ] Pilot wheel joint-state visualization and the final single-setting LiDAR observation; it must not gate baseline mapping/localization/navigation.


## Sequenced world startup — regression checks

Offline checks cover explicit-world spawn arguments, server PID detection, create-result callbacks and Python syntax. The previous `gz model` verification gate timed out on the instructor's machine and was removed; it must not block GUI startup. The new ROS launch sequence itself requires Gazebo testing:

- [ ] With no existing server, start IST; confirm server/create precede GUI and `goosebot` is visible in the Entity Tree.
- [ ] Repeat clean start/stop five times; verify no orphan server remains after Ctrl+C and after GUI close.
- [ ] Try a second launch while the first runs; confirm it refuses with existing PIDs without affecting the first simulation.
- [ ] Confirm explicit-world spawning and failure shutdown with campus and both blocked variants.
- [ ] Confirm camera configuration, /clock, /scan, /joint_states, EKF TF and RViz after delayed GUI startup.


## Campus mesh normals and shutdown repair

The campus OBJ generator now supplies explicit unit normals per triangle corner. All 37 regenerated meshes retain their original triangle coordinates/winding; vertex and normal counts agree. Generated baseline/blocked SDF, reference image, and mission files are unchanged. The baseline configuration helper replaces the odometry script's unconditional rclpy.shutdown() with idempotent rclpy.try_shutdown(); syntax and repeat-setup checks passed. Pilot campus rendering, collisions, scans, spawning, and Nav2 on WSL; An EKF context error during coordinated shutdown may be an independent upstream shutdown race; inspect the first error before the shutdown tail.


## Indoor/outdoor branch validation — main

Required scope now covers IST and campus: short maps, two destinations/home each, IST blocked-route test, indoor single-setting LiDAR comparison, campus GPS inspection at three stationary locations, and 30% system understanding. Campus blocked-route repetition and GPS fusion remain optional. Preserve independent ist_map/campus_map files.

The pinned robot already declares gps_sensor (5 Hz, gps_link, gps/fix), horizontal position Gaussian stddev 1.5 m and vertical 3 m; its bridge maps gz.msgs.NavSat to sensor_msgs/msg/NavSatFix. Campus worlds/generator now add exactly one gz::sim::systems::NavSat world plugin and WGS84 ENU datum (latitude 28.1485, longitude -81.8495, elevation/heading 0), following the official gz-sim8 spherical_coordinates example. The 0.06 teaching-scale geometry means these are synthetic geographic readings, not the full-scale campus building coordinates.

Offline checks passed: generator Python syntax, both generated SDFs, sole-plugin/datum diff against baseline worlds, unchanged scenery/camera/collisions/reference map, baseline/blocked geometric connectivity, Markdown fences and Bash syntax in main/new activity guides. Existing EKF/Nav2 settings and student TODOs were not altered; GPS is not an EKF input in the required baseline. Instructor private setup is retained, with its separate workspace.

Before release, pilot both worlds and map names; AMCL two destinations/home per world; IST barrier; restored LiDAR setting; GPS Gazebo and ROS message flow, status/covariance fields, TF, rate under simulation time, and three-location stationary/moving observations. A bridge publisher alone is not successful GPS publication. Do not infer real-world occlusion/multipath from drawn buildings. Inspect the configuration masks and actual runtime topics when assessing student fusion explanations.


## Saved-map startup and Nav2 RViz correction

Course navigation.launch.py validates the saved YAML/image pair and explicitly injects the absolute yaml_filename in temporary Nav2 parameters as well as forwarding map to standard bringup. Standard Jazzy localization source should honor map already; the exact reason the reported installed system retained an empty parameter is unconfirmed. This wrapper removes reliance on only that forwarding path without claiming an upstream bug. The source YAML is preserved. Step 6 and the campus command use the wrapper; navigation RViz uses explicit nav2_default_view.rviz, including Nav2 Goal, rather than a generic or leftover mapping layout. Manual load_map is no longer part of the documented procedure.

Three offline regression checks pass: blank/stale map parameter override with unrelated settings preserved, early failure for missing map/image, and absolute-image/no-map-server-section support (including paths with spaces). Python/YAML and command syntax checked. For future startup changes, check ROS lifecycle/map publication and RViz plugins. Confirm auto-loaded /map, nonblank map_server yaml_filename, initial-pose scan alignment, Nav2 Goal and reached feedback after a fresh launch on WSL. No ROS rebuild is needed for repository-local launch/doc changes.
