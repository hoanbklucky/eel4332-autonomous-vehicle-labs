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

This is a car-like model, not a model of Goosebot. Goosebot has four conventional, independently powered DC wheels on fixed parallel axes and no geometric steering linkage. It uses four-wheel skid steering through left/right velocity differences and tire slip. Comparing bicycle, differential-drive, and four-wheel skid-steer motion is part of understanding why a controller or model must match the physical platform.

## Background

### Why use a lightweight simulation?

A mathematical simulation makes model assumptions visible and allows one parameter to be changed at a time. Unlike Gazebo, the provided Python program does not simulate rigid-body contact, detailed tires, motors, or sensors. That simplicity is useful here because differences in a plotted trajectory can be attributed directly to the motion model, inputs, and numerical time step.

### State, input, and numerical propagation

The state describes the vehicle's planar position and heading at one instant. Speed and steering angle are inputs that determine how that state changes. Numerical integration approximates continuous motion by repeatedly advancing the state over a finite time step. A smaller step often reduces discretization error but requires more computation; it cannot repair an incorrect physical model.

The kinematic bicycle model replaces a four-wheel car with equivalent front and rear contact points and assumes rolling without important lateral slip. It is most informative at moderate steering and speed when tire-force dynamics are not dominant. The model cannot produce an in-place turn and should not be interpreted as a Goosebot motor model. The assigned propagation equations remain student implementation work.

### Frames and units

Use meters, seconds, meters per second, and radians consistently. State explicitly which direction is positive x, which direction is positive y, and whether positive yaw is counterclockwise. A trajectory may look plausible while being numerically wrong if degrees are supplied where radians are expected or if the plotting convention reverses an axis.

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

## Part 4 — Contrast with the Course Platforms

Explain why the bicycle model cannot represent an in-place differential/skid-steer turn. Identify the inputs that describe TurtleBot and Goosebot motion instead of the bicycle model's speed and steering angle. Explain why a two-wheel differential-drive model is useful but cannot capture all four-wheel tire scrub and slip.

If the instructor assigns the optional F1TENTH extension, run the same or comparable steering/speed cases in F1TENTH and compare trajectories. Otherwise, complete the pure-Python comparison and use instructor-provided reference data.

**INSTRUCTOR VALIDATION REQUIRED:** if F1TENTH is assigned, pin the exact commit and example command before student release.

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
6. Why can TurtleBot's differential-drive model approximate Goosebot while still missing four-wheel skid-steer slip?

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
- optional F1TENTH comparison if assigned.

## Troubleshooting

- Verify the straight-line case before debugging turns.
- Print the state after one time step and compare it with a hand calculation.
- Check radians versus degrees and confirm that the time step is positive.
- If results change greatly when the time step is halved, investigate numerical integration error before interpreting vehicle behavior.
