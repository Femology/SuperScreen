# Optional Virtual Display Driver integration (advanced / experimental)

The Phase 1 SuperScreen viewer **does not create a Windows monitor by itself**. It streams an existing enumerated monitor. An optional, **separate** virtual display driver can enumerate a real extra Windows screen; SuperScreen may then capture that screen by selecting its monitor index.

## Why this exists

The target HP laptop has a damaged built-in LCD and may not retain the LG HDMI TV as an active monitor when HDMI is unplugged. A virtual monitor is a potential way to supply a persistent Windows desktop that SuperScreen can stream to the phone. This integration has **not been validated on the target hardware**, and changes to display drivers can temporarily make a system unviewable.

## Upstream driver

- [Virtual Display Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver), MIT licence (checked root LICENSE on 2026-10-31).
- Install **official signed releases** and **Virtual Driver Control (VDC)** according to upstream instructions. Do not silently download/install drivers inside SuperScreen.
- This driver remains a separate component with its own maintainer, version, installation/update process and recovery procedures. It is not bundled or modified in SuperScreen.

## Safe evaluation plan

1. **Keep the working LG TV connected** and confirm it shows your Windows desktop. Back up files.
2. Create a restore point where supported. Read the upstream driver's uninstall/black-screen recovery guidance **before installation**.
3. Install the driver and virtual display using upstream signed installer/VDC with explicit administrator consent. Do **not** select the virtual screen as the Windows primary display yet.
4. In **Windows Settings → System → Display**, choose **Extend these displays** (not Duplicate). Use **Identify** to note the new virtual monitor's number; test by moving a harmless window to it.
5. Start SuperScreen and use the phone viewer to select that virtual monitor from the dropdown. If it shows your moved window, the pipeline is using a **real extended Windows monitor** created by the third-party driver.
6. Only after repeatable results should you test disconnection of HDMI. Keep TV available as a recovery fallback.
7. Disconnect/reconnect the viewer 20 times. Record whether Windows windows return to a visible display after a disconnect.

## Hard limits of current integration

- SuperScreen does **not** automatically install or remove the driver, negotiate its resolution, switch Windows primary display, recover disconnected windows, or inject touch input.
- Virtual display driver support does not imply capture will work on all hardware/driver combinations.
- No unattended startup or working Windows sign-in screen is guaranteed.
- **If video goes blank, immediately reconnect the TV** and restore the last safe display configuration.

## Recovery

Follow [the upstream recovery instructions](https://github.com/VirtualDrivers/Virtual-Display-Driver#-important-before-updating-drivers). An incorrectly prioritized virtual display can make a physical display look black. Use Windows Display settings or Safe Mode to uninstall the virtual driver if needed. Never disable Windows security or force unsigned kernel drivers just to make the proof of concept work.

Future native SuperScreen releases must implement driver lifecycle management, automatic monitor identity and rollback only after extensive Windows hardware testing.
