# Final Project — Integrated Autonomous Navigation with Goosebot

## Mission

**Integrate localization, mapping/navigation, planning, and control to complete a multi-waypoint autonomous mission, then validate as much of the stack as possible on Goosebot.**

## Project Philosophy

The final project is an integration assessment. It should reuse concepts and code from earlier labs rather than introduce a completely unrelated task.

A successful simulation demonstration is required. Physical Goosebot deployment is the intended final stage, but hardware availability or a documented hardware fault should not erase otherwise valid software/system work.

## Required Milestones

### Milestone 1 — System Architecture

Create a diagram showing:

- sensors;
- state estimation/localization;
- map;
- global/local planning;
- control;
- safety/fault handling;
- robot/vehicle interface.

Identify important ROS topics/services/actions.

### Milestone 2 — Simulation Mission

In the instructor-approved Gazebo/Nav2 environment:

1. start from a known pose;
2. localize on a saved map or establish localization;
3. navigate to multiple waypoints;
4. encounter at least one obstacle/change;
5. complete the mission or document the failure.

### Milestone 3 — Quantitative Evaluation

Report at least three metrics such as:

- mission success;
- completion time;
- path length;
- position error at goal;
- number of replans;
- minimum obstacle clearance;
- recovery count.

### Milestone 4 — Safety / Failure Case

Demonstrate at least one controlled failure or degraded condition and explain the system response.

### Milestone 5 — Goosebot Deployment

Use the instructor Goosebot repository:

https://github.com/hoanbklucky/goose

Expected workflow:

1. verify hardware/network;
2. verify LiDAR/odometry/TF;
3. build or load a map;
4. localize;
5. run Nav2;
6. send multiple goals;
7. observe obstacle/recovery behavior.

**INSTRUCTOR VALIDATION REQUIRED:** insert the exact Goosebot ROS 2 branch, bringup package, topic names, and launch commands before project release.

## Hardware-Failure Policy

If the physical platform is unavailable or fails for reasons outside the team's control:

- demonstrate the full simulation mission;
- provide evidence of physical bringup/debugging attempts;
- identify the failure layer;
- explain what would be required to complete deployment.

## Final Demonstration

During the demonstration, each student should be able to answer questions about:

- system architecture;
- localization;
- planning;
- control;
- failure handling;
- the team's own code and results.

## Suggested Evaluation Categories

- Required milestones / mission completion
- System design and technical correctness
- Testing and quantitative results
- Failure analysis / safety
- Documentation and presentation
- Individual technical understanding

## Deliverables

- source code/configuration;
- system architecture diagram;
- results/plots;
- demonstration video;
- concise report or project README;
- individual contribution summary.
