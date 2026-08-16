# Lab 2 — Vehicle Modeling and Bicycle-Model Simulation

## Mission

**Predict the path of a car-like vehicle from speed and steering commands, then evaluate where the model succeeds and fails.**

## Learning Objectives

- implement the planar kinematic bicycle model;
- numerically integrate vehicle state over time;
- relate wheelbase, steering angle, speed, turning radius, and yaw rate;
- compare model predictions across operating conditions;
- quantify trajectory differences.

## Prerequisites

Review the bicycle-model equations from lecture/homework.

This lab assumes the state:

\[
x = [X,\;Y,\;\psi]^T
\]

with inputs such as longitudinal speed \(v\) and steering angle \(\delta\).

## Provided Files

```text
lab02_vehicle_modeling/
├── README.md
├── src/
│   ├── bicycle_model.py
│   └── run_experiments.py
├── results/
└── answers.md
```

## Part 1 — Implement the Model

Open:

```text
src/bicycle_model.py
```

Complete the `TODO` sections.

Your implementation should advance the state using a fixed time step.

Do not use an external vehicle-dynamics library for the assigned model.

## Part 2 — Sanity Checks

Test at least:

1. zero steering;
2. constant positive steering;
3. same steering at two speeds;
4. same speed with two steering angles.

Verify that the qualitative behavior matches your hand calculations.

## Part 3 — Numerical Experiment

Run:

```bash
python3 src/run_experiments.py
```

Modify the experiment definitions as required by the README/TODO comments.

Generate trajectory plots and save them in `results/`.

## Part 4 — F1TENTH / RoboRacer Comparison

If the instructor-pinned F1TENTH environment is available, run the same or comparable steering/speed cases in F1TENTH and compare trajectories.

If F1TENTH is unavailable, complete the pure-Python comparison and use instructor-provided reference data.

**INSTRUCTOR VALIDATION REQUIRED:** pin the exact F1TENTH commit and example command before student release.

## Quantitative Analysis

For at least one paired trajectory comparison, report an error metric such as:

- final-position error;
- mean Euclidean position error;
- maximum position error.

Also conduct one parameter study:

- wheelbase;
- speed;
- steering angle;
- integration time step.

## Engineering Questions

1. What assumptions make the kinematic bicycle model simple?
2. Why does the model become less reliable when tire slip becomes important?
3. How does wheelbase affect turning radius?
4. Why can two models agree at low speed but disagree at higher speed?
5. Which parameter or assumption had the largest effect in your experiment?

## Success Criteria

- [ ] bicycle model implemented;
- [ ] straight-line and turning cases verified;
- [ ] at least three trajectories plotted;
- [ ] one parameter study completed;
- [ ] one quantitative trajectory-error metric reported;
- [ ] limitations discussed.

## What to Submit

- completed source code;
- trajectory plots;
- parameter-study results;
- completed `answers.md`;
- F1TENTH comparison if assigned.
