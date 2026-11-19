# EEL 4332 — Introduction to Autonomous Vehicles

> **Before each lab:** use branch **`main`**, fetch instructor updates, and verify your local copy includes them. Start with [Setup Part 6](lab00_setup/README.md#part-6--fork-and-clone-the-course-repository) and the [fork/clone/update guide](docs/UPDATING_COURSE_REPOSITORY.md). A fork or ZIP created earlier does not update itself. Labs 4–5 and the final include explicit version checks.

> [!IMPORTANT]
> **Stop Gazebo with Ctrl+C in its launch terminal—not just the window's × button.** Closing the GUI can leave the simulation server and ROS nodes running, causing duplicate simulations or a GUI that does not match the robot/world queried from the terminal.
>
> **Before relaunching, switching worlds, or finishing:**
> 1. Stop robot motion; save any map/results you need.
> 2. Press **Ctrl+C** in each teleop, SLAM and Nav2 terminal that is running.
> 3. Press **Ctrl+C in the simulator launch terminal** (usually Terminal 1).
> 4. Wait for shutdown messages to finish and the shell prompt to return before launching again.
>
> If you already closed the window, return to its launch terminal and press Ctrl+C there. If shutdown seems incomplete, check `pgrep -af 'gz sim|gz-sim'` and identify leftover simulation processes before restarting.

> **Copying ROBOTIS commands:** A leading `$` is a terminal-prompt symbol, not part of the command. Some copy buttons include it. Copy only the command after `$ `, or paste into the editor first and remove that prefix from each command line. For example, `$ sudo apt update` must be entered as:
>
> ```bash
> sudo apt update
> ```
>
> If you see `$: command not found`, remove the leading `$ ` and rerun. **Keep dollar signs inside commands**, such as `$HOME`, `$PWD`, `${TURTLEBOT3_MODEL}`, and `$(...)`; those have a different meaning.

## Goosebot preparation before the final

After Labs 4–5 and the final's package setup, complete the [short Goosebot readiness check](final_project_simulation/README.md#goosebot-readiness-check) in your chosen IST or campus world: drive briefly and verify `/scan`, RobotModel and TF. Then proceed directly to SLAM mapping. The separate practice arena and perfect-map Nav2 goal are [optional troubleshooting exercises](final_project_simulation/README.md#goosebot-warm-up), with no separate submission. Use native Ubuntu/WSL + Jazzy and the final's workspace; Docker and stereo RTAB-Map remain optional.

## ROS 2 + Gazebo + Goosebot Laboratory Repository

This repository contains the hands-on laboratory sequence for **EEL 4332 — Introduction to Autonomous Vehicles**.

The laboratory sequence complements lecture, in-class problem solving, homework, and the written midterm. The labs are not intended to duplicate every lecture topic. Instead, they emphasize:

> **model → sense → estimate → localize → map → plan → control → integrate**

The course uses a simulation-first workflow and ends with a **Goosebot simulation delivery project with a supplied LiDAR**. Autonomous lane following on **Goosebot** provides the course's hardware experience; physical SLAM/Nav2 deployment is optional.

## Course simulation instructions — start here

Select **Jazzy** on each ROBOTIS page. Use **TurtleBot3 Waffle in TurtleBot3 World** for Lab 2 and the first parts of Labs 4–5. Labs 4–5 also use **TurtleBot3 House with Waffle Pi**. The final uses the provided **Goosebot model + supplied 2-D LiDAR** in IST or the campus world.

| Step | Official guide | Course assignment |
|---|---|---|
| Install robot software | [PC Setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup/?ros=jazzy) | [Lab 00](lab00_setup/README.md) |
| Install/run simulation | [Gazebo Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy) | [Lab 2](lab02_turtlebot_playground/README.md) |
| Build/save a map | [SLAM Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy) | [Lab 4](lab04_slam/README.md) |
| Navigate on that map | [Navigation Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/navigation_simulation/?ros=jazzy) | [Lab 5](lab05_navigation/README.md) |

Our lab READMEs contain the required Jazzy installation and launch commands, including WSL sourcing and per-terminal model settings. ROBOTIS links are references; students do not need to work through additional website sections. Existing Ubuntu/ROS installations need only the missing TurtleBot3 software. The official workspace is `~/turtlebot3_ws`; the course repository holds assignments and results.

This replaces the earlier Nav2-minimal simulator and standalone SLAM Toolbox workflow. Stop old processes before switching; do not combine launch commands or apply the old mesh/TF workarounds. Earlier screenshots retained in the repository depict that previous setup.

## Course software stack

The intended course environment is:

- **Windows 11 + WSL2**
- **Ubuntu 24.04 LTS**
- **ROS 2 Jazzy**
- **Gazebo Harmonic / modern Gazebo**
- **RViz2**
- **Nav2**
- **Cartographer** for TurtleBot Lab 4; **SLAM Toolbox** for the Goosebot final
- **robot_localization** for Goosebot's provided EKF
- **Python 3 + NumPy + Matplotlib**
- **Git** for version control and course updates
- **Visual Studio Code + WSL extension** as the supported editor workflow
- **TurtleBot 3 in Gazebo** as the primary simulation platform
- **F1TENTH / RoboRacer Gym** only as an optional car-like path-tracking extension
- **Goosebot** for autonomous lane following; SLAM/Nav2 hardware transfer is optional

ROS 2, Gazebo, and TurtleBot 3 are used for autonomy-system integration. Goosebot is a four-wheel skid-steer robot: it has four conventional wheels powered by four DC motors, all four wheel axes are fixed and parallel, and there is no geometric steering linkage. It turns by producing different left- and right-side velocities, which requires lateral tire slip. TurtleBot is not a digital twin of Goosebot, but its differential-drive motion is a useful approximation for learning the ROS/Nav2 workflow. The instructor must still validate Goosebot's motor-command mapping, slip, and exact kinematic parameters.

Lab 3 first develops differential-drive kinematics and wheel odometry as preparation for TurtleBot and Goosebot, then introduces the Python bicycle model as a deliberate car-like modeling comparison. F1TENTH may be used to extend the bicycle exercise, but it is not required for Goosebot deployment.

## Required lab sequence

| Lab | Mission | Student work |
|---|---|---|
| [00](lab00_setup/README.md) | Set up the course environment | Install and verify the supported tools |
| [01](lab01_ros2_gazebo_fundamentals/README.md) | Learn ROS 2 and Gazebo | Build nodes, inspect interfaces, and bridge simulation data |
| [02](lab02_turtlebot_playground/README.md) | Drive TurtleBot | Complete manual-driving challenges and practice stopping/resetting |
| [03](lab03_vehicle_modeling/README.md) | Predict vehicle motion | Implement and test assigned motion models and odometry |
| [04 - SLAM](lab04_slam/README.md) | Map World and House | Map both environments with Cartographer; retain separate maps and reuse both in Lab 5 |
| [05 - Nav2](lab05_navigation/README.md) | Navigate in World and House | Use each matching map/model; reach one World goal and two House goals in different rooms |
| [Goosebot readiness check](final_project_simulation/README.md#goosebot-readiness-check) | Verify Goosebot in the chosen IST or campus world before mapping | Brief manual driving; check `/scan`, RobotModel and TF; no separate submission |
| [Final](final_project_simulation/README.md) | Goosebot delivery in IST or campus simulation | Use the supplied LiDAR, create a map, localize, navigate to three deliveries/home, test a blocked route |

## How these labs map to the course

Labs 1-3 establish operation and modeling. Lab 4 integrates sensors, timestamps, TF, odometry, and SLAM into a mapping deliverable. Lab 5 introduces saved-map localization and guided navigation. The final transfers these skills to the supplied Goosebot model: students use the supplied 2-D LiDAR and build a new map in IST or the campus world, then navigate with AMCL/Nav2 and test a blocked route.

The former Labs 04-09 are condensed into Labs 04 and 05. Detailed theory is in each lab's **OPTIONAL_BACKGROUND.md**. Separate Kalman-filter, A*, Pure Pursuit, and safety-monitor implementations are optional extensions. Nav2 supplies the live planner/controller. The final's required integration task is mapping/localization/navigation, followed by a short LiDAR settings observation. A mission client is optional. The [legacy sequence](optional_legacy/previous_lab_sequence/README.md) remains an optional reference.

See the [course map](docs/COURSE_MAP.md) for topic placement and the [simulation runbook](docs/SIMULATION_WORKFLOW.md) for the shared launch workflow.

## Start here

1. Complete [`lab00_setup/README.md`](lab00_setup/README.md).
2. Run [`lab00_setup/verify_installation.sh`](lab00_setup/verify_installation.sh).
3. Complete [Lab 01 — ROS 2 and Gazebo Fundamentals](lab01_ros2_gazebo_fundamentals/README.md).
4. Complete the remaining labs in numerical order unless your instructor says otherwise.
5. Keep all experimental results in each lab's `results/` directory.
6. Do not commit large ROS build artifacts or recorded bags unless instructed.

## Fork, open, and sync

New students: [fork and clone through Setup Part 6](lab00_setup/README.md#part-6--fork-and-clone-the-course-repository), selecting `main`. Existing students: save work, verify your fork/instructor remotes and branch, and follow [the update guide](docs/UPDATING_COURSE_REPOSITORY.md). Do this before every lab, especially Labs 4–5 and the final.

With saved work and a clean working tree on `main`:

```bash
git fetch upstream &&
git merge --no-edit upstream/main &&
git merge-base --is-ancestor upstream/main HEAD &&
echo "Current checkout includes the latest fetched main course commits"
git log -1 --oneline
```

After success, `git push -u origin main` backs up your combined work. VS Code Sync synchronizes the tracked fork, not instructor updates. Preserve both maps for Labs 4–5; use each lab's current model/map commands.

## Repository structure

```text
eel4332-autonomous-vehicle-labs/
  lab00_setup/
  lab01_ros2_gazebo_fundamentals/
  lab02_turtlebot_playground/
  lab03_vehicle_modeling/
  lab04_slam/
  lab05_navigation/
  final_project_simulation/
  final_project_goosebot/  # optional hardware extension
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

Follow the copy-ready commands in the course READMEs. They adapt the official ROBOTIS Jazzy workflow and define the course model/world, scope, and submissions.

## Instructor note

Some simulation launch commands and Goosebot topic names are intentionally marked **INSTRUCTOR VALIDATION REQUIRED**. They should be tested on the final Fall 2026 course image before release to students.
