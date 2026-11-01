# Windows 10/11 + Android acceptance test (real hardware)

**Source updated 2026-11-01. Windows CI is now configured to run tests and smoke-test its unsigned EXE. That is not proof that the Windows laptop and Android phone can communicate over USB, nor proof of a virtual monitor.**

For the user's actual goal, the PC must display a usable Windows desktop on Android with **no TV after first successful setup**. Treat these as separate gates; the existing SuperScreen preview meets none of the headless/IDD gates yet.

## A. Safe baseline: existing monitor mirrored over USB

Requires a **working Windows display for initial setup**; do not attempt installing virtual-display drivers on an already screenless laptop.

1. On a Windows 10/11 PC with a visible desktop, download the preview's Windows host and Android debug APK from an **actually passing** GitHub release, and verify checksums. The release is experimental and unsigned.
2. Windows: start `SuperScreen-Windows.exe` or use `scripts/run-windows.ps1` in the repo; allow the executable on **your own trusted network only**, as appropriate. The terminal shows a 6-digit pairing code. Note that first-time pairing requires access to this code.
3. Android: connect a data-capable USB cable and enable **USB tethering**. This uses IP-over-USB; it is **not** SuperDisplay USB/AOAP and does not depend on its driver.
4. Windows: run `ipconfig` or `Get-NetIPAddress -AddressFamily IPv4` to identify its USB/RNDIS adapter IP, e.g. an RFC1918 IP assigned by the phone (the actual address varies). The host's listener should log a matching `http://IP:8765` within a few seconds.
5. Android: open `http://WINDOWS_USB_IP:8765/api/status` in Chrome. A JSON status naming `SuperScreen` demonstrates network reachability, **not** screen-stream success.
6. Open the SuperScreen Android APK, use **Find SuperScreen Host** or enter the Windows USB IP manually, then pair with the one-time code visible on Windows.
7. After pairing, open a harmless window on Windows. Verify it appears and updates on the Android viewer. Record image lag, FPS, orientation, resolution, disconnect/reconnect, and whether the laptop's keyboard and touchpad continue to work.
8. Switch off mobile data during the test to demonstrate **local USB** traffic, then reconnect USB 5 times. Test after a normal Windows user sign-in, not on the locked/BIOS screen.

### If the phone cannot see Windows

- Verify USB tethering **is ON** and a new Windows IP adapter exists.
- Verify the SuperScreen **Windows host** is running; a SuperDisplay driver alone cannot communicate with this app.
- Verify both endpoints use the same USB local network and that TCP **8765** is permitted by the host firewall on that specific trusted profile. **Do not** disable Windows Firewall.
- If discovery fails, open the local `/api/status` URL by the actual USB IP rather than guessing, and enter the address manually.
- If `/api/status` loads but frames fail, inspect display enumeration and capture permissions and check whether the selected monitor still exists.
- The current service listens on all detected RFC1918 host addresses. Avoid running it on any workplace or shared private Wi-Fi; a private IP alone is **not** proof of network trust.

## B. Real extended virtual monitor: separate Windows IDD test

Microsoft's Indirect Display Driver model:
https://learn.microsoft.com/en-us/windows-hardware/drivers/display/indirect-display-driver-model-overview

Open-source signed virtual-display baseline:
https://github.com/VirtualDrivers/Virtual-Display-Driver

This baseline can create an independent monitor for applications to capture; it is **not bundled** with SuperScreen. Follow its official install and recovery instructions and confirm licenses/signatures.

**Only while a second physical display/TV is available for recovery:**

1. Establish a **working mirror** on your phone first.
2. Read the upstream VDD uninstall/Safe Mode recovery instructions before using its official signed installer; create a restore point where supported.
3. Install VDD with explicit permission. Do not change the primary Windows display.
4. Confirm Windows Display Settings enumerates a VDD-created additional monitor in Extend mode and record the monitor index.
5. In SuperScreen's Android viewer, select that new virtual monitor. Move a harmless window onto it and confirm it appears on the phone.
6. Test USB disconnect 5 times, host crash/restart, and normal reboot **with the TV still connected**. Document any loss of access. This remains an integration with a third-party signed VDD, not a custom SuperScreen IDD.

## C. Windows screenless rescue / login-screen gate

**NOT IMPLEMENTED.** The Python host starts in a user session; it does not capture BIOS/secure login, auto-pair an unconfigured Android device, or create a virtual monitor. If Windows has no usable enumerated display, it may send no frames. A functional mirror or virtual-display CI test does **not** imply this gate passes. Configure after-login autostart only after the user has logged in manually and verified a working connection.

Do not unplug the only reliable display until all required functionality is demonstrated.

## D. What GitHub CI validates vs. what it cannot

| Check | GitHub Windows runner | Real PC + Android |
|---|---:|---:|
| Python host unit/integration tests | yes (workflow configured) | additionally recommended |
| Local adapter detection API | yes | yes |
| Portable EXE packaging and --help startup | yes (workflow configured) | actual stream still needed |
| Genuine USB-tether network hardware | no | required |
| Android MediaCodec / touch | not implemented | future |
| Windows IDD monitor enumeration | not installed in CI | required |
| Headless Windows rescue, sign-in/lock screen | no | required |

A CI workflow configuration is not a CI success result. Verify the latest Actions run passes before downloading a release or claiming that Windows works.

## E. Record evidence without exposing personal/corporate data

- Windows version/build and architecture (no device serial numbers)
- Android model and version
- Result of `/api/status`, pairing, animated test window, reconnect count
- USB adapter type and link (omit addresses or redact to avoid sharing network details)
- Whether **mirror** or **real extended monitor** was used
- Screenshot/photo only with no confidential user/work data

**Stop condition:** if a trial causes the Windows display to disappear and you cannot recover it, reconnect a known working monitor rather than making further blind driver changes.
