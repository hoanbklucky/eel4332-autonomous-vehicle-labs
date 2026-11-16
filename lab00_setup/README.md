# EEL 4332 Software Setup

## Before you start — obtain the current repository

**Expected branch: `main`.** This is the current `main` assignment. **New students:** install Git in Part 2, then complete [Part 6 — Fork and clone](#part-6--fork-and-clone-the-course-repository) before running repository-dependent commands. Until then, read setup on GitHub; `code .` opens existing files but does not download them. **Already have a copy?** Save your edits, then use [the update guide](../docs/UPDATING_COURSE_REPOSITORY.md) before continuing. Fetch the instructor updates for this branch; a clean status or up-to-date fork alone is insufficient.

## Open in VS Code through WSL

After cloning the repository, open **Windows Terminal / PowerShell**, run `wsl`, then run these commands in **Ubuntu/WSL**:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
code .
```

Confirm VS Code shows **WSL: Ubuntu** (or your Ubuntu distribution) in the lower-left corner. Open `lab00_setup/README.md` in Explorer. Choose **Terminal → New Terminal**; when working from this lab directory, run:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs/lab00_setup
```

Use that Ubuntu terminal for the commands below; follow any later `cd` commands as written. This assumes VS Code is installed on Windows with the **WSL extension**. If the repository is not cloned yet, complete Lab 00's clone step first.

> **Copying ROBOTIS commands:** A leading `$` is a terminal-prompt symbol, not part of the command. Some copy buttons include it. Copy only the command after `$ `, or paste into the editor first and remove that prefix from each command line. For example, `$ sudo apt update` must be entered as:
>
> ```bash
> sudo apt update
> ```
>
> If you see `$: command not found`, remove the leading `$ ` and rerun. **Keep dollar signs inside commands**, such as `$HOME`, `$PWD`, `${TURTLEBOT3_MODEL}`, and `$(...)`; those have a different meaning.


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
        ├── Cartographer
        ├── TurtleBot3 packages
        └── Python tools
```

F1TENTH / RoboRacer Gym is optional and is not required to begin the course. The required simulation environment uses TurtleBot 3 in Gazebo.

## Background

Autonomous-vehicle software spans several layers. Ubuntu provides the operating environment; ROS 2 connects software components; Gazebo simulates a physical world and sensors; RViz2 visualizes ROS data; and Nav2 supplies localization, planning, and navigation components. Installing the programs is only the first step—students must also learn how to inspect each layer and the interfaces between them.

Lab 00 installs and verifies those tools. [Lab 1](../lab01_ros2_gazebo_fundamentals/README.md) teaches ROS 2 and Gazebo through small systems, [Lab 2](../lab02_turtlebot_playground/README.md) provides a low-pressure TurtleBot driving playground, Lab 3 models the motion students observed, and Lab 4 introduces mapping and Lab 5 introduces saved-map Nav2 navigation using official ROBOTIS tutorials.

Resolve missing prerequisites now; otherwise a later algorithm problem can be confused with an installation or environment problem.

### Setup progression and visible checkpoints

| Stage | Why you do it | Visible checkpoint before continuing |
|---|---|---|
| Establish the Linux environment | ROS 2 and the course tools run inside Ubuntu/WSL | An Ubuntu prompt opens and reports the expected distribution version. |
| Install development tools | Git and VS Code provide the course editing workflow | Git reports a version and VS Code opens the repository through WSL. |
| Install ROS 2 and Gazebo | These provide robot communication and simulation | ROS commands are discovered and a Gazebo window opens. |
| Clone and prepare the course repository | Students need a known location and Python environment | The repository root is visible and the course environment activates. |
| Run the verification script | One repeatable test checks the complete setup | Every required check reports success, or a specific failed layer is identified. |

Treat each checkpoint as evidence, not just a command to type. If a checkpoint fails, stop there and fix that layer before installing or testing the next one.

## WSL/Ubuntu Terminal Shortcuts

You do not need to retype every long path or command. Bash, the shell used by the WSL/Ubuntu Terminal, provides shortcuts that reduce typing and mistakes.

### Complete names with Tab

Type the beginning of a command, folder, or filename and press `Tab`. Bash completes the name when there is one match. If several names match, type another character or press `Tab` twice to list the choices.

For example, the following keystrokes can complete the course repository path. Do not type the text `<Tab>`; press the `Tab` key at those positions.

```text
cd ~/cou<Tab>/eel4332<Tab>
```

Tab completion works only for names that already exist, which also makes it a useful check for misspelled paths.

### Reuse and edit previous commands

| Key or command | What it does |
|---|---|
| `Up Arrow` / `Down Arrow` | move backward or forward through commands already entered |
| `Ctrl+R` | search backward through command history; type part of a command and press `Ctrl+R` again for an older match |
| `Ctrl+A` / `Ctrl+E` | move the cursor to the beginning or end of the current command |
| `Alt+B` / `Alt+F` | move backward or forward by one word |
| `Ctrl+W` | delete the word immediately before the cursor |
| `Ctrl+U` / `Ctrl+K` | delete from the cursor to the beginning or end of the line |
| `Ctrl+L` | clear the visible terminal while keeping command history |
| `Ctrl+C` | cancel the current command or stop a running ROS/Gazebo process |
| `history` | display numbered commands from the current shell's history |

When using `Ctrl+R`, inspect the matched command before running it. Press `Enter` to execute it, use an arrow key to leave the search and edit it, or press `Ctrl+C` to cancel the search.

### Move among common directories

| Command | Destination |
|---|---|
| `cd ~` | your Ubuntu home directory |
| `cd ..` | the parent of the current directory |
| `cd -` | the previous directory |
| `pwd` | prints the current directory instead of changing it |
| `ls` | lists files and folders in the current directory |

Use `pwd` and `ls` whenever you are unsure where you are, and use Tab completion before pressing `Enter` on a long path.

## Required Software

| Component | Where it is installed | Course use |
|---|---|---|
| WSL2 + Ubuntu 24.04 | Windows / WSL | Linux environment for all course commands |
| Git | inside Ubuntu/WSL | clone, update, and track lab work |
| VS Code | Windows | course-supported editor |
| Microsoft WSL extension | VS Code on Windows | opens and runs tools inside Ubuntu/WSL |
| Microsoft Python extension | VS Code WSL environment | Python editing, interpreter selection, and debugging |
| ROS 2 Jazzy Desktop | inside Ubuntu/WSL | robot middleware and visualization |
| Gazebo Harmonic through `ros_gz` | inside Ubuntu/WSL | physics and sensor simulation |
| Nav2, SLAM Toolbox, and localization packages | inside Ubuntu/WSL | later navigation labs |
| Python virtual environment and requirements | inside Ubuntu/WSL | numerical lab dependencies |

F1TENTH/RoboRacer and Goosebot software are not required for the initial setup.

---

## Part 1 — Install WSL2 and Ubuntu 24.04

**Why this part matters:** ROS 2 and Gazebo are Linux tools; WSL2 gives Windows users the consistent Ubuntu environment used throughout the course.

From Windows PowerShell:

```powershell
wsl --install -d Ubuntu-24.04
```

**Command breakdown:** `wsl --install` installs a WSL distribution, and `-d Ubuntu-24.04` selects Ubuntu 24.04 rather than the default distribution.

After installation:

```powershell
wsl -l -v
```

**Command breakdown:** `wsl -l` lists installed WSL distributions, while `-v` adds their state and WSL version. Ubuntu should report version `2`.

Confirm that Ubuntu is using WSL version 2.

**Terminal terminology used throughout this repository:** a **WSL/Ubuntu Terminal** means a shell whose prompt is running inside Ubuntu. It may be an Ubuntu tab in the Windows Terminal application, the Ubuntu application, or VS Code's integrated terminal after VS Code connects to WSL. It does **not** mean a PowerShell or Command Prompt tab.

---

## Part 2 — Install Git and Visual Studio Code

**Why this part matters:** Git delivers course files and updates, while VS Code with WSL lets you edit and run those Linux files from one workspace.

### Install and configure Git inside Ubuntu/WSL

Git downloads the course repository, records changes to your work, and obtains instructor updates. Install Git inside Ubuntu because the course commands and repository live in the WSL environment:

```bash
sudo apt update
sudo apt install git
git --version
which git
```

**Command breakdown:** `sudo apt update` refreshes Ubuntu's package index, `sudo apt install git` installs Git, `git --version` verifies it, and `which git` shows the executable being used.

`which git` should normally print `/usr/bin/git`. Configure the identity attached to your commits, replacing the examples with your real information:

```bash
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
git config --global --get user.name
git config --global --get user.email
```

**Command breakdown:** `git config --global` stores identity settings for your Ubuntu user. The `--get` commands read the saved values so you can verify them; replace the example name and email with your own.

Use an email associated with GitHub or your GitHub-provided private `noreply` address. The name and email identify commits; they are not your GitHub password and do not authenticate `git push`.

If Git is also installed on Windows, it has a separate configuration. For this course, run Git commands from Ubuntu/WSL so paths, permissions, and line endings stay consistent with ROS 2.

### Install VS Code on Windows and connect it to WSL

VS Code is the course-supported editor. Install the graphical application on **Windows**, not inside Ubuntu/WSL:

1. Download and install [Visual Studio Code for Windows](https://code.visualstudio.com/download).
2. During installation, enable **Add to PATH** when offered.
3. Open VS Code and install the **WSL** extension published by Microsoft.
4. Close and reopen the WSL/Ubuntu Terminal so it receives the updated Windows PATH.

Test the connection from a WSL/Ubuntu Terminal:

```bash
code --version
mkdir -p ~/courses
cd ~/courses
code .
```

**Command breakdown:** `code --version` verifies the VS Code command, `mkdir -p` creates `~/courses` if needed, `cd` enters it, and `code .` opens the current directory in VS Code through WSL.

VS Code should open with an indicator such as **WSL: Ubuntu-24.04** in the lower-left corner. Open **Terminal → New Terminal** inside VS Code to create an integrated WSL/Ubuntu Terminal, then run:

```bash
pwd
uname -a
```

**Command breakdown:** `pwd` prints the directory opened by VS Code, and `uname -a` displays Linux system information. Seeing Linux output confirms that the terminal is connected to WSL/Ubuntu.

The integrated WSL/Ubuntu Terminal should show a Linux path and identify Linux/WSL. If VS Code opens the folder locally on Windows instead, use the lower-left remote indicator and select **Connect to WSL**, then reopen the folder.

### Install the Microsoft Python extension in WSL

The Python extension adds syntax checking, code completion, interpreter selection, the **Run Python File** button, and debugging. It is useful for the Python labs, but it does not install Python itself. A `.py` file can still be run from a WSL/Ubuntu Terminal with the `python` command after the course environment is created in Part 7.

Install the extension while VS Code is connected to WSL:

1. Confirm that **WSL: Ubuntu-24.04** appears in the lower-left corner of VS Code.
2. Open **Extensions** from the Activity Bar, or press **Ctrl+Shift+X**.
3. Search for `@id:ms-python.python`.
4. Select **Python**, published by **Microsoft**. Do not choose one of the similarly named third-party extensions.
5. Select **Install in WSL: Ubuntu-24.04** if that button appears. If the button says **Uninstall**, the extension is already installed.
6. Confirm that the extension page says it is enabled in the **Remote Extension Host**. This means it runs where the course files and Python interpreter are located: inside WSL.

You will select the course interpreter after creating it in Part 7.

Keep course repositories in the Linux filesystem, such as `~/courses`, rather than under `/mnt/c`, unless the instructor directs otherwise.

Official references:

- [Developing in WSL with VS Code](https://code.visualstudio.com/docs/remote/wsl)
- [Git installation for Linux](https://git-scm.com/install/linux)
- [First-time Git configuration](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup)

---

## Part 3 — Install ROS 2 Jazzy

**Why this part matters:** ROS 2 provides the command-line tools, communication middleware, and software packages used by every later robotics lab.

Follow the official ROS 2 Jazzy Ubuntu Debian-package instructions:

https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

For this course, install the Desktop variant.

Install the beginner examples and ROS development tools used in Lab 1 and later labs:

```bash
sudo apt update
sudo apt install \
  ros-jazzy-demo-nodes-py \
  ros-jazzy-turtlesim \
  ros-jazzy-rqt-graph \
  ros-jazzy-rqt-image-view \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-rosbag2 \
  python3-colcon-common-extensions \
  python3-rosdep
```

**Command breakdown:** `apt update` refreshes package information and `apt install` installs the listed ROS utilities. Each trailing `\` continues the same command on the next displayed line.

After installation:

```bash
source /opt/ros/jazzy/setup.bash
ros2 --help
```

**Command breakdown:** `source` loads ROS 2 Jazzy into the current terminal environment. `ros2 --help` then verifies the CLI and lists its command groups.

Initialize `rosdep`, which later resolves ROS package dependencies:

```bash
sudo rosdep init
rosdep update
```

**Command breakdown:** `sudo rosdep init` creates the system-wide rosdep configuration and is normally run once per Ubuntu installation. `rosdep update` downloads the current dependency database for your user.

Run `sudo rosdep init` only once. If it reports that the default sources list already exists, leave that file in place and continue with `rosdep update`.

Lab 1 provides guided ROS 2 and Gazebo exercises, and Lab 2 provides manual TurtleBot practice before students model its motion in Lab 3 and use SLAM in Lab 4 and Nav2 in Lab 5.

To source ROS automatically:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

**Command breakdown:** `echo` produces the source command, `>>` appends it to `~/.bashrc`, and Bash reads that file for future interactive terminals. Do not repeat this command unnecessarily, or duplicate lines will be added.

---

## Part 4 — Install ROS–Gazebo integration

**Why this part matters:** Gazebo simulates the physical world, while the integration packages let ROS 2 programs exchange data with that simulation.

```bash
sudo apt update
sudo apt install ros-jazzy-ros-gz
```

**Command breakdown:** `apt update` refreshes package information, and `apt install ros-jazzy-ros-gz` installs the ROS 2 Jazzy packages that integrate modern Gazebo with ROS.

Test Gazebo:

```bash
gz sim shapes.sdf
```

**Command breakdown:** `gz sim` starts Gazebo Sim, and `shapes.sdf` selects Gazebo's installed example world.
A Gazebo window look like the below will open
![alt text](gz_sim_shapes.png)

Press Ctrl + C to close the window.

Test ROS–Gazebo launch support:

```bash
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="shapes.sdf"
```

**Command breakdown:** `ros2 launch PACKAGE FILE` starts `gz_sim.launch.py` from `ros_gz_sim`. The launch argument `gz_args:="shapes.sdf"` passes the example world name to Gazebo.
The same window opens.

---

## Part 5 — Install TurtleBot3 software

The commands below include the required ROBOTIS Jazzy setup. PC/core packages and simulation sources are separate downloads; both are included. Hardware SBC/OpenCR setup is not needed.

### Install packages (once; skip if the checks already pass)

Use an Ubuntu/WSL terminal, not PowerShell. Keep your existing Ubuntu 24.04, ROS 2 Jazzy, and working modern Gazebo installation. Stop old simulations. Use the system ROS terminal for building; if the course Python environment is active, run `deactivate` first.

```bash
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install git python3-colcon-common-extensions python3-rosdep ros-jazzy-ros-gz ros-jazzy-xacro ros-jazzy-cartographer ros-jazzy-cartographer-ros ros-jazzy-navigation2 ros-jazzy-nav2-bringup
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src
```

Download the official Jazzy sources. These commands preserve existing source directories:

```bash
for repository in DynamixelSDK turtlebot3_msgs turtlebot3 turtlebot3_simulations; do
  if [ ! -d "$repository" ]; then
    git clone -b jazzy "https://github.com/ROBOTIS-GIT/$repository.git"
  fi
  git -C "$repository" branch --show-current
done
```

Each branch check should print `jazzy`. If cloning fails or an existing directory is on another branch, stop and ask the instructor; do not delete it or clone duplicate packages elsewhere. `turtlebot3` supplies the core packages; **`turtlebot3_simulations` separately supplies `turtlebot3_gazebo`**.

Install workspace dependencies and build:

```bash
cd ~/turtlebot3_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
colcon build --symlink-install
```

If `rosdep` reports that it is not initialized, run `sudo rosdep init` once, then repeat `rosdep update` and the dependency command. Continue only after dependency installation and the build succeed. Do not use `sudo colcon build`.

Reload the environment **after building**:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 pkg prefix turtlebot3_gazebo
ros2 pkg prefix turtlebot3_teleop
ros2 pkg prefix turtlebot3_cartographer
ros2 pkg prefix turtlebot3_navigation2
```

Every check must print an installation path. Sourcing exposes built packages; it does not install missing ones. Robot software belongs in `~/turtlebot3_ws`; student code/results belong in your course fork.


Choose only one world at a time. The course uses Waffle in TurtleBot3 World; the complete launch and keyboard commands appear in Lab 2. In each new terminal, repeat the ROS/workspace source commands and `export TURTLEBOT3_MODEL=waffle`. An export in one terminal does not affect another.

References: [ROBOTIS PC Setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup/?ros=jazzy) and [Gazebo Simulation](https://docs.robotis.com/docs/systems/turtlebot3/simulation/gazebo_simulation/?ros=jazzy). You do not need to follow additional website steps for the required course workflow.

---

## Part 6 — Fork and clone the course repository

**Required before repository-dependent commands:** use your own fork so you can save work and receive instructor corrections. **Expected branch: `main`.** This is the current `main` assignment.

Open [the public course repository](https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs) on GitHub, click **Fork → Create fork**, and keep its name. For the indoor/outdoor branch, uncheck **Copy the main branch only** if shown; the fetch command below also works for an existing main-only fork.

Replace `YOUR_USERNAME` and run once for a new local copy in **Ubuntu/WSL**:

```bash
mkdir -p ~/courses
cd ~/courses
git clone --branch main https://github.com/YOUR_USERNAME/eel4332-autonomous-vehicle-labs.git
cd eel4332-autonomous-vehicle-labs
git remote add upstream https://github.com/hoanbklucky/eel4332-autonomous-vehicle-labs.git
git fetch upstream
git switch main
git merge --no-edit upstream/main
git push -u origin main
git remote -v
git branch --show-current
code .
```

Stop on errors. Expect **your fork as origin**, **the instructor repository as upstream**, branch **main**, and **WSL: Ubuntu** in VS Code. Download ZIP, reopening VS Code, or updating VS Code Server does not keep course files synchronized.

**Already have a clone? Do not clone over it or repeat remote creation.** Save local work and use [existing-clone migration](../docs/UPDATING_COURSE_REPOSITORY.md#2-already-cloned-the-instructor-repository) and the guide's branch-selection/update steps. Before each lab, fetch/merge `upstream/main` and verify inclusion using that guide. VS Code Sync/pulling your fork alone does not fetch instructor changes. Preserve robot Xacro/settings and maps when resolving conflicts.

---

## Part 7 — Create the course Python environment

**Why this part matters:** A dedicated virtual environment keeps course Python dependencies consistent without changing ROS 2 or system Python packages.

### Why use a virtual environment?

A Python virtual environment gives this course its own location for packages installed with `pip`. This provides several benefits:

- course packages do not overwrite Ubuntu or ROS 2 system packages;
- different projects can use different package versions;
- students can reproduce a known set of dependencies from `requirements.txt`;
- packages can be installed without `sudo`, reducing the risk of damaging the system Python installation.

The environment isolates packages installed by `pip`; it does not contain a second installation of ROS 2. ROS packages from `/opt/ros/jazzy` remain available when the ROS setup file is sourced. This is why the course environment also installs a few Python helpers required by ROS-visible packages.

After activation, the WSL/Ubuntu Terminal prompt normally begins with `(eel4332)`, and `python` and `pip` refer to the course environment. Run `deactivate` to return to the normal system environment. If you open a new WSL/Ubuntu Terminal, activate the environment again before running the pure-Python lab programs:

```bash
source ~/venvs/eel4332/bin/activate
```

**Command breakdown:** `source` runs the virtual environment's activation script in the current shell, changing `python` and `pip` to the isolated course versions.

In Ubuntu:

```bash
sudo apt install python3-venv python3-pip
python3 -m venv ~/venvs/eel4332
source ~/venvs/eel4332/bin/activate
python -m pip install --upgrade pip setuptools
```

**Command breakdown:** `apt install` provides Python's virtual-environment and package tools. `python3 -m venv` creates the environment, `source` activates it, and `python -m pip install --upgrade` updates its packaging tools.

Now tell the Microsoft Python extension to use the environment you just created:

1. Open the repository in a WSL-connected VS Code window.
2. Press **Ctrl+Shift+P** to open the Command Palette.
3. Run **Python: Select Interpreter**.
4. Select `~/venvs/eel4332/bin/python`. If it is not listed, choose **Enter interpreter path** and enter that path.

The selected interpreter controls Python editing, the **Run Python File** button, and debugging in VS Code. It does not automatically activate existing terminals, and it does not replace the need to source `/opt/ros/jazzy/setup.bash` in terminals that run ROS commands. When in doubt, activate the environment in the terminal and use the explicit course command shown in each lab.

Make sure you are still at the repository root established in Part 6, then run:

```bash
python -m pip install -r requirements.txt
```

**Command breakdown:** `python -m pip` uses pip from the active Python interpreter, while `-r requirements.txt` installs every dependency declared in the course requirements file.

The command is successful when it ends with `Successfully installed` or reports that all requirements are already satisfied.

If an older copy of this repository reports that ROS packages such as `generate-parameter-library-py` or `launch-ros` require `setuptools`, `jinja2`, or `typeguard`, update the repository and run the requirements command again:

```bash
git fetch upstream
git merge --no-edit upstream/main
python -m pip install -r requirements.txt
```

**Command breakdown:** fetch/merge receives instructor updates from `upstream`, and the pip command synchronizes the active environment with any updated Python requirements. Protect local changes before pulling as described at the beginning of this lab.

Those messages come from ROS 2 Python packages exposed by `/opt/ros/jazzy/setup.bash`. The updated requirements install the corresponding helpers inside the isolated course environment. Do not use `sudo pip` and do not delete the ROS installation.

Verify:

```bash
python -c "import numpy, matplotlib, yaml; print('Python dependencies OK')"
python -c "import setuptools, jinja2, typeguard; print('ROS Python helpers OK')"
python -m pip check
```

**Command breakdown:** The two `python -c` commands run short import checks. `python -m pip check` verifies that installed Python packages have compatible declared dependencies.

All three verification commands should complete without dependency-conflict messages. Use `deactivate` when you want to leave the course Python environment.

---

## Part 8 — Optional F1TENTH / RoboRacer Gym

**Why this part matters:** This optional simulator offers another vehicle-control environment without making it a dependency for the required labs.

F1TENTH, now also known as RoboRacer, is an autonomous-driving education and racing platform built around a small car-like vehicle. Unlike the differential-drive TurtleBot used in this course's primary Gazebo simulation, an F1TENTH vehicle uses car-like steering. Its simulator can therefore be useful when studying vehicle kinematics, planning, and control.

The [F1TENTH Gym repository](https://github.com/f1tenth/f1tenth_gym) provides an optional simulation environment for experimenting with this type of vehicle. It is not required for Labs 00–02, and students should not delay the required TurtleBot/Gazebo setup or playground to install it.

The F1TENTH organization also publishes an [open collection of teaching labs](https://github.com/f1tenth/f1tenth_labs_openrepo). These are examples and exercises developed for F1TENTH courses at other institutions. They may be useful as supplemental reading, but they are not EEL 4332 assignments and their installation instructions, software versions, and deliverables may differ from this repository.

Lab 3 first implements differential-drive odometry and then uses the repository's pure-Python bicycle model for comparison. F1TENTH Gym is optional; install or explore it only if the instructor specifically assigns an extension that uses it.

---

## Part 9 — Run the verification script

**Why this part matters:** Verification catches missing tools and packages now, before they appear as harder-to-diagnose failures during a lab.

Source ROS 2 and activate the Python environment before running the verification:

```bash
source ~/venvs/eel4332/bin/activate
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
chmod +x lab00_setup/verify_installation.sh
./lab00_setup/verify_installation.sh
```

**Command breakdown:** The two `source` commands activate the course Python environment and ROS 2 Jazzy. `chmod +x` makes the verification script executable, and `./` runs that script from the repository root.

Fix any required item marked `MISSING` before starting Lab 01.
If there is no missing, the output should look like below

![alt text](verification.png)

---

## Part 10 — Goosebot

Goosebot autonomous lane following is the course's hardware component. The required [final project](../final_project_simulation/README.md) uses the supplied Goosebot model in Gazebo; follow this branch's current final instructions. Physical Goosebot SLAM/Nav2 deployment is optional and requires separately validated interfaces.

---

## What to Submit

Submit the following two screenshots:

1. **Gazebo shapes:** the Gazebo window from Part 4 showing the world with several different shapes.
2. **Installation verification:** the complete Terminal output from Part 9 showing that the installation verification script ran successfully and that no required item is marked `MISSING`.

Make sure both screenshots are readable and show enough of the application window to identify Gazebo or the WSL/Ubuntu Terminal.

---

# Setup Success Criteria

Before Lab 01, you should be able to:

- [ ] run `ros2 --help`
- [ ] run `git --version` and confirm Git name/email configuration
- [ ] run `code .` from WSL and confirm VS Code reports a WSL connection
- [ ] confirm VS Code recognizes the repository and selects `~/venvs/eel4332/bin/python`
- [ ] run `rosdep update` successfully
- [ ] run `gz sim shapes.sdf`
- [ ] launch Gazebo through `ros_gz_sim`
- [ ] open RViz2
- [ ] import NumPy and Matplotlib
- [ ] fork/clone (or open the private instructor copy), verify branch `main`, and confirm it includes the latest fetched instructor commits
- [ ] verify `ros2 bag`, `teleop_twist_keyboard`, and `rqt_image_view` are available

After every item passes, continue to [Lab 1 — ROS 2 and Gazebo Fundamentals](../lab01_ros2_gazebo_fundamentals/README.md).
