# Goosebot final-project integration

All required commands and the end-of-project LiDAR settings activity are in the [main final-project README](../README.md).

- `world.launch.py` owns a separate server/GUI startup sequence, reads the chosen world's `mission.json`, explicitly selects the spawn world, and verifies the robot with `wait_for_robot.py` before opening the GUI. It rejects existing Gazebo servers and shuts down its owned processes together. It does not launch any global localizer.
- `slam_goosebot.yaml` is a starting LiDAR SLAM Toolbox configuration.
- `nav2_goosebot.yaml` is a full starting saved-map AMCL/Nav2 configuration: `/scan`, `base_footprint`, `/odometry/filtered`, full-map global costmap, NavFn/Dijkstra and DWB. Verify/tune it locally.

Model/config provenance: [hoanbklucky/goose](https://github.com/hoanbklucky/goose/tree/bffaf3cdf2b38f3b5a53a977064e0c787e046ff7/11_simulation), revision `bffaf3cdf2b38f3b5a53a977064e0c787e046ff7`; the upstream package declares Apache-2.0. The model is fetched rather than duplicating the full robot/assets here. Preserve upstream attribution in student copies.

The original perfect-map bridge and stereo SLAM launch are separate modes, not this project's assessed AMCL workflow. Do not run them together. The build helper applies `provided_lidar.xml` and a wheel joint-state publisher with `configure_goosebot.py`, preserving complete custom settings. Students use the baseline for mapping/AMCL/Nav2, then do the final LiDAR settings activity. Mission-client TODOs remain optional.
