# Goosebot hardware extension — Optional

## Open in VS Code through WSL

After cloning the repository, open **Windows Terminal / PowerShell**, run `wsl`, then run these commands in **Ubuntu/WSL**:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs
code .
```

Confirm VS Code shows **WSL: Ubuntu** (or your Ubuntu distribution) in the lower-left corner. Open `final_project_goosebot/README.md` in Explorer. Choose **Terminal → New Terminal**; when working from this lab directory, run:

```bash
cd ~/courses/eel4332-autonomous-vehicle-labs/final_project_goosebot
```

Use that Ubuntu terminal for the commands below; follow any later `cd` commands as written. This assumes VS Code is installed on Windows with the **WSL extension**. If the repository is not cloned yet, complete Lab 00's clone step first.

The required final is now the [Autonomous Campus Delivery Robot simulation project](../final_project_simulation/README.md).

Students have already demonstrated autonomous lane following on Goosebot. SLAM and Nav2 deployment on Goosebot is **not required** this semester and is not needed for full credit on the simulation final.

A future hardware extension would revalidate sensing, wheel odometry, timestamps, TF, footprint, motor-command mapping, skid-steer slip, speed limits, and stopping before attempting saved-map navigation. Use the [Goosebot repository](https://github.com/hoanbklucky/goose) only with instructor-validated interfaces and hardware procedures.

Do not assume TurtleBot configuration and motor commands transfer directly to Goosebot.
