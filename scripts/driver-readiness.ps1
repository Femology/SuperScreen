# Read-only readiness report. DOES NOT install, disable or modify drivers.
# Requires a running Windows session. Do not change display modes on a screenless PC.
[CmdletBinding()]
param()

Write-Host "SUPER/SCREEN | Windows Driver & USB Readiness" -ForegroundColor Cyan
Write-Host "This is diagnostic only. No settings will be changed."
Write-Host ""

try {
  Write-Host "OS:"
  Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption, Version, OSArchitecture |
    Format-Table -AutoSize
} catch {
  Write-Warning "OS information unavailable: $($_.Exception.Message)"
}

try {
  Write-Host "Detected display devices (SuperDisplay is NOT a SuperScreen driver):"
  Get-PnpDevice -Class Display -ErrorAction Stop |
    Select-Object FriendlyName, Status, InstanceId |
    Format-Table -AutoSize
} catch {
  Write-Warning "Display enumeration unavailable: $($_.Exception.Message)"
}

try {
  Write-Host "USB / Wi-Fi / Ethernet adapters:"
  Get-NetAdapter -ErrorAction Stop |
    Where-Object { $_.InterfaceDescription -match 'USB|RNDIS|Remote NDIS|Mobile|Ethernet|Wi-Fi|Wireless' -or $_.Name -match 'USB|Ethernet|Wi-Fi|Wireless' } |
    Select-Object Name, InterfaceDescription, Status, LinkSpeed |
    Format-Table -AutoSize
} catch {
  Write-Warning "Network adapter information unavailable: $($_.Exception.Message)"
}

try {
  Write-Host "Private IPv4 addresses:"
  Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
    Where-Object { $_.IPAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' } |
    Select-Object InterfaceAlias, IPAddress, PrefixLength |
    Format-Table -AutoSize
} catch {
  Write-Warning "IP information unavailable: $($_.Exception.Message)"
}

try {
  Write-Host "SuperScreen TCP 8765 listener (may be missing until host is running):"
  Get-NetTCPConnection -State Listen -LocalPort 8765 -ErrorAction Stop |
    Select-Object LocalAddress, LocalPort, State |
    Format-Table -AutoSize
} catch {
  Write-Host "No existing TCP 8765 listener detected."
}

Write-Host ""
Write-Host "Next: verify a *working* viewer before any virtual-display/primary-screen changes." -ForegroundColor Yellow
