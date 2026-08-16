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
check_cmd ros2 "ROS 2 CLI"
check_cmd gz "Gazebo CLI"
check_cmd rviz2 "RViz2"

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
fi

if command -v ros2 >/dev/null 2>&1; then
  distro="${ROS_DISTRO:-not-sourced}"
  echo "[INFO]    ROS_DISTRO=$distro"
fi

echo "---------------------------"
echo "OK: $ok   Missing: $missing"

if [ "$missing" -gt 0 ]; then
  exit 1
fi
