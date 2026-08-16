# EEL 4332 Software Setup

## Goal

Prepare one consistent environment for the EEL 4332 simulation labs.

The recommended Windows workflow is:

```text
Windows 11
└── WSL2
    └── Ubuntu 24.04
        ├── ROS 2 Jazzy
        ├── Gazebo Harmonic
        ├── RViz2
        ├── Nav2
        ├── SLAM Toolbox
        ├── robot_localization
        └── Python tools
```

F1TENTH / RoboRacer Gym is installed separately for the vehicle-model and path-tracking activities.

---

## Part 1 — Install WSL2 and Ubuntu 24.04

From Windows PowerShell:

```powershell
wsl --install -d Ubuntu-24.04
```

After installation:

```powershell
wsl -l -v
```

Confirm that Ubuntu is using WSL version 2.

---

## Part 2 — Install ROS 2 Jazzy

Follow the official ROS 2 Jazzy Ubuntu Debian-package instructions:

https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

For this course, install the Desktop variant.

After installation:

```bash
source /opt/ros/jazzy/setup.bash
ros2 --help
```

Verify with the standard talker/listener examples.

To source ROS automatically:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

---

## Part 3 — Install ROS–Gazebo integration

```bash
sudo apt update
sudo apt install ros-jazzy-ros-gz
```

Test Gazebo:

```bash
gz sim shapes.sdf
```

Test ROS–Gazebo launch support:

```bash
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="shapes.sdf"
```

---

## Part 4 — Install navigation / localization packages

```bash
sudo apt update
sudo apt install \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-robot-localization
```

The exact demo-robot package used for Fall 2026 will be specified by the instructor.

**INSTRUCTOR VALIDATION REQUIRED:** test the final Nav2 demo launch on the course image before publishing a fixed command to students.

Official Nav2 setup guide:

https://docs.nav2.org/setup_guides/gazebo.html

---

## Part 5 — Create the course Python environment

In Ubuntu:

```bash
sudo apt install python3-venv python3-pip
python3 -m venv ~/venvs/eel4332
source ~/venvs/eel4332/bin/activate
python -m pip install --upgrade pip
```

From the repository root:

```bash
python -m pip install -r requirements.txt
```

Verify:

```bash
python -c "import numpy, matplotlib, yaml; print('Python dependencies OK')"
```

---

## Part 6 — F1TENTH / RoboRacer Gym

The official F1TENTH Gym repository is:

https://github.com/f1tenth/f1tenth_gym

The official organization also maintains course lab repositories:

https://github.com/f1tenth/f1tenth_labs_openrepo

For Fall 2026, use the **course-pinned installation instructions supplied by the instructor** rather than blindly mixing old ROS/F1TENTH tutorials with Jazzy.

Why: some public F1TENTH ROS bridge documentation was originally written for older ROS 2 distributions.

**INSTRUCTOR VALIDATION REQUIRED:** pin the exact Gym commit / Python environment after testing Lab 02 and Lab 06 on the instructor machine.

Lab 02 can still be completed using the repository's pure-Python bicycle model if the F1TENTH environment is unavailable.

---

## Part 7 — Clone this repository

Example:

```bash
mkdir -p ~/courses
cd ~/courses
git clone <COURSE_REPOSITORY_URL>
cd eel4332-autonomous-vehicle-labs
```

---

## Part 8 — Run the verification script

```bash
chmod +x Lab00_setup/verify_installation.sh
./Lab00_setup/verify_installation.sh
```

Fix any required item marked `MISSING` before starting Lab 01.

---

## Part 9 — Goosebot

Do **not** install Goosebot-specific dependencies during the first week unless instructed.

The final physical deployment will use:

https://github.com/hoanbklucky/goose

The instructor will provide the final ROS 2 branch/package names and network/hardware configuration before the physical-robot project.

---

# Setup Success Criteria

Before Lab 01, you should be able to:

- [ ] run `ros2 --help`
- [ ] run `gz sim shapes.sdf`
- [ ] launch Gazebo through `ros_gz_sim`
- [ ] open RViz2
- [ ] import NumPy and Matplotlib
- [ ] clone and edit this repository
