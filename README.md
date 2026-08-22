# EEL 4332 — Introduction to Autonomous Vehicles

## ROS 2 + Gazebo + Goosebot Laboratory Repository

This repository contains the hands-on laboratory sequence for **EEL 4332 — Introduction to Autonomous Vehicles**.

The laboratory sequence complements lecture, in-class problem solving, homework, and the written midterm. The labs are not intended to duplicate every lecture topic. Instead, they emphasize:

> **model → sense → estimate → localize → map → plan → control → integrate**

The course uses a simulation-first workflow and ends with deployment on the **Goosebot** physical platform.

## Course software stack

The intended course environment is:

- **Windows 11 + WSL2**
- **Ubuntu 24.04 LTS**
- **ROS 2 Jazzy**
- **Gazebo Harmonic / modern Gazebo**
- **RViz2**
- **Nav2**
- **SLAM Toolbox**
- **robot_localization**
- **Python 3 + NumPy + Matplotlib**
- **TurtleBot 3 in Gazebo** as the primary simulation platform
- **F1TENTH / RoboRacer Gym** only as an optional car-like path-tracking extension
- **Goosebot** for final physical deployment

ROS 2, Gazebo, and TurtleBot 3 are used for autonomy-system integration. Goosebot is a four-wheel skid-steer robot: it has four conventional wheels powered by four DC motors, all four wheel axes are fixed and parallel, and there is no geometric steering linkage. It turns by producing different left- and right-side velocities, which requires lateral tire slip. TurtleBot is not a digital twin of Goosebot, but its differential-drive motion is a useful approximation for learning the ROS/Nav2 workflow. The instructor must still validate Goosebot's motor-command mapping, slip, and exact kinematic parameters.

The Python bicycle model remains a deliberate car-like modeling exercise. F1TENTH may be used to extend that exercise, but it is not required for Goosebot deployment.

## Required lab sequence

| Lab | Mission | Main concepts |
|---|---|---|
| 01 | Inspect an autonomous system and its sensors | ROS 2 architecture, topics, frames, sensors |
| 02 | Predict car-like motion from steering and speed | bicycle model, kinematics, comparison with differential drive |
| 03 | Characterize noisy sensors | bias, variance, sampling, measurement models |
| 04 | Estimate vehicle state and evaluate localization | Kalman filtering, odometry, localization error |
| 05 | Build and evaluate a map | occupancy grids, SLAM, loop closure, map quality |
| 06 | Plan a path and track it | A*, path metrics, Pure Pursuit, car-like tracking limits |
| 07 | Make autonomy fail safely | system integration, timing, sensor faults, safety monitor |
| Final | Complete an autonomous navigation mission | SLAM/localization/Nav2/Goosebot integration |

## How these labs map to the course

The labs deliberately group related lecture topics into larger engineering tasks.

- **Lab 01** supports system architecture and autonomous-vehicle sensors.
- **Lab 02** supports vehicle kinematics and modeling.
- **Lab 03** supports sensor uncertainty and measurement models.
- **Lab 04** supports state estimation and localization.
- **Lab 05** supports mapping and SLAM.
- **Lab 06** supports path planning and path tracking/control.
- **Lab 07** supports system integration, safety, and failure handling.
- **Final Project** supports end-to-end autonomy and sim-to-real deployment.

The simulation-to-hardware transfer is intentionally layered. ROS topics, TF, mapping, localization, Nav2, and safety concepts transfer from TurtleBot simulation. The final project then requires students to validate Goosebot's four-wheel skid-steer interface, dimensions, sensor frames, slip behavior, and safety limits.

## Start here

1. Complete [`lab00_setup/README.md`](lab00_setup/README.md).
2. Run [`lab00_setup/verify_installation.sh`](lab00_setup/verify_installation.sh).
3. Complete labs in numerical order unless your instructor says otherwise.
4. Keep all experimental results in each lab's `results/` directory.
5. Do not commit large ROS build artifacts or recorded bags unless instructed.

## Repository structure

```text
eel4332-autonomous-vehicle-labs/
├── README.md
├── AGENTS.md
├── requirements.txt
├── lab00_setup/
├── docs/
├── common/
├── lab01_system_architecture_sensors/
├── lab02_vehicle_modeling/
├── lab03_sensor_characterization/
├── lab04_state_estimation_localization/
├── lab05_mapping_slam/
├── lab06_planning_tracking/
├── lab07_integration_safety/
└── final_project_goosebot/
```

Each required lab follows the same structure:

```text
labXX_.../
├── README.md
├── src/
├── results/
└── answers.md
```

## Rules for student code

- Use **SI units** unless a lab explicitly states otherwise.
- Clearly distinguish measured values, estimated values, and ground truth.
- Do not replace a required algorithm with a library call unless the lab explicitly permits it.
- Keep reusable math in functions rather than writing one long script.
- Plot and label quantitative results.
- Preserve starter-code `TODO` markers until you implement them.
- Do not commit instructor solutions to this repository.

## Submission convention

Unless your instructor specifies otherwise, submit the requested source code, plots/tables, and `answers.md` for each lab. A typical lab submission contains:

```text
labXX_.../
├── src/
├── results/
└── answers.md
```

Do not submit:

- `.git/`
- ROS `build/`, `install/`, or `log/`
- virtual environments
- large bag files unless specifically requested

## External references

Useful official references:

- ROS 2 Jazzy: https://docs.ros.org/en/jazzy/
- ROS–Gazebo integration (`ros_gz`): https://docs.ros.org/en/jazzy/p/ros_gz/
- Gazebo: https://gazebosim.org/
- Nav2: https://docs.nav2.org/
- Nav2 Gazebo setup guide: https://docs.nav2.org/setup_guides/gazebo.html
- ROBOTIS TurtleBot 3 Gazebo simulation (select **Jazzy**): https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy
- ROBOTIS TurtleBot 3 SLAM simulation (select **Jazzy**): https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy
- RoboRacer / F1TENTH: https://github.com/f1tenth
- F1TENTH Gym: https://github.com/f1tenth/f1tenth_gym
- F1TENTH open course labs: https://github.com/f1tenth/f1tenth_labs_openrepo
- Goosebot course/platform repository: https://github.com/hoanbklucky/goose

The instructions in this repository take precedence for **EEL 4332** because they define the versions, deliverables, and workflow used in this course.

## Instructor note

Some simulation launch commands and Goosebot topic names are intentionally marked **INSTRUCTOR VALIDATION REQUIRED**. They should be tested on the final Fall 2026 course image before release to students.
