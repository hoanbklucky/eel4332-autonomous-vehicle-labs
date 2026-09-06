# Troubleshooting Guide

## Identify the failing layer

Troubleshoot from the bottom up:

```text
Ubuntu / WSL
    ↓
ROS 2
    ↓
Gazebo
    ↓
ROS–Gazebo bridge / simulation
    ↓
topics + TF
    ↓
student node
    ↓
algorithm
```

Do not debug all layers at once.

## Git and VS Code checks

Run Git from a WSL/Ubuntu Terminal for this course:

```bash
git --version
which git
git config --global --get user.name
git config --global --get user.email
```

**Command breakdown:** `git --version` verifies Git, `which git` locates its executable, and the two `git config --global --get` commands display the identity saved for commits.

If `git` is missing, install it with `sudo apt install git`. If the identity commands print nothing, return to Part 2 of [`../lab00_setup/README.md`](../lab00_setup/README.md).

VS Code should be installed on Windows and connected using Microsoft's WSL extension. From a WSL/Ubuntu Terminal, run:

```bash
code --version
code .
```

**Command breakdown:** `code --version` verifies the VS Code command, and `code .` opens the current WSL directory as a VS Code workspace.

Confirm the lower-left VS Code indicator names WSL and that the integrated WSL/Ubuntu Terminal's `pwd` is a Linux path. Do not install a separate Linux copy of VS Code inside WSL. If `code` is not found, confirm the Windows installation added VS Code to PATH, install the WSL extension, and reopen the WSL/Ubuntu Terminal.

## ROS 2 checks

```bash
echo $ROS_DISTRO
ros2 --help
ros2 topic list
ros2 node list
```

**Command breakdown:** `echo $ROS_DISTRO` prints the sourced distribution. `ros2 --help` checks the CLI, while the two `list` commands query discoverable topics and nodes.

Expected ROS distribution:

```text
jazzy
```

If `ros2` is not found in a WSL/Ubuntu Terminal:

```bash
source /opt/ros/jazzy/setup.bash
```

**Command breakdown:** `source` loads the ROS 2 Jazzy environment into only the current terminal.

If ROS works but the Lab 1 practice package is not found, source the workspace overlay after the base installation:

```bash
source /opt/ros/jazzy/setup.bash
source ~/eel4332_ws/install/setup.bash
ros2 pkg prefix eel4332_ros_practice
```

**Command breakdown:** The first `source` loads the Jazzy underlay and the second loads the workspace overlay. `ros2 pkg prefix` prints where ROS found the practice package.

If the package is still missing, return to the workspace build steps in [ROS 2 Fundamentals — Part 2](../lab01_ros2_gazebo_fundamentals/ros2_fundamentals_part2.md). Do not source another workspace merely to hide a failed build.

## Gazebo check

```bash
gz sim shapes.sdf
```

**Command breakdown:** `gz sim` launches Gazebo Sim with its installed `shapes.sdf` example world.

If this fails, fix Gazebo before running a course lab.

To isolate course-world problems from TurtleBot/Nav2, run the Lab 1 practice world from the repository root:

```bash
gz sim -v 4 lab01_ros2_gazebo_fundamentals/worlds/gazebo_practice.sdf
```

**Command breakdown:** `gz sim` starts Gazebo, `-v 4` enables detailed logging, and the last argument identifies the course SDF world.

Use `gz topic -l` and `gz service -l` to inspect the Gazebo Transport graph. Confirm that the world is playing and that `/clock` advances. Gazebo's GUI, simulation server, and Transport graph are related but distinct; a visible window alone does not prove that physics or topics are updating.

## ROS–Gazebo check

```bash
ros2 pkg list | grep ros_gz
```

**Command breakdown:** The pipe sends the installed ROS package list to `grep`, which keeps package names containing `ros_gz`.

If the required bridge or simulation package is missing, return to `lab00_setup/README.md`.

Gazebo Transport and ROS 2 are separate graphs. Compare them directly:

```bash
gz topic -l
ros2 topic list
```

**Command breakdown:** `gz topic -l` lists Gazebo Transport topics, while `ros2 topic list` lists the separate ROS 2 topics.

If a value exists only in Gazebo, verify that the launch file or an explicit `ros_gz_bridge` process bridges its topic and supported message type. Use the [Lab 1 Gazebo practice](../lab01_ros2_gazebo_fundamentals/gazebo_fundamentals.md) to test a simple `/clock` bridge before debugging a robot-specific bridge.

## TF checks

```bash
ros2 topic echo /tf --once
ros2 topic echo /tf_static --once
```

**Command breakdown:** Each `ros2 topic echo` command captures one transform message because `--once` exits after the first sample.

Use RViz2 to confirm that frames form a connected tree.

## Sensor checks

For a numeric topic:

```bash
ros2 topic hz /TOPIC_NAME
ros2 topic echo /TOPIC_NAME --once
ros2 topic info /TOPIC_NAME
```

**Command breakdown:** Replace `/TOPIC_NAME` with the real topic. `topic hz` measures rate, `topic echo --once` captures one message, and `topic info` reports its type and endpoints.

For image topics, use RViz2 or launch the installed image viewer:

```bash
ros2 run rqt_image_view rqt_image_view
```

**Command breakdown:** `ros2 run PACKAGE EXECUTABLE` starts the `rqt_image_view` executable from its package so you can select and view an image topic.

## Nav2 checks

Before debugging a planner/controller:

- verify TF
- verify odometry
- verify sensor data
- verify map
- verify localization pose
- only then debug Nav2

The Nav2 setup guide follows the same dependency order.

## Student-code checks

Run:

```bash
python3 -m py_compile path/to/script.py
```

**Command breakdown:** `python3 -m py_compile` checks the named Python file for syntax errors without running the lab algorithm; replace the placeholder path with the actual script.

For pure Python labs, run unit tests before connecting the code to a simulator.

## What to include when asking for help

Provide:

- exact command
- complete error message
- ROS distribution
- relevant topic list
- relevant controller/node list
- screenshot if GUI behavior matters
- the smallest code snippet that reproduces the issue
