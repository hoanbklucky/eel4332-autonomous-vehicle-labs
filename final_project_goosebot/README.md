# Final Project — Integrated Autonomous Navigation with Goosebot

## Mission

**Integrate localization, mapping/navigation, planning, and control to complete a multi-waypoint autonomous mission, then validate as much of the stack as possible on Goosebot.**

## Project Philosophy

The final project is an integration assessment. It should reuse concepts and code from earlier labs rather than introduce a completely unrelated task.

A successful simulation demonstration is required. Physical Goosebot deployment is the intended final stage, but hardware availability or a documented hardware fault should not erase otherwise valid software/system work.

The simulation uses TurtleBot in Gazebo; it is not a Goosebot digital twin. TurtleBot uses two-wheel differential drive. Goosebot uses four-wheel skid steering, with four conventional wheels powered by four DC motors on fixed parallel axes. Students should transfer the ROS 2 architecture while validating Goosebot's motor mapping, lateral slip, effective turning behavior, and safety limits rather than assuming that simulator parameters are interchangeable.

## Prerequisites

- Complete Labs 00–07 and preserve evidence from their successful baseline tests.
- Obtain the instructor-approved simulation image and Goosebot access procedure.
- Review the team's command authority, stop, reset, and hardware-test boundaries.

## Background

### Why require simulation before hardware?

The final project combines many individually reasonable components into one timed, stateful system. TurtleBot in Gazebo provides a repeatable integration environment for checking launch order, topics, TF, maps, localization, Nav2 behavior, metrics, logging, and controlled failures before hardware variability is introduced. A staged simulation result narrows later Goosebot problems to the platform interface or sim-to-real assumptions.

Simulation completion is necessary but not sufficient. Goosebot differs in geometry, four-motor skid-steer motion, tire slip, sensor placement, latency, computational load, braking, and safe operating limits. Transfer the software architecture and validation method; do not transfer unverified topic names, controller gains, footprints, speeds, or thresholds.

### Integration contracts and staged evidence

Each connection between components is an interface contract: message type, units, frame, timing, update rate, range, and ownership must agree. Verify the system in layers—platform motion, sensors, TF, localization, map, planning, control, then safety—before attempting the complete mission. Save commands, configurations, logs, and quantitative baselines so a failure can be reproduced rather than diagnosed from memory.

Ground truth available in Gazebo is useful for evaluation but should not silently become an autonomy input. On Goosebot, define an independent reference or acknowledge when a metric cannot be measured directly.

## Provided Files

```text
final_project_goosebot/
├── README.md
├── src/
└── results/
```

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
2. verify the four-motor skid-steer command mapping and safe stop;
3. verify LiDAR/odometry/TF;
4. confirm the physical footprint, speed limits, and controller parameters;
5. build or load a map;
6. localize;
7. run Nav2;
8. send multiple goals;
9. observe obstacle/recovery behavior.

**INSTRUCTOR VALIDATION REQUIRED:** insert the exact Goosebot ROS 2 branch, bringup package, topic names, and launch commands before project release.

Do not send TurtleBot commands to Goosebot until the instructor-provided interface and limits have been validated. Topic names and message types may differ even when both platforms expose a velocity-command abstraction.

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

## Troubleshooting

- Return to the last independently verified layer instead of repeatedly launching the full mission.
- Record exact package versions, launch arguments, topic types, frames, and parameter files.
- Do not hide a simulation failure by switching to hardware or bypass a hardware safety check to meet a deadline.
- When simulator and hardware behavior differ, identify the specific model, interface, timing, or calibration assumption being tested.
- Follow the hardware-failure policy and preserve evidence of diagnosis when an external limitation prevents deployment.
