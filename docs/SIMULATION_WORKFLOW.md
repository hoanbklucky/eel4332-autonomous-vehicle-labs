# Simulation workflow index

> **Final-project update:** the required final now uses Goosebot with a supplied LiDAR in both IST and campus. Follow [the final README](../final_project_simulation/README.md); TurtleBot commands below apply to Labs 2/4/5. Validate sensor/bridge/TF, LiDAR SLAM, indoor saved-map AMCL, dual GPS/RTK-like localization and live outdoor GPS/Nav2. The supplied ground-truth mode is used only for the optional Goosebot troubleshooting warm-up, not as final SLAM/AMCL evidence.

Follow the self-contained course READMEs. Required commands are included there; ROBOTIS links are references.

| Task | Course instructions |
|---|---|
| Install core and simulation packages | [Lab 00](../lab00_setup/README.md) or [Lab 4 installation](../lab04_slam/README.md) |
| Launch and drive | [Lab 2](../lab02_turtlebot_playground/README.md) |
| Cartographer mapping and map saving | [Lab 4](../lab04_slam/README.md) |
| Saved-map Nav2 navigation | [Lab 5](../lab05_navigation/README.md) |
| Goosebot readiness check in the selected IST/campus world | [Final README, Step 4](../final_project_simulation/README.md#goosebot-readiness-check) |
| Optional practice arena and perfect-map Nav2 | [Optional troubleshooting](../final_project_simulation/README.md#goosebot-warm-up) |
| GPS/RTK-like localization comparison and GPS-aided campus Nav2 | [Final Step 9](../final_project_simulation/README.md#9-part-b--gps-fusion-comparison) |
| Delivery mission and evaluation | [Final](../final_project_simulation/README.md) |

Lab 2 and the first environment in Labs 4–5 use Waffle/World; Labs 4–5 also use Waffle Pi/House. The final uses its own Goosebot/LiDAR SLAM Toolbox in both worlds, AMCL indoors and live GPS/Nav2 outdoors. Keep these launch workflows separate.

Use native WSL/Jazzy and the final's workspace for the warm-up and final. Docker and stereo SLAM are optional; if using the optional perfect-map exercise, keep it separate from final SLAM/AMCL.

Lab 4 now maps two environments: World with Waffle, then House with Waffle Pi. Restart cleanly and save separate maps. Lab 5 navigates in both: one World/Waffle goal and two House/Waffle Pi goals in different rooms, using matching saved maps. For Goosebot libexec errors, follow final README Step 1a: check the complete source package, chmod source scripts, rebuild/re-source, and verify `ros2 pkg executables goosebot_0`.
