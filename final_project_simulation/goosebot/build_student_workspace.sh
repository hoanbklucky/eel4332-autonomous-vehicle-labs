#!/usr/bin/env bash
# Configure and build the supplied Goosebot baseline; no Git commits or pushes.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -- "$script_dir/../.." && pwd -P)"
workspace="$HOME/goosebot_ws"
model_source="$repo_root/final_project_simulation/src/goosebot_0"
model_link="$workspace/src/goosebot_0"

if [[ -f "$repo_root/INSTRUCTOR_README.md" ]]; then
  echo "Use build_instructor_workspace.sh in the instructor checkout; this helper uses the student workspace." >&2
  exit 1
fi
if [[ ! -f "$model_source/package.xml" || ! -f "$model_source/CMakeLists.txt" ]]; then
  echo "Goosebot source is missing: $model_source" >&2
  echo "Copy/import the full source package using final-project Step 1, then retry." >&2
  exit 1
fi
for directory in scripts launch urdf config maps worlds; do
  if [[ ! -d "$model_source/$directory" ]]; then
    echo "Incomplete source: directory $directory is missing. Copy the full package from Step 1." >&2
    exit 1
  fi
done
model_source="$(readlink -f -- "$model_source")"
case "$model_source" in
  "$repo_root/"*) ;;
  *) echo "Model source resolves outside this student checkout: $model_source" >&2; exit 1 ;;
esac
for program in cmd_vel_to_odom.py ground_truth_map_odom_bridge.py stereo_camera_info_fixer.py; do
  if [[ ! -f "$model_source/scripts/$program" ]]; then
    echo "Incomplete source: scripts/$program is missing. Complete Step 1's source copy." >&2
    exit 1
  fi
done
mkdir -p "$workspace/src"
if [[ -e "$model_link" || -L "$model_link" ]]; then
  if [[ "$(readlink -f -- "$model_link" || true)" != "$(readlink -f -- "$model_source")" ]]; then
    echo "Existing workspace source points elsewhere: $model_link" >&2
    echo "Inspect it and preserve any edits before changing the link. Nothing was overwritten." >&2
    exit 1
  fi
else
  ln -s "$model_source" "$model_link"
fi
chmod +x "$model_source"/scripts/*.py
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo "ROS 2 Jazzy setup is missing. Complete the installation step first." >&2
  exit 1
fi
set +u
source /opt/ros/jazzy/setup.bash
set -u
cd "$workspace"
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
python3 "$script_dir/configure_goosebot.py" "$model_source"
colcon build --symlink-install --packages-select goosebot_0 --cmake-force-configure
set +u
source "$workspace/install/setup.bash"
set -u
prefix="$(ros2 pkg prefix goosebot_0)"
case "$prefix" in
  "$workspace/install"|"$workspace/install/"*) ;;
  *) echo "Unexpected package prefix: $prefix" >&2; exit 1 ;;
esac
for program in cmd_vel_to_odom.py ground_truth_map_odom_bridge.py stereo_camera_info_fixer.py; do
  if [[ ! -x "$prefix/lib/goosebot_0/$program" ]]; then
    echo "Installed executable still missing or not executable: $program" >&2
    exit 1
  fi
done
echo "Student workspace is built: $workspace"
readlink -f "$model_link"
ros2 pkg executables goosebot_0
echo "In every launch terminal, now run: source $workspace/install/setup.bash"
