#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo "ROS 2 Jazzy was not found at /opt/ros/jazzy." >&2
  exit 1
fi

source /opt/ros/jazzy/setup.bash

simulation_pid=""
bridge_pid=""

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "$bridge_pid" ]]; then
    kill "$bridge_pid" 2>/dev/null || true
  fi
  if [[ -n "$simulation_pid" ]]; then
    kill "$simulation_pid" 2>/dev/null || true
  fi
  wait "$bridge_pid" 2>/dev/null || true
  wait "$simulation_pid" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting the Nav2 TurtleBot 3 simulation..."
ros2 launch nav2_bringup tb3_simulation_launch.py \
  headless:=False autostart:=False &
simulation_pid=$!

sleep 2

echo "Starting the Gazebo-to-ROS TF bridge..."
ros2 run ros_gz_bridge parameter_bridge \
  '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V' &
bridge_pid=$!

echo "Keep this terminal open. Press Ctrl+C here to stop the simulation."
wait "$simulation_pid"
