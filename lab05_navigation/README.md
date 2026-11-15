# Lab 5 — Navigate on Your Map

## Mission

Follow the official ROBOTIS navigation tutorial to localize on your Lab 4 map and reach three destinations.

## Prerequisites

Complete [Lab 4](../lab04_slam/README.md) and retain its map YAML/image pair. Select **Jazzy** in the official tutorial.

## Procedure

Run commands in **VS Code's integrated terminal connected to WSL** or a separate **Ubuntu/WSL terminal**. Both work; do not use PowerShell. “Remote PC” in the ROBOTIS instructions means your Ubuntu/WSL computer, not a physical robot.

In each new terminal, after completing the official setup:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
```

Use the same model (**Burger**) and environment (**TurtleBot3 World**) throughout Labs 2, 4, 5, and the final.

1. Stop all applications from mapping with **Ctrl+C**, including Cartographer and teleoperation.
2. Follow [ROBOTIS Navigation Simulation — Jazzy](https://docs.robotis.com/docs/systems/turtlebot3/simulation/navigation_simulation/?ros=jazzy), in order: **Launch Simulation World → Run Navigation Node → Estimate Initial Pose → Set Navigation Goal**.
3. Use the same world/model as mapping. Replace the tutorial's example map path with the **absolute path to your Lab 4 `map.yaml`**. Keep the referenced map image beside the YAML.
4. Initialize the robot pose in RViz2 and check scan/wall alignment. If using teleoperation to refine localization as the tutorial describes, stop and terminate that keyboard node before sending navigation goals.
5. Reach three open-space destinations, one at a time. Record their map-frame x/y coordinates (metres), yaw (radians), outcomes, and approximate simulation-time durations in `answers.md`. Save destinations in `config/goals.csv`.
6. Capture a screenshot showing the map, robot, scan, and planned path. Save the home/start pose and exact launch commands for the final.

Keep the simulator and navigation terminals running while sending goals. Do not run Cartographer or SLAM Toolbox during saved-map navigation, or add the old custom lifecycle-startup/TF-bridge commands.

**Stopping:** use RViz2's navigation cancel control if available and confirm actual stopping in Gazebo. If motion continues unexpectedly, pause Gazebo and end the launch processes before a clean restart. Do not treat a new destination at the current pose as a guaranteed stop.

## What to Submit

- Completed `answers.md` and `config/goals.csv`.
- Map identity/path, home pose, and the navigation configuration path/version used (copy the full file if modified).
- A screenshot and short demonstration of three successful goals.

## Questions

1. How does localization differ from building a map?
2. How does the planned path differ from actual robot motion?
3. What would need validation before using this system on Goosebot?

## Final Handoff

Reuse your map, goals, and working official navigation setup in the [delivery final](../final_project_simulation/README.md). The mission-client scaffold and odometry recorder in `src/` support that project. Separate A*, Pure Pursuit, and safety-monitor exercises are optional.

## Optional Background

[Navigation background](OPTIONAL_BACKGROUND.md) and [algorithm exercises](ALGORITHM_EXPERIMENTS.md).

## Troubleshooting

Check the map path, initial pose, Jazzy tab, sourced workspace, model, and duplicate command publishers before changing parameters. The official tutorial supplies startup instructions; this README supplies the course tasks. The instructor must test the workflow on the course WSL image.
