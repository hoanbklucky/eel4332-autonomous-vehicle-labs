# Troubleshooting Guide

## 1. Identify the failing layer

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

## 2. ROS 2 checks

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

If `ros2` is not found in an Ubuntu terminal:

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

## 3. Gazebo check

```bash
gz sim shapes.sdf
```

If this fails, fix Gazebo before running a course lab.

To isolate course-world problems from TurtleBot/Nav2, run the Lab 00 practice world from the repository root:

```bash
gz sim -v 4 lab00_setup/worlds/gazebo_practice.sdf
```

Use `gz topic -l` and `gz service -l` to inspect the Gazebo Transport graph. Confirm that the world is playing and that `/clock` advances. Gazebo's GUI, simulation server, and Transport graph are related but distinct; a visible window alone does not prove that physics or topics are updating.

## 4. ROS–Gazebo check

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

## 5. TF checks

```bash
ros2 topic echo /tf --once
ros2 topic echo /tf_static --once
```

Use RViz2 to confirm that frames form a connected tree.

## 6. Sensor checks

For a numeric topic:

```bash
ros2 topic hz /TOPIC_NAME
ros2 topic echo /TOPIC_NAME --once
ros2 topic info /TOPIC_NAME
```

For image topics, use RViz2 or `rqt_image_view` when available.

## 7. Nav2 checks

Before debugging a planner/controller:

- verify TF
- verify odometry
- verify sensor data
- verify map
- verify localization pose
- only then debug Nav2

The Nav2 setup guide follows the same dependency order.

## 8. Student-code checks

Run:

```bash
python3 -m py_compile path/to/script.py
```

For pure Python labs, run unit tests before connecting the code to a simulator.

## 9. What to include when asking for help

Provide:

- exact command
- complete error message
- ROS distribution
- relevant topic list
- relevant controller/node list
- screenshot if GUI behavior matters
- the smallest code snippet that reproduces the issue
