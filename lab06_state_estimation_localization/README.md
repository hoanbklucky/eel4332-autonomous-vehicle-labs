# Lab 6 — State Estimation and Localization

## Before You Begin — Update Course Files

In a **WSL/Ubuntu Terminal**, go to your local course repository and check for changes:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

**Command breakdown:** `cd` changes to the repository directory; `~` means your Ubuntu home directory. `git status --short` gives a compact list of local changes and prints nothing when the working tree is clean.

If the command prints nothing, run `git pull --rebase`. If it lists files, protect your work first by following [Updating the Course Repository](../docs/UPDATING_COURSE_REPOSITORY.md). Use your actual repository path if you cloned it elsewhere.

## Mission

**Fuse imperfect measurements into a better estimate of vehicle motion, then quantify whether the estimator actually improves localization.**

## Learning Objectives

- implement the predict/update cycle of a Kalman filter;
- interpret process noise \(Q\) and measurement noise \(R\);
- compare raw/dead-reckoned and fused estimates;
- compute localization error metrics;
- analyze estimator behavior when measurements are degraded or removed.

## Prerequisites

- Complete Labs 03 and 04.
- Be able to explain how Lab 3 integrates wheel-derived velocity into a dead-reckoned pose.
- Review the assigned Kalman-filter equations, covariance, and matrix dimensions.
- Be able to identify timestamps, frames, and ground-truth versus estimated data.

## Background

### Why estimate state in simulation?

No single practical sensor directly and perfectly reports every state needed for autonomy. An estimator combines a process model with measurements over time. Gazebo makes controlled dropout, noise, and bias experiments repeatable and may provide a reference trajectory for evaluation. That reference is for scoring the estimate; feeding privileged simulator truth into the filter would invalidate the experiment unless explicitly assigned.

### Prediction, correction, and uncertainty

The prediction step advances the estimate using the process model and increases or transforms its uncertainty. The correction step compares a measurement with the predicted measurement and uses their modeled uncertainties to decide how much to adjust the state. The innovation is therefore both a correction signal and a diagnostic quantity.

The process-noise covariance (Q) represents uncertainty in the motion model and unmodeled disturbances. The measurement-noise covariance (R) represents uncertainty in measurements. Neither matrix is simply a smoothing knob: each encodes assumptions that should be supported by units, sensor characterization, and experimental behavior. The assigned predict/update mathematics remains student implementation work.

### Localization, frames, and time

Dead reckoning is locally continuous but accumulates drift. A global or map-relative measurement can bound drift but may be noisy, delayed, or intermittent. Comparisons are meaningful only when trajectories use compatible frames, timestamps, and units. Interpolate or align samples using a documented method rather than comparing array indices blindly.

## Provided Files

```text
lab06_state_estimation_localization/
├── README.md
├── src/
│   ├── kalman_filter.py
│   └── localization_metrics.py
├── results/
└── answers.md
```

## Learning Path and Visible Checkpoints

| Stage | What you are learning | Visible checkpoint |
|---|---|---|
| Warm-up baseline | Whether the estimator equations work on a small known case | Prediction and correction values agree with a hand-checkable first step. |
| Implement the estimator | How state and uncertainty change together | The log shows a predicted state, innovation, corrected state, and covariance. |
| Tune assumptions | How `Q` and `R` change trust in model and measurement | Three overlaid estimates respond differently in the predicted directions. |
| Test realistic data | Whether the method improves a motion dataset | Raw, fused, and reference trajectories share compatible frames and timestamps. |
| Expose a failure | When a smooth estimate can still be wrong | A controlled dropout, bias, noise, or rate change causes a measurable degradation. |

Plots are debugging evidence as well as deliverables. Before interpreting a metric, confirm that the trajectory, measurements, and uncertainty behave sensibly during both normal data and the chosen failure.

**Optional challenge after the required failure test:** Predict which tuning configuration will recover most slowly after the degradation ends, then use the plot to test the prediction. This is not an additional submission unless assigned.

## Part 1 — Warm-Up Dataset

**Why this part matters:** A small, known dataset lets you verify the estimator mathematics before adding implementation and simulation complexity.

Use the instructor-provided 1-D or 2-D dataset first.

Complete:

```text
src/kalman_filter.py
```

The assigned filter implementation must be your own.

## Part 2 — Prediction and Correction

**Why this part matters:** Implementing the two Kalman-filter phases separately makes their roles—and mistakes in either phase—easier to understand.

For each time step:

1. predict the state;
2. predict covariance;
3. compute innovation;
4. compute Kalman gain;
5. correct the state;
6. correct covariance.

Log the estimate and uncertainty.

## Part 3 — Tune Q and R

**Why this part matters:** Varying process and measurement uncertainty shows how the filter decides whether to trust its model or its sensors.

Run at least three configurations:

- trust the model more;
- trust measurements more;
- balanced configuration.

Choose and record the numerical $Q$ and $R$ values for all three configurations before running them. For each configuration, predict relative smoothness, response to a new measurement, and uncertainty. Hold the dataset, initial state, and all non-$Q$/$R$ settings constant so the covariance assumptions are the controlled change.

Plot the resulting estimates. Compare the measured response and error metrics with the predictions; do not select a preferred configuration solely because its curve looks smooth.

## Part 4 — Localization Dataset / Simulation

**Why this part matters:** Applying the estimator to realistic data tests whether its improvement survives noise and motion beyond the warm-up example.

Apply the estimator or a comparable fusion workflow to instructor-provided odometry + global/localization measurements.

The default live simulation source is TurtleBot/Gazebo. Treat its differential-drive odometry as preparation for Goosebot rather than ground-truth four-wheel skid-steer behavior. Goosebot's wheel slip, encoder interpretation, effective turning geometry, and process-noise tuning must be established from hardware measurements.

Compare at least:

- raw/dead-reckoned trajectory;
- fused/estimated trajectory;
- ground truth when available.

## Part 5 — Failure Experiment

**Why this part matters:** Dropouts and bias expose estimator limitations that may remain hidden during normal operation.

Repeat with one degradation:

- measurement dropout;
- increased noise;
- artificial bias;
- reduced measurement frequency.

Before applying the degradation, predict which output or metric will change most, the direction of that change, and how the estimator should behave when valid measurements return. Then test the prediction using the same estimator configuration and initial condition as the undegraded baseline.

## Quantitative Analysis

Report at least two metrics, for example:

- position RMSE;
- final drift;
- maximum position error;
- heading RMSE.

## Engineering Questions

1. What does a larger \(Q\) communicate about the process model?
2. What does a larger \(R\) communicate about the measurements?
3. Why can a filter produce a smooth but wrong estimate?
4. What happened during your failure experiment?
5. Which metric best revealed the estimator weakness?

## Success Criteria

- [ ] Kalman predict/update implemented;
- [ ] Q/R parameter study completed;
- [ ] Q/R and degradation outcomes predicted before testing and compared with evidence;
- [ ] raw vs fused estimates compared;
- [ ] at least two localization metrics reported;
- [ ] one degradation experiment analyzed.

## What to Submit

- completed filter code;
- plots;
- metric table;
- completed tuning/failure prediction tables;
- `answers.md`.

## Troubleshooting

- Check vector and matrix dimensions before tuning (Q) or (R).
- Verify covariance matrices use units consistent with their corresponding state or measurement.
- Plot measurements, prediction, correction, and uncertainty separately to locate divergence.
- If live trajectories disagree immediately, verify frames and timestamp alignment before changing filter gains.
