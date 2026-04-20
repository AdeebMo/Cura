$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRunner = Join-Path $PSScriptRoot "run-backend.ps1"
$frontendRunner = Join-Path $PSScriptRoot "run-frontend.ps1"

& $backendRunner -Background

if ((Get-Command node -ErrorAction SilentlyContinue) -or (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages")) {
  & $frontendRunner
} else {
  Write-Host ""
  Write-Host "Backend is running, but Node.js is not installed, so the frontend could not be started." -ForegroundColor Yellow
  Write-Host "Install Node.js LTS, then run .\\scripts\\run-frontend.ps1"
}
