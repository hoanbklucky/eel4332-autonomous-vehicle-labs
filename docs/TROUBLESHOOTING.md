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

If `git` is missing, install it with `sudo apt install git`. If the identity commands print nothing, return to Part 2 of [`../lab00_setup/README.md`](../lab00_setup/README.md).

VS Code should be installed on Windows and connected using Microsoft's WSL extension. From a WSL/Ubuntu Terminal, run:

```bash
code --version
code .
```

Confirm the lower-left VS Code indicator names WSL and that the integrated WSL/Ubuntu Terminal's `pwd` is a Linux path. Do not install a separate Linux copy of VS Code inside WSL. If `code` is not found, confirm the Windows installation added VS Code to PATH, install the WSL extension, and reopen the WSL/Ubuntu Terminal.

## ROS 2 checks

```bash
echo $ROS_DISTRO
ros2 --help
ros2 topic list
ros2 node list
```

Expected ROS distribution:

```text
jazzy
```

If `ros2` is not found in a WSL/Ubuntu Terminal:

```bash
source /opt/ros/jazzy/setup.bash
```

If ROS works but the Lab 00 practice package is not found, source the workspace overlay after the base installation:

```bash
source /opt/ros/jazzy/setup.bash
source ~/eel4332_ws/install/setup.bash
ros2 pkg prefix eel4332_ros_practice
```

If the package is still missing, return to the workspace build steps in [`../lab00_setup/ros2_fundamentals.md`](../lab00_setup/ros2_fundamentals.md). Do not source another workspace merely to hide a failed build.

## Gazebo check

```bash
gz sim shapes.sdf
```

If this fails, fix Gazebo before running a course lab.

To isolate course-world problems from TurtleBot/Nav2, run the Lab 00 practice world from the repository root:

```bash
gz sim -v 4 lab00_setup/worlds/gazebo_practice.sdf
```

Use `gz topic -l` and `gz service -l` to inspect the Gazebo Transport graph. Confirm that the world is playing and that `/clock` advances. Gazebo's GUI, simulation server, and Transport graph are related but distinct; a visible window alone does not prove that physics or topics are updating.

## ROS–Gazebo check

```bash
ros2 pkg list | grep ros_gz
```

If the required bridge or simulation package is missing, return to `lab00_setup/README.md`.

Gazebo Transport and ROS 2 are separate graphs. Compare them directly:

```bash
gz topic -l
ros2 topic list
```

If a value exists only in Gazebo, verify that the launch file or an explicit `ros_gz_bridge` process bridges its topic and supported message type. Use the [Lab 00 Gazebo practice](../lab00_setup/gazebo_fundamentals.md) to test a simple `/clock` bridge before debugging a robot-specific bridge.

## TF checks

```bash
ros2 topic echo /tf --once
ros2 topic echo /tf_static --once
```

Use RViz2 to confirm that frames form a connected tree.

## Sensor checks

For a numeric topic:

```bash
ros2 topic hz /TOPIC_NAME
ros2 topic echo /TOPIC_NAME --once
ros2 topic info /TOPIC_NAME
```

For image topics, use RViz2 or launch the installed image viewer:

```bash
ros2 run rqt_image_view rqt_image_view
```

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
