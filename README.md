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
- **Git** for version control and course updates
- **Visual Studio Code + WSL extension** as the supported editor workflow
- **TurtleBot 3 in Gazebo** as the primary simulation platform
- **F1TENTH / RoboRacer Gym** only as an optional car-like path-tracking extension
- **Goosebot** for final physical deployment

ROS 2, Gazebo, and TurtleBot 3 are used for autonomy-system integration. Goosebot is a four-wheel skid-steer robot: it has four conventional wheels powered by four DC motors, all four wheel axes are fixed and parallel, and there is no geometric steering linkage. It turns by producing different left- and right-side velocities, which requires lateral tire slip. TurtleBot is not a digital twin of Goosebot, but its differential-drive motion is a useful approximation for learning the ROS/Nav2 workflow. The instructor must still validate Goosebot's motor-command mapping, slip, and exact kinematic parameters.

Lab 3 first develops differential-drive kinematics and wheel odometry as preparation for TurtleBot and Goosebot, then introduces the Python bicycle model as a deliberate car-like modeling comparison. F1TENTH may be used to extend the bicycle exercise, but it is not required for Goosebot deployment.

## Required lab sequence

| Lab | Mission | Student work |
|---|---|---|
| [00](lab00_setup/README.md) | Set up the course environment | Install and verify the supported tools |
| [01](lab01_ros2_gazebo_fundamentals/README.md) | Learn ROS 2 and Gazebo | Build nodes, inspect interfaces, and bridge simulation data |
| [02](lab02_turtlebot_playground/README.md) | Drive TurtleBot | Complete manual-driving challenges and practice stopping/resetting |
| [03](lab03_vehicle_modeling/README.md) | Predict vehicle motion | Implement and test assigned motion models and odometry |
| [04 - SLAM](lab04_slam/README.md) | Build a reusable map | Implement/test a Kalman filter; configure SLAM, compare maps, and select one |
| [05 - Nav2](lab05_navigation/README.md) | Navigate on your map | Implement/test A*, Pure Pursuit, and safety logic; write and evaluate a Nav2 mission client |
| [Final](final_project_goosebot/README.md) | Transfer autonomy to Goosebot | Integrate, evaluate, and validate the physical platform |

## How these labs map to the course

Labs 1-3 establish operation and modeling. Lab 4 integrates sensors, timestamps, TF, odometry, and SLAM into a mapping deliverable. Lab 5 integrates localization, planning, tracking, mission execution, and failure handling into a navigation mission. The final project validates these workflows on Goosebot's four-wheel skid-steer platform.

The former Labs 04-09 are condensed into required Labs 04 and 05. Detailed theory and reading checks are in each new lab's **OPTIONAL_BACKGROUND.md**. Required steps, experiments, and submissions remain in the README. Kalman filtering is required within Lab 4; A*, Pure Pursuit, and safety-monitor implementations are required within Lab 5. Their unfinished starters are in the active labs. The [legacy sequence](optional_legacy/previous_lab_sequence/README.md) preserves the former manuals as optional references. Two integrated labs replace six separate lab numbers; the required algorithms remain assessed, so each integrated lab may span multiple sessions. Lecture/homework mathematics remains distinct from the simulation work.

See the [course map](docs/COURSE_MAP.md) for topic placement and the [simulation runbook](docs/SIMULATION_WORKFLOW.md) for the shared launch workflow.

## Start here

1. Complete [`lab00_setup/README.md`](lab00_setup/README.md).
2. Run [`lab00_setup/verify_installation.sh`](lab00_setup/verify_installation.sh).
3. Complete [Lab 01 — ROS 2 and Gazebo Fundamentals](lab01_ros2_gazebo_fundamentals/README.md).
4. Complete the remaining labs in numerical order unless your instructor says otherwise.
5. Keep all experimental results in each lab's `results/` directory.
6. Do not commit large ROS build artifacts or recorded bags unless instructed.

## Repository structure

```text
eel4332-autonomous-vehicle-labs/
  lab00_setup/
  lab01_ros2_gazebo_fundamentals/
  lab02_turtlebot_playground/
  lab03_vehicle_modeling/
  lab04_slam/
  lab05_navigation/
  final_project_goosebot/
  docs/
  common/
  optional_legacy/previous_lab_sequence/
```

Labs 4 and 5 contain a required `README.md`, an `OPTIONAL_BACKGROUND.md` reference, an `answers.md` experiment record, and directories for configurations and results. Lab 5 also provides mission-client starter code and a recording utility. See [REPOSITORY_CONTENTS.txt](REPOSITORY_CONTENTS.txt) for the file inventory.

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

- Git for Linux: https://git-scm.com/install/linux
- Visual Studio Code with WSL: https://code.visualstudio.com/docs/remote/wsl
- ROS 2 Jazzy: https://docs.ros.org/en/jazzy/
- ROS 2 Jazzy beginner CLI tutorials: https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html
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
