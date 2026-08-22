#!/usr/bin/env bash
set -u

ok=0
missing=0

check_cmd () {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf "[OK]      %s\n" "$label"
    ok=$((ok+1))
  else
    printf "[MISSING] %s\n" "$label"
    missing=$((missing+1))
  fi
}

echo "EEL 4332 setup verification"
echo "---------------------------"

check_cmd python3 "Python 3"
check_cmd git "Git"
check_cmd code "VS Code WSL command"
check_cmd ros2 "ROS 2 CLI"
check_cmd gz "Gazebo CLI"
check_cmd rviz2 "RViz2"
check_cmd colcon "colcon build tool"
check_cmd rosdep "rosdep"
check_cmd rqt_graph "rqt_graph"

if command -v git >/dev/null 2>&1; then
  git_name="$(git config --global --get user.name 2>/dev/null || true)"
  git_email="$(git config --global --get user.email 2>/dev/null || true)"
  if [ -n "$git_name" ] && [ -n "$git_email" ]; then
    echo "[OK]      Git user.name / user.email"
    ok=$((ok+1))
  else
    echo "[MISSING] Git user.name / user.email"
    missing=$((missing+1))
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  if python3 - <<'PY' >/dev/null 2>&1
import numpy, matplotlib, yaml
PY
  then
    echo "[OK]      NumPy / Matplotlib / PyYAML"
    ok=$((ok+1))
  else
    echo "[MISSING] NumPy / Matplotlib / PyYAML"
    missing=$((missing+1))
  fi

  if python3 - <<'PY' >/dev/null 2>&1
import setuptools, jinja2, typeguard
PY
  then
    echo "[OK]      ROS Python helpers"
    ok=$((ok+1))
  else
    echo "[MISSING] setuptools / Jinja2 / typeguard"
    missing=$((missing+1))
  fi
fi

if command -v ros2 >/dev/null 2>&1; then
  distro="${ROS_DISTRO:-not-sourced}"
  echo "[INFO]    ROS_DISTRO=$distro"

  for pkg in demo_nodes_py turtlesim rqt_image_view teleop_twist_keyboard rosbag2_transport ros_gz_bridge ros_gz_sim eel4332_ros_practice; do
    if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
      echo "[OK]      ROS package: $pkg"
      ok=$((ok+1))
    else
      echo "[MISSING] ROS package: $pkg"
      missing=$((missing+1))
    fi
  done
fi

if command -v rosdep >/dev/null 2>&1; then
  if rosdep resolve rclpy >/dev/null 2>&1; then
    echo "[OK]      rosdep initialized"
    ok=$((ok+1))
  else
    echo "[MISSING] rosdep initialization/update"
    missing=$((missing+1))
  fi
fi

if [ -f "lab00_setup/worlds/gazebo_practice.sdf" ]; then
  echo "[OK]      Gazebo practice world"
  ok=$((ok+1))
else
  echo "[MISSING] Run this script from the repository root"
  missing=$((missing+1))
fi

echo "---------------------------"
echo "OK: $ok   Missing: $missing"

if [ "$missing" -gt 0 ]; then
  exit 1
fi
