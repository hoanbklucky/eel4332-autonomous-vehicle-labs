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

**Pedestrian paths, bridges, separate sidewalks and short mapped crossings across asphalt are permitted. Travel along asphalt lanes, grass, medians, water and buildings remains forbidden.** The broad tan crossing at Home is a pedestrian feature even though its old generic `kind` was `road`; its explicit access class resolves that ambiguity.

The world still displays asphalt carriageways using their existing estimated widths (6 m per carriageway, 3.5 m service roads). These are not newly measured widths and do not grant robot access. Separate pedestrian features remain permitted beside them. At an overlap, asphalt stays blocked except inside a short transverse crossing supported by mapped pedestrian pavement on both sides. The supplied rule requires a crossing angle of at least 45 degrees, a crossing patch no longer than 20 m, and obstacle-free pedestrian endpoints. It opens only existing pedestrian pavement within that patch, retains the physical-obstacle mask and one-cell boundary margin, and does not permit lengthwise asphalt travel. This is a simulation access rule, not recognition of a real marked crosswalk or a traffic-safety system. No blanket 21.87 m road strip is opened.

The same feature widths generate the visible world and the temporary pedestrian navigation mask. The mask intersects permitted pavement with obstacle-free cells and leaves a conservative one-cell margin. Both global and local costmaps use it, so LiDAR clearing cannot open a shortcut. Required A/B/Home remain on the pedestrian crossing; the outdoor forward-speed cap remains 1 m/s and the footprint remains 20 × 20 cm.

After updating, **stop all launches and restart campus and GPS/Nav2** to load the new visible pavement and regenerate the mask. No ROS rebuild is needed. Navigation uses the supplied matching map assets; do not shrink the robot or remove the pedestrian restriction to make a route pass.

Edit widths/access in `layout.json`, then run `python3 final_project_simulation/campus/generate_campus.py` to regenerate the asset bundle. Keep the generated world/map/manifest together. The Google Maps screenshots are not embedded in the repository; only the supplied measurements and provenance are recorded. Live Gazebo validation is still required.

## Pavement continuity review

The BARC corner and approximate Campus Store/Residence III footprints overlapped mapped pedestrian pavement. Their teaching footprints now retain the main building mass outside that pavement with 0.75 m clearance; original coordinates remain in `source_points_before_pavement_review`. These are documented geometry approximations, not surveyed building corrections. Gazebo visuals, collision meshes and the obstacle map all use the corrected footprints, so this does not hide a physical obstacle from navigation. Indoor/covered paths at IST remain blocked by the actual building footprint.

Flat round pavement joins now fill the triangular wedges between adjacent path segments at bends. The same joins appear in Gazebo and the pedestrian mask. The former post-like notches were geometry artifacts; this campus model contains no street lamp posts. Asphalt exclusions still take precedence.

After this crossing-rule update, restart GPS/Nav2 to regenerate its temporary planning mask; no world geometry, map-source pixels or ROS build changes are needed. A world restart is necessary only if its geometry is also being updated. Test crossing clearance and confirm the global path returns to the sidewalk after crossing.
