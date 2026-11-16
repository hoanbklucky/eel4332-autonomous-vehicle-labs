# Simulation workflow index

> **Final-project update:** the required final now uses Goosebot with a student-added LiDAR in IST or campus. Follow [the final README](../final_project_simulation/README.md); TurtleBot commands below apply to Labs 2/4/5. Validate sensor/bridge/TF, LiDAR SLAM, saved-map AMCL/Nav2, and both world variants. The supplied ground-truth mode is used only for the required Goosebot warm-up, not as final SLAM/AMCL evidence.

Follow the self-contained course READMEs. Required commands are included there; ROBOTIS links are references.

| Task | Course instructions |
|---|---|
| Install core and simulation packages | [Lab 00](../lab00_setup/README.md) or [Lab 4 installation](../lab04_slam/README.md) |
| Launch and drive | [Lab 2](../lab02_turtlebot_playground/README.md) |
| Cartographer mapping and map saving | [Lab 4](../lab04_slam/README.md) |
| Saved-map Nav2 navigation | [Lab 5](../lab05_navigation/README.md) |
| Required Goosebot maze warm-up | [Final README, Step 1b](../final_project_simulation/README.md#goosebot-warm-up) |
| Delivery mission and evaluation | [Final](../final_project_simulation/README.md) |

Labs 2/5 and Lab 4's first environment use Waffle in TurtleBot3 World; Lab 4's second environment uses Waffle Pi in House. The final uses its own Goosebot/LiDAR SLAM Toolbox + AMCL/Nav2 procedure in IST or campus. Keep these launch workflows separate.

Use native WSL/Jazzy and the final's workspace for the warm-up and final. Docker and stereo SLAM are optional; complete perfect-map warm-up and final SLAM/AMCL in separate runs.

Lab 4 now maps two environments: World with Waffle, then House with Waffle Pi. Restart cleanly and save separate maps. Lab 5 retains World/Waffle. For Goosebot libexec errors, follow final README Step 1a: check the complete source package, chmod source scripts, rebuild/re-source, and verify `ros2 pkg executables goosebot_0`.
