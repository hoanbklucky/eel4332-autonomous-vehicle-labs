# Lab 5 — Sensor Characterization and Measurement Uncertainty

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
lab05_sensor_characterization/
├── README.md
├── src/
│   └── sensor_stats.py
├── results/
└── answers.md
```

## Learning Path and Visible Checkpoints

| Stage | What you are learning | Visible checkpoint |
|---|---|---|
| Inspect a baseline signal | Which field, frame, unit, and timestamp you are measuring | One live message is decoded and its chosen numeric field is identified. |
| Record controlled data | How stationary and moving conditions isolate different effects | Both datasets cover the stated duration and contain changing timestamps. |
| Measure quality | How statistics describe bias, spread, and outliers | A labeled table and plot summarize at least two signals. |
| Measure timing | Why nominal topic rate does not describe every timing problem | Sample-period results show the mean, variation, and any gaps. |
| Build a measurement model | How evidence becomes an uncertainty assumption | Every term in the model is tied to a measured signal or documented limitation. |

The expected result is not necessarily a visibly noisy trace. A nearly constant simulated signal is valid evidence when you verify that timestamps advance and explain what the simulator configuration can—and cannot—establish.

**Optional challenge after the required analysis:** Without changing the required datasets, identify the single most suspicious sample in one signal and explain whether it is likely an outlier, a real motion effect, or a processing mistake. This is not an additional submission unless assigned.

## Procedure

Use the same TurtleBot/Gazebo environment introduced in Lab 4 unless the instructor supplies a recorded dataset. The resulting measurement workflow transfers to Goosebot, although its physical sensors, mounting locations, noise, timing, and calibration will differ.

### Part 1 — Choose sensor signals

**Why this part matters:** Choosing the correct signal, field, frame, and unit is necessary before any statistical result can be interpreted correctly.

Use at least two numeric sensor/state signals from the instructor simulation, such as:

- IMU angular velocity;
- IMU linear acceleration;
- LiDAR range at a selected angle;
- wheel/odometry velocity;
- GNSS-like position if available.

Before recording data, state what you expect each selected signal to do while the robot is stationary and during your planned controlled motion. Predict the direction of any mean change, how each signal's variability should change between conditions, and whether its sample rate should change. These are hypotheses to test, not answers to revise after seeing the plots.

### Part 2 — Record a stationary experiment

**Why this part matters:** Holding the robot still isolates measurement bias and random noise from changes caused by motion.

Keep the robot stationary and record at least 20–30 seconds.

You may use `ros2 bag record` or export data to CSV using the instructor-provided workflow.

Record topic rate with:

```bash
ros2 topic hz /TOPIC
```

**Command breakdown:** `ros2 topic hz` measures the arrival frequency of messages. Replace `/TOPIC` with the selected sensor topic and press `Ctrl+C` after collecting a representative timing window.

### Part 3 — Record a controlled-motion experiment

**Why this part matters:** A repeatable motion test shows how the sensor behaves under the dynamic conditions an autonomous system actually encounters.

Choose a simple repeatable motion, such as constant forward speed or a constant turn. Define the commanded speed, duration, starting condition, and stopping rule before recording. Change only the motion condition between the stationary and controlled trials; keep the selected signals, collection method, and analysis method the same.

After collecting both datasets, compare the measured direction, variability, and sample rate with your predictions. Identify at least one agreement or discrepancy and explain a plausible physical, simulation, or processing cause.

### Part 4 — Analyze statistics

**Why this part matters:** Statistics turn qualitative impressions of “noisy data” into measurable bias, spread, and outlier behavior.

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

**Why this part matters:** Update rate and timing jitter affect how reliably controllers and estimators can use a sensor stream.

Examine timestamps or sample intervals.

Report:

- mean sample period;
- standard deviation of sample period;
- any obvious gaps.

### Part 6 — Measurement model

**Why this part matters:** Converting observations into a measurement model provides evidence-based uncertainty values for the estimator in the next lab.

For one signal, write a model such as:

$$
z = h(x) + b + v
$$

and identify what each term represents in your experiment.

## Engineering Questions

1. Can a sensor be precise but inaccurate?

   <details>
   <summary>Show answer</summary>

   Yes. Precision describes repeatability, while accuracy describes closeness to a reference. A range sensor that repeatedly reads 1.10 m for a target actually 1.00 m away is precise but has a +0.10 m bias and is inaccurate.

   </details>
2. Why is a constant bias dangerous for dead reckoning?

   <details>
   <summary>Show answer</summary>

   A constant bias accumulates when measurements are integrated. For example, a constant velocity bias produces position error that grows with elapsed time. A heading-rate bias accumulates heading error, which also sends the estimated trajectory in the wrong direction. Repeated samples do not average away a systematic offset.

   </details>
3. Why does differentiating a noisy signal often make the noise worse?

   <details>
   <summary>Show answer</summary>

   A numerical derivative subtracts nearby samples and divides by their time separation. Noise in those samples can therefore become a large fluctuation, especially at short sample intervals. Differentiation emphasizes rapid changes, including high-frequency noise; filtering can help but may introduce delay.

   </details>
4. How could timestamp jitter affect sensor fusion?

   <details>
   <summary>Show answer</summary>

   If an estimator assumes regular timing despite jitter, it may propagate state over the wrong interval or combine measurements from different physical instants. This can distort innovations, estimated motion, and uncertainty. Use measurement timestamps and actual elapsed intervals; distinguish measurement-time jitter from variable message-delivery delay.

   </details>
5. Which pair of sensors in your experiment would be most complementary?

   <details>
   <summary>Show answer</summary>

   The answer depends on the signals you actually recorded. Look for different strengths and failure modes. For example, wheel-derived velocity and IMU angular velocity provide complementary information about forward motion and turning, although neither alone supplies an absolute global position reference. If available, a global position measurement can complement drifting dead reckoning. Support your choice with the measured bias, variability, timing, and limitations of your selected signals.

   </details>

## Success Criteria

- [ ] two numeric signals recorded;
- [ ] stationary and controlled-motion data collected;
- [ ] signal behavior predicted before collection and compared with measured results;
- [ ] mean/std/variance computed;
- [ ] timing statistics reported;
- [ ] one measurement model written;
- [ ] limitations interpreted.

## What to Submit

- completed `sensor_stats.py`;
- plots/tables in `results/`;
- completed `answers.md`;
- short description of data-collection procedure;
- pre-run prediction and evidence table.

## Troubleshooting

- Confirm the exact topic name and type with `ros2 topic list` and `ros2 topic info`.
- Inspect one message before recording a long experiment.
- If timestamps stop, verify that Gazebo is playing and simulation time is configured consistently.
- If a signal has zero variance, determine whether it is genuinely constant, rounded, or configured without noise.
- Keep large bag files outside Git unless the instructor explicitly requests them.
