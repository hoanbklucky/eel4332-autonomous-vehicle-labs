# Goosebot final-project integration

All required commands, the indoor LiDAR comparison and the outdoor GPS activity are in the [main final-project README](../README.md).

- `world.launch.py` owns a separate server/GUI startup sequence, reads the chosen world's `mission.json`, explicitly selects the spawn world, and opens the GUI after the create service accepts the robot. A separate `gz model` query is not a startup requirement. It rejects existing Gazebo servers and shuts down its owned processes together. It does not launch any global localizer.
- `slam_goosebot.yaml` is a starting LiDAR SLAM Toolbox configuration.
- `nav2_goosebot.yaml` is a full starting saved-map AMCL/Nav2 configuration: `/scan`, `base_footprint`, `/odometry/filtered`, full-map global costmap, NavFn/Dijkstra and DWB. Verify/tune it locally.

Model/config provenance: [hoanbklucky/goose](https://github.com/hoanbklucky/goose/tree/bffaf3cdf2b38f3b5a53a977064e0c787e046ff7/11_simulation), revision `bffaf3cdf2b38f3b5a53a977064e0c787e046ff7`; the upstream package declares Apache-2.0. The model is fetched rather than duplicating the full robot/assets here. Preserve upstream attribution in student copies.

The original perfect-map bridge and stereo SLAM launch are separate modes, not this project's assessed AMCL workflow. Do not run them together. The build helper applies `provided_lidar.xml` and a wheel joint-state publisher with `configure_goosebot.py`, preserving complete custom settings. Students use the baseline for mapping/AMCL/Nav2, then do the IST LiDAR comparison, restore its defaults, and complete campus mapping/AMCL/Nav2 and GPS inspection. Mission-client TODOs remain optional.


On `final-project-indoor-outdoor`, **both** IST and campus are required. See [CAMPUS_GPS.md](CAMPUS_GPS.md) for the supplied NavSat world plugin, existing GPS sensor/bridge, and measurements. The local EKF uses measured wheel-joint forward speed and IMU yaw rate; indoor AMCL remains separate. Live campus navigation adds the supplied global GPS filter. Complete the [system explanation](../SYSTEM_EXPLANATION.md) from actual runtime/configuration evidence.


Saved-map startup uses `navigation.launch.py map:=/absolute/path/to/map.yaml`. It checks the YAML/image pair and prepares an explicit map-server `yaml_filename` while preserving the source Nav2 YAML. It runs standard AMCL/Nav2; no manual load-map service is required. In the separate RViz terminal, use the main guide's explicit `rviz2 -d .../nav2_default_view.rviz` command to obtain Nav2 Goal and the Navigation 2 panel. Offline regression checks: `python3 -m unittest discover -s final_project_simulation/goosebot/tests -p 'test_navigation_launch.py' -v`. Pilot startup/map delivery and RViz plugins on the course WSL installation.

The course world launcher uses `wheel_joint_odometry.py` and `ekf_wheel.yaml`: actual `/joint_states` wheel velocities → `/wheel/odometry` → local EKF with IMU yaw rate. It never starts the upstream command-derived odometry node. Raw wheel pose is diagnostic only; only wheel forward velocity is fused, and the EKF alone publishes `odom → base_footprint`.
