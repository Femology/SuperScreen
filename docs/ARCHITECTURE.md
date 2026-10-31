# SuperScreen architecture

## Goals and constraints

SuperScreen's product goal is to show a Windows workspace on an Android phone with the **same phone providing the hotspot**. Local traffic must work with mobile data disabled. A normal Windows mouse and keyboard must continue to work. A failed connection must never strand the user on an invisible virtual display.

## Phase 1: truthful architecture

```text
Windows desktop (real monitor, including an external TV)
    ↓ mss capture (GDI / desktop screenshot)
    ↓ Pillow RGB resize / JPEG encode (up to 15 FPS in this prototype)
    ↓ aiohttp WebSocket over local Wi-Fi, default TCP 8765
Android browser on the very same phone running the hotspot
    ↓ decode JPEG frame and paint canvas
    ↖ authenticated monitor-selection command
```

This is **view-only mirror**. It does **not** duplicate Windows composition in hardware, display Windows secure desktop, create a virtual monitor, or implement input injection. JPEG over WebSocket is a functional architecture experiment, not a competitive low-latency video pipeline.

The app does not require internet once local dependencies are installed. Turning on a phone hotspot is an explicit system action; standard third-party Android apps cannot guarantee activating the internet-sharing hotspot automatically.

## Target native architecture (not yet implemented)

```text
Windows per-user session
 ├─ Device discovery and authenticated pairing
 ├─ Capture / duplicate / optionally create and enumerate IDD virtual monitor
 ├─ Hardware encode via Media Foundation/Video Encode Accelerator
 ├─ Secure video/control transport (QUIC/TLS or secured RTP)
 ├─ Input backchannel with permission gating
 ├─ Session state, telemetry and recovery
 └─ Startup agent, user-visible override and uninstall recovery

Android app
 ├─ Connect via own hotspot or ADB/USB
 ├─ Persistent paired-device identity + cert pinning
 ├─ Hardware MediaCodec decode into Surface
 ├─ Compose UI controls: Mirror | Extend | Rescue
 ├─ Touch/keyboard/scroll through input channel
 └─ Reconnect with stateful layout restoration
```

### Windows virtual display

Use documented [Microsoft Indirect Display Driver (IDD)](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/indirect-display-driver-model-overview) concepts. Evaluate the MIT-licensed [Virtual Display Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver) separately. Installing a virtual driver on a system with an already damaged built-in display is high risk and **must require user consent and tested recovery instructions**.

### Discovery on the phone's hotspot

The simplest reliable baseline is laptop joins the phone's saved hotspot and the phone opens the laptop's IPv4 address. Later, native discovery can use UDP broadcasts/mDNS but Android hotspot implementations can filter multicast/broadcast: **always retain manual address/QR pairing as a fallback**. The phone's hotspot does not depend on a second handset or router. Devices need not have internet access.

### Security

Phase 1 uses a six-digit one-use code and a high-entropy bearer token stored as a SHA-256 digest on Windows. Authentication is only a prototype on unencrypted transport. Phase 2+ must implement authenticated encryption and device key pinning **before** enabling remote input. Never allow arbitrary OS command execution through the data channel.

## UI principles

- Primary destination is visible in one action; don't ask users to repeatedly choose outputs.
- Distinguish 'Phone mirrors monitor 2' from 'Phone is monitor 2'.
- Make rescue mode explicit and reversible.
- Show an intelligible error for bad pairing, missing virtual driver, wrong monitor, firewall blocking, or stream failure.
- Respect accessibility, reduced motion, large touch targets, and dark mode.
