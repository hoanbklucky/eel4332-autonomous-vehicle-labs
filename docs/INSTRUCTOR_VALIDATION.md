# Instructor validation — course simulation

Validate on the course WSL installation; upstream tutorials and offline geometry checks do not certify an end-to-end run.

## Labs 2/4/5 — TurtleBot preparation

- [ ] Verify Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, and the installed ROBOTIS Jazzy sources.
- [ ] Map World with Waffle and House with Waffle Pi in separate Cartographer sessions, saving distinct map pairs.
- [ ] Initialize AMCL on each matching map/model; reach one World goal and two House goals in different rooms, including doorway traversal.
- [ ] Verify the one-video/short-explanation submission can show both environments clearly.
- [ ] Check meshes, scans, clock, TF, cancellation, and actual stopping.

## Final — Goosebot with supplied LiDAR

Use [the final README](../final_project_simulation/README.md). The baseline LiDAR/bridge/wheel visualization is supplied by the build helper; pilot that baseline before release. The sensor-settings activity comes after mapping/localization/navigation.

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


## Sequenced world startup — local pilot required

Offline checks cover explicit-world spawn arguments, server PID detection, create-result callbacks and Python syntax. The previous `gz model` verification gate timed out on the instructor's machine and was removed; it must not block GUI startup. The new ROS launch sequence itself requires Gazebo testing:

- [ ] With no existing server, start IST; confirm server/create precede GUI and `goosebot` is visible in the Entity Tree.
- [ ] Repeat clean start/stop five times; verify no orphan server remains after Ctrl+C and after GUI close.
- [ ] Try a second launch while the first runs; confirm it refuses with existing PIDs without affecting the first simulation.
- [ ] Confirm explicit-world spawning and failure shutdown with campus and both blocked variants.
- [ ] Confirm camera configuration, /clock, /scan, /joint_states, EKF TF and RViz after delayed GUI startup.

