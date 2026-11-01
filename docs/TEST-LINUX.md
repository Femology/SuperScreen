# Ubuntu/Linux acceptance test — November 2, 2026

**Purpose:** Validate the SuperScreen first-party Android receiver, paired Windows/Linux Python host transport, and USB-tether networking on a Linux laptop **without claiming Windows driver compatibility**.

**Status:** Linux network-adapter discovery source/tests added; **no phone/Linux hardware test yet**. Existing video capture uses Python MSS, which typically requires an X11 display session. A GNOME Wayland session may fail or capture only XWayland windows.

> Only install software or drivers on a workplace laptop if authorized. No system-level changes are needed for the basic SuperScreen mirror test. Do not stream confidential work information: this experimental preview uses unencrypted HTTP/WebSocket, even when the network is private.

## A. Test our own SuperScreen first (no system display driver)

### 1. Check your desktop

```bash
echo "Session: $XDG_SESSION_TYPE"
python3 --version
ip -br -4 addr
```

Use Python 3.11+. If `$XDG_SESSION_TYPE` is `wayland`, the current MSS screenshot backend may not work. For this experiment only, use an available X11/Xorg session if allowed (log out, choose an Xorg session from the login menu). Do not alter system display settings on a managed device without permission.

### 2. Clone, install and unit test

```bash
git clone https://github.com/Femology/SuperScreen.git
cd SuperScreen
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

This should run entirely in the user's home directory; `pip` may need an Internet connection the first time.

### 3. Connect the phone over USB

1. Use a data-capable USB cable.
2. On Android enable **USB tethering** in Settings → Hotspot & tethering. This is **not ADB** and does not require USB debugging.
3. On Linux check `ip -br -4 addr` again. A new USB/RNDIS network interface may appear (`enx...`, `usb0`, `enp...u...`); record its private `10.*`, `172.16–31.*`, or `192.168.*` IPv4.
4. On a corporate laptop, disconnect workplace Wi-Fi before streaming if permitted, or only proceed with IT-approved network isolation. The unencrypted preview otherwise may listen on **every RFC1918 network interface**, including work Wi-Fi.

### 4. Start the SuperScreen Linux experiment

```bash
python -m superscreen
```

Expect a six-digit pairing code and printed local addresses. The dynamic listener checks for new USB-interface addresses about every four seconds. To diagnose a missing screen capture, check `echo $XDG_SESSION_TYPE` and whether MSS lists a display. Use Ctrl+C to stop.

### 5. Open on your phone

**Most reliable first test:** open Android Chrome and navigate to:

```text
http://<LINUX_USB_IP>:8765
```

Replace `<LINUX_USB_IP>` with the Linux USB interface address (NOT the phone's own). Enter the six-digit pairing code from the Linux terminal.

**Next test:** install the debug-signed SuperScreen Android preview built by GitHub Actions, tap **Find SuperScreen Host**, then pair. Do not assume that an Actions preview package exists until the build succeeds; the APK is not a native H.264 decoder.

### 6. Acceptance gates

- [ ] `python -m pytest -q` passes locally
- [ ] USB tether creates a private Linux network interface
- [ ] Linux host logs that it is listening on the USB interface address
- [ ] Chrome connects to `http://<LINUX_USB_IP>:8765`
- [ ] Pairing succeeds, screen is visible and responds to changes
- [ ] SuperScreen Android APK (if available) discovers and displays the same host
- [ ] Unplug/replug USB and reconnect manually without restarting the host
- [ ] No confidential windows were transmitted, firewall/network remains safe

**What passing means:** the Python host + Android viewer + local TCP-over-USB path works on **this Linux computer and phone**. It does **not** verify Microsoft Windows IDD, Windows USB RNDIS drivers, Windows firewall permissions, Windows virtual extended monitor, or headless Windows recovery. The current stream mirrors an already-existing Linux display.

## B. Optional reference comparison — genuine USB extended monitor via UScreen

UScreen is a separate MIT-licensed, Linux-specific project. It uses a host daemon, EVDI Linux virtual display driver, ADB-reversed TCP video, and its own Android APK.

- Repository: https://github.com/majmichu1/UScreen
- Official installation: https://github.com/majmichu1/UScreen/blob/main/docs/installation.md
- Releases: https://github.com/majmichu1/UScreen/releases

**Only with administrator/IT approval and access to a recovery display:**

1. Obtain the matching official Ubuntu/Debian `.deb` package and `uscreen.apk` from **one release** (check SHA256SUMS and read installation/rollback instructions).
2. Install the Linux release as documented (Ubuntu/Debian `sudo apt install ./uscreen_*_amd64.deb`); this may install `evdi-dkms` and modify kernel modules/system files. It may fail on a newer kernel unless the matching evdi source and kernel headers are used.
3. Install the matching `uscreen.apk` on Android. Enable USB debugging, connect USB, accept the computer's authorization prompt.
4. Run `systemctl --user enable --now uscreen`; test `uscreen doctor`. Confirm Linux settings list a **new independent display**, not just a mirror.
5. Move a window onto that new monitor and verify Android touch and reconnect behaviour.
6. Record performance and remove the package according to its uninstall docs if needed.

**Important:** Successful UScreen operation means the **Linux EVDI + ADB + UScreen Android** pipeline works. Our existing SuperScreen APK **cannot** simply connect to UScreen without implementing its independent transport/session protocol. It also does not establish compatibility with the **Windows IDD** we still need to build.

## Reporting results

Write down:

- Linux version and kernel: `lsb_release -a`; `uname -r`
- Desktop/session: `echo "$XDG_CURRENT_DESKTOP / $XDG_SESSION_TYPE"`
- Android OS and phone model
- USB adapter from `ip -br -4 addr` (hide employer-sensitive details)
- Pairing, video frames, reconnect outcome
- If fail: specific terminal error and whether the phone can open `/api/status`

Never post pairing tokens, credentials, internal corporate IP/network layout, or screenshots with sensitive data into a public repository.
