# Create your own Gazebo world (optional)

> The required final uses Goosebot with your added LiDAR. The simple builder below creates environment geometry; use the final README's Goosebot world wrapper with your generated `campus.sdf` and adjacent `mission.json`. The TurtleBot launch examples below are optional reference checks, not the assessed robot workflow.

You may use the instructor's campus world or design your own. Both options have the **same mission requirements and grading**; visual complexity earns no extra credit. Keep the project focused on mapping/navigation.

A **Gazebo world** (`.sdf`) defines 3-D objects, collisions, and sensors' surroundings. A **navigation map** (`.yaml` + image) is the 2-D occupancy representation. First create the world, then run SLAM to map it. Editing only a map image does not change Gazebo.

## 1. Copy the provided world builder

Run from the course repository root:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs/final_project_simulation
cp -r -n campus custom_world
code custom_world/create_simple_world.py
```

The geographic campus builder uses polygon data in `layout.json`. For this beginner guide, edit/run the included **`create_simple_world.py`** instead: it keeps the simpler BOXES/STOPS interface described below and writes a matching `mission.json` that the launch reads.

Do this copy only once. If `custom_world` already exists, keep/edit that directory rather than copying into it again. Work in your own fork.

## 2. Arrange buildings and obstacles

Edit the `BOXES` list. Each entry describes a solid rectangular object:

```python
('library', 5, 2, 3, 4, 1.5, '#806aa7'),
```

| Field | Meaning in the example |
|---|---|
| Name | Unique name: library |
| x, y | Center at (5, 2) m |
| Width, depth | 3 m along x; 4 m along y |
| Height | 1.5 m |
| Color | Hexadecimal display color |

Coordinates are in metres; +x is right and +y is up in the generated overhead plan. Objects are axis-aligned. Keep the four `boundary_...` entries and arena dimensions unchanged for this beginner workflow. Replace the other buildings/lakes with your own layout. Boxes automatically have **both visual and collision geometry**, so LiDAR can observe raised obstacles and the robot cannot drive through them.

A simple project could be a library delivery floor, warehouse, hospital courtyard, or campus. Use a few distinctive obstacles and wide connected routes. Keep obstacles at least 0.5 m high and design passages at least **1.5 m wide**, preferably wider near corners. Do not make a nearly empty arena or an unsolvable maze.

The generator currently also draws campus-style ground strips; these are visual-only and do not constrain driving.

## 3. Set deliveries, home, and the challenge barrier

Edit `STOPS` to contain home plus three delivery locations:

```python
STOPS = [('Home', -8, -11), ('Library', -4, 8),
         ('Office', 6, 6), ('Lab', 6, -9)]
```

Keep **Home at (-8, -11)** for this beginner example. The simple generator writes it to `mission.json`, which the launch reads; this differs from the geographic campus world's home. Keep all pads clear of obstacles. Choose locations that require meaningful travel and turns.

Edit `BARRIER` to obstruct one baseline route while leaving an alternative:

```python
BARRIER = ('route_barrier', -8, -3, 8, .5, 1, '#ed9c25')
```

The barrier is added only to `campus_blocked.sdf`. It must not cover home or a delivery pad. Keep it fixed throughout the obstacle trial. Update any inherited descriptions/labels in your custom documentation to match your design.

## 4. Generate and check

```bash
python3 custom_world/create_simple_world.py
code custom_world/campus_plan.svg
```

This creates the baseline/blocked SDFs, reference occupancy map, and plan **inside your copied folder**. It also checks that all stops are connected with 0.4 m center clearance in both layouts. If an assertion fails, adjust obstacles/stops and rerun. Passing this geometric check does not prove that Nav2 can drive the route.

Keep the generated filenames; the local launch uses them. Do not hand-edit the generated SDF/map and then regenerate, because regeneration overwrites those edits.

The copied `reference_goals.csv` is **not automatically updated** when you change `STOPS`; update it yourself if using the geometric reference map for checks, or leave it unused. Your mission must ultimately use goal coordinates selected on your own SLAM map.

## 5. Launch your world

Stop existing Gazebo, SLAM, navigation, and teleop processes first. In a new Ubuntu/WSL terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/custom_world/campus.launch.py"
```

The copied launch file reads SDF files from its own folder and reuses ROBOTIS's Waffle model, bridges, and TF setup. No extra ROS package build is needed after changing world geometry. Check that Waffle spawns, obstacles appear, LiDAR sees them, and manual driving works.

## 6. Map, navigate, and evaluate

Use the Cartographer, teleop, and map-saving commands in the [campus guide](campus/README.md), but launch your custom world instead. Save the result under a distinct basename, such as `results/custom_map`. Select home and three goals in **that SLAM map's frame**, not from the world-coordinate table.

For the obstacle trial, restart with:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/custom_world/campus.launch.py" world_file:=campus_blocked.sdf
```

Navigate using your original baseline SLAM map; do not remap the barrier. Keep your chosen layout fixed during evaluation. Include your generator, SDFs, layout preview, and world/obstacle description with the project's normal source/configuration deliverables. Do not include Python cache or ROS build files.

This guide provides a simple code-based world builder. Gazebo GUI editing and advanced 3-D modeling are optional, but require saving/retesting matching collision geometry and are unnecessary for this project.
