# ROS 2 Fundamentals Practice

## Before You Begin — Update Course Files

In a **WSL/Ubuntu Terminal**, go to your local course repository and check for changes:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
git status --short
```

**Command breakdown:** `cd` changes to the repository directory; `~` means your Ubuntu home directory. `git status --short` gives a compact list of local changes and prints nothing when the working tree is clean.

If the command prints nothing, run `git pull --rebase`. If it lists files, protect your work first by following [Updating the Course Repository](../docs/UPDATING_COURSE_REPOSITORY.md). Use your actual repository path if you cloned it elsewhere.

Most students are not expected to have previous ROS 2 experience. Complete these two required parts in order:

1. [Part 1 — Graph and Communication](ros2_fundamentals_part1.md)

   Learn nodes, topics, messages, services, parameters, actions, ROS CLI inspection, and `rqt_graph`.

2. [Part 2 — Packages, Workspaces, and Launch](ros2_fundamentals_part2.md)

   Learn packages, `rosdep`, colcon workspaces, underlays and overlays, launch files, and launch arguments.

Each part begins with a visual overview and a short glossary. Run one command block at a time and examine its output before continuing.

After both parts, return to the [Lab 1 overview](README.md) and complete the [Gazebo Fundamentals Practice](gazebo_fundamentals.md).
