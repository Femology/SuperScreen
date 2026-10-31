# Read-only troubleshooting for SuperScreen on Windows. Does not install drivers.
param([int]$Port = 8765)
Write-Host "\nSuperScreen: local network diagnostic\n" -ForegroundColor Cyan
Write-Host "Windows:" (Get-CimInstance Win32_OperatingSystem).Caption
Write-Host "Wi-Fi / LAN IPv4 addresses:"
Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Where-Object { $_.IPAddress -notmatch '^(127|169\.254)\.' } |
  Select-Object InterfaceAlias, IPAddress, PrefixLength | Format-Table -AutoSize
Write-Host "\nTCP $Port local listener:"
Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
  Select-Object LocalAddress, LocalPort, OwningProcess | Format-Table -AutoSize
Write-Host "\nNetwork profiles:"
Get-NetConnectionProfile | Select-Object Name, InterfaceAlias, NetworkCategory | Format-Table -AutoSize
Write-Host "If the phone cannot connect, first verify the laptop is connected to the phone hotspot and Windows Firewall allows the app only on the trusted Private network."
