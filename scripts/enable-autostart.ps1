# Opt-in Windows sign-in startup. Use ONLY after a successful manual device test.
# Requires an existing .venv. This task starts AFTER user sign-in, NOT on login screen.
param([switch]$Remove)
$ErrorActionPreference = "Stop"
$Name = "SuperScreen Host (after login)"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if ($Remove) {
  Unregister-ScheduledTask -TaskName $Name -Confirm:$false -ErrorAction SilentlyContinue
  Write-Host "Removed SuperScreen startup task"
  return
}
if (-not (Test-Path $Python)) {
  throw "Run scripts\run-windows.ps1 at least once before installing startup"
}
$User = "$env:USERDOMAIN\$env:USERNAME"
$Action = New-ScheduledTaskAction -Execute $Python -Argument "-m superscreen" -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $User
$Principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Trigger -Principal $Principal -Force | Out-Null
Write-Host "SuperScreen will launch after $User signs in. This does not enable Windows login-screen access." -ForegroundColor Green
Write-Host "To undo: .\scripts\enable-autostart.ps1 -Remove"
