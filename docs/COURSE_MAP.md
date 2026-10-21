# EEL 4332 Laboratory-to-Course Map

| Course topic | Required hands-on activity | Additional theory / practice |
|---|---|---|
| ROS 2 and Gazebo | Lab 01: nodes, interfaces, bridges, simulation | Lab 01 references |
| Robot operation | Lab 02: driving, stopping, resetting | Lab 02 explanations |
| Vehicle modeling and odometry | Lab 03: student implementations and experiments | Lecture/homework mathematics |
| Sensors, architecture, TF, timing | Lab 04: verify mapper inputs | [SLAM optional background](../lab04_slam/OPTIONAL_BACKGROUND.md) |
| Sensor uncertainty | Lab 04: explain input/map limitations | Optional sensor-statistics exercise |
| Mapping and SLAM | [Lab 04](../lab04_slam/README.md): configure, build, compare, export maps | SLAM optional background |
| Estimation/localization | Lab 05: initialize and verify AMCL | [Navigation optional background](../lab05_navigation/OPTIONAL_BACKGROUND.md); required Lab 4 Kalman experiment |
| Planning/tracking | [Lab 05](../lab05_navigation/README.md): configure Nav2 and compare missions | Navigation optional background; required A*/Pure Pursuit experiments |
| Execution/failure handling | Lab 05: student mission client, timeout/cancellation, recovery | Required safety-monitor implementation and STOP-to-cancellation test |
| Hardware transfer | [Final project](../final_project_goosebot/README.md): validate Goosebot and mission | Instructor platform validation |

Required progression: **00 setup -> 01 foundations -> 02 driving -> 03 modeling -> 04 SLAM -> 05 Nav2 -> final project**.

The former Labs 04-09 are condensed into two integrated labs. Students configure and test autonomy components, write mission code, produce reusable artifacts, and quantify repeatability.

The [optional previous sequence](../optional_legacy/previous_lab_sequence/README.md) retains algorithm starters. Kalman filtering remains required in Lab 4; A*, Pure Pursuit, and safety-monitor logic remain required in Lab 5. Their starters are in the active lab folders and their measured experiments are assessed alongside SLAM/Nav2 integration. Detailed theory remains optional reading; lecture/homework provides the mathematical derivations. SLAM and Nav2 are central integration tasks alongside the sensing, estimation, control, and safety concepts they depend on.
