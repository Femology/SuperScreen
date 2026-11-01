# Windows virtual-display driver track

**Current status (2026-11-01): NOT IMPLEMENTED / NOT TESTED.**

SuperScreen currently contains a first-party Windows **screen-streaming host**, not a first-party Windows **Indirect Display Driver (IDD)**. It mirrors an existing enumerated monitor. Installing an Android APK cannot enumerate a new Windows monitor or change the existing SuperDisplay driver.

## Engineering foundation

- Microsoft's [Indirect Display Driver overview](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/indirect-display-driver-model-overview) describes how Windows enumerates a virtual monitor and hands frames to a UMDF IddCx driver.
- Microsoft's [IndirectDisplay sample](https://github.com/microsoft/Windows-driver-samples/tree/main/video/IndirectDisplay) demonstrates monitor enumeration and swap-chain frame processing but contains major TODOs and is **not** a production-ready driver.
- [VirtualDrivers/Virtual-Display-Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver) is a maintained open-source MIT-licensed implementation with published signed Windows builds. It is a promising **external** virtual-monitor provider. Its code and binary are **not** part of this SuperScreen repository.

Do not call the streaming Python host an IDD. Do not silently install a driver, disable driver-signature requirements, alter Windows boot configuration, or mark a virtual monitor primary on a system without a working recovery screen.

## Integration we can build without owning a kernel driver

1. Install the independently signed upstream VDD via its official instructions **only when a physical recovery display is available**.
2. Enumerate monitors from SuperScreen's existing `/api/monitors` endpoint.
3. Let the user choose the VDD-created monitor from the existing viewer UI, then capture and stream only that monitor.
4. Explicitly distinguish `mirror (existing display)` vs `extend (VDD-created display)` and verify the new monitor is in **Extend**, not Duplicate, mode.
5. Next, add a Windows companion API for dynamically attaching/removing **only SuperScreen-owned displays**; changing any other drivers is out of scope. Gate all privileged operations behind informed consent and rollback.
6. Create a true SuperScreen IDD fork only after a Win10/11 WDK build environment and hardware tests exist, keeping the upstream licence and notices.

## First-party driver acceptance criteria (not met)

- Build using Visual Studio + Windows Driver Kit on supported Windows versions.
- Enumerate exactly one virtual display after authorized enable; remove it on disable.
- Safely process IddCx swap-chain frames and handle GPU reset, sleep/restart and hotplug.
- Produce signed, verifiable driver packages with uninstall/rollback.
- Capture and stream the correct display with phone unplug/replug 20 times.
- Ensure Windows login and recovery without a physical monitor **before** claiming screenless rescue.
- Add device-based end-to-end test results, not just static unit tests.

## Useful read-only assessment

When you have a usable Windows console, run `powershell -ExecutionPolicy Bypass -File scripts/driver-readiness.ps1` and review the output. The script reads system state only. It does not install or change drivers.

## Current no-TV constraint

If SuperDisplay is installed but its *Android* viewer is blocked by an expired trial, our existing Android viewer cannot speak to SuperDisplay's host. The local USB-tether experiment added to SuperScreen requires the **SuperScreen Windows host** to be installed and running beforehand. This cannot be accomplished by an Android-only update tonight.

**Do not change the primary display or install untested virtual-display drivers while the only physical display is unavailable.**
