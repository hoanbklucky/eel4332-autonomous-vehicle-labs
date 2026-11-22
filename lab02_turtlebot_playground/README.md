# Lab 2 — TurtleBot Playground

## Before you start — use the current course files

**Expected branch: `main`.** First-time user? Fork and clone using [Setup Part 6](../lab00_setup/README.md#part-6--fork-and-clone-the-course-repository). An old ZIP download or an unchanged fork may contain obsolete commands.

In Ubuntu/WSL, save all editor files and check:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git remote -v
git branch --show-current
git status --short
```

`origin` must be your GitHub fork; `upstream` must be `hoanbklucky/eel4332-autonomous-vehicle-labs`. The branch must match the expected name. **If the branch differs or status lists changes, stop here:** [save/commit your work and follow the branch/update guide](../docs/UPDATING_COURSE_REPOSITORY.md) before proceeding. Do not discard edits, especially robot Xacro/configuration changes or maps.

Once on the correct branch with a clean working tree:

```bash
git fetch upstream &&
git merge --no-edit upstream/main &&
git merge-base --is-ancestor upstream/main HEAD &&
echo "Current checkout includes the latest fetched main course commits"
git log -1 --oneline
```

Continue only after the inclusion check succeeds. Reopen **this local README** in VS Code (**WSL: Ubuntu**) and follow it. VS Code Sync or pulling your fork alone does not fetch instructor updates; push your combined commits to your fork after a successful update. A Git update changes files, not installed packages: rebuild only when this lab's setup says it is needed.

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

## Open in VS Code through WSL

After cloning the repository, open **Windows Terminal / PowerShell**, run `wsl`, then run these commands in **Ubuntu/WSL**:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
code .
```

Confirm VS Code shows **WSL: Ubuntu** (or your Ubuntu distribution) in the lower-left corner. Open `lab02_turtlebot_playground/README.md` in Explorer. Choose **Terminal → New Terminal**; when working from this lab directory, run:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs/lab02_turtlebot_playground
```

Use that Ubuntu terminal for the commands below; follow any later `cd` commands as written. This assumes VS Code is installed on Windows with the **WSL extension**. If the repository is not cloned yet, complete Lab 00's clone step first.

## Mission

Drive TurtleBot3 manually in Gazebo before studying modeling, SLAM, and navigation. Allow about 45–60 minutes after installation. Complete Lab 00 and Lab 1 first.

Use **VS Code's integrated terminal with the WSL: Ubuntu indicator**, or a separate **Ubuntu/WSL terminal**. Both work. Open additional VS Code terminals with **Terminal → New Terminal** or **+**. Run each long-running node in its own terminal.

Commands below are ready to copy: no leading `$` prompt is included. Keep dollar signs *inside* commands, such as `$PWD` and `$(...)`.

Use **Waffle in TurtleBot3 World** throughout. Before switching worlds, stop motion, stop teleoperation/SLAM/navigation, and press **Ctrl+C in the simulator launch terminal**. Wait for the processes to exit; closing the Gazebo window alone may leave the server running.


## 1. Install and verify

### Install packages (once; skip if the checks already pass)

Use an Ubuntu/WSL terminal, not PowerShell. Keep your existing Ubuntu 24.04, ROS 2 Jazzy, and working modern Gazebo installation. Stop old simulations. Use the system ROS terminal for building; if the course Python environment is active, run `deactivate` first.

```bash
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install git python3-colcon-common-extensions python3-rosdep ros-jazzy-ros-gz ros-jazzy-xacro ros-jazzy-cartographer ros-jazzy-cartographer-ros ros-jazzy-navigation2 ros-jazzy-nav2-bringup
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src
```

Download the official Jazzy sources. These commands preserve existing source directories:

```bash
for repository in DynamixelSDK turtlebot3_msgs turtlebot3 turtlebot3_simulations; do
  if [ ! -d "$repository" ]; then
    git clone -b jazzy "https://github.com/ROBOTIS-GIT/$repository.git"
  fi
  git -C "$repository" branch --show-current
done
```

Each branch check should print `jazzy`. If cloning fails or an existing directory is on another branch, stop and ask the instructor; do not delete it or clone duplicate packages elsewhere. `turtlebot3` supplies the core packages; **`turtlebot3_simulations` separately supplies `turtlebot3_gazebo`**.

Install workspace dependencies and build:

```bash
cd ~/turtlebot3_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install
```

If `rosdep` reports that it is not initialized, run `sudo rosdep init` once, then repeat `rosdep update` and the dependency command. Continue only after dependency installation and the build succeed. Do not use `sudo colcon build`.

Reload the environment **after building**:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 pkg prefix turtlebot3_gazebo
ros2 pkg prefix turtlebot3_teleop
ros2 pkg prefix turtlebot3_cartographer
ros2 pkg prefix turtlebot3_navigation2
```

Every check must print an installation path. Sourcing exposes built packages; it does not install missing ones. Robot software belongs in `~/turtlebot3_ws`; student code/results belong in your course fork.


## 2. Start the world — Terminal 1

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Leave this terminal running. Wait for Waffle to appear and confirm Gazebo is playing.

## 3. Drive — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 run turtlebot3_teleop teleop_keyboard
```

**Click inside Terminal 2 before pressing keys.** A model setting in Terminal 1 does not configure Terminal 2. If you see `KeyError: 'TURTLEBOT3_MODEL'`, rerun the export in the terminal launching teleop.

| Key | Effect |
|---|---|
| `w` / `x` | Increase/decrease linear velocity |
| `a` / `d` | Increase/decrease angular velocity |
| `s` or Space | Stop |
| Ctrl+C | Exit teleop |

Press keys a few times and watch the printed velocity values. Start slowly; forward motion persists until changed/stopped. Drive around two obstacles without contact, practice curves and in-place turns, then return near the start. Stop before switching windows.

## 4. Inspect feedback — Terminal 3

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 topic echo /odom --once
ros2 topic info /cmd_vel --verbose
```

Record the actual command type and publishers/subscribers. If key presses do not change teleop's printed velocity, check terminal focus. If values change but the robot does not move, confirm Gazebo is playing and inspect the command connections above.

## 5. Stop and restart

Press `s` in Terminal 2 and confirm zero motion. Press Ctrl+C in Terminal 2, then Terminal 1. Relaunch once to practice a clean reset.

Other optional worlds are `empty_world.launch.py` and `turtlebot3_house.launch.py`, launched from `turtlebot3_gazebo` **instead of** the world above. Keep only one world running. Use TurtleBot3 World for the assigned obstacle route and later mapping/navigation.

## What to Submit

A short driving video, Gazebo screenshot, and `answers.md` describing commands, command-message type, stopping/reset procedure, and observations.

## Questions

1. What does a velocity command specify, compared with a destination?
2. How does the robot turn in place?
3. What does odometry report?
4. What additional capabilities are needed for autonomous navigation?

## Troubleshooting

### Robot missing after relaunch: check leftover Gazebo processes

If the launch reports **Entity creation successful** but the Entity Tree has no `waffle`, and the log warns **Found additional publishers on /clock** or **/stats**, another simulation may still be running. This cleanup resolved that symptom on the instructor's WSL system.

1. Stop motion. Save any map/results you need, then press **Ctrl+C** in all simulator, teleoperation, SLAM, and navigation launch terminals.
2. In a separate Ubuntu/WSL terminal, inspect remaining Gazebo processes:

```bash
pgrep -af 'gz sim|gz-sim'
```

3. If the output lists leftover Gazebo processes and you intend to stop **all Gazebo simulations owned by your user**, run:

```bash
pkill -f 'gz sim'
pkill -f 'gz-sim'
pgrep -af 'gz sim|gz-sim'
```

No output from the final check means no matching processes remain. These commands close matching Gazebo servers/GUI processes, so use them only for cleanup, not during a trial you want to keep.

4. Relaunch **one** world:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Confirm `waffle` appears in Gazebo's Entity Tree before restarting teleoperation, SLAM, or navigation in separate sourced terminals. If the robot is still absent, capture the complete launch output rather than repeatedly launching more worlds.


## References

These procedures adapt the official **Jazzy** workflow, with explicit per-terminal environment setup:
- [ROBOTIS PC Setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup/?ros=jazzy)
- [ROBOTIS Gazebo Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy)
- [ROBOTIS SLAM Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy)
- [ROBOTIS Navigation Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/navigation_simulation/?ros=jazzy)

