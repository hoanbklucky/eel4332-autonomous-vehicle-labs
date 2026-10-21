# Lab 5 - Navigation Experiment Record

## Required algorithm experiments

### A*

Record coordinate convention, heuristic, expected/observed feasibility, path validation, cost in cells/metres, and plots for passage-open, passage-closed, empty-grid, start-equals-goal, and invalid-endpoint cases.

### Pure Pursuit

Record model parameters, target-selection method, predictions, and results for both look-ahead distances. Report cross-track RMSE/maximum error, saturation fraction, and trajectory plots. Identify the Lab 3 model version used.

### Safety monitor

Record policy, thresholds/units, and expected-versus-observed states, including boundary cases and invalid inputs. Explain the speed-dependent urgency rule. Link the injected-health sequence to the live mission's STOP/cancellation timestamps and actual stopping evidence. Describe the explicit restart policy.

## Mission definition

Record the selected map YAML/image identity, known map-frame initial pose, three ordered goals, per-goal timeout, success rule, and simulation restart/localization procedure. Describe your mission client's result and cancellation handling.

## Parameter plan before running

| Configuration | Global inflation parameter/value (m) | Local inflation parameter/value (m) | Predicted effect on success, route, duration, clearance |
|---|---|---|---|
| A | | | |
| B | | | |

Record planner/controller plugins and footprint or radius. Explain which factors remain fixed. Include commands and output verifying loaded values.

## Normal trials

| Run | Goals succeeded / 3 | Mission success | Elapsed simulation time (s) | Odom path length (m) | Goal/trajectory log paths | Observed issue |
|---|---|---|---|---|---|---|
| A1 | | | | | | |
| A2 | | | | | | |
| A3 | | | | | | |
| B1 | | | | | | |
| B2 | | | | | | |
| B3 | | | | | | |

Report success counts separately and mean duration/distance only for successful trials, including sample counts. Describe mission-interval selection, units, and odometry limitations. Include a comparison plot.

## Failure and recovery

Before running: define injected-health transition, expected monitor state, cancellation condition, stopping velocity threshold/window, expected response, and manual simulation stop procedure.

After running: record cancellation request, terminal status/time, observed stopping time, residual motion, and evidence of a clean recovery run. Keep this separate from the six normal trials. If using an instructor-approved alternative fault, define its equivalent failure and stopping criteria.

## Engineering questions

Answer Questions 1-4 from the README and recommend a configuration using your data.
