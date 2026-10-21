# Optional Background - Nav2 Navigation

This file is a reference, not a prerequisite reading assignment or an additional deliverable. Use the [lab manual](README.md) for required work. Lecture and homework develop the mathematics; the lab applies the concepts through configuration, implementation of a mission client, and measured simulation experiments.

## Find an explanation

- **Estimation and localization:** model/measurement uncertainty, drift, and reference frames.
- **Planning and tracking:** mission goals, graph search, feasible motion, and control.
- **Execution and failure handling:** state machines, Behavior Trees, freshness, and stopping authority.

## Estimation and Localization

### Why estimate state in simulation?

No single practical sensor directly and perfectly reports every state needed for autonomy. An estimator combines a process model with measurements over time. Gazebo makes controlled dropout, noise, and bias experiments repeatable and may provide a reference trajectory for evaluation. That reference is for scoring the estimate; feeding privileged simulator truth into the filter would invalidate the experiment unless explicitly assigned.

### Prediction, correction, and uncertainty

The prediction step advances the estimate using the process model and increases or transforms its uncertainty. The correction step compares a measurement with the predicted measurement and uses their modeled uncertainties to decide how much to adjust the state. The innovation is therefore both a correction signal and a diagnostic quantity.

The process-noise covariance (Q) represents uncertainty in the motion model and unmodeled disturbances. The measurement-noise covariance (R) represents uncertainty in measurements. Neither matrix is simply a smoothing knob: each encodes assumptions that should be supported by units, sensor characterization, and experimental behavior. The required Lab 4 Kalman experiment retains predict/update implementation as student work.

### Localization, frames, and time

Dead reckoning is locally continuous but accumulates drift. A global or map-relative measurement can bound drift but may be noisy, delayed, or intermittent. Comparisons are meaningful only when trajectories use compatible frames, timestamps, and units. Interpolate or align samples using a documented method rather than comparing array indices blindly.

## Planning and Tracking

### Why separate planning and tracking?

A planner chooses a geometric route through free space. A tracker converts that route into motion commands while the vehicle continues to move. A path can be valid on a grid yet impossible to track because it passes too close to obstacles, turns too sharply, uses the wrong coordinate transform, or ignores the vehicle footprint.

The provided Python experiments isolate the assigned algorithms and make search effort and tracking error easy to measure. Gazebo/RViz2 visualization, when enabled, adds the integration questions of frames, message types, robot footprint, and physical motion. Simulator success still depends on model assumptions and does not validate Goosebot's four-motor skid-steer command interface.

### Grid search

An occupancy grid becomes a graph whose free cells are states and whose allowed neighbor moves are edges. A* prioritizes nodes using accumulated path cost and a heuristic estimate of remaining cost. Connectivity, obstacle inflation, diagonal corner rules, and map resolution all affect whether the returned sequence is truly collision-free. The required A* search implementation remains student work.

### Path tracking

Pure Pursuit selects a target ahead on the reference path and commands curvature toward it. Short look-ahead distances can react quickly but amplify oscillation; long distances smooth motion but can cut corners. Speed, sampling interval, path spacing, steering limits, and the motion model interact, so change one experimental factor at a time and report failures as well as successful trials.

### From mission goals to a route

**Mission planning** selects *what* goals to achieve, in what order, and under what constraints. For example, a campus delivery robot might need to visit a pickup point, then a drop-off point, then return to its charging station. A mission planner can optimize task order using travel time, deadlines, energy budget, or precedence constraints. The **path planner** then solves the different problem of finding a traversable route to the current goal. A **task executive** monitors whether a navigation action succeeds, fails, or needs to be retried. These distinctions matter because the shortest path to the wrong destination does not satisfy the mission.

For a simple multi-stop mission, one can compare candidate orders using a travel-cost matrix \(c_{ij}\), where each entry estimates the cost of navigating from waypoint \(i\) to \(j\). If the robot must visit A before B, a shorter permutation that visits B first is **invalid** even if its geometric distance is lower. We focus this lab's graded work on planning and tracking, not on coding a full mission scheduler.

### Dijkstra and A*: selecting an efficient path

For each graph node \(n\), **Dijkstra's algorithm** prioritizes the known accumulated cost \(g(n)\). **A\*** prioritizes:

\[
f(n)=g(n)+h(n),
\]

where \(h(n)\) estimates the cheapest remaining cost to the goal. For a shortest-path guarantee under standard A* graph-search assumptions, use an admissible (and normally consistent) heuristic; with 4-connected, unit-cost moves, Manhattan distance is appropriate, while 8-connected grids require a heuristic compatible with diagonal move costs (such as octile distance for unit/\(\sqrt{2}\) costs). The heuristic should **not overestimate** the true remaining cost. Setting \(h=0\) reduces A* to uniform-cost/Dijkstra-style search.

Obstacle inflation prevents the reference point of a robot from passing too close to obstacles. Adjacent diagonal cells can create an illegal corner-cutting shortcut if the algorithm does not enforce a collision rule for intervening occupied cells. A* returns a discrete **geometric path**; it does not by itself ensure acceptable speed, acceleration, curvature, or steering actuation.

### Vehicle feasibility, trajectory planning, and tracking

A geometric **path** describes where to go, often as \((x(s),y(s))\) parameterized by distance \(s\). A **trajectory** additionally specifies *when* to be there: \((x(t),y(t),v(t))\) and possibly heading, curvature, and acceleration. Planning a path and then imposing a feasible time/speed profile are separate steps.

For an ideal bicycle-model car, curvature \(\kappa\), wheelbase \(L\), and front steering angle \(\delta\) satisfy:

\[
\kappa=\frac{\tan\delta}{L},\qquad R=\frac{1}{|\kappa|}.
\]

Thus a finite steering limit imposes a **minimum turning radius**. An arbitrary occupancy-grid path with sharp 90-degree corners may be collision-free for a point but impossible to follow with car-like steering. **Hybrid A\*** or curvature-constrained methods address this by considering heading and feasible motion primitives; their implementation is *not required* here. TurtleBot's differential-drive simulation and Goosebot's skid-steer platform have different turning constraints than a bicycle-model car—do not use the above steering equation as their motor model.

Pure Pursuit supplies a steering/curvature command toward a look-ahead target; it is a **tracking controller**, not a mission planner or a substitute for collision checking. If the planned route becomes blocked or the robot loses localization, the higher-level system must decide whether to replan, stop, or abort.

**Reading check:** A* finds a path through free cells, but the robot clips a corner. Name one map-related cause, one geometry/vehicle-model cause, and one tracking-related cause; propose a measurement for each.

<details>
<summary>Show answer</summary>

Several explanations are possible:

- **Map:** Coarse resolution or insufficient obstacle inflation leaves a path too close to the corner. Measure the mapped obstacle boundary against a reference and the minimum path-to-obstacle clearance in metres.
- **Geometry/vehicle model:** A point-robot collision check ignores the vehicle footprint, or the turn exceeds the vehicle's motion constraints. Measure the swept-footprint clearance and compare the required turn with the platform's measured turning capability.
- **Tracking:** A long look-ahead distance can cut the corner even when the reference path has clearance. Record the executed trajectory and cross-track error near the corner, then compare matched trials with different look-ahead distances.

</details>

## Execution and Failure Handling

### Why inject faults in Gazebo?

An integrated autonomy stack can keep running while using stale, inconsistent, or unsafe information. Gazebo provides a recoverable place to reproduce sensor loss, blocked paths, timing faults, and collision approaches without risking Goosebot or nearby people. It also permits matched baseline and faulted trials.

Simulation is not a complete safety argument. Contact, braking, communication loss, actuator saturation, wheel slip, and sensor failure may differ substantially on hardware. Thresholds established here are hypotheses to revalidate, not permission to repeat collision-approach experiments on Goosebot.

### Faults, symptoms, and dependencies

A **fault** is an underlying problem, such as dropped scans. A **symptom** is observable evidence, such as an old timestamp or a planner that no longer receives obstacle updates. One fault can cause several symptoms, and one symptom can have several causes. Diagnose from the simulator and communication layers upward before changing high-level logic.

Safety monitoring depends on data validity, freshness, coordinate-frame connectivity, estimator health, path status, motion state, and obstacle geometry. A safe response also needs command authority: detecting danger without inhibiting motion is only an alarm. State transitions should be deterministic, logged, and recoverable through an explicit reset policy.

### Reactive control, finite state machines, and Behavior Trees

**Reactive control** chooses an immediate response from current measurements (for example, slow down or stop when an obstacle violates a distance threshold). It is useful for fast safety responses but can be short-sighted without a global route or mission context.

A **finite state machine (FSM)** models discrete operational modes plus guarded transitions. A simple navigation executive might have `IDLE`, `NAVIGATING`, `WAITING`, `RECOVERY`, and `SAFE_STOP` modes:

```text
IDLE --new goal--> NAVIGATING --goal reached--> IDLE
                       |     ^
                path failure  | successful recovery
                       v     |
                    RECOVERY
                       |
                 retry limit exceeded
                       v
                    SAFE_STOP

Any active state --critical safety fault--> SAFE_STOP
SAFE_STOP --explicit reset + validated conditions--> IDLE
```

This is an *illustration*, not required implementation logic. Separate a **guard** (the condition permitting a transition) from an **action** (e.g., send a zero-velocity command), and specify whether a fault must be acknowledged before leaving `SAFE_STOP`. A state label alone cannot physically stop a robot.

A **Behavior Tree (BT)** organizes decisions into reusable conditions and actions. Typical control nodes include a **Sequence** (run children in order, failing when a child fails) and a **Fallback/Selector** (try alternatives until one succeeds). Leaf nodes return `SUCCESS`, `FAILURE`, or `RUNNING`. An illustrative navigation BT may try *follow path* after *compute path*, and invoke a bounded recovery when navigation fails. ROS 2 Nav2 uses BTs for navigation orchestration. Students need to recognize this role, not build a BT engine or a hierarchical FSM in this lab.

FSMs are easy to draw for a few clear modes; BTs often make retry/recovery flows easier to compose. **Neither replaces a safety monitor**. A safety override must have a reliable route to inhibit motion independently of normal mission progress. Test stale-data detection, bounded retry counts, logging, and explicit reset behavior in simulation before considering real hardware.

**Reading check:** A LiDAR topic is still publishing, but each message is two seconds old. Why is “topic exists” insufficient, what state transition would be reasonable, and what should prevent a stale navigation command from moving the vehicle?

<details>
<summary>Show answer</summary>

Topic presence shows that an interface is advertised; even continued delivery does not prove that its measurements are current. Compare measurement timestamps with the current time using a consistent clock. Two-second-old scans describe past obstacle positions and can invalidate navigation decisions. A reasonable response is to leave NAVIGATING for SAFE_STOP when freshness violates the allowed limit. A safety override on the final command path, together with command-freshness checks or a base-controller watchdog, must inhibit motion so that an old navigation command cannot keep the vehicle moving. Resume only after valid data and the specified reset conditions are restored.

</details>

## Practical Nav2 responsibilities

`map_server` loads the saved occupancy map. AMCL estimates the map-relative pose and publishes the global correction. The planner computes a route using a global costmap; the controller follows the route using current pose and local obstacle information. The Behavior Tree navigator coordinates navigation actions and recoveries. Your mission client decides goal order and handles outcomes.

A goal accepted by an action server has not yet succeeded. Treat acceptance, ongoing feedback, and terminal result as separate events. A client must preserve failure results, enforce its timeout policy, and avoid sending another goal after an unsuccessful one. Cancellation must be followed by observation of the terminal result and actual motion.

Keep a single owner for each TF relationship. In mapping mode SLAM owns `map -> odom`; in saved-map navigation AMCL owns it. The robot model supplies mounting geometry and odometry supplies local motion. Do not start AMCL and SLAM simultaneously to fill a missing transform.

An inflation radius defines the extent of an obstacle cost field. The footprint and collision checks still matter; increasing inflation may discourage close routes or make narrow passages unattractive, while decreasing it does not make the robot smaller. Compare loaded parameters, outcomes, and trajectories under matched conditions.

## Required implementations and optional reading

The [algorithm experiments](ALGORITHM_EXPERIMENTS.md) require your own A*, Pure Pursuit, and safety-monitor implementations. The Lab 4 [Kalman experiment](../lab04_slam/ALGORITHM_EXPERIMENT.md) is also required. Completed algorithms are not supplied here. Nav2 configuration and successful live missions do not replace these submissions.

The [legacy archive](../optional_legacy/previous_lab_sequence/README.md) preserves the original full lab manuals as additional references. Use the new manuals and experiment specifications for current required inputs, outputs, and assessments.
