# Repository instructions for coding agents

This is a student-facing university laboratory repository for **EEL 4332 — Introduction to Autonomous Vehicles**.

## Instructional content

- Treat each lab `README.md` as authoritative instructional content.
- Do not substantially rewrite pedagogy, learning objectives, mission statements, questions, or deliverables unless explicitly requested.
- Do not add new course topics without instructor approval.
- Keep the lab sequence stable unless explicitly asked to reorganize it.
- Preserve the distinction between lecture/homework mathematics and simulation-based lab work.

## Current semester scope

- Required final: `final_project_simulation/README.md`; Goosebot lane following is the completed hardware component.
- Physical Goosebot SLAM/Nav2 is optional.
- Separate Kalman, A*, Pure Pursuit, and synthetic safety-monitor implementations are optional extensions. Preserve their TODOs.
- Labs 4–5 provide guided mapping/navigation preparation. Final student work is mapping, localization, navigation and explanation, with an indoor LiDAR comparison, outdoor GPS inspection, and an assessed system explanation. The baseline LiDAR/bridge/wheel visualization is supplied. The mission-client scaffold is an optional extension; preserve its TODOs.

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

## Original building-reference images

- Do not commit or embed the original IST evacuation/floor-plan reference images. Keep only the generated teaching-world preview and derived simulation assets.

## Final-project AI assistance

- Students may use AI to help with final-project coding, model/sensor changes, configuration and debugging. They must test their work and explain it in their own words.
- This permission does not authorize publishing completed instructor solutions in the public starter repository. Preserve student-required TODOs when maintaining the public repository.

## ROS / Gazebo

- Lab 2 and the first environment in Labs 4–5 use ROBOTIS Jazzy Waffle/World; Labs 4–5 also use House with Waffle Pi. Cartographer is used for Lab 4 mapping. The final uses the provided Goosebot model with a supplied 2-D LiDAR, LiDAR SLAM Toolbox, and saved-map AMCL/Nav2 in both IST interior and the campus world (custom world optional). These new integrations require instructor simulation validation.
- Keep required course READMEs self-contained with the necessary official Jazzy commands, explicit sourcing/model exports, and terminal assignments. ROBOTIS links are references, not additional required procedures.
- Do not reintroduce nav2_minimal_tb3_sim or the obsolete TurtleBot SLAM Toolbox workflow into Labs 2/4/5. The final's documented Goosebot LiDAR SLAM Toolbox workflow is explicitly authorized. The Goosebot ground-truth localizer is allowed only for the optional troubleshooting warm-up; it must not be used as final-project SLAM/AMCL evidence.


- Required Goosebot readiness check: use each IST/campus world, confirm brief manual driving, /scan, RobotModel and TF before SLAM. The low-wall practice arena and perfect-map Nav2 goal are optional troubleshooting exercises with no separate submission. Use native WSL/Jazzy in the final's workspace; Docker and stereo RTAB-Map are optional. Perfect localization is permitted only for the optional exercise, never as the final SLAM/AMCL result.
- Lab 4 maps both TurtleBot3 World (waffle) and House (waffle_pi), in separate Cartographer sessions/maps. Keep two videos, one per environment, each showing exploration and revisit. Lab 5 navigates in both: one World goal with waffle/map.yaml and two House goals in different rooms with waffle_pi/house_map.yaml. Keep one joined video plus a short Nav2 explanation; tuning is optional.
- Goosebot source Python scripts need executable permission before --symlink-install; verify installed libexec names after building. Copy the complete source package and preserve model edits.
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

- Final simplification: supply the LiDAR mount/sensor, /scan bridge and wheel joint-state visualization automatically. Do not require manual Xacro/sensor construction before mapping. On this branch, require both worlds; put the IST LiDAR comparison after indoor baseline navigation, restore defaults before campus, and use guided campus GPS inspection instead of a second LiDAR experiment. GPS fusion is optional; never claim the baseline EKF consumes GPS. Keep system understanding at 30%. Preserve mission-client and unrelated algorithm TODOs.

- Keep the final README concise: required runnable steps and short command explanations stay inline; extended diagnostics live in optional COMMAND_REFERENCE.md. Campus GPS activity is Home → landmark → Home in one run, comparing stationary GPS means with local odometry return displacement. It is an independent position-reference exercise, not GPS fusion or evidence of improved SLAM/Nav2. Preserve the 30% system explanation and both-world requirements.
