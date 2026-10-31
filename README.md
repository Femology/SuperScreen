# SuperScreen

**Turn an Android phone into a dependable display for a Windows PC — no router, cloud account, or second phone required.**

> **Status: experimental Phase 1 prototype.** The initial receiver runs in an Android browser over the phone's own hotspot and **mirrors an existing Windows display**. It is **not** a native Android app, virtual monitor, USB transport, Windows login-screen solution, or production-secure remote-desktop service yet.

## The first working slice

```
Android phone hotspot ── local Wi-Fi ── Windows 10/11 laptop
       │                                    │
       │     browser over local WebSocket   │
       └──────── desktop JPEG frames ◀──────┘
```

**The phone that runs the hotspot is also the receiver.** No internet data is needed for local screen traffic. Windows must connect to the phone's saved Wi-Fi network; third-party Android apps cannot reliably turn on the system hotspot without user action.

### Run the prototype on Windows

Prerequisites: Windows 10/11, Python 3.11+, Android phone with hotspot, and temporary access to a working Windows display for setup.

1. Clone this repository, open PowerShell in the project root, and run:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -e ".[dev]"
   python -m superscreen
   ```

2. Enable your **phone's own hotspot**; connect the Windows laptop to it.
3. In the PowerShell output, note the local URL and six-digit pairing code. Open the URL **on that same phone**, using Chrome or another modern browser.
4. Enter the six-digit code. The receiver starts displaying the captured Windows screen.
5. Keep the Windows terminal running. After a temporary network interruption, the browser tries to reconnect. A paired token is remembered locally on the phone.

If PowerShell blocks activation, use `\.venv\Scripts\python.exe -m superscreen` instead.

**Security warning:** Phase 1 uses unencrypted HTTP/WebSocket on a trusted personal hotspot. It does not yet provide encryption or authenticated device discovery. **Do not use on public/shared Wi-Fi or expose port 8765 to the internet.** No remote mouse/keyboard input is enabled in this release.

### Running tests

```powershell
python -m pytest -q
```

## Scope and milestones

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repo, protocol notes, test automation, honest scope | In progress |
| 1 | Trusted-hotspot pairing, browser receiver, mirror | Prototype |
| 2 | Stable capture/encode, performance telemetry | Planned |
| 3 | Native Android client, LAN discovery, remembered pairing | Planned |
| 4 | Real Windows extend/duplicate modes via IDD integration | Research required |
| 5 | Primary-screen rescue, input controls, layout recovery | Planned |
| 6 | USB transport, packaging, accessibility, polish | Planned |
| 7 | Security hardening, stress tests, signed installers | Planned |

See [Architecture](docs/ARCHITECTURE.md), [Roadmap](docs/ROADMAP.md), and [Security](docs/SECURITY.md).

## Important engineering distinction

A **mirrored screen** copies an existing Windows monitor. A **real extended monitor** requires Windows to enumerate a new display (usually via an Indirect Display Driver). We will not present browser mirroring as an extended monitor. Microsoft's [Indirect Display Driver sample](https://github.com/microsoft/Windows-driver-samples/tree/main/video/IndirectDisplay) is the reference for researching this part, **not** a production-ready component.

## License

MIT, see [LICENSE](LICENSE). Third-party source code is not vendored into this repository.
