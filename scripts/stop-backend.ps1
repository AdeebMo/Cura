$ErrorActionPreference = "Stop"

$stateDir = Join-Path $env:TEMP "Cura"
$pidFile = Join-Path $stateDir "backend.pid"

if (-not (Test-Path $pidFile)) {
  Write-Host "No backend PID file was found."
  exit 0
}

$backendPid = Get-Content $pidFile | Select-Object -First 1

if (-not $backendPid) {
  Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
  Write-Host "Backend PID file was empty and has been removed."
  exit 0
}

try {
  Stop-Process -Id ([int]$backendPid) -Force -ErrorAction Stop
  Write-Host "Stopped backend process $backendPid."
} catch {
  Write-Host "Backend process $backendPid was not running."
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
