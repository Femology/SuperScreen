# Manual Windows + Android acceptance tests

**Important:** These require actual Windows and Android hardware. CI only tests Python protocol, image encoding, auth and mocked streams.

## Equipment
- Windows 10/11 laptop, built-in LCD broken or healthy
- External TV/monitor via HDMI during initial setup
- Android phone with hotspot, browser and charged battery
- Wi-Fi adapter on laptop

## Test A: local hotspot without internet
1. Keep TV connected. Turn mobile data off if safe to do so, and enable phone hotspot.
2. Join that phone hotspot from Windows (saved network preferred).
3. Run SuperScreen and open the host Wi-Fi IPv4 address from the same phone.
4. Enter Windows terminal's single-use pairing code.
5. Verify frames continue, and that mouse/keyboard on Windows still work. Note FPS on phone.
6. Choose the TV monitor from dropdown if the built-in LCD is unusable.
7. Toggle hotspot off/on; verify reconnection. Record results.

## Test B: robustness
- Open/close File Explorer on TV; see it on phone without freezing the host.
- Reconnect after unplugging and reconnecting laptop power.
- Start/stop streaming 20 times; count failures.
- Attempt invalid pairing five times; sixth rejected, retry in 60 s.
- Revoke tokens via host API or remove paired-devices.json with app stopped, then test rejection.
- Try oversized image resolutions; ensure Windows is still usable.
- Verify Windows Firewall does not expose port 8765 on a public network.

## Test C: avoid deceptive success criteria
A wallpaper showing on phone does not prove the intended monitor is selected. A stream using real monitor #1 is **not** the same as a new virtual display. A Windows system startup with broken LCD requires a separate bootstrap test; the current app does not run before login.

## Bug reporting template
Windows build / GPU / phone model / Android version / monitor index / local IP range (no public IP) / FPS / exact repro / what TV showed / what phone showed / recovery / logs without secrets.
