# Lab 7 — System Integration, Safety, and Failure Handling

## Mission

**Make the autonomy stack fail in controlled ways, detect the failures, and transition the vehicle to a safer behavior.**

## Learning Objectives

- trace dependencies among sensing, localization, planning, and control;
- distinguish sensor, estimator, planner, controller, and communication failures;
- quantify timing/latency effects;
- design a simple safety monitor;
- demonstrate graceful degradation or safe stop.

## Part 1 — Establish a Baseline

Run a known-good autonomous mission with TurtleBot in Gazebo.

The final Goosebot deployment will reuse the system-level workflow but not every simulator parameter. In particular, verify the physical robot's command interface, braking behavior, wheel slip, sensor timing, footprint, and safe-stop mechanism before reusing simulation thresholds.

Record:

- mission completion time;
- path/tracking error if available;
- sensor update rates;
- localization status.

## Part 2 — Inject Faults

Test at least three fault types from different categories:

- sensor dropout;
- delayed sensor data;
- biased measurement;
- localization jump/loss;
- blocked path;
- control-command saturation.

The instructor may provide fault-injection nodes or configuration switches.

## Part 3 — Implement a Safety Monitor

Complete:

```text
src/safety_monitor.py
```

The monitor should evaluate a small set of health conditions and select a state such as:

```text
NORMAL
DEGRADED
STOP
```

Do not create an excessively complicated fault-management system.

## Part 4 — Evaluate Response

For each fault, report:

- whether it was detected;
- detection delay;
- selected response;
- whether the response prevented continued unsafe motion;
- false positives/limitations.

## Engineering Questions

1. Why can a system remain "running" while no longer being safe?
2. Which failures can be detected from timestamps alone?
3. Why is a safe stop not always the only possible degraded behavior?
4. Which component should own the final authority to inhibit unsafe motion?
5. What information should be logged after a failure?

## Success Criteria

- [ ] baseline mission recorded;
- [ ] three fault types tested;
- [ ] safety monitor implemented;
- [ ] normal/degraded/stop behavior demonstrated;
- [ ] detection/response metrics reported.

## What to Submit

- `safety_monitor.py`;
- fault-results table;
- one short video demonstrating a fault and response;
- `answers.md`.
