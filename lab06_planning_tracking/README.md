# Lab 6 — Path Planning and Path Tracking

## Mission

**Compute a collision-free path and make a vehicle follow it accurately enough to reach the goal.**

## Learning Objectives

- implement grid-based A* search;
- explain the role of \(g(n)\), \(h(n)\), and \(f(n)\);
- evaluate path length and planning effort;
- implement basic Pure Pursuit path tracking;
- analyze the tradeoff between look-ahead distance, speed, and tracking error.

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

Do not use a library A* implementation for the assigned algorithm.

## Part 2 — Planner Experiments

Compare at least:

- A* with an admissible heuristic;
- Dijkstra behavior by setting \(h(n)=0\).

Report:

- path length;
- number of expanded nodes;
- computation time.

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

This Pure Pursuit formulation produces an Ackermann/bicycle steering angle. It is a car-like control exercise and must not be sent directly to Goosebot, which has no steering joints. A Goosebot deployment requires a tested conversion or a controller designed for differential/skid-steer commands.

## Part 4 — Lightweight Vehicle Experiment

Track the same path for at least:

- two look-ahead distances;
- two speeds.

Use the Lab 02 bicycle simulator plus the tracking controller. If the instructor provides a pinned F1TENTH environment, it may be used as an optional second experiment.

## Part 5 — Quantitative Evaluation

Report:

- mean cross-track error;
- maximum cross-track error;
- completion time;
- failed/off-track cases.

## Engineering Questions

1. Why does A* generally expand fewer nodes than Dijkstra with a useful heuristic?
2. What makes a heuristic admissible?
3. Why can a short Pure Pursuit look-ahead cause oscillation?
4. Why can a long look-ahead cut corners?
5. How did increasing speed change tracking performance?
6. Why can an Ackermann steering command not be applied directly to a skid-steer robot?

## Success Criteria

- [ ] A* implemented;
- [ ] Dijkstra comparison completed;
- [ ] Pure Pursuit implemented;
- [ ] at least four tracking configurations tested;
- [ ] tracking metrics reported;
- [ ] tradeoffs explained.

## What to Submit

- source code;
- planned-path figure;
- tracking trajectories;
- metrics table;
- `answers.md`.
