# SuperDisplay USB interoperability: feasibility decision (2026-11-01)

## Exact user goal

Use an **Android-only SuperScreen app** as the laptop's visible Windows desktop through a USB cable, **without an additional Windows install, TV, dummy plug, second phone, or active SuperDisplay Android trial**. The Windows laptop already has the SuperDisplay Windows host installed and may not have a usable screen for configuration.

## Verdict

**No working compatibility demonstrated. Do not claim an APK or bridge is ready.**

SuperDisplay's Windows host and Android client communicate with a proprietary application protocol. UScreen's Android app is paired to **its own Linux host**, EVDI virtual display, and ADB-reversed TCP stream; simply importing it into SuperScreen does not establish interoperability with the installed Windows SuperDisplay host. An Android USB accessory listener alone is not a display receiver.

### Evidence from the supplied APK (static inspection; not source recovery)

Uploaded APK: `SuperDisplay v1.2.22 (Premium).apk`; SHA256 `c44b5c9de1e551904110e8475a0e1b01748ea239e30584cbfab5b0e05e6792fc`.

- Package: `com.kelocube.mirrorclient`; version 1.2.22, versionCode 67.
- DEX symbols: `AOAPPipe`, `AOAPTransport`, `AOAPTransportListener`, `TCPTransport`, `HostPoller`, `MirrorSession`, `AsyncDecoder`, `SyncDecoder`, `VideoStream`, `Input`.
- USB accessory filters specify manufacturer `Software by KeloCube` and models `superDisplay` / `SuperDisplay` in `res/xml/accessory_filter.xml`.
- Strings referring to handshake and protocol checking exist, but **neither message layout nor successful communication with Windows has been verified**.
- The APK contains Android application code, not the PC virtual-display driver. The filename says Premium and there are indicators of possible repackaging; do not distribute or install this unverified artifact.

SuperDisplay's official help confirms a zero-configuration **Android Open Accessory Protocol (AOAP)** path and an **ADB** fallback, and that AOAP can be exclusive to one USB app:
https://superdisplay.app/help/

UScreen documents ADB-reversed TCP streaming plus Linux/EVDI and per-session auth; it **does not support Windows**:
https://github.com/majmichu1/UScreen
https://github.com/majmichu1/UScreen/blob/main/docs/architecture.md

### Why only Android development cannot be promised as a fix

1. USB transport must be recognised and opened (AOAP/ADB).
2. The Android app must understand the host's message framing, version negotiation, codec parameters, stream packets, and session lifecycle.
3. Video must be decoded and shown; input events must travel back.
4. The PC host must be running and have a session/display active before the phone has a desktop to show.
5. Trial expiration concerns the official Android app; this project must **not patch licensing checks, transplant proprietary bytecode/assets, or misrepresent compatibility**.

There is no verified open SuperDisplay-compatible Android client or public protocol spec in the references checked so far. Without a separately authorised host protocol specification or runtime interoperability tests, success cannot be established from the APK alone.

## What to do tonight (existing Windows installations only)

### Option A: If spacedesk Windows driver is still installed

1. Boot Windows and connect the normal data-capable USB cable.
2. Install/open the **official spacedesk Viewer for Android** (on the phone, not on Windows).
3. If **spacedesk Driver Console → Communication Interfaces → USB Cable Android** was previously enabled, select the detected desktop in the viewer. On some configurations it auto-connects.
4. If that direct USB mode was **not** previously enabled, it normally needs one-time Windows console access. **Do not assume it is on or that it will turn on from the phone.**
5. Alternative if the spacedesk server is already running: enable **USB tethering** in Android Settings after plugging in, then use spacedesk Viewer to discover the host over the cable's local IP network. This depends on Windows recognising the tethered network and its firewall allowing traffic. Manual IP is device-dependent; never promise a guessed address.
6. If Windows is locked or asleep, a driver may not present the screen immediately. If USB is claimed by SuperDisplay's AOAP host, spacedesk USB can conflict. Do not blindly change Windows display modes without a recovery display.

Official instructions:
- https://manual.spacedesk.net/AndroidUSBCableConnection.html
- https://manual.spacedesk.net/USBTetheringiOSandAndroid.html
- https://www.spacedesk.net/facts-figures/ (free for private, non-commercial use; commercial use requires a license)
- https://www.spacedesk.net/download/

### Option B: Existing SuperScreen prototype

This repository's current Android viewer is a **WebView-based hotspot mirror**, not USB or extended display, and still needs the SuperScreen Python Windows host to be running. It cannot replace either driver by merely installing its Android APK.

### Option C: Future independent build

For a reliable, independently developed **SuperScreen Android + Windows** system, a Windows-side host/driver (or a **documented and genuinely compatible preinstalled host**) is unavoidable. UScreen provides MIT-licensed Android MediaCodec/input design examples, not the Windows host. Public Microsoft IDD samples can inform the Windows virtual-display driver; this is a later project and requires actual Windows testing.

## Non-destructive acceptance gates

1. **Existing host identified:** Verify which Windows driver (SuperDisplay/spacedesk/SuperScreen) is installed and active, from a working Windows session once available.
2. **USB enumeration confirmed:** Android sees an expected accessory or tether network. Accessory detection is **not** proof of video compatibility.
3. **Protocol confirmed:** A licensed/authorized interoperability test exchanges connection and frame data with the PC host; no license bypass.
4. **Video visible:** Host display rendered on the phone and usable for reading Windows UI.
5. **Input usable:** Touch, Windows sign-in (if supported), mouse/keyboard behavior verified; auto-start tested after restart.
6. **Recovery:** Reliable reconnect after USB unplug and laptop restart; ability to undo virtual displays and drivers.

**Status:** static APK assessment completed; no USB hardware test, no Windows host binary, no build, no signed Android release, no successful USB connection. Do not call this feature implemented.
