# Lab 8 — Path Planning and Path Tracking

## Before You Begin — Update Course Files

In a **WSL/Ubuntu Terminal**, go to your local course repository and check for changes:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

**Command breakdown:** `cd` changes to the repository directory; `~` means your Ubuntu home directory. `git status --short` gives a compact list of local changes and prints nothing when the working tree is clean.

If the command prints nothing, run `git pull --rebase`. If it lists files, protect your work first by following [Updating the Course Repository](../docs/UPDATING_COURSE_REPOSITORY.md). Use your actual repository path if you cloned it elsewhere.

## Mission

**Compute a collision-free path and make a vehicle follow it accurately enough to reach the goal.**

## Learning Objectives

- implement grid-based A* search;
- explain the role of \(g(n)\), \(h(n)\), and \(f(n)\);
- evaluate path length and planning effort;
- implement basic Pure Pursuit path tracking;
- analyze the tradeoff between look-ahead distance, speed, and tracking error.

## Prerequisites

- Complete Labs 03 and 05.
- Review graphs, priority queues, admissible heuristics, and the assigned Pure Pursuit geometry.
- Be able to distinguish grid-cell coordinates, world coordinates, and vehicle pose.

## Background

### Why separate planning and tracking?

A planner chooses a geometric route through free space. A tracker converts that route into motion commands while the vehicle continues to move. A path can be valid on a grid yet impossible to track because it passes too close to obstacles, turns too sharply, uses the wrong coordinate transform, or ignores the vehicle footprint.

The provided Python experiments isolate the assigned algorithms and make search effort and tracking error easy to measure. Gazebo/RViz2 visualization, when enabled, adds the integration questions of frames, message types, robot footprint, and physical motion. Simulator success still depends on model assumptions and does not validate Goosebot's four-motor skid-steer command interface.

### Grid search

An occupancy grid becomes a graph whose free cells are states and whose allowed neighbor moves are edges. A* prioritizes nodes using accumulated path cost and a heuristic estimate of remaining cost. Connectivity, obstacle inflation, diagonal corner rules, and map resolution all affect whether the returned sequence is truly collision-free. The assigned search implementation remains student work.

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

## Provided Files

```text
lab08_planning_tracking/
├── README.md
├── src/
│   ├── astar.py
│   └── pure_pursuit.py
├── results/
└── answers.md
```

## Learning Path and Visible Checkpoints

| Stage | What you are learning | Visible checkpoint |
|---|---|---|
| Establish planning cases | What success, failure, and invalid input mean | Reachable, unreachable, and invalid cases return distinct, verified outcomes. |
| Implement and measure search | How heuristic guidance changes search effort | A* and Dijkstra use the same problem while reporting path validity and expanded nodes. |
| Add vehicle behavior | How a path becomes steering rather than instant motion | The simulated vehicle advances toward successive look-ahead targets. |
| Visualize the chain | How map, path, target, and motion relate | One labeled view shows obstacles, expansions, path, target, and tracked trajectory. |
| Test limits | How speed and look-ahead create success or failure | Four matched configurations expose corner cutting, oscillation, or tracking error. |

Do not count a nonempty path or a final “success” message as sufficient evidence. Verify collision-free adjacency for planning and show the vehicle behavior and failure criteria for tracking.

**Optional challenge after the required configurations:** Find one safe parameter change that improves a chosen tracking metric without violating the fixed collision or off-track criterion. Report the tradeoff only if the instructor assigns the extension.

## Part 1 — A* Planning

**Why this part matters:** Implementing A* connects the search concepts from class to the practical task of finding a collision-free route on a grid.

Complete:

```text
src/astar.py
```

Inputs:

- occupancy grid;
- start cell;
- goal cell.

Output:

- ordered path or a clear failure result.

### Planning data contract

| Item | Representation | Required interpretation |
|---|---|---|
| occupancy grid | 2-D array; `0` is free and nonzero is occupied | row/column convention must be documented |
| start and goal | grid-cell coordinates | both must be inside the grid and free |
| path | ordered list of grid cells | begins at start, ends at goal, and never crosses an occupied cell |
| expanded nodes | count or recorded collection | used to compare planning effort |
| computation time | seconds | measured with the same method for every planner run |

Do not use a library A* implementation for the assigned algorithm.

Before reporting a path as successful, verify programmatically that every path cell is free and every consecutive pair is a permitted neighbor under your chosen connectivity rule. Test at least one reachable case, one blocked or unreachable case, and one invalid-input case.

## Part 2 — Planner Experiments

**Why this part matters:** Changing maps and planner settings exposes tradeoffs among path length, safety clearance, and computational effort.

Compare at least:

- A* with an admissible heuristic;
- Dijkstra behavior by setting \(h(n)=0\).

Report:

- path length;
- number of expanded nodes;
- computation time.

Use the same grid, start, goal, connectivity, and timing method for A* and Dijkstra. State the heuristic and whether diagonal moves are allowed.

## Part 3 — Path Tracking

**Why this part matters:** A geometric path alone does not move a vehicle; tracking converts that path into steering commands while correcting error.

Complete:

```text
src/pure_pursuit.py
```

The function should compute a steering command from:

- current vehicle pose;
- a target/look-ahead point;
- wheelbase;
- look-ahead distance.

This Pure Pursuit formulation produces an Ackermann/bicycle steering angle. It is a car-like control exercise and must not be sent directly to Goosebot, whose wheel axes are fixed and parallel. Goosebot deployment requires a tested controller or conversion that produces the appropriate left/right skid-steer motion commands and respects the four-motor interface.

### Tracking data contract

| Item | Units/representation | Required interpretation |
|---|---|---|
| vehicle pose | meters, meters, radians | pose used by the controller at the current step |
| reference path | ordered (x,y) points in meters | desired geometric route |
| look-ahead target | one (x,y) point in meters | current controller target |
| steering command | radians | bicycle-model front-wheel steering angle |
| tracked trajectory | ordered (x,y) positions | actual simulated motion used for error metrics |

## Part 4 — Visualize Planning and Tracking

**Why this part matters:** Visualization makes coordinate, waypoint, collision, and tracking errors much easier to diagnose than numerical output alone.

Create a figure that overlays:

- the occupancy grid;
- start and goal;
- expanded nodes;
- the final A* path;
- the tracked vehicle trajectory;
- a sample look-ahead target.

Use a legend, equal axis scaling, and labeled units. The visualization must make collisions, corner cutting, oscillation, and failure to reach the goal visible rather than showing only a final success message.

For the ROS/RViz2 version of the course exercise, visualize the same information with ROS messages:

| Visualization | Standard ROS type | Content |
|---|---|---|
| planned path | `nav_msgs/msg/Path` | ordered path poses in one fixed frame |
| look-ahead target | `visualization_msgs/msg/Marker` | current target point or sphere marker |
| start and goal | `visualization_msgs/msg/MarkerArray` | distinct, labeled markers |
| vehicle pose | TF or `geometry_msgs/msg/PoseStamped` | current simulated pose |

All messages displayed together must use consistent frame IDs and timestamps. Capture one RViz2 screenshot showing the path, current pose, and look-ahead target.

**INSTRUCTOR VALIDATION REQUIRED:** provide or validate the thin ROS visualization wrapper and final topic/frame names before making the RViz2 portion required on the Fall 2026 image. Until then, the labeled Python figure is required and RViz2 visualization is an extension.

## Part 5 — Lightweight Vehicle Experiment

**Why this part matters:** Testing vehicle-model assumptions shows when a controller that works for one platform may not transfer directly to another.

Track the same path for at least:

- two look-ahead distances;
- two speeds.

Use the bicycle-model portion of the Lab 3 simulator plus the tracking controller. The differential-drive odometry portion of Lab 3 uses different physical inputs and is not a direct Pure Pursuit steering-angle model. If the instructor provides a pinned F1TENTH environment, it may be used as an optional second experiment.

## Part 6 — Quantitative Evaluation

**Why this part matters:** Common metrics let you compare planning and tracking performance objectively instead of judging only by appearance.

Report:

- mean cross-track error;
- maximum cross-track error;
- completion time;
- failed/off-track cases.

Before running the experiment, define a numerical goal tolerance and an off-track or collision criterion. Apply the same criteria to all four tracking configurations.

## Optional Extensions — Reactive Driving

These extensions are not required submissions unless assigned by the instructor. They are useful examples of a direct LiDAR-to-control autonomy loop:

- **wall following:** estimate distance and orientation relative to a wall, then use a feedback controller to maintain a desired offset;
- **Follow the Gap:** identify collision-free regions in a LiDAR scan and select a safe local direction of travel.

The [F1TENTH wall-following lab](https://github.com/f1tenth/f1tenth_lab3_template) and [Follow-the-Gap lab](https://github.com/f1tenth/f1tenth_lab4_template) provide background. Their examples assume an Ackermann-steered F1TENTH vehicle and ROS 2 interfaces that differ from TurtleBot and Goosebot. Do not copy their `/drive` commands or steering assumptions into the course robots.

## Engineering Questions

1. Why does A* generally expand fewer nodes than Dijkstra with a useful heuristic?
2. What makes a heuristic admissible?
3. Why can a short Pure Pursuit look-ahead cause oscillation?
4. Why can a long look-ahead cut corners?
5. How did increasing speed change tracking performance?
6. What parameters and interface information are needed to convert a path-tracking command into safe Goosebot left/right motor commands?

## Success Criteria

- [ ] A* is implemented and passes reachable, unreachable, and invalid-input tests;
- [ ] every reported path is checked for valid adjacency and collision-free cells;
- [ ] Dijkstra comparison uses the same map, endpoints, connectivity, and timing method;
- [ ] Pure Pursuit is implemented without replacing the assigned algorithm with a library controller;
- [ ] at least four tracking configurations tested;
- [ ] path, expanded nodes, tracked trajectory, and look-ahead target are shown in one labeled visualization;
- [ ] tracking metrics and fixed success/failure criteria are reported;
- [ ] tradeoffs explained.

## What to Submit

- source code;
- planned-path figure;
- planning/tracking overlay with expanded nodes and a look-ahead target;
- RViz2 screenshot if the instructor enables the ROS visualization extension;
- metrics table;
- `answers.md`.

## Troubleshooting

- Plot the occupancy grid, expanded nodes, and path before connecting the tracker.
- Verify row/column versus x/y conventions and map resolution explicitly.
- Reject paths that enter occupied cells or make disallowed diagonal corner cuts.
- If tracking diverges, first confirm units, heading convention, target selection, and motion-model update rate.
