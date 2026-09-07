# Lab 3 — Differential-Drive Odometry and Vehicle Modeling

## Before You Begin — Update Course Files

In a **WSL/Ubuntu Terminal**, go to your local course repository and check for changes:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

**Command breakdown:** `cd` changes to the repository directory; `~` means your Ubuntu home directory. `git status --short` gives a compact list of local changes and prints nothing when the working tree is clean.

If the command prints nothing, run `git pull --rebase`. If it lists files, protect your work first by following [Updating the Course Repository](../docs/UPDATING_COURSE_REPOSITORY.md). Use your actual repository path if you cloned it elsewhere.

## Mission

**Predict planar robot motion from wheel rotation, construct a differential-drive odometry estimate, and compare that model with car-like bicycle motion.**

## Learning Objectives

- convert left and right wheel speeds into robot linear and angular velocity;
- numerically integrate differential-drive wheel odometry;
- recognize why odometry is an estimate rather than ground truth;
- implement the planar kinematic bicycle model;
- compare differential-drive, bicycle, and four-wheel skid-steer motion;
- quantify the effect of one model parameter or numerical setting.

## Prerequisites

- Complete [Lab 2 — TurtleBot Playground](../lab02_turtlebot_playground/README.md).
- Recall how straight, curved, and in-place TurtleBot motion appeared in Gazebo, and how `/cmd_vel` and `/odom` changed while the robot moved.
- Review planar position, heading, angular velocity, and fixed-step numerical integration.
- Use the course Python virtual environment from Lab 00.

Both models use the planar pose

$$
\mathbf{x}=[x,\;y,\;\theta]^T,
$$

where $x$ and $y$ are expressed in a fixed world or odometry frame and $\theta$ is the robot heading.

## Background

### From wheel rotation to robot motion

The ideal differential-drive model has two independently driven wheels with radius $r$, separated by track width $b$. Let $\omega_L$ and $\omega_R$ be the left and right wheel angular speeds in radians per second. The forward speed $v$ and yaw rate $\dot{\theta}$ of the robot are

$$
v=\frac{r}{2}(\omega_R+\omega_L),
\qquad
\dot{\theta}=\frac{r}{b}(\omega_R-\omega_L).
$$

The body-forward speed must then be expressed in the fixed frame:

$$
\dot{x}=v\cos\theta,
\qquad
\dot{y}=v\sin\theta.
$$

These equations predict important special cases:

- equal wheel speeds produce straight motion;
- one stationary wheel produces a turn about the stationary side;
- equal and opposite wheel speeds produce an in-place rotation;
- a faster right wheel produces a counterclockwise turn under the sign convention used in this lab.

### From forward kinematics to odometry

**Forward kinematics** converts wheel speeds into instantaneous robot velocity. **Wheel odometry** repeatedly integrates that velocity to estimate pose:

$$
\mathbf{x}_{k+1}\approx \mathbf{x}_k+
\begin{bmatrix}
v_k\cos\theta_k\\
v_k\sin\theta_k\\
\dot{\theta}_k
\end{bmatrix}\Delta t.
$$

This is a dead-reckoning estimate, not a direct measurement of world position. Wheel-radius error, unequal wheels, slip, encoder quantization, timestamp error, and finite integration steps accumulate over time. A smooth odometry trajectory can therefore be precise but wrong.

This progression follows the textbook treatment from [differential-wheel forward kinematics to odometry, followed by car-like steering](https://eng.libretexts.org/Bookshelves/Mechanical_Engineering/Introduction_to_Autonomous_Robots_%28Correll%29/03%3A_Forward_and_Inverse_Kinematics/3.02%3A_Forward_kinematics_of_selected_Mechanisms).

TurtleBot is well approximated by a two-wheel differential-drive model. Goosebot also turns through left/right velocity differences, but it has four conventional wheels with fixed parallel axes. Its tires must scrub sideways during a turn, so ideal differential-drive odometry does not capture all Goosebot slip.

### Car-like bicycle model

The kinematic bicycle model replaces a four-wheel car with equivalent front and rear contact points. Its inputs are longitudinal speed $v$ and steering angle $\delta$, and its wheelbase is $L$:

$$
\dot{x}=v\cos\theta,
\qquad
\dot{y}=v\sin\theta,
\qquad
\dot{\theta}=\frac{v}{L}\tan\delta.
$$

Unlike differential drive, this model cannot rotate in place. It represents car-like steering and remains useful for comparing platform assumptions and for the Pure Pursuit exercise in Lab 8. It is not a model of Goosebot.

### Frames, signs, and units

Use meters, seconds, meters per second, radians, and radians per second. This lab defines positive $x$ as the initial forward direction, positive $y$ to the left, and positive yaw as counterclockwise. State the convention on every trajectory plot.

## Provided Files

```text
lab03_vehicle_modeling/
├── README.md
├── src/
│   ├── differential_drive.py
│   ├── bicycle_model.py
│   └── run_experiments.py
├── results/
└── answers.md
```

The propagation functions contain required `TODO` sections. Do not replace them with an external kinematics or vehicle-dynamics library.

## Step-by-Step Procedure

The work progresses from hand predictions to code, validation, sensitivity analysis, and model comparison so that each implementation result has a physical and mathematical reference.

### Part 1 — Predict differential-drive motion by hand

**Why this part matters:** Hand predictions provide a simple reference for catching sign, unit, and interpretation errors in the code that follows.

Before writing code, use the equations above to predict the sign of $v$ and $\dot{\theta}$ for:

1. $\omega_L=5\ \text{rad/s}$, $\omega_R=5\ \text{rad/s}$;
2. $\omega_L=0$, $\omega_R=5\ \text{rad/s}$;
3. $\omega_L=-3\ \text{rad/s}$, $\omega_R=3\ \text{rad/s}$;
4. $\omega_L=5\ \text{rad/s}$, $\omega_R=4.8\ \text{rad/s}$.

Record whether each case should move straight, curve left, curve right, or rotate in place. These predictions are your first debugging test.

### Part 2 — Implement differential-drive kinematics and odometry

**Why this part matters:** This step translates the wheel-motion equations from lecture into an executable estimate of robot pose.

Open:

```text
src/differential_drive.py
```

Complete the `TODO` sections in this order:

1. `wheel_speeds_to_twist`;
2. `step_differential_drive`;
3. `simulate_differential_drive`.

Use fixed-step Euler integration and include the initial pose as the first trajectory sample. Keep wheel angular speeds separate from linear wheel-edge speeds and verify their units.

### Part 3 — Validate differential-drive special cases

**Why this part matters:** Straight, rotating, and curved cases isolate different behaviors and make implementation errors easier to diagnose.

For $r=0.033\ \text{m}$, $b=0.16\ \text{m}$, and $\Delta t=0.02\ \text{s}$, simulate at least:

1. equal positive wheel speeds;
2. one stationary wheel;
3. equal and opposite wheel speeds;
4. slightly unequal positive wheel speeds.

For every case, compare the simulated result with your Part 1 prediction. An in-place rotation changes yaw while $x$ and $y$ remain approximately constant; it may appear as a single point on an $x$–$y$ plot, so also inspect the final yaw.

### Part 4 — Conduct an odometry-sensitivity experiment

**Why this part matters:** Changing model assumptions shows why small wheel or geometry errors accumulate into odometry drift.

Choose **one** experiment:

- repeat a curved trajectory with at least three integration time steps;
- introduce a small left/right wheel-speed mismatch during nominally straight motion;
- use a slightly incorrect wheel radius or track width in the odometry calculation.

Treat one trajectory as the reference. Report final position error and final heading error for the other cases. Explain why the error accumulates even when the wheel-speed input is constant.

If the instructor assigns a live comparison, record the TurtleBot `/odom` topic during a short straight or turning command and compare its qualitative behavior with your ideal model. Do not treat `/odom` as Gazebo ground truth.

### Part 5 — Implement and test the bicycle model

**Why this part matters:** Comparing a car-like steering model with differential drive clarifies why vehicle geometry determines the appropriate kinematics.

Open:

```text
src/bicycle_model.py
```

Complete its existing `TODO` sections. Test these compact cases:

1. zero steering;
2. one constant positive steering angle;
3. the same speed with a larger steering angle.

Confirm that zero steering produces a straight line and that increasing steering magnitude reduces turning radius. The bicycle portion is intentionally smaller than the differential-drive portion.

### Part 6 — Run and compare the models

**Why this part matters:** Common plots and metrics make similarities, limitations, and modeling errors easier to evaluate objectively.

From the Lab 3 directory, run:

```bash
source ~/venvs/eel4332/bin/activate
python src/run_experiments.py
```

**Command breakdown:** `source` activates the course Python environment. `python src/run_experiments.py` runs the experiment driver using that environment's interpreter and dependencies.

The script saves plots in `results/`. Add plot titles or captions that identify each model, its inputs, its parameters, and the coordinate convention.

Use your results to compare:

| Platform/model | Motion inputs | Can rotate in place? | Important limitation |
|---|---|---:|---|
| TurtleBot ideal differential drive | left/right wheel speeds | yes | omits real slip and calibration error |
| kinematic bicycle | speed and steering angle | no | omits tire-force dynamics and lateral slip |
| Goosebot four-wheel skid steer | four motor commands reduced to left/right motion | physically possible | turning depends strongly on tire scrub and slip |

If the instructor assigns the optional F1TENTH extension, run comparable bicycle-model cases in the pinned environment. Otherwise, no F1TENTH installation is required.

**INSTRUCTOR VALIDATION REQUIRED:** pin the exact F1TENTH commit and command before assigning that extension, and provide the exact TurtleBot ground-truth topic if a quantitative live-simulation comparison is required.

## Experiment / Quantitative Analysis

Your results must include:

- differential-drive plots for the four special cases;
- a table of final $x$, $y$, and $\theta$ for those cases;
- the Part 4 odometry-sensitivity plot and its final position and heading errors;
- one bicycle-model plot containing the three Part 5 cases;
- a concise comparison of the assumptions behind all three platform models.

Do not compare trajectories point by point unless they use the same time samples, initial pose, and compatible commands. A steering angle and a left/right wheel-speed pair are different physical inputs.

## Engineering Questions

1. Why is integrating wheel-derived velocity called dead reckoning?
2. Which differential wheel-speed combinations produce straight motion, curved motion, and an in-place turn?
3. Why can a small wheel-radius or wheel-speed mismatch create a large position error after a long drive?
4. Why is `/odom` an estimate rather than ground truth?
5. Why can the bicycle model not represent an in-place turn?
6. How do wheelbase and steering angle affect bicycle-model turning radius?
7. Why can TurtleBot’s differential-drive model approximate Goosebot while missing four-wheel tire scrub and slip?
8. Which model should be used for the Pure Pursuit steering-angle exercise in Lab 8, and which model better prepares you to interpret TurtleBot odometry?

## Success Criteria

- [ ] differential-drive forward kinematics implemented and unit-checked;
- [ ] wheel odometry integrated from an initial pose;
- [ ] straight, curved, pivot, and in-place cases verified;
- [ ] one odometry-sensitivity experiment completed quantitatively;
- [ ] bicycle-model straight and turning cases verified;
- [ ] differential-drive, bicycle, and skid-steer assumptions compared;
- [ ] required plots and tables saved in `results/`.

## What to Submit

- completed `src/differential_drive.py` and `src/bicycle_model.py`;
- any documented changes to `src/run_experiments.py`;
- differential-drive, odometry-sensitivity, and bicycle-model plots;
- final-pose and error tables;
- completed `answers.md`;
- optional F1TENTH or live TurtleBot comparison only if assigned.

## Troubleshooting

- Verify the wheel-speed-to-twist calculation before debugging pose integration.
- Print one update and compare it with a hand calculation.
- If equal positive wheel speeds do not produce zero yaw rate, check the subtraction order.
- If a left turn appears as a right turn, check wheel labels and the yaw sign convention.
- If in-place rotation seems motionless on the $x$–$y$ plot, inspect yaw versus time.
- Check radians versus degrees and angular wheel speed versus linear wheel-edge speed.
- If results change greatly when the time step is halved, investigate integration error before interpreting vehicle behavior.

After completing this lab, continue to [Lab 4 — Autonomous-System Architecture and Sensors](../lab04_system_architecture_sensors/README.md).
