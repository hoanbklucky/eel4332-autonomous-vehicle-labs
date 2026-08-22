# Lab 6 — Path Planning and Path Tracking

## Mission

**Compute a collision-free path and make a vehicle follow it accurately enough to reach the goal.**

## Learning Objectives

- implement grid-based A* search;
- explain the role of \(g(n)\), \(h(n)\), and \(f(n)\);
- evaluate path length and planning effort;
- implement basic Pure Pursuit path tracking;
- analyze the tradeoff between look-ahead distance, speed, and tracking error.

## Prerequisites

- Complete Labs 02 and 05.
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

## Provided Files

```text
lab06_planning_tracking/
├── README.md
├── src/
│   ├── astar.py
│   └── pure_pursuit.py
├── results/
└── answers.md
```

## Part 1 — A* Planning

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

Compare at least:

- A* with an admissible heuristic;
- Dijkstra behavior by setting \(h(n)=0\).

Report:

- path length;
- number of expanded nodes;
- computation time.

Use the same grid, start, goal, connectivity, and timing method for A* and Dijkstra. State the heuristic and whether diagonal moves are allowed.

## Part 3 — Path Tracking

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

Track the same path for at least:

- two look-ahead distances;
- two speeds.

Use the Lab 02 bicycle simulator plus the tracking controller. If the instructor provides a pinned F1TENTH environment, it may be used as an optional second experiment.

## Part 6 — Quantitative Evaluation

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
