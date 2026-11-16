# Instructor validation — course simulation

Validate on the course WSL installation; upstream tutorials and offline geometry checks do not certify an end-to-end run.

## Labs 2/4/5 — TurtleBot preparation

- [ ] Verify Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, and the installed ROBOTIS Jazzy sources.
- [ ] Map World with Waffle and House with Waffle Pi in separate Cartographer sessions, saving distinct map pairs.
- [ ] Initialize AMCL on each matching map/model; reach one World goal and two House goals in different rooms, including doorway traversal.
- [ ] Verify the one-video/short-explanation submission can show both environments clearly.
- [ ] Check meshes, scans, clock, TF, cancellation, and actual stopping.

## Final — Goosebot with student-added LiDAR

Use [the final README](../final_project_simulation/README.md). Its required sensor addition remains student work; pilot with an instructor's completed copy.

- [ ] Build the pinned Goosebot source natively in the course WSL installation.
- [ ] Verify the added 360° LiDAR, scan frame, bridge, mounting clearance and complete robot footprint.
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
