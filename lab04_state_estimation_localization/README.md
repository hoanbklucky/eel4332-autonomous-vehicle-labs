# Lab 4 — State Estimation and Localization

## Mission

**Fuse imperfect measurements into a better estimate of vehicle motion, then quantify whether the estimator actually improves localization.**

## Learning Objectives

- implement the predict/update cycle of a Kalman filter;
- interpret process noise \(Q\) and measurement noise \(R\);
- compare raw/dead-reckoned and fused estimates;
- compute localization error metrics;
- analyze estimator behavior when measurements are degraded or removed.

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
