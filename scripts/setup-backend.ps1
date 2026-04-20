$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend"
$venvRoot = Join-Path $backendRoot ".venv"
$pythonExe = Join-Path $venvRoot "Scripts\python.exe"

if (-not (Test-Path $venvRoot)) {
  Write-Host "Creating backend virtual environment..."
  python -m venv $venvRoot
}

Write-Host "Installing backend dependencies..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -e ".[dev]" --config-settings editable_mode=compat --no-warn-script-location

Write-Host "Backend setup complete."

