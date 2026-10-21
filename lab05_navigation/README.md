# Lab 5 - Navigation with Nav2

## Mission

**Make TurtleBot complete a repeatable three-goal mission on your own SLAM map.** Implement A*, Pure Pursuit, and safety-monitor logic, then write a mission client, compare two Nav2 configurations, and demonstrate a STOP-triggered cancellation without a collision.

## Learning Objectives

- load a saved map and establish localization with AMCL;
- implement and evaluate A* search, Pure Pursuit tracking, and a safety policy;
- configure and test Nav2 planning and control;
- write a mission client that handles action results and cancellation;
- measure repeatability and diagnose a controlled failure.

## Prerequisites

Complete [Lab 4](../lab04_slam/README.md), including a selected map YAML/image pair. Know how to teleoperate, stop, and restart the simulation. Update course files using [the repository update guide](../docs/UPDATING_COURSE_REPOSITORY.md).

## Background

AMCL estimates the robot pose on a saved map. Nav2 uses this pose, the map, and live obstacle data to plan and execute motion. Your mission client selects goals and reacts to results; Nav2 supplies the planner and controller.

Keep the required workflow below alongside your terminal. TF explanations, uncertainty, costmaps, planning/control theory, and algorithm explanations are in [OPTIONAL_BACKGROUND.md](OPTIONAL_BACKGROUND.md).

## Provided Files

- `src/astar.py`, `src/pure_pursuit.py`, and `src/safety_monitor.py`: required algorithm starters.
- [Required algorithm experiments](ALGORITHM_EXPERIMENTS.md): inputs, verification, metrics, and safety integration.
- `src/mission_client.py`: student mission-client scaffold; TODOs must be completed.
- `src/record_odometry.py`: provided recording utility; no algorithm implementation required.
- `config/goals.csv`: header for your three map-frame goals.
- `config/`: your two full Nav2 parameter files.
- `answers.md` and `results/`: experiment plan, action logs, trajectories, and evidence.
- [Simulation runbook](../docs/SIMULATION_WORKFLOW.md#navigation-mode): saved-map startup and stop procedure.

## Step-by-Step Procedure

### 0. Implement planning, tracking, and safety

Complete the [required algorithm experiments](ALGORITHM_EXPERIMENTS.md): verify your A* paths, compare two Pure Pursuit look-ahead distances using your Lab 3 bicycle model, and test your safety-monitor policy. Write the required experiment runner. In the live steps below, connect your monitor's STOP decision to mission cancellation; Nav2 supplies the live planner/controller, independently of your Python algorithm experiments.

### 1. Load your map and localize

Stop the Lab 4 simulation, mapper, and teleoperation nodes. Start [Navigation mode](../docs/SIMULATION_WORKFLOW.md#navigation-mode), passing the absolute path to your selected map YAML. Mapping is disabled in this mode: AMCL owns `map -> odom`.

Activate localization once, then use RViz2 **2D Pose Estimate** at the known starting pose and heading. Confirm that the scan aligns with mapped walls and that `map` connects to `base_link`. Activate navigation only after these checks. Send one nearby goal using **Nav2 Goal** to verify the baseline.

### 2. Prepare two Nav2 configurations

From this lab directory in WSL/Ubuntu:

```bash
source /opt/ros/jazzy/setup.bash
cp "$(ros2 pkg prefix --share nav2_bringup)/params/nav2_params.yaml" config/nav2_a.yaml
cp config/nav2_a.yaml config/nav2_b.yaml
```

These commands copy the complete installed parameter file so plugin definitions and other required settings remain available. Inspect the actual planner/controller plugins and robot footprint or radius. Do not replace the footprint or weaken safety settings to force a result.

Change only `inflation_radius` in the existing global and local costmap inflation-layer sections of `nav2_b.yaml`, treating the common radius as one experimental factor. Choose two conservative values with the instructor based on this robot and world. Record the full parameter paths, units (metres), and values. Predict the effect on route choice, clearance, success, and duration. Inflation is a cost field, not a guaranteed minimum clearance.

Restart Navigation mode with `params_file` pointing to configuration A. Repeat the localization sequence. Confirm the loaded parameters using `ros2 param get` on the observed costmap node names before collecting data. Use complete restarts for both configurations rather than mixing live edits with saved files.

### 3. Define and implement the mission

Choose three reachable poses in open mapped space. Record their `x_m`, `y_m`, and `yaw_rad` in `config/goals.csv`; use map coordinates and radians. Define a known initial pose, goal order, per-goal timeout, and success rule before running. Keep the goals fixed throughout the parameter experiment.

Complete the TODOs in `src/mission_client.py` using Nav2 Simple Commander. Your implementation must:

1. wait for active, localized Nav2;
2. send the three poses in order, with a current timestamp for each;
3. poll feedback without a busy loop and log each accepted, rejected, succeeded, failed, canceled, or timed-out goal;
4. advance only after success; terminate the mission on rejection, failure, timeout, or user interruption;
5. cancel an active goal on timeout/interruption and confirm its terminal result before exiting;
6. save per-goal results and elapsed simulation time to CSV, including failed attempts;
7. evaluate your safety monitor against the documented injected-health sequence; a STOP decision must cancel the active goal, inhibit further goals, and require an explicit restart.

The scaffold intentionally raises `NotImplementedError` until you implement the mission. Use installed Nav2 components for live planning/control. Your separate A* and Pure Pursuit implementations remain required in the algorithm experiments; library components do not satisfy those submissions. See the [official Simple Commander API](https://docs.nav2.org/commander_api/index.html) and the optional background for API roles.

Run your completed client from this lab directory:

```bash
python3 src/mission_client.py --goals config/goals.csv --output results/a1_goals.csv --timeout 120 --ros-args -p use_sim_time:=true
```

`--timeout` is the per-goal simulation-time limit in seconds. Choose and document a suitable limit before testing; 120 is an example, not a guaranteed mission duration. Do not run teleoperation concurrently with Nav2.

### 4. Record and compare repeatable trials

In a separate sourced terminal, start the recorder before the mission:

```bash
python3 src/record_odometry.py --output results/a1_odom.csv --ros-args -p use_sim_time:=true
```

The utility records `/odom` message timestamps and planar position. Stop it with `Ctrl+C` when the mission finishes. It reports odometry-frame distance, not independent ground-truth distance. Run labels must match your goal and trajectory logs.

Run three trials for A and three for B. Before every trial, restart at the same simulator pose, load the same map, initialize localization the same way, and use the same goals. Do not change the world between these six trials. Preserve failed runs. Submit both parameter files and verify the loaded radius for each configuration.

### 5. Test a controlled failure and recovery

After the comparison, choose one configuration and perform a separate simulation-only STOP/cancellation test. Start a reachable goal and inject the planned healthy-to-stale-sensor health sequence from the algorithm experiment. Your implemented monitor must select STOP and your client must request cancellation while the robot is moving. Also verify user-interruption cancellation handling separately. Record cancellation request time, terminal action status, and when odometry velocity settles near zero. Define the velocity threshold and observation window before the test.

Confirm that the robot actually stops in Gazebo. Action cancellation is a software request, not a hardware emergency stop. If it does not stop, pause Gazebo immediately and end the trial using the runbook. Diagnose before resuming. Restart cleanly and demonstrate that the original mission can run again.

An instructor-approved blocked/unreachable-goal experiment may supplement this trial; it does not replace the required monitor-to-cancellation demonstration. Do not remove sensing, disable collision checking, or run collision approaches for this lab.

## Experiment / Quantitative Analysis

For every normal trial report mission success, successful goals out of three, elapsed simulation time, and odometry-derived path length in metres. For consecutive recorded positions, sum their planar Euclidean separations over the mission interval. Exclude setup motion and reject logs spanning a simulation-time reset. Explain that accumulated odometry drift affects this measure.

Compare mean duration and path length across successful trials, and report success count out of three separately for each configuration. Do not hide failures inside averages. If one configuration has no successful trials, report that fact rather than inventing a mean.

For the separate failure trial, report request-to-terminal-result time, request-to-observed-stop time, and the evidence used to distinguish them. Compare observed behavior with your prediction, then recommend one configuration with a stated limitation. Lower duration alone does not establish safer navigation.

## Engineering Questions

1. Why does loading a map not immediately tell Nav2 where the robot is?

   <details>
   <summary>Show answer</summary>

   The map describes the environment. AMCL must establish the robot pose in that map using an initial pose hypothesis, sensor observations, and motion information. Navigation also needs a connected, timely TF chain.

   </details>

2. Why can changing inflation radius alter a route without changing the map image?

   <details>
   <summary>Show answer</summary>

   The costmap assigns costs around obstacles based on the robot and configured inflation. Changing those costs can change the planner's preferred route while the underlying occupancy map remains the same. Inflation alone does not guarantee a specific physical clearance.

   </details>

3. Why must you check actual motion after an action is canceled?

   <details>
   <summary>Show answer</summary>

   Action status reports software progress. Command delivery, arbitration, drive behavior, and residual motion determine whether the vehicle has stopped. Compare the terminal result with odometry and Gazebo motion; hardware needs an independently validated stopping path.

   </details>

4. Which configuration worked better, and what failure did your test expose?

   <details>
   <summary>Show answer guidance</summary>

   Cite your success counts, successful-run metrics, loaded parameter values, and cancellation evidence. Discuss uncertainty and a failed or limited case. Your measured results determine the answer.

   </details>

## Success Criteria

- [ ] Your Lab 4 map is loaded and localization is verified.
- [ ] Your A* implementation passes path-validity and no-path checks.
- [ ] Your Pure Pursuit implementation is compared at two look-ahead distances using your bicycle model.
- [ ] Your safety monitor passes the documented policy cases and drives STOP-to-cancellation handling.
- [ ] Your own mission client handles three goals, failures, timeout, and interruption.
- [ ] Two saved configurations are verified and tested in three matched trials each.
- [ ] Logs support the reported success, time, and distance results.
- [ ] A separate controlled failure/cancellation test ends without collision and includes a recovery demonstration.

## What to Submit

- completed A*, Pure Pursuit, safety-monitor code, experiment runner, and required checks/plots/metrics;
- completed mission client, goal CSV, and both Nav2 parameter files;
- per-goal CSVs and odometry logs for six normal trials and the failure trial;
- results table, comparison plot, and completed `answers.md`;
- a short mission and cancellation/recovery video;
- the Lab 4 map path and map identity used for every run.

## Troubleshooting

- Robot or scan misaligned with the map: verify the selected YAML, initial pose, TF, and clocks before tuning.
- No route: check unknown/occupied cells, footprint, goal placement, and costmap settings.
- Client waits indefinitely: check AMCL and Nav2 lifecycle states and action-server availability.
- Timeout during a paused simulation: simulation time stops while paused; use the manual stop procedure if needed.
- Conflicting motion: stop teleoperation and extra mission clients before restarting the trial.

**INSTRUCTOR VALIDATION REQUIRED:** test all six trials, the student-client API, recorder QoS, loaded inflation parameters, and cancellation/stop behavior on the course image. See the [validation checklist](../docs/INSTRUCTOR_VALIDATION.md).

Continue to the [Goosebot final project](../final_project_goosebot/README.md); physical interfaces and stopping behavior require separate instructor validation.
