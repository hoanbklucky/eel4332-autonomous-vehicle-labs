# EEL 4332 Laboratory-to-Course Map

| Course topic | Required hands-on activity | Optional extension |
|---|---|---|
| ROS 2 and Gazebo | Lab 01: nodes, interfaces, bridges | Reference tutorials |
| Robot operation | Lab 02: driving, stopping, resetting | Additional driving challenges |
| Vehicle modeling and odometry | Lab 03: assigned models and experiments | Car-like tracking comparisons |
| Sensors, TF, timing | Lab 04: verify mapper inputs | Sensor statistics |
| Mapping and SLAM | Lab 04: follow official Cartographer tutorial and export a map | Separate Kalman-filter implementation |
| Localization and navigation | Lab 05: official saved-map Nav2 tutorial and three goals | A*, Pure Pursuit, safety-monitor exercises; parameter comparison |
| Goosebot preparation | [Required warm-up](../final_project_simulation/README.md#goosebot-warm-up): manual driving and one perfect-map Nav2 goal | Docker and stereo RTAB-Map |
| Mission integration and evaluation | [Simulation final](../final_project_simulation/README.md): Goosebot + student-added LiDAR, new SLAM map, three deliveries/home, blocked-route test | Extra tuning experiments |
| Physical autonomy | Goosebot autonomous lane following, already completed | [Hardware SLAM/Nav2 transfer](../final_project_goosebot/README.md) |

Progression: **00 setup → 01 foundations → 02 driving → 03 modeling → 04 SLAM → 05 Nav2 → Goosebot warm-up → simulation final**.

Labs 4–5 are guided TurtleBot preparation. The final requires Goosebot LiDAR/model/bridge integration and a new map of IST or campus. Nav2 supplies live planning/control; mission-client programming is optional. Separate Kalman, A*, Pure Pursuit, and synthetic-health safety-monitor exercises are optional and do not gate the SLAM/Nav2 work.

The [legacy sequence](../optional_legacy/previous_lab_sequence/README.md) remains optional reading. No physical SLAM/Nav2 deployment is required this semester.

Labs 2/4/5 use ROBOTIS TurtleBot3 Waffle in TurtleBot3 World with Cartographer. The final instead uses the supplied Goosebot model, a student-added 2-D LiDAR, SLAM Toolbox, and AMCL/Nav2. Use the final README's complete procedure; do not combine it with the original Goosebot ground-truth mode.

The warm-up and final use the same native Ubuntu/WSL Jazzy workspace. Docker is an optional alternative. Warm-up evidence is one screenshot plus two sentences (or an observed in-class demonstration); supplied perfect-map localization does not count as SLAM/AMCL.
