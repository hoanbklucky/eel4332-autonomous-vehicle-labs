# Final Project — Autonomous Campus Delivery Robot

## Mission

Use TurtleBot in ROS 2 Jazzy and Gazebo Harmonic to visit three delivery locations and return home using your own SLAM map. At each delivery location, stop and wait for 3 seconds of simulation time. No physical robot, object detection, or manipulation is required.

Your Goosebot autonomous lane-following work is the course's hardware achievement. This final assesses map-based autonomy in simulation. Reuse the Lab 4–5 skills and mission code, but create a new map of the supplied campus arena.

## Learning Objectives

- integrate mapping, saved-map localization, planning, and mission execution;
- write a small waypoint client with result handling and cancellation;
- evaluate repeatability and response to a changed environment;
- explain which assumptions would need revalidation on Goosebot.

## Prerequisites

Complete [Lab 4](../lab04_slam/README.md) and [Lab 5](../lab05_navigation/README.md). Use the provided campus-inspired world with TurtleBot3 Waffle. Students do not need to design a new world.

Use **Waffle in the supplied campus arena**, following the [campus launch/mapping instructions](campus/README.md). Source ROS Jazzy and `~/turtlebot3_ws/install/setup.bash` and export `TURTLEBOT3_MODEL=waffle` in every terminal. Stop mapping/teleoperation before navigation. The instructor must validate the new world on the course image before release; Lab 5's standard TurtleBot3 World remains a fallback only if the instructor chooses it.

## Background

The official ROBOTIS Cartographer tutorial creates your map. During the delivery mission, stop SLAM and use AMCL on the saved map. Nav2 supplies the live planner, controller, and navigation recovery. Your Python client sequences destinations and handles outcomes.

The final does not require implementing SLAM, A*, Pure Pursuit, Kalman filtering, a custom Nav2 plugin, autonomous exploration, or a synthetic safety monitor.

## Campus Environment

The supplied images inspired a **schematic 24 × 30 m arena**, not an exact geographic reconstruction. Buildings, a central lake chain, crossings, and yellow delivery pads provide the mission setting. Lake regions are solid obstacles in simulation.

<details>
<summary>Preview — campus layout, delivery stops, and obstacle variant</summary>

![Campus-inspired arena](campus/campus_plan.svg)

Blue blocks represent non-traversable lakes. The dashed orange barrier appears only in the obstacle variant. Dimensions and building placements are approximate teaching geometry.

</details>

**How to create the map:** launch `campus/campus.launch.py`, run Cartographer and teleoperation, explore both sides/crossings, then save `results/campus_map.yaml` and its image. The [campus README](campus/README.md) contains the exact commands, spawn pose, delivery locations, and obstacle launch.

Do not turn the supplied campus photograph directly into a navigation map: a map needs metric coordinates and obstacles matching the simulator. The supplied `campus/reference.yaml` is a geometric instructor reference; students create their own SLAM map. World/reference-map coordinates must not be copied blindly into a different SLAM map.

## Provided Files

- [Mission scaffold](../lab05_navigation/src/mission_client.py): complete its TODOs.
- [Odometry recorder](../lab05_navigation/src/record_odometry.py): provided utility.
- [Goal CSV](../lab05_navigation/config/goals.csv): three delivery poses.
- [Results template](results_template.md).
- [Campus world, preview, reference map, and launch instructions](campus/README.md).
- Your newly created campus SLAM map YAML/image and Lab 5 navigation setup/configuration record. Use the official TurtleBot3 model-specific configuration; preserve a copy of any modified full parameter file.

Keep final code and configuration in `final_project_simulation/src/` and `config/`, and evidence in `results/`. Create those directories in your submission. Preserve the supplied algorithms' TODOs unless you elect to complete an optional exercise.

## Step-by-Step Procedure

### 0. Map the campus arena

Follow the [campus README](campus/README.md) to launch the baseline world, map the required delivery routes with Cartographer, and save `results/campus_map`. Restart cleanly and verify AMCL alignment with this map. Select your delivery/home coordinates in this map frame. The old TurtleBot3 World map does not describe this arena.

### 1. Freeze the mission

Choose three reachable delivery poses in open mapped space and a home pose. Record all poses in the saved map frame, using metres and radians. Home is the documented starting location. Define goal tolerances, a per-goal timeout (300 simulation seconds is an example for this larger arena), and an overall mission limit before testing.

Use the same map, world, robot, starting pose, goals, order, and configuration throughout evaluation. Record package versions and launch commands. Retain the original map even when an obstacle is added.

### 2. Complete the mission client

Copy the scaffold into your final `src/` directory. Use Nav2 Simple Commander; do not replace Nav2 planning/control with the optional Python algorithms.

Required behavior:

1. Wait for initialized localization and active Nav2.
2. Visit the three delivery poses in the CSV order, then return home.
3. Stamp each goal with the current ROS simulation time.
4. Wait 3 simulation seconds after each successful delivery before continuing.
5. Log acceptance, terminal outcome, start/end simulation timestamps, and elapsed time for every attempted goal, including home.
6. Advance only after success. On rejection, failure, timeout, or user interruption, end the mission; cancel an active task and confirm its terminal result.
7. Keep partial logs and require an explicit restart after interruption/failure. Avoid busy polling.

Add a required `--home X Y YAW` argument to your copied scaffold; its initial CSV parser intentionally reads exactly three delivery goals. Document the command, for example:

```bash
python3 src/mission_client.py --goals config/goals.csv \
  --home X_HOME Y_HOME YAW_HOME --output results/baseline1_goals.csv \
  --timeout 300 --ros-args -p use_sim_time:=true
```

Replace the home placeholders with numbers from your map. The command works only after you implement the client and its added home argument. Explain your own sequencing/result-handling code during the demonstration.

### 3. Evaluate three baseline runs

Start the provided recorder in a separate sourced terminal before each mission:

```bash
python3 ../lab05_navigation/src/record_odometry.py \
  --output results/baseline1_odom.csv --ros-args -p use_sim_time:=true
```

Run from `final_project_simulation/`. Stop the recorder after the mission. Use fresh labels for every run.

Complete three trials, each from a clean simulator launch and reinitialized localization at the same pose. Keep failures. Do not record across a simulation clock reset. Delivery waits count toward mission duration; setup/localization time does not.

### 4. Test an additional obstacle

Use one instructor-approved static obstacle placement, absent from the saved map, that obstructs a baseline route while leaving a feasible alternative. Start a fresh trial with the obstacle already in place before the mission; keep its pose fixed. Do not spawn it onto or immediately in front of a moving robot.

The provided `campus/campus_blocked.sdf` is the second world variant; its [README](campus/README.md) gives the exact launch, barrier dimensions, and world-frame pose. Check that it has collision geometry and is detected by the simulated LiDAR. Students must not improvise moving obstacles or modify the map to hide the challenge.

Predict the response, then run the same mission once. Capture RViz2 costmap/path evidence and Gazebo motion. Explain whether you observed local avoidance, a changed global path, recovery, stopping, or failure. A detour alone does not prove global replanning. If the mission fails, retain the logs, diagnose it, and document any additional attempt separately.

### 5. Demonstrate cancellation and discuss transfer

Reuse Lab 5 cancellation/restart evidence if it already shows both action outcome and actual stopping. Otherwise perform one separate cancellation trial. Never treat cancellation status alone as proof of zero motion. If cancellation fails to stop motion, pause Gazebo, end the launch processes, and restart cleanly.

Include a short discussion of the sensing, wheel odometry, TF, footprint, motor interface, skid-steer slip, and stopping checks needed to transfer this system to Goosebot. Physical SLAM/Nav2 deployment is not required.

## Experiment / Quantitative Analysis

For each baseline and obstacle trial report:

- delivery goals succeeded / 3 and whether home was reached;
- mission success: all three deliveries, all waits, and return home within your fixed limits, without observed collision;
- elapsed simulation time, including delivery waits;
- odometry-derived traveled distance over the mission interval;
- failure/timeout reason and any observed collision or recovery.

Compute distance by summing consecutive planar odometry-position differences. This estimates traveled distance; it is not independent ground truth. Report success count out of three and mean duration/distance for successful baseline trials only, with sample count. If none succeed, report no successful-run mean. Describe collision observation as visual evidence unless you provide a validated contact measurement.

Compare the obstacle trial with the baseline and explain limitations. Parameter tuning or a second configuration is optional; label extra experiments and preserve the required fixed baseline.

## Engineering Questions

1. How do SLAM and AMCL serve different roles in your workflow?
2. Which planner/controller plugins run, and how does your client interact with them?
3. What evidence supports your explanation of the obstacle response?
4. What failed or remains unreliable, and what would you improve?
5. What would need to change or be validated for Goosebot?

## Success Criteria

- [ ] Your saved map loads and supports AMCL localization.
- [ ] Your client attempts three deliveries and return home with waits and result handling.
- [ ] Three baseline runs and one obstacle trial have preserved logs.
- [ ] Cancellation and actual stopping are demonstrated.
- [ ] Results are reproducible and failures are explained.

A failed trial is evidence to analyze, not a reason to remove it. Grades consider technical correctness, diagnosis, and understanding as well as mission completion.

## What to Submit

- Source code, map YAML/image, full Nav2 configuration, destination CSV, home pose, versions, and run commands.
- A 3–5 minute video showing mapping/localization, delivery/return behavior, and obstacle response; include cancellation evidence.
- A concise report or project README (about 3–5 pages equivalent) with system diagram, results table, one trajectory plot, answers, and limitations.
- Individual contribution statements. Each student must explain the system and their contribution.

| Category | Weight |
|---|---:|
| Mapping and localization | 20% |
| Delivery mission and client behavior | 30% |
| Obstacle response and cancellation | 20% |
| Quantitative evaluation and explanation | 20% |
| Reproducibility and individual understanding | 10% |

## Suggested Schedule

- First week: reuse/verify map and localization; implement the client; complete a baseline mission.
- Second week: collect trials, test the obstacle, analyze results, and prepare the demonstration.

For an instructor-designated one-week version, the instructor may provide a working mission client; students customize destinations/configuration and perform the evaluation. No completed client is supplied in this repository update.

## Troubleshooting

Use the campus launch/map commands and Lab 5's scan/map alignment checks. Confirm map identity, initial pose, time, TF, and lifecycle states before tuning. Keep teleoperation stopped during autonomous missions.

**INSTRUCTOR VALIDATION REQUIRED:** test the full mapping-to-delivery sequence, exact obstacle world/placement, and cancellation on the course image before release. This document does not certify an end-to-end run.
