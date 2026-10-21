# Lab 4 - SLAM Experiment Record

## Required Kalman-filter experiment

Record the seed, data files, state/measurement definitions, matrix dimensions/units, initial conditions, and your independent one-step expected/observed values.

| Configuration | Q and R values | Prediction before running | Position RMSE (m) | Maximum position error (m) | Observed response/uncertainty |
|---|---|---|---|---|---|
| Model trust | | | | | |
| Measurement trust | | | | | |
| Balanced | | | | | |

For the dropout run, identify the fixed configuration, prediction, error/uncertainty during the missing interval, and recovery evidence. Compare raw and filtered errors on the same available-sample mask. Link your runner and plots; explain why the reference was used only for evaluation.

## Input and configuration check

| Scan topic/type/frame | Rate over 10 s | Two timestamps | Observed publisher/bridge and consumer | Base/odom/map frame parameters | Map resolution (m/cell) |
|---|---|---|---|---|---|
| | | | | | |

Record the sensor-to-base-to-odom TF chain and the actual start pose. Explain how you verified advancing time and changing odometry before mapping.

## Plan before running

| Run | Route sketch / region order | Single factor changed | Speed policy / duration target | Revisit plan | Predicted outcome |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |

Record world, configuration file, initial pose, and reset method held constant.

## Results

| Run | Duration (s) | Wall 1 endpoints / length (m) | Wall 2 endpoints / length (m) | Reference errors or between-map differences (m) | Missing/duplicated regions | Revisit evidence |
|---|---|---|---|---|---|---|
| A | | | | | | |
| B | | | | | | |

Identify the independent reference source, or explicitly label results as consistency rather than accuracy. Explain endpoint-selection uncertainty and deviations from each route plan.

## Selected map handoff

Record the selected YAML and image paths, selection evidence, limitations, and saved-map starting pose for navigation. Verify the copied YAML's image reference. In Lab 5 record whether it loads and supports localization.

## Engineering questions

Answer Questions 1-3 from the README using your evidence.
