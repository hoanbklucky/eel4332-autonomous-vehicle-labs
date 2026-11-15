# Goosebot final-project integration

All required commands and the student LiDAR assignment are in the [main final-project README](../README.md).

- `world.launch.py` reuses the provided Goosebot spawn launch and reads the chosen world's `mission.json`. It does not launch any global localizer.
- `slam_goosebot.yaml` is a starting LiDAR SLAM Toolbox configuration.
- `nav2_goosebot.yaml` is a full starting saved-map AMCL/Nav2 configuration: `/scan`, `base_footprint`, `/odometry/filtered`, full-map global costmap, NavFn/Dijkstra and DWB. Verify/tune it locally.

Model/config provenance: [hoanbklucky/goose](https://github.com/hoanbklucky/goose/tree/bffaf3cdf2b38f3b5a53a977064e0c787e046ff7/11_simulation), revision `bffaf3cdf2b38f3b5a53a977064e0c787e046ff7`; the upstream package declares Apache-2.0. The model is fetched rather than duplicating the full robot/assets here. Preserve upstream attribution in student copies.

The original perfect-map bridge and stereo SLAM launch are separate modes, not this project's assessed AMCL workflow. Do not run them together. No completed student LiDAR addition or mission-client solution is supplied.
