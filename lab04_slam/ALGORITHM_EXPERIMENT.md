# Required Experiment - Student Kalman Filter

This is a required part of [Lab 4](README.md). Use the assigned lecture equations; supporting theory is in [OPTIONAL_BACKGROUND.md](OPTIONAL_BACKGROUND.md). You implement the filter rather than calling a library estimator. This small Python experiment tests estimation behavior independently of SLAM Toolbox; it does not replace SLAM Toolbox's estimator or feed ground truth into ROS.

## 1. Generate repeatable inputs

From `lab04_slam/`, using your course Python environment:

```bash
python3 src/make_estimation_data.py --output results/estimation_inputs
```

The provided utility creates paired `normal.csv` and `dropout.csv` datasets with the same seeded measurement noise. Columns are time in seconds, noisy position in metres, and reference position/velocity. The second file removes measurements from 25 s through just before 35 s. The reference is a synthetic evaluation trajectory, not physical sensor truth.

Use a state containing position and velocity and a position-only measurement. Document your initial state/covariance, transition and measurement matrices, Q/R values, units, and handling of missing measurements. Reference columns are for scoring only; do not use them to initialize, predict, correct, or tune against each individual sample.

## 2. Implement and verify

Complete `predict` and `update` in `src/kalman_filter.py`. Keep the existing API. Write `src/run_estimation.py` to load data, call your implementation, record state/covariance/innovation, compute metrics, and produce plots. This experiment runner is part of your submission.

Before the full dataset, hand-check a single predict/update step for a small case of your choice with positive measurement variance. Compare your code's state and covariance with your independent calculation. Check dimensions, finite outputs, and covariance symmetry/nonnegative diagonal throughout the run.

## 3. Compare uncertainty assumptions

Choose three numerical Q/R configurations before running: greater trust in the model, greater trust in measurements, and a balanced case. Predict their relative smoothness, response at the velocity change, and uncertainty. Keep dataset and initial conditions fixed. Report position RMSE and maximum absolute position error for each, plus plots of position, velocity, and uncertainty.

A generic RMSE helper is provided in `src/localization_metrics.py`; a one-dimensional position can be compared using a second coordinate fixed at zero, or you may compute scalar RMSE directly. Label the metric and units. Compare raw measurement and filtered position errors on the same available-sample mask; do not compare metrics over different intervals as if they were equivalent.

## 4. Test the dropout

Repeat one chosen configuration with `dropout.csv`, using the same initial conditions. Missing position is represented by `nan`; predict without a measurement correction for those rows. Do not replace missing data with the reference or zero. Report error during the dropout and after measurements resume. Plot uncertainty and explain whether recovery matched your prediction. The filter need not beat every metric in every condition; explain its measured limitations.

## Submit with the SLAM results

Submit completed `kalman_filter.py`, your `run_estimation.py`, the one-step verification, Q/R table, baseline/dropout metrics, and plots. Include the random seed and data-generation command. Both this experiment and the SLAM map deliverable are required to complete Lab 4.
