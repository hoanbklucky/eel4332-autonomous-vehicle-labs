# Lab 3 — Sensor Characterization and Measurement Uncertainty

## Mission

**Measure how noisy simulated sensor data really is and build a measurement model from experimental evidence.**

## Learning Objectives

- distinguish accuracy, precision, bias, and random noise;
- compute sample mean, variance, and standard deviation;
- measure sensor update rate and timing consistency;
- identify outliers/dropouts;
- connect empirical data to a measurement model.

## Procedure

### Part 1 — Choose sensor signals

Use at least two numeric sensor/state signals from the instructor simulation, such as:

- IMU angular velocity;
- IMU linear acceleration;
- LiDAR range at a selected angle;
- wheel/odometry velocity;
- GNSS-like position if available.

### Part 2 — Record a stationary experiment

Keep the robot stationary and record at least 20–30 seconds.

You may use `ros2 bag record` or export data to CSV using the instructor-provided workflow.

Record topic rate with:

```bash
ros2 topic hz /TOPIC
```

### Part 3 — Record a controlled-motion experiment

Use a simple repeatable motion, such as constant forward speed or a constant turn.

### Part 4 — Analyze statistics

Complete:

```text
src/sensor_stats.py
```

For at least two signals report:

- sample count;
- mean;
- standard deviation;
- variance;
- minimum/maximum;
- estimated bias if ground truth is available.

### Part 5 — Timing

Examine timestamps or sample intervals.

Report:

- mean sample period;
- standard deviation of sample period;
- any obvious gaps.

### Part 6 — Measurement model

For one signal, write a model such as:

\[
z = h(x) + b + v
\]

and identify what each term represents in your experiment.

## Engineering Questions

1. Can a sensor be precise but inaccurate?
2. Why is a constant bias dangerous for dead reckoning?
3. Why does differentiating a noisy signal often make the noise worse?
4. How could timestamp jitter affect sensor fusion?
5. Which pair of sensors in your experiment would be most complementary?

## Success Criteria

- [ ] two numeric signals recorded;
- [ ] stationary and controlled-motion data collected;
- [ ] mean/std/variance computed;
- [ ] timing statistics reported;
- [ ] one measurement model written;
- [ ] limitations interpreted.

## What to Submit

- completed `sensor_stats.py`;
- plots/tables in `results/`;
- completed `answers.md`;
- short description of data-collection procedure.
