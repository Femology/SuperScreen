# SuperScreen

**Turn an Android phone into a dependable display for a Windows PC — no router, cloud account, or second phone required.**

> **Status: experimental Phase 1 prototype.** The first receiver runs in an Android browser over the phone's own hotspot and **mirrors an existing Windows display**. There is now also an **experimental native Android WebView launcher** (not yet a native video decoder). There is **no** true extended virtual monitor, USB transport, Windows login-screen access, or production-secure remote-desktop service yet.

## New: experimental USB-tether discovery (source added 2026-11-01)

An Android **USB-tethered network connection** may now carry the existing SuperScreen mirror stream without an external router. The Windows host watches for private USB/RNDIS network interfaces after start, and the Android app can look for the **SuperScreen Windows host** by scanning its own private local subnet. Manual IP entry remains available.

This is a **TCP network over USB**, not a SuperDisplay driver adapter, AOAP protocol implementation, ADB reverse tunnel, Windows IDD, or functioning screenless rescue. It requires SuperScreen's own Windows host to be running, first pairing, permissive **trusted private** Windows firewall rules, and an already enumerated Windows display. Automatic discovery and new Android code have not yet been hardware validated. Do **not** rely on this preview as your only screen.

See [Android USB/tethering setup](android/README.md), [read-only Windows diagnostics](scripts/driver-readiness.ps1), and [real virtual-driver project and acceptance gates](windows/driver/README.md).

## The first working slice

```
Android phone hotspot ── local Wi-Fi ── Windows 10/11 laptop
       │                                    │
       │     browser over local WebSocket   │
       └──────── desktop JPEG frames ◀──────┘
```

**The phone that runs the hotspot is also the receiver.** No internet data is needed for local screen traffic. Windows must connect to the phone's saved Wi-Fi network; third-party Android apps cannot reliably turn on the system hotspot without user action.

### Preview downloads

When the build-and-release workflow succeeds on `main`, unsigned Windows and debug-signed Android preview packages are published together under [SuperScreen preview releases](https://github.com/Femology/SuperScreen/releases/tag/v0.1.0-preview.1) with SHA-256 checksums. **This is a prerelease, not a production build.** Keep the LG TV or another external screen available until the phone connection passes your hardware checks.

### Run the prototype on Windows

Prerequisites: Windows 10/11, Python 3.11+ (or the portable Windows EXE), Android phone with hotspot, and temporary access to a working Windows display for setup.

**First turn on the Android phone's own hotspot, and join it from the Windows laptop before starting the host.** The Windows server intentionally binds only to private local addresses detected at launch. If the hotspot network changes IP addresses, restart the host.

1. Clone this repository, open PowerShell in the project root, then run **either** `./scripts/run-windows.ps1` for one-command setup **or** the following manual steps:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -e ".[dev]"
   python -m superscreen
   ```

2. In the PowerShell output, note the local URL and six-digit pairing code. Open the URL **on that same phone**, using Chrome or another modern browser (or use the experimental Android APK).
3. Enter the six-digit code. The receiver starts displaying the captured Windows screen.
4. Keep the Windows terminal running. After a temporary network interruption, the browser tries to reconnect. A paired token is remembered locally on the phone.

If PowerShell blocks activation, use `\.venv\Scripts\python.exe -m superscreen` instead.

**Security warning:** Phase 1 uses unencrypted HTTP/WebSocket on a trusted personal hotspot. It does not yet provide encryption or authenticated device discovery. **Do not use on public/shared Wi-Fi or expose port 8765 to the internet.** No remote mouse/keyboard input is enabled in this release.

### Android native alpha and portable Windows build

The experimental [Android Kotlin launcher](android/README.md) embeds the browser receiver, remembers the laptop's local IP address, and opens wireless settings for hotspot setup. It does **not** decode native H.264 or activate the phone's hotspot automatically. Open `android/` in Android Studio to build it.

GitHub Actions builds both packages and, on a passing `main` release workflow, publishes them to the versioned preview release with checksums. These are experimental builds, not signed production installers; Windows SmartScreen or Android may show installation warnings. Do not disable security protections globally to install them.

If manual Windows mirroring works and you want the Windows host to open after sign-in, run `./scripts/enable-autostart.ps1`. This is opt-in and can be undone with `./scripts/enable-autostart.ps1 -Remove`. It does **not** start at the Windows login screen or automatically join a hotspot that has never been saved.

### Running tests

```powershell
python -m pytest -q
```

## Scope and milestones

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repo, protocol notes, test automation, honest scope | Complete |
| 1 | Trusted-hotspot pairing, browser receiver, mirror | Prototype |
| 2 | Stable capture/encode, performance telemetry | Planned |
| 3 | Native Android client, LAN discovery, remembered pairing | Planned |
| 4 | Real Windows extend/duplicate modes via IDD integration | Research required |
| 5 | Primary-screen rescue, input controls, layout recovery | Planned |
| 6 | USB transport, packaging, accessibility, polish | Planned |
| 7 | Security hardening, stress tests, signed installers | Planned |

See [Windows phone-hotspot setup](docs/SETUP-WINDOWS.md), [Virtual display research](docs/VIRTUAL-DISPLAY.md), [Architecture](docs/ARCHITECTURE.md), [Roadmap](docs/ROADMAP.md), [Security](docs/SECURITY.md), [Test plan](docs/TEST-PLAN.md), and [Upstream licence study](docs/UPSTREAM.md).

## Important engineering distinction

A **mirrored screen** copies an existing Windows monitor. A **real extended monitor** requires Windows to enumerate a new display (usually via an Indirect Display Driver). We will not present browser mirroring as an extended monitor. Microsoft's [Indirect Display Driver sample](https://github.com/microsoft/Windows-driver-samples/tree/main/video/IndirectDisplay) is the reference for researching this part, **not** a production-ready component.

## License

MIT, see [LICENSE](LICENSE). Third-party source code is not vendored into this repository.
