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

## 3. Gazebo check

```bash
gz sim shapes.sdf
```

If this fails, fix Gazebo before running a course lab.

## 4. ROS–Gazebo check

```bash
ros2 pkg list | grep ros_gz
```

If the required bridge or simulation package is missing, return to `lab00_setup/README.md`.

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
