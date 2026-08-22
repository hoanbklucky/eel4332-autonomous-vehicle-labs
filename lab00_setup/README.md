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

F1TENTH / RoboRacer Gym is optional and is not required to begin the course. The required simulation environment uses TurtleBot 3 in Gazebo.

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
A Gazebo window look like the below will open
![alt text](gz_sim_shapes.png)

Press Ctrl + C to close the window.

Test ROS–Gazebo launch support:

```bash
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="shapes.sdf"
```
The same window opens.

---

## Part 4 — Install navigation / localization packages

```bash
sudo apt update
sudo apt install \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-minimal-tb3-sim \
  ros-jazzy-slam-toolbox \
  ros-jazzy-robot-localization
```


Official Nav2 setup guide:

https://docs.nav2.org/setup_guides/gazebo.html

Official TurtleBot 3 learning references:

- [TurtleBot 3 Gazebo simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy)
- [TurtleBot 3 SLAM simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/slam_simulation/?ros=jazzy)

These ROBOTIS pages are useful for learning the usual simulation sequence: launch a world, move the robot, visualize its data, run SLAM, and save a map. They use the ROBOTIS `turtlebot3_gazebo` package workflow, while the first course labs use the installed `nav2_bringup` and `nav2_minimal_tb3_sim` packages. Do not clone another TurtleBot workspace or substitute ROBOTIS launch commands for course commands unless the instructor asks you to do so. Also confirm that the **Jazzy** tab is selected before using a command from the website.

---

## Part 5 — Clone this repository and enter its root

Run these commands in Ubuntu/WSL:

```bash
mkdir -p ~/courses
cd ~/courses
git clone https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs.git
cd eel4332-autonomous-vehicle-labs
```

If you already cloned the repository, do not clone it again. Enter the existing copy instead:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
```

The **repository root** is the `eel4332-autonomous-vehicle-labs` directory that contains the top-level `README.md`, `requirements.txt`, `lab00_setup/`, and the other lab directories. Confirm your current location:

```bash
pwd
ls
```

`pwd` should end with `/eel4332-autonomous-vehicle-labs`, and the `ls` output should include `requirements.txt`. If you cloned the repository somewhere other than `~/courses`, use that location in the `cd` command.

---

## Part 6 — Create the course Python environment

### Why use a virtual environment?

A Python virtual environment gives this course its own location for packages installed with `pip`. This provides several benefits:

- course packages do not overwrite Ubuntu or ROS 2 system packages;
- different projects can use different package versions;
- students can reproduce a known set of dependencies from `requirements.txt`;
- packages can be installed without `sudo`, reducing the risk of damaging the system Python installation.

The environment isolates packages installed by `pip`; it does not contain a second installation of ROS 2. ROS packages from `/opt/ros/jazzy` remain available when the ROS setup file is sourced. This is why the course environment also installs a few Python helpers required by ROS-visible packages.

After activation, the terminal prompt normally begins with `(eel4332)`, and `python` and `pip` refer to the course environment. Run `deactivate` to return to the normal system environment. If you open a new terminal, activate the environment again before running the pure-Python lab programs:

```bash
source ~/venvs/eel4332/bin/activate
```

In Ubuntu:

```bash
sudo apt install python3-venv python3-pip
python3 -m venv ~/venvs/eel4332
source ~/venvs/eel4332/bin/activate
python -m pip install --upgrade pip setuptools
```

Make sure you are still at the repository root established in Part 5, then run:

```bash
python -m pip install -r requirements.txt
```

The command is successful when it ends with `Successfully installed` or reports that all requirements are already satisfied.

If an older copy of this repository reports that ROS packages such as `generate-parameter-library-py` or `launch-ros` require `setuptools`, `jinja2`, or `typeguard`, update the repository and run the requirements command again:

```bash
git pull
python -m pip install -r requirements.txt
```

Those messages come from ROS 2 Python packages exposed by `/opt/ros/jazzy/setup.bash`. The updated requirements install the corresponding helpers inside the isolated course environment. Do not use `sudo pip` and do not delete the ROS installation.

Verify:

```bash
python -c "import numpy, matplotlib, yaml; print('Python dependencies OK')"
python -c "import setuptools, jinja2, typeguard; print('ROS Python helpers OK')"
python -m pip check
```

All three verification commands should complete without dependency-conflict messages. Use `deactivate` when you want to leave the course Python environment.

---

## Part 7 — Optional F1TENTH / RoboRacer Gym

The official F1TENTH Gym repository is:

https://github.com/f1tenth/f1tenth_gym

The official organization also maintains course lab repositories:

https://github.com/f1tenth/f1tenth_labs_openrepo


Lab 02 can still be completed using the repository's pure-Python bicycle model if the F1TENTH environment is unavailable.

---

## Part 8 — Run the verification script

```bash
chmod +x lab00_setup/verify_installation.sh
./lab00_setup/verify_installation.sh
```

Fix any required item marked `MISSING` before starting Lab 01.

---

## Part 9 — Goosebot

Do **not** install Goosebot-specific dependencies during the first week unless instructed.

The final physical deployment will use:

https://github.com/hoanbklucky/goose

The instructor will provide the final ROS 2 branch/package names and network/hardware configuration before the physical-robot project.

Goosebot is a four-wheel skid-steer robot. It has four conventional wheels, each powered by a DC motor, with fixed parallel wheel axes and no geometric steering linkage. Turning requires different left- and right-side wheel velocities and lateral tire slip. Before deployment, the instructor must document how motion commands are mapped to the four motors. The TurtleBot simulation is not an exact Goosebot model; it is used to exercise the ROS 2 autonomy layers before the physical interface is introduced.

---

# Setup Success Criteria

Before Lab 01, you should be able to:

- [ ] run `ros2 --help`
- [ ] run `gz sim shapes.sdf`
- [ ] launch Gazebo through `ros_gz_sim`
- [ ] open RViz2
- [ ] import NumPy and Matplotlib
- [ ] clone and edit this repository
