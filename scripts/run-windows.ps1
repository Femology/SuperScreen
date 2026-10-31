# SuperScreen Windows first-run bootstrap. Does not install any display driver.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path $Python)) {
  Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
  py -3 -m venv $Venv
  if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ launcher not found. Install Python first." }
}
Write-Host "Installing host dependencies into the local environment..." -ForegroundColor Cyan
& $Python -m pip install -e $Root
if ($LASTEXITCODE -ne 0) { throw "Could not install dependencies" }
Write-Host "Starting SuperScreen. Keep this window open. Only use on your personal hotspot." -ForegroundColor Cyan
& $Python -m superscreen
