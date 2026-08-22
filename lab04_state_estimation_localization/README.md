# Lab 4 — State Estimation and Localization

## Mission

**Fuse imperfect measurements into a better estimate of vehicle motion, then quantify whether the estimator actually improves localization.**

## Learning Objectives

- implement the predict/update cycle of a Kalman filter;
- interpret process noise \(Q\) and measurement noise \(R\);
- compare raw/dead-reckoned and fused estimates;
- compute localization error metrics;
- analyze estimator behavior when measurements are degraded or removed.

## Prerequisites

- Complete Labs 02 and 03.
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
lab04_state_estimation_localization/
├── README.md
├── src/
│   ├── kalman_filter.py
│   └── localization_metrics.py
├── results/
└── answers.md
```

## Part 1 — Warm-Up Dataset

Use the instructor-provided 1-D or 2-D dataset first.

Complete:

```text
src/kalman_filter.py
```

The assigned filter implementation must be your own.

## Part 2 — Prediction and Correction

For each time step:

1. predict the state;
2. predict covariance;
3. compute innovation;
4. compute Kalman gain;
5. correct the state;
6. correct covariance.

Log the estimate and uncertainty.

## Part 3 — Tune Q and R

Run at least three configurations:

- trust the model more;
- trust measurements more;
- balanced configuration.

Plot the resulting estimates.

## Part 4 — Localization Dataset / Simulation

Apply the estimator or a comparable fusion workflow to instructor-provided odometry + global/localization measurements.

The default live simulation source is TurtleBot/Gazebo. Treat its differential-drive odometry as preparation for Goosebot rather than ground-truth four-wheel skid-steer behavior. Goosebot's wheel slip, encoder interpretation, effective turning geometry, and process-noise tuning must be established from hardware measurements.

Compare at least:

- raw/dead-reckoned trajectory;
- fused/estimated trajectory;
- ground truth when available.

## Part 5 — Failure Experiment

Repeat with one degradation:

- measurement dropout;
- increased noise;
- artificial bias;
- reduced measurement frequency.

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
- [ ] raw vs fused estimates compared;
- [ ] at least two localization metrics reported;
- [ ] one degradation experiment analyzed.

## What to Submit

- completed filter code;
- plots;
- metric table;
- `answers.md`.

## Troubleshooting

- Check vector and matrix dimensions before tuning (Q) or (R).
- Verify covariance matrices use units consistent with their corresponding state or measurement.
- Plot measurements, prediction, correction, and uncertainty separately to locate divergence.
- If live trajectories disagree immediately, verify frames and timestamp alignment before changing filter gains.
