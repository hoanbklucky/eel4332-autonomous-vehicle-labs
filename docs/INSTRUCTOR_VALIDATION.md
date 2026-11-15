# Instructor Validation Checklist

These checks must be completed on the actual course image before release. Documentation/static checks are not substitutes for a ROS/Gazebo run. Record test date, OS, package versions, robot model, world, start pose, and results.

## Environment and foundations
- [ ] Labs 00–03 run in supported Ubuntu 24.04 / ROS 2 Jazzy / Gazebo Harmonic.
- [ ] Installation checker passes, including the SLAM/Nav2 packages.
- [ ] ROS Python imports work in the interpreter used for mission code.
- [ ] ROS 2 practice package builds from a clean workspace.
- [ ] Simulator, RViz2, scan, odometry, clock, teleoperation, stop, and reset work.
- [ ] Confirm actual command message type and documented launch arguments.
- [ ] Confirm one owner per TF edge; add no duplicate bridge.

## Lab 4 — SLAM
- [ ] Run the mapping sequence in the shared runbook on the course image.
- [ ] Freeze a full SLAM configuration with observed topics/frames and simulation time.
- [ ] Confirm mapping works with AMCL/navigation inactive.
- [ ] Build two maps from fresh states using planned routes.
- [ ] Supply independent wall geometry or use explicitly labeled consistency measures.
- [ ] Save YAML/image pairs, copy the selected pair, and load that exact copy in Lab 5.
- [ ] Capture a successful mapping screenshot showing map, robot, scan, and TF.
- [ ] Keep the separate Kalman exercise optional.

## Lab 5 — Guided navigation
- [ ] Freeze a full Nav2 configuration for the exact world/model and package versions.
- [ ] Test AMCL startup, initial pose, scan alignment, and navigation activation.
- [ ] Reach three open-space goals in RViz2.
- [ ] Confirm cancellation terminal status, actual stopping, and clean restart.
- [ ] Capture a navigation screenshot identifying global path, costmap, scan, and robot.
- [ ] Keep separate A*, Pure Pursuit, and synthetic safety-monitor exercises optional.

## Simulation final — Delivery mission
- [ ] Publish the exact world/model, initial pose, baseline configuration, and mission limits.
- [ ] Verify installed Jazzy Simple Commander API and simulation-time behavior.
- [ ] Validate a reference delivery mission: three deliveries, 3-second waits, return home.
- [ ] Verify acceptance/results, failed-goal termination, timeout, interruption, and cancellation.
- [ ] Confirm recorder QoS, mission interval selection, and clock-reset rejection.
- [ ] Complete three repeatable baseline runs with preserved logs.
- [ ] Provide a tested obstacle world variant or exact reproducible placement instructions.
- [ ] Record obstacle size/world-frame pose; verify collision geometry and LiDAR visibility.
- [ ] Verify an alternate route exists and goals/start remain free.
- [ ] Run the obstacle trial with the original saved map and fixed configuration.
- [ ] Capture obstacle/costmap/path evidence and a sample results table.
- [ ] Decide whether the shortened one-week version needs an instructor-provided client.
- [ ] Confirm students can reuse Lab 4–5 artifacts without duplicating submissions.

## Optional work
Validate algorithm extensions separately only if assigning them. Goosebot lane following is the completed hardware component; SLAM/Nav2 deployment is not required. Any future hardware extension needs separate validated interfaces, odometry, TF, footprint, skid-steer parameters, and stopping procedures.
