# SuperScreen Android: native receiver preview

**Status: experimental Kotlin WebView receiver; not a replacement for the SuperDisplay Android client.**

The app embeds the existing paired JPEG/WebSocket browser receiver. It now supports **user-initiated discovery** of the first-party SuperScreen Windows host on local USB-tether or phone-hotspot interfaces, a manual host IP fallback, fullscreen viewing, and remembered addresses.

## Build

Open `android/` in Android Studio with JDK 17, Android SDK 35, and Gradle 8.10.2, or use the repository's GitHub Actions preview workflow. Run `gradle :app:testDebugUnitTest :app:assembleDebug`. Hardware compatibility has **not** been validated. The output is a debug-signed experimental APK.

## Connection A — Android USB tethering (experimental)

1. The **SuperScreen Windows host**, not just the SuperDisplay Windows driver, must already be installed and running in a Windows session. The current viewer cannot communicate with SuperDisplay's proprietary host.
2. Connect your Android phone using a **data-capable USB cable**.
3. On Android, enable **USB tethering** in Settings → Hotspot & tethering (the Android app can only open general network settings, not enable this automatically).
4. Windows should detect a new network adapter. The updated host watches for new private IP addresses and starts listening on them. Windows firewall policies may still block port **8765**.
5. Tap **Find SuperScreen Host** in the Android app. It checks only private local /24 subnets associated with USB or Wi-Fi interface names; discovery does not require internet data.
6. Enter the six-digit pairing code printed by the **SuperScreen Windows host** (first pairing only).

USB tethering exposes a TCP/IP network over the cable. It is **not** SuperDisplay's AOAP connection and is not UScreen's ADB reverse tunnel. USB interface visibility, routing, subnet mask and Windows firewall behaviour vary by phone and Windows build; automatic discovery can fail. Use a manual IP fallback when necessary.

## Connection B — Your phone's own hotspot

1. Enable the phone's private hotspot and connect the Windows laptop to it.
2. Start (or keep running) the SuperScreen Windows host.
3. Tap **Find SuperScreen Host**, or enter the host's Wi-Fi IPv4 address.
4. Pair with the one-time code.

## What the receiver can and cannot do

| Feature | Status |
| --- | --- |
| Windows screen mirrored to Android browser viewer | Experimental |
| Android app with remembered PC IP and fullscreen control | Source implemented, unverified on device |
| Local host auto-discovery on USB tether / hotspot | Source implemented; /24 heuristic; unverified |
| Host interface hotplug detection | Source implemented; Windows tests needed |
| Separate Windows virtual extended display / IDD | **Not implemented** |
| Native H.264/HEVC hardware decoding | **Not implemented** |
| Touch/keyboard control | **Not implemented** |
| USB ADB reverse / AOAP streaming | **Not implemented** |
| Login-screen/BIOS/lock-screen rescue | **Not implemented** |
| End-to-end encryption | **Not implemented** |

The prototype is **not** a safe screenless rescue tool yet. Keep a working external screen during initial installation and testing; don't change Windows primary display until the fallback has passed hardware tests.

## Security

The preview transports frames and session credentials over unencrypted local HTTP/WebSocket. Use only a directly cabled network or your own password-protected hotspot; avoid sensitive content during tests and do not expose TCP 8765 to the internet. Discovery does not pair or fetch private data and must never bypass SuperDisplay's purchase mechanism.
