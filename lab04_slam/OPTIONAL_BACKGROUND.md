# Optional Background - SLAM

This file is a reference, not a prerequisite reading assignment or an additional deliverable. Use the [lab manual](README.md) for required work. Lecture and homework develop the mathematics; the lab applies the concepts through configuration, implementation of a mission client, and measured simulation experiments.

## Find an explanation

- **Frames, TF, and architecture:** how scan coordinates become map coordinates.
- **Sensor quality and timing:** why a live topic can still carry unusable data.
- **Mapping and SLAM:** occupancy grids, uncertainty, drift, and loop closure.

## Frames, TF, and System Architecture

A practical autonomous system is not one monolithic program. Sensor drivers, state estimation, mapping, planning, and control are commonly separated into components that exchange typed messages.

Lab 1 introduced the core ROS 2 and Gazebo tools using small systems, Lab 2 provided direct experience with TurtleBot motion, and Lab 3 explained that motion mathematically. This lab now applies those foundations to a realistic autonomy graph. ROS 2 is the instrumentation and integration layer that lets you inspect how sensing, localization, planning, and control interact.

### Why simulate this system?

Gazebo supplies a repeatable world, robot motion, contacts, and sensor measurements. ROS 2 carries selected simulated data to autonomy nodes, while RViz2 displays ROS messages and transforms. Keeping these roles separate is essential when diagnosing a failure: a correct 3-D scene does not prove that ROS receives the data, and a visible RViz2 map does not prove that Gazebo physics is running.

Simulation also provides controlled starting poses and repeatable obstacles, so observations can be compared across students and trials. It does not prove that the same rates, noise, traction, latency, or calibration will occur on Goosebot. Treat simulator outputs as measurements from a model and validate physical assumptions before deployment.

### Data, time, and frames

Every useful sensor message needs more than numeric values. Its message type defines the fields and units, its timestamp says when the measurement applies, and its frame ID says where the measurement is expressed. TF connects those frames over time. A topic can therefore be publishing at a healthy rate while still being unusable because its timestamps or frame chain are wrong.

### What TF does: connect different coordinate systems

A **coordinate frame** is an origin plus directions for its axes. A point described as "2 m ahead" needs a frame: ahead of the LiDAR, ahead of the robot, or along the map's x-axis? Those can be different directions and start at different locations.

A **transform** describes the position and orientation of one frame relative to another. ROS 2's **tf2** library stores these relationships over time and lets a consumer convert coordinates between connected frames. In this lab, **TF** refers to this transform system. Nodes publish frame relationships; consumers such as RViz2 and navigation nodes use them to interpret data together.

#### Example: placing a LiDAR detection on the map

Consider a simplified top-down example, using metres:

1. A LiDAR detects an obstacle 2.0 m along its own positive x-axis.
2. The LiDAR is mounted 0.2 m ahead of the robot base, with the same axis directions. The obstacle is therefore 2.2 m ahead of the base.
3. The base is at map coordinates (3.0, 1.0), facing along the map's positive y-axis. The same obstacle is therefore at map coordinates (3.0, 3.2).

The sensor measurement, mounting offset, and robot pose supply different pieces of information. TF connects the frames so a consumer can combine them. Without the mounting transform, the consumer cannot correctly place the scan relative to the robot. Without the robot-to-map chain, it cannot place that scan on the map. Merely changing a message's `frame_id` does not convert its coordinates.

#### The frame tree used in this lab

```text
map
  -> odom
       -> base_footprint
            -> base_link
                 -> sensor frames
```

These arrows mean **parent-to-child frame relationships**, rather than sensor-data flow. Exact sensor frame names must be read from the running simulation.

| Relationship | What it contributes | Source in this lab |
|---|---|---|
| `map -> odom` | Global localization correction; can change as localization corrects drift | AMCL |
| `odom -> base_footprint` | Locally continuous robot motion; can accumulate drift | Gazebo motion through the dedicated TF bridge |
| `base_footprint -> base_link` | Relationship between the planar base reference and robot body | Robot model through robot-state publisher |
| Body/joint frames to sensor frames | Sensor mounting positions and orientations | Robot model through robot-state publisher |

A consumer can combine several edges to relate a sensor directly to `map`; a separate publisher for every pair is unnecessary. Fixed mounting relationships normally use `/tf_static`. Changing relationships use `/tf`. A sensor on a moving joint needs changing transforms even though it remains attached to the robot.

#### Why time matters

If the robot turns after a scan was captured, using its current orientation to place the old scan puts obstacles in the wrong locations. Consumers need the transforms valid at the measurement timestamp. tf2 keeps a buffer of dynamic transform history, but a lookup can fail if the requested time is outside that buffer, clocks disagree, or an edge is missing.

#### What TF supplies, and where its information comes from

Localization, odometry, and the robot model determine frame relationships; TF distributes those relationships for other components to use. A connected tree can still contain an incorrect pose or mounting offset. TF connectivity therefore establishes that coordinate conversion is available, while calibration and estimation quality determine whether it is accurate.

In this simulation, the dedicated bridge makes Gazebo's moving pose relationship available on ROS `/tf`. This explains why Gazebo can show motion while RViz2 cannot place the robot correctly: the physics may work even when the ROS frame relationship is missing. Likewise, receiving `/odom` messages does not by itself guarantee that the corresponding TF edge is being published.

**Reading check:** A LiDAR scan arrives normally, but TF has no connection from the LiDAR frame to the robot base. Can RViz2 correctly place the scan in the map frame? Would increasing the scan rate fix the problem?

<details>
<summary>Show answer</summary>

No. The consumer lacks the sensor's position and orientation relative to the robot, so it cannot complete the transformation into the map frame. Increasing the scan rate supplies more measurements without the missing spatial relationship. Restore the correct mounting transform and verify the rest of the chain at the scan timestamp.

</details>

For further explanation, see the official [ROS 2 Jazzy tf2 overview](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Tf2.html).

### Where task execution fits in an autonomy stack

A navigation system answers several *different* questions. **Mission planning** selects the goals and their order (for example, visit pickup A, then delivery B). **Task execution** decides what the robot should do *now* (navigate, wait, recover, or stop). **Path planning** computes a route through free space to a selected goal, and **tracking/control** turns a feasible route into motion commands. Sensing, localization, and mapping supply the information these components need.

A useful conceptual pipeline is:

```text
Mission goals -> Task executive -> Path planner -> Path tracker -> Vehicle
                    ^                 ^                ^
                    |                 |                |
              success/failure    map + robot pose   measured state
                    ^                 ^                ^
                    +------------ sensing and estimation ---------+
```

The arrows represent responsibilities, not necessarily literal ROS topic connections. A high-level decision does not replace the lower-level planner or a safety override. In ROS 2, Nav2 can use a **Behavior Tree** to orchestrate navigation actions (such as planning a path, following it, and recovery); it does not mean every sensor or controller must be implemented as a tree node.

**Reading check:** A robot has a valid map and path but stops because it loses localization. Which component detects invalid state information, which component decides whether to retry or abort, and which component must have authority to stop the motors?

<details>
<summary>Show answer</summary>

The localization/estimation component reports pose validity or uncertainty, and a health or safety monitor checks that the state is usable, including freshness and TF availability. The task executive (for example, a navigation Behavior Tree) decides whether to retry localization, recover, or abort. A safety override with authority over the final motor-command path must inhibit motion when the state is unsafe; a valid map and path alone do not authorize movement.

</details>

## Sensor Quality and Timing

### Why characterize simulated sensors?

Gazebo sensors exercise the same message, timing, frame, recording, and analysis workflow used with hardware. The simulator also allows the robot state and experiment conditions to be repeated. However, simulated noise may be idealized, configured, or absent. Low variation in Gazebo is evidence about the simulation configuration, not proof that a physical sensor will be equally precise.

### Measurement quality

A measurement can differ from the quantity of interest through systematic bias, random noise, quantization, outliers, dropout, and delay. **Accuracy** describes closeness to a reference value, while **precision** describes repeatability. A sensor may be precise but biased, or unbiased on average but noisy in individual samples.

Stationary trials reveal offsets and variation under nominally constant conditions. Controlled-motion trials reveal effects that appear only during dynamics, such as delay, vibration, changing scan geometry, or odometry error. Repeatable conditions and a documented ground-truth source are necessary for a defensible comparison.

### Sampling and simulation time

Message arrival time is not necessarily measurement time. Use message timestamps when available and report how sample intervals are computed. Keep Gazebo playing during collection and ensure the relevant ROS nodes use simulation time consistently. A topic rate alone cannot reveal stale timestamps, gaps, duplicated values, or an incorrect frame.

## Mapping and SLAM

### Why map in Gazebo?

Gazebo provides a fixed world that can be explored repeatedly with controlled trajectories. SLAM does not receive the world file as a map: it must infer occupancy from bridged range measurements, odometry, and coordinate transforms. This separation lets you compare the map produced by the autonomy stack with the known simulated environment.

A clean Gazebo world does not guarantee a clean map. Fast turns, sparse observations, odometry drift, timestamp mismatch, poor sensor frames, and missed loop closures can all distort the result. Simulation makes these causes easier to reproduce, but it usually underrepresents physical vibration, wheel slip, reflective surfaces, and calibration error.

### Occupancy grids and SLAM

An occupancy grid divides the planar environment into cells representing free, occupied, or unknown space. Resolution trades spatial detail against memory and computation. Mapping estimates the environment when pose is known; localization estimates pose in a known map; SLAM estimates pose and map together, coupling errors in the two results.

LiDAR observations constrain nearby geometry while odometry connects observations over motion. Reobserving a distinctive area can create a loop-closure constraint that reduces accumulated drift. It can also produce a bad correction when data association or transforms are wrong, so inspect both the map and the robot trajectory.

### Frame and time contract

A typical mapping chain connects `map`, `odom`, the robot base, and the LiDAR frame. Each transform has a specific owner; publishing competing versions of the same transform can make the tree unstable. Sensor timestamps must be transformable at the time of each scan, and all simulation nodes must use a consistent clock.

### How occupancy probabilities become a useful map

For each grid cell \(m_i\), an occupancy-grid mapper represents a belief such as \(P(m_i=\mathrm{occupied}\mid z_{1:t},x_{1:t})\), given sensor readings \(z\) and estimated poses \(x\). A common implementation updates **log-odds** rather than multiplying probabilities repeatedly:

\[
L_t(m_i)=L_{t-1}(m_i)+\log\frac{p_i}{1-p_i}-L_0(m_i),
\]

where \(p_i\) is the inverse-sensor-model occupancy estimate for the current observation and \(L_0\) is the prior log-odds. This is a conceptual update rule, **not an implementation requirement for this lab**. Range beams typically provide evidence of free space along a ray and occupied space near a detected endpoint, subject to sensor limits and model assumptions.

A grid cell marked **unknown** is not automatically free. Navigation may classify occupancy above a threshold as blocked, keep uncertain cells separate, and **inflate** obstacles by the robot's footprint plus a safety margin. At \(0.05\) m/cell, a \(4\) m-wide corridor spans about 80 cells; decreasing the cell size improves detail but increases grid storage and search work quadratically for a fixed 2-D area.

### Why SLAM needs both sensing and localization

Dead reckoning integrates wheel/IMU motion and therefore drifts. Scan matching compares a new observation with earlier observations or the emerging map to constrain relative motion. **Loop closure** adds a constraint when the robot revisits an area, potentially correcting both past poses and map alignment. A false match can instead distort the entire map. Inspect whether an apparent improvement is supported by the scan geometry rather than assuming a closed loop is always correct.

Distinguish the frames: `odom` should provide locally continuous motion estimates, while `map` supplies a globally corrected reference and may shift when SLAM revises its estimate. Plan and display data in compatible frames; do not treat a discontinuity in `map -> odom` as the wheels physically teleporting.

### Connection to mission planning and path planning

A planner usually consumes a **costmap**, not only a pretty occupancy-grid image. Costmaps distinguish traversable, dangerous, occupied, and sometimes unexplored areas. A mission may be impossible because the map is incomplete, the goal lies inside inflation space, or localization is uncertain—even when there is an apparent visual gap. Better exploration trajectories improve both future mapping quality and the availability of feasible paths.

**Reading check:** If an aisle is 0.7 m wide but the vehicle is 0.6 m wide, why might a planner still reject it? Consider localization error, grid resolution, and clearance margins.

<details>
<summary>Show answer</summary>

Even when perfectly centered, the vehicle has only (0.7 - 0.6) / 2 = 0.05 m of clearance on each side. Localization error and required clearance margins can consume that space. Grid discretization can also represent the aisle as narrower than its physical width. With the configured footprint, obstacle inflation, and collision rules, the planner may therefore find no traversable passage. Compare the physical width with the mapped free width and the clearance required by the configured footprint and margins.

</details>

## From TurtleBot to Goosebot

TurtleBot is a differential-drive simulation platform. Goosebot has four conventional wheels on fixed parallel axes and turns through different left/right velocities with tire scrub and slip. ROS interfaces, TF, SLAM, and Nav2 concepts transfer, but the physical footprint, encoder interpretation, effective turning geometry, sensor mounting, motor mapping, speed limits, noise, and stopping behavior require hardware validation. A successful simulation is not permission to reuse unvalidated motor commands.

## Required estimation experiment

The [Kalman-filter experiment](ALGORITHM_EXPERIMENT.md) is required. Implement its predict/update TODOs using the assigned lecture equations and compare normal/dropout behavior. This supporting file is optional reading; the implementation and experiment are not. The estimation and covariance explanations in the [navigation background](../lab05_navigation/OPTIONAL_BACKGROUND.md#estimation-and-localization) can help.

## Optional sensor characterization

The previous [sensor characterization exercise](../optional_legacy/previous_lab_sequence/lab05_sensor_characterization/README.md) includes statistics practice and collapsed conceptual answers. It can support lecture or an optional investigation; it adds no required submission to this lab.
