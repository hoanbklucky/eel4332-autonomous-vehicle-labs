# Gazebo Fundamentals Practice

Complete this guided practice before Lab 01. It assumes ROS 2 Jazzy, Gazebo Harmonic, and `ros_gz` were installed in the main [Lab 00 setup](README.md).

## Learning Objectives

By the end of this practice, you should be able to:

- distinguish Gazebo, ROS 2, and RViz2;
- identify worlds, models, links, joints, visuals, collisions, inertial properties, and sensors;
- pause, play, reset, and inspect a simulation;
- recognize simulation time and real-time factor;
- inspect the Gazebo Transport graph;
- explain why a ROS–Gazebo bridge is needed;
- make and verify one controlled change to an SDF world.

## Background — Three Tools with Different Jobs

Gazebo, ROS 2, and RViz2 often run together, but they are not the same program.

| Tool | Main job | Typical evidence |
|---|---|---|
| Gazebo | Simulates a 3-D world, rigid-body motion, contacts, and sensors | a model falls, collides, or moves in the world |
| ROS 2 | Connects autonomy software through nodes, messages, services, actions, and parameters | nodes and typed topics appear in the ROS graph |
| RViz2 | Visualizes ROS messages and coordinate frames | a map, scan, path, robot model, or TF tree appears |

Gazebo does not automatically make every value available to ROS 2. Gazebo Transport and ROS 2 are separate communication systems. A `ros_gz_bridge` process translates selected message types and topics between them. A bridge is therefore an explicit interface, not a second simulator.

### The Gazebo model hierarchy

- A **world** contains the complete scene, physics settings, lights, and models.
- A **model** is an object such as a robot, wall, or box.
- A **link** is one rigid body within a model.
- A **joint** constrains the motion between links.
- A **visual** controls what an object looks like.
- A **collision** controls the geometry used for contacts.
- **Inertial** properties describe mass and resistance to rotation.
- A **sensor** is normally attached to a link and generates simulated measurements.
- A Gazebo **system plugin** adds behavior such as physics, sensors, or joint control.

These elements are normally described using SDF, an XML-based simulation-description format. A visually convincing model can still behave incorrectly if its collision or inertial properties are wrong.

### Simulation time

Gazebo advances **simulation time** while the world is playing. Pausing Gazebo stops simulation time even though your computer's wall clock continues. The **real-time factor** compares simulated elapsed time with wall-clock elapsed time. A value near `1.0` means one simulated second takes about one real second; a lower value means the simulation is running more slowly.

ROS nodes that process simulated sensors should normally use the Gazebo clock consistently. Mixing wall time, stale data from an older run, and reset simulation time can cause timestamp and TF errors.

## Practice 1 — Open and Inspect the Course World

From the repository root, run:

```bash
source /opt/ros/jazzy/setup.bash
gz sim -v 4 lab00_setup/worlds/gazebo_practice.sdf
```

The world contains:

- a gray ground plane;
- a static blue wall;
- a red dynamic box initially above the ground;
- a green reference marker at approximately `x = -2 m`, `y = -1 m`.

In the Gazebo window:

1. Find the **play/pause** control. Play the world and observe the red box fall under gravity.
2. Pause the world and confirm that the simulated scene stops changing.
3. Use the camera controls to orbit, pan, and zoom. The exact mouse bindings are shown in the Gazebo interface and may depend on the selected camera tool.
4. Open the **Entity Tree** if it is hidden. Select `red_dynamic_box`, `blue_wall`, and `ground_plane` one at a time.
5. Inspect each entity's pose. Notice that a pose has position `(x, y, z)` and orientation `(roll, pitch, yaw)`.
6. Reset the world and verify that the red box returns to its original pose.

Do not continue until you can reliably play, pause, reset, select an entity, and move the camera.

## Practice 2 — Read and Modify SDF

Do not edit the course copy. Make a working copy:

```bash
cp lab00_setup/worlds/gazebo_practice.sdf ~/eel4332_gazebo_practice.sdf
```

Open the copied file in a text editor. Find:

```xml
<model name="red_dynamic_box">
  <pose>0 0 1.5 0 0 0</pose>
```

The six pose numbers are `x y z roll pitch yaw`, using meters and radians. Change only the box's `x` value from `0` to `-1`, save, and launch the copy:

```bash
gz sim -v 4 ~/eel4332_gazebo_practice.sdf
```

Verify that the red box begins one meter farther in the negative x-direction. Close this second simulation before continuing; running multiple worlds with overlapping names makes troubleshooting harder.

Record the original pose, modified pose, and what changed visually. This is a controlled experiment: one input changed while the rest of the world remained constant.

## Practice 3 — Inspect Gazebo Transport

Launch the original practice world again and keep it open. In a second Ubuntu terminal, run:

```bash
gz topic -l
gz service -l
```

These lists belong to Gazebo Transport, not ROS 2. Find the clock topic:

```bash
gz topic -l | grep clock
gz topic -i -t /clock
```

Echo a few clock messages, then stop with `Ctrl+C`:

```bash
gz topic -e -t /clock
```

Repeat while Gazebo is playing and paused. The simulation-time values should advance only while the world is playing.

World-specific topics and services include the world name `eel4332_gazebo_practice`. Names can differ in other worlds, so discover them with `gz topic -l` and `gz service -l` instead of guessing.

## Practice 4 — Bridge the Gazebo Clock to ROS 2

First compare the two communication graphs:

```bash
ros2 topic list
gz topic -l
```

Seeing `/clock` in Gazebo does not guarantee that it is available to ROS 2. Start a one-way Gazebo-to-ROS bridge in a third terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
  '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
```

Keep the bridge running. In another terminal, verify the ROS topic:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic info /clock --verbose
ros2 topic echo /clock --once
```

The bridge syntax used here means:

- `/clock` is the topic name;
- `rosgraph_msgs/msg/Clock` is the ROS message type;
- `gz.msgs.Clock` is the Gazebo message type;
- `[` requests Gazebo-to-ROS communication.

Stop the bridge with `Ctrl+C`. Gazebo can continue simulating, but ROS 2 no longer receives new clock messages through that bridge. Later course launch files create several bridges automatically. Lab 01 also makes one TF bridge explicit so you can see exactly how Gazebo motion reaches ROS localization and visualization.

## Practice 5 — Connect the Concepts to a Robot

Before launching TurtleBot, be able to explain this chain in your own words:

```text
SDF world and robot model
        ↓
Gazebo physics and simulated sensors
        ↓  selected ros_gz bridges
ROS 2 topics and coordinate transforms
        ↓
RViz2, localization, planning, and control nodes
```

A failure at a lower layer can appear as a higher-layer symptom. For example, a robot may move in Gazebo but remain stationary in RViz2 when its motion transform is not bridged into ROS 2.

## Required Evidence

Submit or show the instructor:

- one screenshot of the practice world with the Entity Tree visible;
- the original and modified red-box poses;
- output showing `/clock` in the Gazebo topic list;
- output from `ros2 topic echo /clock --once` while the bridge is running;
- two or three sentences explaining the different jobs of Gazebo, ROS 2, and RViz2.

## Success Criteria

- [ ] play, pause, reset, camera movement, and entity selection demonstrated;
- [ ] world, model, link, visual, collision, inertial property, sensor, and plugin described;
- [ ] one SDF pose changed and verified;
- [ ] simulation time observed while playing and paused;
- [ ] Gazebo and ROS topic graphs compared;
- [ ] one Gazebo-to-ROS bridge launched and verified;
- [ ] required evidence saved.

## Troubleshooting

- Run all Linux, ROS, and Gazebo commands in Ubuntu/WSL, not PowerShell.
- Close extra Gazebo instances before retrying a world.
- If `gz` is not found, return to Part 3 of [Lab 00](README.md).
- If `ros2` is not found, source `/opt/ros/jazzy/setup.bash`.
- If the bridge package is missing, install `ros-jazzy-ros-gz`.
- If `/clock` does not advance, confirm Gazebo is playing.
- If a model is visible but passes through another object, inspect its collision geometry rather than only its visual geometry.

## Official References

- [Gazebo Harmonic: Getting Started](https://gazebosim.org/docs/harmonic/getstarted/)
- [Gazebo Harmonic GUI](https://gazebosim.org/docs/harmonic/gui/)
- [Building your own world with SDF](https://gazebosim.org/docs/harmonic/sdf_worlds/)
- [Gazebo sensors](https://gazebosim.org/docs/harmonic/sensors/)
- [ROS 2 integration and bridge syntax](https://gazebosim.org/docs/harmonic/ros2_integration/)

The course README remains authoritative for required commands, versions, and deliverables.
