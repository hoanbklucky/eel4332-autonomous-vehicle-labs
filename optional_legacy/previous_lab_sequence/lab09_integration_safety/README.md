# Lab 9 — System Integration, Safety, and Failure Handling

> **Optional legacy exercise.** This is part of the previous six-lab sequence. Its original requirements and numbering apply only if the instructor assigns this archived version. Required algorithm implementations now live in the active Labs 4 and 5. The current required sequence is [Lab 4 - SLAM](../../../lab04_slam/README.md) and [Lab 5 - Nav2 Navigation](../../../lab05_navigation/README.md).

## Before You Begin — Update Course Files

In a **WSL/Ubuntu Terminal**, go to your local course repository and check for changes:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

**Command breakdown:** `cd` changes to the repository directory; `~` means your Ubuntu home directory. `git status --short` gives a compact list of local changes and prints nothing when the working tree is clean.

If the command prints nothing, run `git pull --rebase`. If it lists files, protect your work first by following [Updating the Course Repository](../../../docs/UPDATING_COURSE_REPOSITORY.md). Use your actual repository path if you cloned it elsewhere.

## Mission

**Make the autonomy stack fail in controlled ways, detect the failures, and transition the vehicle to a safer behavior.**

## Learning Objectives

- trace dependencies among sensing, localization, planning, and control;
- distinguish sensor, estimator, planner, controller, and communication failures;
- quantify timing/latency effects;
- design a simple safety monitor;
- demonstrate graceful degradation or safe stop.

## Prerequisites

- Complete Labs 01, 03, 04, 05, and 06.
- Be able to verify Gazebo motion, ROS topics, TF, localization, and Nav2 separately.
- Review the course-approved simulated stop and reset procedure before injecting faults.

## Background

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

## Provided Files

```text
lab09_integration_safety/
├── README.md
├── src/
│   └── safety_monitor.py
├── results/
└── answers.md
```

## Learning Path and Visible Checkpoints

| Stage | What you are learning | Visible checkpoint |
|---|---|---|
| Establish healthy behavior | What normal timing, sensing, localization, and motion look like | A mission succeeds and its normal input ranges are recorded. |
| Inject one fault at a time | How an underlying fault produces observable symptoms | Each injected condition changes the intended signal or system state. |
| Measure collision urgency | Why distance must be interpreted together with motion | Two low-speed approaches show different urgency as speed changes. |
| Implement a safety response | How detection gains command authority | The monitor transitions among documented states and inhibits unsafe simulated motion. |
| Test failure and recovery | Whether the design is effective without excessive false stops | Results include delay, clearance, outcome, limitations, and an explicit reset. |

The required demonstration is behavioral: printing `STOP` is not enough. The simulated robot must stop through the approved command path, and the recorded evidence must connect the triggering condition to that physical outcome.

**Optional challenge after the required tests:** Find a safe, repeatable case near your decision boundary and explain whether changing the threshold would reduce a false positive or increase stopping risk. Do not increase the approved speed or reproduce collision approaches on hardware.

## Safety Interface Contract

The expected TurtleBot interfaces are listed below. Verify them on the live graph and record any instructor-approved replacement.

| Interface | Expected type | Safety use |
|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | obstacle range, scan timestamp, and data validity |
| `/odom` | `nav_msgs/msg/Odometry` | current forward speed and motion state |
| `/tf` | `tf2_msgs/msg/TFMessage` | confirms sensor, base, odometry, and map frames remain connected |
| Nav2 status/actions | Nav2 action and lifecycle interfaces | mission progress, cancellation, and component health |
| safe motion-command path | course-validated velocity interface | normal command or inhibited/zero command |

A production robot needs an explicit command-arbitration design so that autonomous control and the safety monitor do not fight by publishing conflicting commands. For this lab, use only the instructor-validated simulated command path. Do not invent a Goosebot topic or copy TurtleBot topic names to hardware.

**INSTRUCTOR VALIDATION REQUIRED:** document the final Nav2 cancellation method, command-arbitration mechanism, velocity topic/type, and reset procedure on the Fall 2026 image.

## Part 1 — Establish a Baseline

**Why this part matters:** A healthy baseline provides the reference needed to distinguish injected failures from normal system variation.

Run a known-good autonomous mission with TurtleBot in Gazebo.

The final Goosebot deployment will reuse the system-level workflow but not every simulator parameter. In particular, verify the four-motor command mapping, braking behavior, skid-steer slip, sensor timing, footprint, and safe-stop mechanism before reusing simulation thresholds.

Record:

- mission completion time;
- path/tracking error if available;
- sensor update rates;
- localization status.

Also record the normal ranges of `/scan` age and update rate, forward speed, and nearest valid forward obstacle distance. These baseline measurements are needed to justify monitor thresholds.

## Part 2 — Inject Faults

**Why this part matters:** Controlled faults reveal causal links among sensing, estimation, planning, and control without waiting for unpredictable failures.

Test at least three fault types from different categories:

- sensor dropout;
- delayed sensor data;
- biased measurement;
- localization jump/loss;
- blocked path;
- control-command saturation.

The instructor may provide fault-injection nodes or configuration switches.

## Part 3 — Controlled Collision-Approach Experiment

**Why this part matters:** Measuring the approach and stop response turns an abstract safety concern into a timing and distance requirement.

Perform this experiment in Gazebo only. Do not reproduce it on Goosebot.

The [F1TENTH automatic-emergency-braking lab](https://github.com/f1tenth/f1tenth_lab2_template) is useful supplemental reading about combining LiDAR and vehicle motion for collision detection. It assumes an Ackermann vehicle and different ROS interfaces; do not copy its topic names, command message, or thresholds into this lab.

1. Place the simulated robot in open space facing a wall or fixed obstacle, with enough distance to stop.
2. Confirm that Gazebo's pause/reset controls work and keep a manual stop command ready.
3. Record `/scan` and `/odom` while approaching at a low, constant speed.
4. Repeat at a second speed while keeping the initial pose and obstacle approximately the same.
5. Use LiDAR range and odometry speed together to construct a collision-urgency measure. A valid design must respond more urgently when the robot approaches the same obstacle faster.
6. Repeat one approach with the safety monitor enabled and verify that it selects `STOP` before contact.
7. Drive approximately parallel to a wall at a similar speed to check that the monitor does not produce an obvious false stop merely because an obstacle is nearby.

Handle invalid LiDAR values, stale messages, zero or reverse motion, and an unavailable transform explicitly. The collision-urgency calculation and thresholds are student design work; document and defend them rather than copying fixed values from another robot.

For every approach, record:

- commanded and measured speed;
- initial obstacle distance;
- detection time and detection delay;
- obstacle distance when `STOP` is selected;
- minimum remaining clearance;
- whether contact occurred;
- any false positive or missed detection.

## Part 4 — Implement a Safety Monitor

**Why this part matters:** A separate monitor can detect unsafe conditions and request a safer state even when another component behaves incorrectly.

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

The monitor must consider freshness, localization/path health, obstacle distance, and forward speed. Explain which conditions produce `NORMAL`, `DEGRADED`, and `STOP`. A transition to `STOP` must use the instructor-validated command-arbitration or Nav2 cancellation path; printing `STOP` without inhibiting simulated motion is not a successful safe response.

## Part 5 — Evaluate Response

**Why this part matters:** Response metrics verify whether the safety mechanism reduces risk and reveal the performance cost of its thresholds.

For each fault, report:

- whether it was detected;
- detection delay;
- selected response;
- whether the response prevented continued unsafe motion;
- false positives/limitations.

Use one results table for both injected faults and collision approaches. Keep timing definitions consistent—for example, measure detection delay from the first invalid/stale sample or first threshold crossing to the state transition.

## Engineering Questions

1. Why can a system remain "running" while no longer being safe?
2. Which failures can be detected from timestamps alone?
3. Why is a safe stop not always the only possible degraded behavior?
4. Which component should own the final authority to inhibit unsafe motion?
5. What information should be logged after a failure?
6. Why is obstacle distance alone insufficient for choosing the same stop threshold at all speeds?
7. Why can two independent publishers on a velocity-command topic undermine a safety monitor?

## Success Criteria

- [ ] baseline mission and normal input ranges are recorded;
- [ ] three fault types from different categories are tested;
- [ ] two controlled Gazebo approaches at different speeds are measured;
- [ ] safety-monitor decision logic is implemented and its thresholds are documented;
- [ ] `NORMAL`, `DEGRADED`, and `STOP` behavior is demonstrated;
- [ ] a simulated stop prevents obstacle contact in the assigned test;
- [ ] detection delay, stop distance/clearance, and false-positive behavior are reported.

## What to Submit

- `safety_monitor.py`;
- combined fault and collision-approach results table;
- one short video demonstrating a fault and response;
- `answers.md`.

## Troubleshooting

- Reproduce a known-good baseline before each injected fault.
- Confirm the fault actually changed the intended topic, timestamp, transform, or command path.
- If STOP is reported but the robot moves, inspect command arbitration and active publishers.
- Reset the complete simulation between trials when simulation time or lifecycle state becomes inconsistent.
- Perform collision approaches only in Gazebo and at the instructor-approved speeds.
