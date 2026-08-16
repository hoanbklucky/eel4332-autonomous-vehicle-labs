# Repository instructions for coding agents

This is a student-facing university laboratory repository for **EEL 4332 — Introduction to Autonomous Vehicles**.

## Instructional content

- Treat each lab `README.md` as authoritative instructional content.
- Do not substantially rewrite pedagogy, learning objectives, mission statements, questions, or deliverables unless explicitly requested.
- Do not add new course topics without instructor approval.
- Keep the lab sequence stable unless explicitly asked to reorganize it.
- Preserve the distinction between lecture/homework mathematics and simulation-based lab work.

## Student code

- Do not solve student-required algorithms.
- Preserve `TODO` markers for:
  - bicycle-model propagation
  - Kalman-filter prediction/update
  - A* search
  - Pure Pursuit steering
  - safety-monitor logic
  - other explicitly assigned algorithms
- Utility code may be completed when it is not itself a learning objective.
- Use Python 3 and NumPy unless a lab specifies ROS 2 nodes or another tool.
- Use SI units.

## ROS / Gazebo

- Target ROS 2 Jazzy and modern Gazebo.
- Avoid Gazebo Classic instructions.
- Do not silently change topic names or launch commands.
- If a command depends on an instructor-specific simulation package, mark it `INSTRUCTOR VALIDATION REQUIRED`.
- Do not invent Goosebot topic names. Use placeholders and flag them for instructor validation if the exact interface is unknown.

## Repository maintenance

- Fix internal links after moves/renames.
- Run Python syntax checks after code edits.
- Do not commit `build/`, `install/`, `log/`, bag files, or virtual environments.
- Report files changed and any steps requiring manual simulation testing.

## Lab manual structure

Preserve this order where practical:

1. Mission
2. Learning Objectives
3. Prerequisites
4. Background
5. Provided Files
6. Step-by-Step Procedure
7. Experiment / Quantitative Analysis
8. Engineering Questions
9. Success Criteria
10. What to Submit
11. Troubleshooting
