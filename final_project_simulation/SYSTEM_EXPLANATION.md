# Required system explanation — both environments

Submit one concise explanation covering IST and campus: about 2–3 pages plus the topic table and diagram. Use your own words. Refer to actual files, topic output, screenshots and results; listing software names alone is insufficient. This component is **30%** of the project grade.

## 1. Sensors, topics and roles

Complete the table for **every sensor available in your robot**: mapping LiDAR, forward ToF, IMU, both stereo cameras, and GPS. Include image calibration topics where present. Mark a sensor as **available but unused** if the required mapping/navigation nodes do not consume it. Separate derived estimates, joint visualization, ground truth and motion commands from sensor measurements.

| Sensor or derived signal | Exact ROS 2 topic | Message type | Header / reference frame | Publisher and consumer(s) | Used for what in your run? |
|---|---|---|---|---|---|
| Mapping LiDAR | Fill | Fill | Fill | Fill | Fill |
| Forward ToF | Fill | Fill | Fill | Fill | Fill |
| IMU | Fill | Fill | Fill | Fill | Fill |
| Stereo left/right | Fill | Fill | Fill | Fill | Fill |
| GPS (campus) | Fill | Fill | Fill | Fill | Fill |
| Command-derived odometry | Fill | Fill | Fill | Fill | Fill |
| Filtered odometry | Fill | Fill | Fill | Fill | Fill |
| Map / localization estimate | Fill | Fill | Fill | Fill | Fill |
| Motion command | Fill | Fill | Applicable frame/convention | Fill | Fill |

Useful evidence, in a sourced terminal (inspect while the relevant phase is running):

```bash
ros2 topic list -t
ros2 topic info /scan --verbose
ros2 topic info /imu/data --verbose
ros2 topic info /gps/fix --verbose
ros2 node list
ros2 node info /ekf_filter_node
```

Repeat `ros2 node info` using the actual SLAM, AMCL and navigation node names you discovered. A publisher or subscriber count is evidence about connections, not proof that measurements are fused correctly. A bridge changes transport/message representation; explain which node estimates state.

## 2. Data-flow diagram and TF

Draw your **actual** data flow from Gazebo sensors through bridges and ROS nodes to mapping, localization, costmaps, planning/control, `/cmd_vel` and robot motion. Label important arrows with topic names. Show the mapping phase and the saved-map navigation phase separately (or label mutually exclusive nodes).

Identify who supplies each transform in `map → odom → base_footprint → base_link → sensor frames`, and explain how TF lets a scan be placed on a map. Which transform changes when you initialize AMCL? Why must SLAM, AMCL and a ground-truth localizer not all publish the same global transform?

## 3. What is actually fused?

Inspect the **installed** `config/ekf.yaml` in your selected workspace and the running EKF node. Identify its input topics and **enabled state components** in each configuration mask, not just sensor names. Explain how the estimate is produced from these inputs. Does the baseline use absolute IMU heading, yaw rate, linear acceleration, wheel encoder odometry, or command-derived dead reckoning? Support your answer from the configuration/script, rather than assumptions about a typical robot.

Does the running baseline EKF consume LiDAR, images or GPS in your run? Distinguish it from Step 9's separate supplied offline position filter, which does consume GPS. If not, where are those measurements used, if anywhere? Distinguish EKF state fusion from SLAM scan matching and AMCL scan-to-map localization. Explain why camera or GPS messages appearing in `ros2 topic list` do not establish fusion.

## 4. Mapping versus localization

What measurements and transforms does SLAM Toolbox use to estimate a map/trajectory? What does an occupancy-grid cell represent? Show a revisit and explain the result you observed; do not claim loop closure from a screenshot alone.

After saving the map, what changes when SLAM stops and AMCL starts? Explain AMCL's use of the saved map, laser measurements and motion information, and why a reasonable initial pose and scan alignment matter. Identify the roles of `map`, `odom` and robot frames. Explain how your own saved-map origin can differ from Gazebo world coordinates.

## 5. From goal to motion

Trace one goal: map-frame destination → global costmap and planner → path → local costmap and controller → velocity command → simulated drive. Identify the configured global planner, search method and local controller from `nav2_goosebot.yaml`. Explain global versus local planning, occupancy versus inflated cost, and what live scans contribute.

Show evidence that two goals and return home succeeded **in each world**. For the IST barrier, describe what actually happened: detection, path change, local avoidance, recovery, stop or failure. What evidence supports your explanation? A changed robot trajectory alone does not identify which algorithm replanned.

## 6. Indoor/outdoor observations and limits

- **IST LiDAR:** baseline/changed setting, controlled conditions, two screenshots, measured/visible difference, and any limitation. Did you inspect scans only or also retest mapping/navigation? State this explicitly.
- **Campus GPS:** include the comparison plot and error table from [Step 9](README.md#9-part-b--gps-fusion-comparison). Identify A (existing odometry/IMU) and B (supplied offline 2-D GPS position fusion); discuss both unmodified and deliberately scaled prediction cases. State that known Home pose/heading initializes both, truth is only for scoring, and the plot does not establish improved SLAM/Nav2. Give a reason for GPS helping or hurting in your recorded run.
- **Comparison:** what changed between the indoor and outdoor routes (structure within sensor range, map coverage, localization or planning difficulty)? Ground the comparison in observations.
- **Reality gap:** explain at least two limits, including the simulated GPS/teaching scale or command-derived odometry, and what would require validation on physical Goosebot.
- **Reproducibility:** identify your branch/revision, maps, chosen goals/home, changed settings and one diagnosed problem/fix. List each member's contribution and briefly state how AI assistance was verified if used.

## How the 30% explanation component is assessed

| Criterion | Project percentage points |
|---|---:|
| Accurate sensors/topics/frames and evidence-backed data-flow diagram | 8 |
| Correct EKF inputs, TF ownership, mapping/localization distinction | 10 |
| Correct goal-to-motion explanation and blocked-route interpretation | 6 |
| Thoughtful sensor comparisons, indoor/outdoor observations and limits | 6 |

Specific, correct statements about your tested configuration earn credit. Unsupported claims that all sensors are fused together, GPS replaced the map, or simulation proves hardware readiness do not.
