# Required Experiments - Planning, Tracking, and Safety

These are required parts of [Lab 5](README.md), alongside the live Nav2 mission. Implement the assigned algorithms yourself; use lecture equations and [OPTIONAL_BACKGROUND.md](OPTIONAL_BACKGROUND.md) as references. Library planners/controllers do not satisfy these implementation requirements.

Write `src/run_algorithms.py` to run the experiments below and save paths, trajectories, decisions, tables, and plots. Submit the runner with your completed starters. State each coordinate convention and use SI units outside the discrete grid.

## 1. Implement A* and verify its paths

Complete `src/astar.py`. Use `(row, column)` cells, 4-connected unit-cost moves, and a compatible admissible heuristic. Return an ordered start-to-goal path, or a documented failure result. Blocked and out-of-bounds endpoints must not produce a valid path.

Construct a 20-by-20 grid initialized to free (zero). Mark its outer boundary occupied (one), then mark column 10 occupied in rows 1 through 18, leaving rows 5 and 6 free as a passage. Plan from `(2, 2)` to `(17, 17)`. For the second case, close those two passage cells. Also test an empty grid with a known shortest distance, `start == goal` on a free cell, and invalid endpoints.

Before running, predict feasibility for each case. Verify every returned cell is free, consecutive cells share an edge, endpoints match, and path cost agrees with the move count. Report length in cells and metres using a declared 0.25 m/cell scale. The closed-passage case must report no path. Save a grid plot with the returned path; do not draw a straight line over a failed result.

This controlled grid tests the algorithm independently of map-image conversion. In the live mission, Nav2 uses your saved SLAM map and its own installed planner. Compare the roles of the two planners without claiming that your function is a Nav2 plugin.

## 2. Implement Pure Pursuit and compare look-ahead values

Complete `src/pure_pursuit.py`. Use your completed Lab 3 bicycle model for propagation; import it from `lab03_vehicle_modeling/src` in your runner. Keep the motion-model TODOs as your own work and submit any changes to that model. Do not use a library tracking controller.

Use a circular reference of radius 5 m centered at `(0, 0)`, sampled at at least 360 uniformly spaced angles. Follow it counterclockwise from initial pose `(5.25 m, 0 m, pi/2 rad)`. Use forward speed 0.5 m/s, time step 0.05 s, wheelbase 0.30 m, wheel radius 0.05 m, steering limit +/-0.50 rad, and a 70 s duration. Convert forward speed to the wheel input expected by your Lab 3 model, documenting the units.

In the runner, select a forward look-ahead target on the ordered reference and call your steering function each step. Document target selection, including wraparound; do not select a point behind the vehicle. Clamp steering to the stated limit before propagation. Keep these details fixed while comparing look-ahead distances 0.5 m and 1.5 m. Record predictions before running.

Plot both executed trajectories against the reference. Report cross-track RMSE and maximum error in metres, measured against the circle, plus the fraction of steps at the steering limit. Explain the response from the initially offset pose and any oscillation. A completed simulation is not evidence that either setting is universally best.

This is a car-like Python simulation for studying steering. TurtleBot is differential drive and Goosebot is skid steer; do not publish bicycle steering angles as their motor commands. Nav2's installed controller performs the live tracking task.

## 3. Implement and exercise the safety monitor

Complete `src/safety_monitor.py`. Define a documented policy for NORMAL, DEGRADED, and STOP using measurement age, localization validity, path availability, obstacle distance, and forward speed. Use a speed-dependent collision-urgency rule and explicit treatment of nonfinite or invalid inputs. Choose and record thresholds before testing; distinguish units and justify each choice.

Create a table of expected states for healthy inputs, a missing path, stale sensing, invalid localization, invalid numeric data, and close obstacles at two positive forward speeds. Include cases just below and above each chosen boundary. Run your function against that table and report disagreements and fixes. These are required tests of your policy; no completed safety rule set is provided.

In your mission client, use STOP decisions from a documented simulated-health input sequence to cancel an active goal and prevent advancing to the next goal. At minimum, demonstrate a healthy-to-stale-sensor input transition during the separate failure trial. Label the injected health values as synthetic; they do not prove live sensor monitoring. Confirm terminal action status and actual stopping using the README's observation procedure. Clearing the injected fault must not automatically resume the interrupted mission: require an explicit restart after conditions are verified.

This tests decision-to-action integration in simulation. It is not a validated hardware safety system and does not replace the manual Gazebo pause/shutdown fallback.

## Submit with the Nav2 results

Submit completed A*, Pure Pursuit, safety-monitor code, the experiment runner, path-validity checks, tracking plots/metrics, policy/threshold table, expected-versus-observed decisions, and evidence that STOP reaches mission cancellation. The three implementations, mission client, and live Nav2 comparison are all required for Lab 5.
