# EEL 4332 Laboratory-to-Course Map

| Course topic | Required hands-on activity | Optional extension |
|---|---|---|
| ROS 2 and Gazebo | Lab 01: nodes, interfaces, bridges | Reference tutorials |
| Robot operation | Lab 02: driving, stopping, resetting | Additional driving challenges |
| Vehicle modeling and odometry | Lab 03: assigned models and experiments | Car-like tracking comparisons |
| Sensors, TF, timing | Lab 04: verify mapper inputs | Sensor statistics |
| Mapping and SLAM | Lab 04: map TurtleBot3 World and House in separate Cartographer sessions; save both maps | Separate Kalman-filter implementation |
| Localization and navigation | Lab 05: AMCL/Nav2 on both saved maps; one World goal and two House goals in different rooms | A*, Pure Pursuit, safety-monitor exercises; parameter comparison |
| Goosebot preparation | [Short readiness check](../final_project_simulation/README.md#goosebot-readiness-check) in IST/campus: brief manual driving, `/scan`, RobotModel and TF | [Practice arena and perfect-map Nav2](../final_project_simulation/README.md#goosebot-warm-up); Docker and stereo RTAB-Map |
| Mission integration and evaluation | [Simulation final](../final_project_simulation/README.md): Goosebot + supplied LiDAR, new SLAM map, three deliveries/home, blocked-route test | Extra tuning experiments |
| Physical autonomy | Goosebot autonomous lane following, already completed | [Hardware SLAM/Nav2 transfer](../final_project_goosebot/README.md) |

Progression: **00 setup → 01 foundations → 02 driving → 03 modeling → 04 SLAM → 05 Nav2 → simulation final (readiness check → mapping → navigation)**.

Labs 4–5 are guided TurtleBot preparation. The final requires a supplied Goosebot/LiDAR baseline and a new map of IST or campus. Nav2 supplies live planning/control; mission-client programming is optional. Separate Kalman, A*, Pure Pursuit, and synthetic-health safety-monitor exercises are optional and do not gate the SLAM/Nav2 work.

The [legacy sequence](../optional_legacy/previous_lab_sequence/README.md) remains optional reading. No physical SLAM/Nav2 deployment is required this semester.

Lab 2 and the first environment in Labs 4–5 use Waffle/World; Labs 4–5 also use House/Waffle Pi. Lab 4 maps with Cartographer; Lab 5 localizes/navigates with AMCL/Nav2. The final instead uses the supplied Goosebot model, a supplied 2-D LiDAR, SLAM Toolbox, and AMCL/Nav2. Use the final README's complete procedure; do not combine it with the original Goosebot ground-truth mode.

The final and optional warm-up use the same native Ubuntu/WSL Jazzy workspace. Docker is an optional alternative. The readiness check and optional practice arena have no separate submission; supplied perfect-map localization does not count as SLAM/AMCL.

Lab 4 uses Waffle for World and Waffle Pi for House. Submit two videos, one per environment, each showing exploration and revisit. Lab 5 uses both maps: one World goal and two House goals in different rooms, with one joined video and a short explanation. Goosebot source scripts require executable permission and a successful package install check before launching the selected project world.
