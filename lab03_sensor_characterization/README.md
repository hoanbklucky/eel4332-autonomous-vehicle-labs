# Lab 3 — Sensor Characterization and Measurement Uncertainty

## Mission

**Measure how noisy simulated sensor data really is and build a measurement model from experimental evidence.**

## Learning Objectives

- distinguish accuracy, precision, bias, and random noise;
- compute sample mean, variance, and standard deviation;
- measure sensor update rate and timing consistency;
- identify outliers/dropouts;
- connect empirical data to a measurement model.

## Prerequisites

- Complete Labs 00 and 01, including the ROS 2 and Gazebo fundamentals practices.
- Be able to identify a topic's type, rate, timestamp, and frame.
- Review descriptive statistics and SI units.

## Background

### Why characterize simulated sensors?

Gazebo sensors exercise the same message, timing, frame, recording, and analysis workflow used with hardware. The simulator also allows the robot state and experiment conditions to be repeated. However, simulated noise may be idealized, configured, or absent. Low variation in Gazebo is evidence about the simulation configuration, not proof that a physical sensor will be equally precise.

### Measurement quality

A measurement can differ from the quantity of interest through systematic bias, random noise, quantization, outliers, dropout, and delay. **Accuracy** describes closeness to a reference value, while **precision** describes repeatability. A sensor may be precise but biased, or unbiased on average but noisy in individual samples.

Stationary trials reveal offsets and variation under nominally constant conditions. Controlled-motion trials reveal effects that appear only during dynamics, such as delay, vibration, changing scan geometry, or odometry error. Repeatable conditions and a documented ground-truth source are necessary for a defensible comparison.

### Sampling and simulation time

Message arrival time is not necessarily measurement time. Use message timestamps when available and report how sample intervals are computed. Keep Gazebo playing during collection and ensure the relevant ROS nodes use simulation time consistently. A topic rate alone cannot reveal stale timestamps, gaps, duplicated values, or an incorrect frame.

## Provided Files

```text
lab03_sensor_characterization/
├── README.md
├── src/
│   └── sensor_stats.py
├── results/
└── answers.md
```

## Procedure

Use the same TurtleBot/Gazebo environment introduced in Lab 01 unless the instructor supplies a recorded dataset. The resulting measurement workflow transfers to Goosebot, although its physical sensors, mounting locations, noise, timing, and calibration will differ.

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

## Troubleshooting

- Confirm the exact topic name and type with `ros2 topic list` and `ros2 topic info`.
- Inspect one message before recording a long experiment.
- If timestamps stop, verify that Gazebo is playing and simulation time is configured consistently.
- If a signal has zero variance, determine whether it is genuinely constant, rounded, or configured without noise.
- Keep large bag files outside Git unless the instructor explicitly requests them.
