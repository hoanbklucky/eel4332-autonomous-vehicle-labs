# Lab 5 — Navigate on your SLAM map

## Mission

Load your Lab 4 map, localize TurtleBot with AMCL, and use Nav2 to reach three goals in Gazebo. This guided lab prepares you for the [simulation final project](../final_project_simulation/README.md).

## Learning Objectives

- distinguish mapping from localization on a saved map;
- inspect the global path, local costmap, and executed motion;
- send navigation goals and recognize success, failure, and cancellation;
- save reproducible mission inputs and evidence.

## Prerequisites

Complete Lab 4 and retain the selected map YAML/image pair. Use ROS 2 Jazzy and Gazebo Harmonic. Follow the [shared runbook](../docs/SIMULATION_WORKFLOW.md) for terminal commands, startup, and stopping.

## Background

SLAM Toolbox builds the map during mapping. In saved-map navigation, stop SLAM and let AMCL estimate the pose on that map. Nav2 supplies planning, control, and recovery. Your project client will choose destinations and handle results.

Your optional Python A* and Pure Pursuit exercises are independent of Nav2; they are not plugins used by the live robot. See [optional background](OPTIONAL_BACKGROUND.md) and [optional algorithm exercises](ALGORITHM_EXPERIMENTS.md).

## Provided Files

- `src/mission_client.py`: final-project mission scaffold; the guided lab can use RViz2.
- `src/record_odometry.py`: ready-to-use odometry recorder.
- `config/goals.csv`: header for three delivery destinations.
- `answers.md`: lab record.
- [Simulation runbook](../docs/SIMULATION_WORKFLOW.md#navigation-mode).

## Step-by-Step Procedure

### 1. Load your map and localize

Stop the mapper, teleoperation, and previous simulator. Follow Navigation mode in the runbook. Copy the installed full Nav2 configuration as described there, pass your own map and parameter paths, and use simulation time.

Initialize AMCL with **2D Pose Estimate** at the starting pose expressed in your saved map. Check laser/wall alignment and `map -> odom -> base_link` connectivity before activating navigation. Keep teleoperation stopped.

### 2. Reach three destinations

Choose three reachable, open-space poses. Record map-frame x/y in metres and yaw in radians in `config/goals.csv`. Use RViz2 **Nav2 Goal** to visit them one at a time. Observe the planned path and actual motion. Confirm each result before sending the next goal.

Capture one screenshot showing the map, robot, scan, global path, and costmap. Label what each display represents. A visible path alone is not evidence that the destination was reached.

### 3. Practice cancellation and restart

Send a reachable goal, then cancel it in RViz2 while the robot moves. Confirm both the action result and actual stopping in Gazebo/odometry. If motion continues, pause Gazebo and follow the runbook shutdown procedure.

Restart cleanly, reinitialize localization, and reach one goal again. Do not collect data across a simulator clock reset.

### 4. Prepare the final-project handoff

Save the map pair, full Nav2 configuration, three goal poses, map-frame home pose, and exact launch commands. Identify the installed planner/controller plugins and footprint or robot radius. Reuse these artifacts in the final rather than remapping unnecessarily.

## Experiment / Quantitative Analysis

For this guided lab, record three goal outcomes and approximate simulation-time durations. Explain one difference between the planned path and observed motion. Repeated trials, CSV metrics, and the obstacle challenge belong to the final project.

Optional: compare two inflation-radius settings while holding the map, goals, initial pose, and other parameters fixed. Inflation changes costs around obstacles; it does not guarantee minimum clearance. Do not alter the footprint to force passage.

## Engineering Questions

1. Why does loading the map not tell AMCL the robot's initial pose?
2. What is the difference between the global path and the robot's executed trajectory?
3. What evidence shows that cancellation actually stopped the robot?
4. Which components would need platform-specific validation on Goosebot?

## Success Criteria

- [ ] Your own saved SLAM map loads and localization aligns with it.
- [ ] Three reachable goals complete using Nav2.
- [ ] Cancellation and a clean restart are demonstrated.
- [ ] Map, configuration, and destination poses are ready for the final.

## What to Submit

Completed `answers.md`, the goal CSV, full Nav2 configuration, map identity/path, and screenshots or a short demonstration. The separate Kalman, A*, Pure Pursuit, and synthetic safety-monitor implementations are optional; the mission client is completed for the final.

## Troubleshooting

- Misaligned scans: check the selected map, initial pose, TF, and clocks.
- No route: check occupied/unknown cells, footprint, and goal placement.
- No motion: check lifecycle states, simulation play state, and command type.
- Conflicting commands: stop teleoperation and extra mission clients.
- Use the [troubleshooting guide](../docs/TROUBLESHOOTING.md).

**Instructor validation:** the runbook must be tested on the course image before student use. No new end-to-end simulation test is claimed by these instructions.
