# Instructor validation — ROBOTIS Jazzy workflow

The required baseline follows the official ROBOTIS tutorials linked in Lab 00, Lab 4, and Lab 5. Validate on the course WSL image; upstream instructions do not certify this local environment.

- [ ] Confirm Ubuntu 24.04, ROS 2 Jazzy, and modern Gazebo.
- [ ] Complete official PC/software and simulation installation in `~/turtlebot3_ws`.
- [ ] Record package versions/commits, model (Burger), world (TurtleBot3 World), and start pose.
- [ ] Run the updated installation checker after sourcing the workspace.
- [ ] Complete Lab 2 with official teleoperation and its actual command type.
- [ ] Run the official Cartographer mapping tutorial; save and inspect the course map pair.
- [ ] Load that same map with official TurtleBot3 Nav2; initialize AMCL and reach three goals.
- [ ] Confirm robot meshes, scan, map, clock, and TF work in RViz2.
- [ ] Test final-client readiness, results, simulation-time waits/timeouts, cancellation, and actual stopping.
- [ ] Test odometry recording and three matched baseline trials.
- [ ] Publish exact obstacle size, pose, world variant/reset procedure, and feasible alternative route.
- [ ] Run the final obstacle trial with the original map and fixed navigation configuration.
- [ ] Keep algorithm extensions and physical Goosebot SLAM/Nav2 optional.

No old custom TF bridge, Nav2-minimal mesh workaround, manual lifecycle sequence, or standalone SLAM Toolbox is part of this baseline.
