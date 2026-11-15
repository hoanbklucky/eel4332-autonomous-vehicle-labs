# Instructor validation — course simulation

Validate on the course WSL installation; upstream tutorials and offline geometry checks do not certify an end-to-end run.

## Labs 2/4/5 — TurtleBot preparation

- [ ] Verify Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, and the installed ROBOTIS Jazzy sources.
- [ ] Run Waffle in TurtleBot3 World, teleoperate, map with Cartographer, save the map, initialize AMCL, and navigate to three goals.
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
