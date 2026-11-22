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
- Labs 4–5 provide guided mapping/navigation preparation. Final student work is mapping, localization, navigation and explanation, with a supplied outdoor GPS fusion comparison and an assessed system explanation. Blocked-route testing and LiDAR tuning are optional and ungraded. The baseline LiDAR/bridge/wheel visualization is supplied. The mission-client scaffold is an optional extension; preserve its TODOs.

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

- Lab 2 and the first environment in Labs 4–5 use ROBOTIS Jazzy Waffle/World; Labs 4–5 also use House with Waffle Pi. Cartographer is used for Lab 4 mapping. The final uses the provided Goosebot model with a supplied 2-D LiDAR, LiDAR SLAM Toolbox, and saved-map AMCL/Nav2 indoors and live GPS-aided Nav2 outdoors (custom world optional). These new integrations require instructor simulation validation.
- Keep required course READMEs self-contained with the necessary official Jazzy commands, explicit sourcing/model exports, and terminal assignments. ROBOTIS links are references, not additional required procedures.
- Do not reintroduce nav2_minimal_tb3_sim or the obsolete TurtleBot SLAM Toolbox workflow into Labs 2/4/5. The final's documented Goosebot LiDAR SLAM Toolbox workflow is explicitly authorized. The Goosebot ground-truth localizer is allowed only for the optional troubleshooting warm-up; it must not be used as final-project SLAM/AMCL evidence.


- Goosebot mapping startup: launch the selected IST/campus world, start SLAM, then open RViz with Fixed Frame map and drive. Confirm motion, /scan, RobotModel and TF during mapping; separate sensor/TF checks are troubleshooting only. The low-wall practice arena and perfect-map Nav2 goal are optional troubleshooting exercises with no separate submission. Use native WSL/Jazzy in the final's workspace; Docker and stereo RTAB-Map are optional. Perfect localization is permitted only for the optional exercise, never as the final SLAM/AMCL result.
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

- Final simplification: supply the LiDAR mount/sensor, /scan bridge and wheel joint-state visualization automatically. Do not require manual Xacro/sensor construction before mapping. On this branch, require both worlds and the supplied campus GPS position-fusion comparison. Blocked-route testing and LiDAR tuning are optional, with no required screenshots, discussion or grading. Assign the full 15% experiment category to the GPS comparison; keep navigation at 25%. The course local EKF fuses measured wheel-joint forward speed and IMU yaw rate using goosebot/ekf_wheel.yaml; it does not consume GPS; indoor AMCL remains. Campus navigation uses a separate live supplied x/y/yaw GPS filter, rolling LiDAR costmaps and a command health gate. Live GPS-aided campus Nav2 is now supplied as a separate mode; only its global EKF may publish map -> odom, with no AMCL/SLAM/ground-truth transform publisher. Keep system understanding at 30%. Preserve mission-client and unrelated algorithm TODOs.

- Keep the final README concise: required runnable steps and short command explanations stay inline; extended diagnostics live in optional COMMAND_REFERENCE.md. Campus GPS activity records one stationary-start loop and compares existing odometry/IMU with supplied ordinary-GPS and RTK-like two-state position filters on identical data from two independent simulated sensors. Known Home initialization comes from mission.json, never truth. Ground truth must be separate and used only for scoring. Report unmodified and explicitly artificial +15% prediction-scale cases separately; improvement is not guaranteed. Separately use live GPS navigation initialized with known Home pose/heading, with no ground-truth input. RTK-like means an idealized ~2 cm noise profile, not simulated correction infrastructure. Preserve student TODOs; utility/filter code here is instructor-supplied. Preserve the 30% system explanation and both-world requirements.

- Required GPS campus-map navigation: use 1:1 horizontal meters and the unscaled Goosebot. gps_navigation.launch.py defaults to the supplied matching reference.yaml and rejects an empty map argument; retire the short-range exercise. Keep pedestrian access masks lethal off-route in both costmaps, live LiDAR, GPS-only map -> odom and no AMCL. Required nearby goals A/B/Home come from mission.json; named distant delivery pads are optional landmarks. 25 cm global and 2.5 cm local grids, a 20 x 20 cm footprint and 1.0 m/s outdoor forward-speed cap are supplied. Width assumptions are explicit, not surveyed. Regenerate world/meshes/map/mission/asset manifest together. Preserve indoor workflow, local campus SLAM evidence, GPS comparison and rubric weights. Require a live pilot.

- Optional budget localization experiment is authorized: budget_compare.py records measured /joint_states velocities, /imu/data yaw rate, ordinary /gps/fix and /scan. Supplied offline particle filters compare wheel/gyro, GPS, GPS+LiDAR map matching and LiDAR-only controls using the obstacle reference map (never the artificial road mask). Do not label cmd_vel-derived odometry as encoders. No RTK or absolute simulated IMU orientation enters the filters. Known Home initializes all variants; truth stays separate for scoring only. Controlled GPS withholding must be labeled artificial. No TF/motion publication, grade change or claim of hardware/live-navigation validation.

- Course world odometry uses measured /joint_states through goosebot/wheel_joint_odometry.py and goosebot/ekf_wheel.yaml, loaded directly by world.launch.py. Never restore cmd_vel_to_odom as the motion estimate. Fuse wheel forward velocity and IMU yaw rate, not wheel pose or a synthetic zero lateral velocity. Local EKF alone owns odom -> base_footprint; wheel node publishes no TF. Preserve missing/stale-wheel fail-stop and mark old command-derived GPS examples as historical; new comparisons need fresh recordings.

- Campus full-scale migration: geographic XY coordinates are restored from 0.06 to 1:1; do not rescale the robot, sensors or GPS noise. Widths/heights remain documented approximations. Use matching generated assets and new maps/recordings. The active required GPS/map assignment is on final-project-indoor-outdoor; main retains its legacy assignment with an explicit link to that branch.

- Pedestrian-only campus navigation is required: allow mapped sidewalks/pedestrian paths/bridges, exclude motor/asphalt carriageways and service roads even at overlaps. Keep medians/verges/grass forbidden. Width measurements M01-M03 and explicit access classes are recorded in layout.json; unmeasured walks have a 3 m minimum. M04 (21.87 m) includes median/sidewalk/verge and is context only, never drivable pavement. Preserve 1 m/s outdoor speed, 20 x 20 cm footprint, A/B/Home and the existing rubric. Regenerate matching assets after layout changes.

- Surface correction: a generic source kind=road is NOT evidence of asphalt. Permit reviewed interior non-asphalt paved corridors/plazas as well as mapped pedestrian paths and sidewalks alongside asphalt roads. Explicit surface and robot_access fields must agree; only identified asphalt carriageways, connectors and parking access/aisles are excluded. Preserve separate sidewalks. Keep the 21.87 m overall corridor from becoming an exclusion or permission strip. Connectivity checks must include Residence/GCW and both ends of all five pedestrian crossings, not only A/B/Home. No invented grass/water links.
