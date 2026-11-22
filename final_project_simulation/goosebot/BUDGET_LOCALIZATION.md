# Optional — ordinary GPS + wheel encoders + IMU + 2D LiDAR

**Question:** can LiDAR map matching make an ordinary-GPS localization system more accurate? Record one manual campus drive and compare all estimates on the **same sensor data**. This is optional and ungraded. It measures **offline localization**, not live Nav2 performance; complete the required project first.

| Estimate | Inputs |
|---|---|
| A | Simulated wheel-encoder proxy + IMU gyro |
| B | A + ordinary GPS |
| C | A + ordinary GPS + LiDAR matching against the supplied obstacle map |
| D — control | A + LiDAR map matching, GPS withheld for the whole drive |

C versus B shows the effect of LiDAR; C versus D shows what ordinary GPS adds when LiDAR is available. B/C/D use the same supplied 600-particle filter, motion uncertainty and initial pose distribution. A integrates the same measured motion without position corrections. No RTK topic is recorded or used.

Each particle is a possible robot position/heading. Wheel/gyro motion advances it, GPS weights its position, and LiDAR weights how closely its projected scan endpoints match known obstacle boundaries. The report records the fixed random seed; this is a teaching filter, not a guarantee of robustness.

**Wheel measurements matter:** this activity uses actual wheel-joint angular velocities from `/joint_states`, multiplied by radii read from `/robot_description`. These are a **simulated encoder proxy**, without electronic quantization/noise. The normal course baseline now uses these same measured joints through `/wheel/odometry`; this optional replay implements its own filters. Wheel slip can still make wheel rotation differ from robot travel. The IMU contributes measured yaw rate, not its perfect simulated absolute orientation. Every estimate starts at the known Home pose/heading; a stationary gyro-bias estimate is made before driving.

LiDAR matches against `campus/reference.yaml`, the supplied world-aligned **obstacle** map. It does not match against the artificial road-only mask, which would falsely treat grass edges as physical walls. An accurate prior map is an advantage of this experiment; hardware deployment would need a suitable measured/surveyed map and independent validation.

## 1. Start ordinary-GPS campus — Terminal 1

Stop all previous launches with Ctrl+C. Install the analysis dependencies once:

```bash
sudo apt install -y python3-numpy python3-scipy python3-matplotlib python3-pil
```

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
ros2 launch "$PWD/final_project_simulation/goosebot/world.launch.py" \
  world:="$PWD/final_project_simulation/campus/campus.sdf" gps_profile:=ordinary
```

Keep stationary at fresh Home. Leave SLAM, AMCL, GPS navigation and other teleop processes stopped. The existing baseline EKF may run with the world, but this experiment reads wheel joints directly rather than its filtered output. No new sensor XML or ROS rebuild is needed if the supplied wheel-state bridge is already installed.

## 2. Record — Terminal 2

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
cd ~/courses/eel4332-autonomous-vehicle-labs
python3 final_project_simulation/goosebot/budget_compare.py record \
  --output final_project_simulation/results/budget_localization_run1
```

Wait for **READY**. It checks joint velocities, gyro, ordinary GPS, scans and the sensor mounts. The recorder prints measured wheel travel periodically. Minimum travel is **5 m**; aim for **10–20 m with turns**, near buildings where LiDAR can see mapped structure. Open areas, long featureless walls and repetitive geometry can make LiDAR localization ambiguous.

## 3. Drive — Terminal 4

```bash
source /opt/ros/jazzy/setup.bash
source ~/goosebot_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.81 -p turn:=1.73
```

Use **i** forward, **j/l** turn and **k** stop; reduce speed where needed. Follow paved routes manually. This recorder does not control motion or enforce the road mask. After the loop, press k, wait three simulated seconds, then **Ctrl+C in Terminal 2**. Expect saved `sensors.jsonl`, `metadata.json` and separate evaluation-only `truth.csv`. Use a new output directory for each recording. No special RViz setup is required; watch Gazebo while driving.

**Command breakdown:** `record` saves real sensor messages; `--output` names a new recording folder. No localization or TF is published. If wheel velocities are missing, inspect `ros2 topic echo /joint_states --once` and rerun the main Step 1 setup helper if the bridge is absent; do not substitute `/cmd_vel` or truth.

## 4. Generate the comparison — Terminal 2

```bash
python3 final_project_simulation/goosebot/budget_compare.py report \
  --input final_project_simulation/results/budget_localization_run1
```

Expect **`budget_comparison.png`**, **`budget_comparison_metrics.json`** and **`budget_comparison_estimates.csv`** in that folder. The plot shows trajectories and error over time. The JSON has `metrics → A/B/C/D`, each with `rmse_m`, `final_error_m` and `max_error_m`. Diagnostics show wheel travel and accepted/skipped LiDAR matches. Reports do not overwrite existing outputs.

| Estimate | Horizontal RMSE (m) | Final error (m) | Maximum error (m) |
|---|---|---|---|
| A — encoder + gyro | Your result | Your result | Your result |
| B — A + ordinary GPS | Your result | Your result | Your result |
| C — A + ordinary GPS + LiDAR | Your result | Your result | Your result |
| D — A + LiDAR, no GPS | Your result | Your result | Your result |

Use **your measurements**, not an expected ranking. If C does not improve on B, inspect map alignment, mapped structure, wheel/gyro gaps and skipped scan matches. If C and D are similar, LiDAR plus known starting pose may already provide most of the useful correction on that route. A low final error alone does not establish low error over the whole drive.

## 5. Optional controlled GPS interruption

Replay the **same recording**, withholding GPS only between 10 and 25 simulated seconds after READY:

```bash
python3 final_project_simulation/goosebot/budget_compare.py report \
  --input final_project_simulation/results/budget_localization_run1 \
  --gps-dropout 10 25
```

This writes separate `budget_dropout` outputs and shades the artificial interval. Compare B and C during it; D is the no-GPS control and should be unchanged. Choose a recording longer than the selected interval. This is a **controlled missing-data test**, not simulated real-world multipath, an overhang or hardware GPS failure.

## Interpret carefully

- Ground truth is read **after** all estimates are computed and is used only for scoring at matching timestamps. No trajectory is realigned to truth to improve the result.
- No artificial wheel bias is added in the activity. Simulation joint signals, sensor noise and the geometric prior map are idealized; centimeter-level results would not establish hardware accuracy.
- A supplied likelihood-field particle filter is used, not a production AMCL/GPS stack. Fixed seed 7 makes the replay reproducible; particle depletion, poor geometry, map changes and poor initialization can still cause failure. It does not demonstrate arbitrary-start relocalization.
- GPS can help or hurt; LiDAR cannot guarantee localization in every outdoor scene. The report establishes position-estimation performance on this drive, not obstacle avoidance, road compliance or successful live navigation.
- Historical RTK screenshots used command-derived motion; the current RTK comparison uses wheel/IMU EKF increments and different filters. Do not claim this activity beats RTK by comparing unrelated runs. A fair hardware comparison needs the same route, initialization and evaluation protocol.

**Experiment checks:** inspect wheel-joint velocities, recorder startup, the report and any controlled GPS-withholding replay using your own run. This optional activity has no extra required submission or rubric weight.

The campus is now full horizontal scale. Use matching new world/map assets and a fresh recording; earlier screenshots/results are historical. A local 10–20 m drive is sufficient; do not scale wheel radii, IMU rates, GPS noise or sensor ranges.
