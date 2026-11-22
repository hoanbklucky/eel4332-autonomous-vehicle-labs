# Campus widths and pedestrian access

The campus and Goosebot use full-scale meters. Widths vary by feature. The instructor supplied approximate Google Maps cross-section measurements; these are map readouts, not a survey.

| Reference | Approximate width | Model use |
|---|---:|---|
| Narrow lake-side walk | 3.12 m | `path_467810969_0` |
| Broad pedestrian crossing at Home | 11.31 m | `path_467811278_0` |
| Diagonal paved route toward Residence Hall I | 7.22 m | `path_507676803_0`; its short continuation `path_481476620_0` inherits this estimate |
| Polytechnic Circle overall corridor | 21.87 m | Context only; instructor confirms it includes median/sidewalk/verge. Never used as a drivable width |

The instructor reports the smallest walking paths are about **3 m**. Unmeasured pedestrian paths therefore use a 3 m minimum assumption. Measurements apply at visible cross-sections; extending a constant width along the listed feature remains an approximation. Feature matching is based on the surrounding campus geometry. `layout.json` records measurement IDs, source image names, width sources and explicit `robot_access` classes.

## Where Goosebot may drive

**Non-asphalt interior paved corridors, plazas, pedestrian paths/crossings and separate sidewalks—including sidewalks alongside asphalt roads—are permitted.** Identified asphalt traffic carriageways, carriageway connectors and asphalt parking access/aisles remain forbidden, as do grass, medians, water and buildings.

A generic source `kind: road` does not identify a surface material. That earlier shortcut incorrectly blocked 33 interior paved features, including the measured 7.22 m route. The layout now records separate `surface` and `robot_access` classifications, with the reviewed feature IDs and assumptions. Non-asphalt corridors render tan in Gazebo; identified asphalt lanes remain gray. Surface assignments are a simulation approximation, not a surveyed material map.

A sidewalk beside an asphalt carriageway is its own permitted feature. Neither the road label nor the 21.87 m overall corridor may blanket-block it. At an actual overlap with an identified asphalt lane, that lane remains forbidden; this does not authorize traffic-lane driving. The connected network is checked from Home to IST, Residence, GCW, both A/B goals and both ends of all five pedestrian crossings with footprint clearance.

The same feature widths generate the visible world and the temporary pedestrian navigation mask. The mask intersects permitted pavement with obstacle-free cells and leaves a conservative one-cell margin. Both global and local costmaps use it, so LiDAR clearing cannot open a shortcut. Required A/B/Home remain on the pedestrian crossing; the outdoor forward-speed cap remains 1 m/s and the footprint remains 20 × 20 cm.

After updating, **stop all launches and restart campus and GPS/Nav2** to load the new visible pavement and regenerate the mask. No ROS rebuild is needed. Navigation uses the supplied matching map assets; do not shrink the robot or remove the pedestrian restriction to make a route pass.

Edit widths/access in `layout.json`, then run `python3 final_project_simulation/campus/generate_campus.py` to regenerate the asset bundle. Keep the generated world/map/manifest together. The Google Maps screenshots are not embedded in the repository; only the supplied measurements and provenance are recorded. Live Gazebo validation is still required.
