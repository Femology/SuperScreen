# Windows 11 + Android phone hotspot: first hardware acceptance test

This is the supported path for the **experimental, view-only local mirror**. Keep an external TV connected to a laptop with a damaged panel until the connection is proven. SuperScreen has not been validated with every Android hotspot chipset or Windows GPU.

## One-time pairing

1. On Android, enable **Personal Hotspot** in system settings. It is the same device that will view the screen. Turn off mobile data if you want to prove that no internet is used.
2. On Windows 11, join your phone's SSID using the saved Wi-Fi password. You do not need a router or another handset. Mark this specific **trusted personal hotspot** as a **Private network** in Wi-Fi properties if appropriate.
3. Clone SuperScreen and launch PowerShell from the project directory:
   ```powershell
   .\scripts\run-windows.ps1
   ```
   Or install Python 3.11+ manually and run `python -m superscreen`.
4. The terminal prints one or more **local IPv4 URLs** and a **six-digit pairing code**. On the phone, use Chrome to open `http://WINDOWS_IP:8765` (replace WINDOWS_IP with the laptop's **Wi-Fi** IPv4 address, not the hotspot phone's gateway).
5. Enter the code in the mobile viewer. If the code expires, restart the host to print a new one.
6. If you see only wallpaper, select the **TV's monitor number** from the viewer's dropdown. The built-in HP screen might appear as monitor 1 and the HDMI TV as monitor 2. Display numbering can differ.
7. Confirm opening a Windows window on the TV makes it appear in the phone viewer. Confirm the Windows keyboard and touchpad **continue to work**.
8. Only then try disconnecting the TV. The current mirror captures an existing Windows display: if Windows disables that physical display when HDMI is unplugged, the capture may stop. **A reliable no-TV recovery requires a virtual display or a headless display adapter and is not yet guaranteed.**

### Windows Firewall

If the phone cannot open the URL, check `./scripts/windows-check.ps1` on Windows. Windows Defender Firewall may block inbound TCP 8765. Prefer a narrowly scoped rule for your **trusted Private hotspot network**, and never disable the firewall globally. The Python process must be allowed to listen on the selected network. An enterprise/public network is not suitable for this early unencrypted prototype.

### Reconnect after a reboot

- The phone can save its hotspot configuration. Windows can reconnect to a saved Wi-Fi profile if configured by the OS and the phone hotspot is on.
- SuperScreen's browser client remembers the previously paired token; the native alpha launcher also remembers the Windows address.
- For **opt-in host auto-start after Windows login**, first run `scripts/run-windows.ps1` and complete a normal test, then run `scripts/enable-autostart.ps1`.
- This is **not a login-screen receiver**. On an HP with an unviewable LCD, keep the TV as the recovery fallback until the no-TV boot test succeeds on your hardware.

## Privacy and security

The current TCP stream is HTTP/WebSocket **without encryption**. Use only your private phone hotspot with a strong WPA2/WPA3 password. Do not open TCP 8765 to the internet, share the six-digit pairing code, or stream sensitive content. The production roadmap requires TLS and pinned identities.

## If it fails

- Phone browser cannot connect: wrong PC IP, OS firewall, Windows Wi-Fi disconnected, or hotspot client isolation.
- Pairing code rejected: expired or already used; restart Windows host and try the new code.
- Image shows wallpaper: wrong monitor selected; switch in dropdown.
- Mouse does not respond: input from Android is intentionally disabled. Physical Windows keyboard/touchpad should still respond.
- Screen goes black after unplugging TV: the chosen physical monitor disappeared, not proof that the phone connection failed. Reattach TV.

Log your findings in [test plan](TEST-PLAN.md) before enabling any virtual display driver.
