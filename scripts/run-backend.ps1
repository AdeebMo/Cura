param(
  [switch]$Background,
  [int]$Port = 8000,
  [switch]$Reload
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend"
$venvPython = Join-Path $backendRoot ".venv\Scripts\python.exe"
$pythonCommand = if (Test-Path $venvPython) { $venvPython } else { "python" }
$pidFile = Join-Path $backendRoot "data\backend.pid"
$logDir = Join-Path $backendRoot "data\logs"
$stdoutLog = Join-Path $logDir "backend.stdout.log"
$stderrLog = Join-Path $logDir "backend.stderr.log"
$arguments = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $Port.ToString())

if ($Reload) {
  $arguments += "--reload"
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (Test-Path $pidFile) {
  $existingPid = Get-Content $pidFile | Select-Object -First 1
  if ($existingPid) {
    try {
      $null = Get-Process -Id ([int]$existingPid) -ErrorAction Stop
      throw "Backend already appears to be running with PID $existingPid. Stop it first with scripts\\stop-backend.ps1."
    } catch [System.Management.Automation.RuntimeException] {
      Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
  }
}

if ($Background) {
  $process = Start-Process `
    -FilePath $pythonCommand `
    -ArgumentList $arguments `
    -WorkingDirectory $backendRoot `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

  Set-Content -Path $pidFile -Value $process.Id
  Write-Host "Backend started in the background at http://127.0.0.1:$Port"
  Write-Host "PID: $($process.Id)"
  Write-Host "Logs: $stdoutLog and $stderrLog"
} else {
  Set-Location $backendRoot
  & $pythonCommand @arguments
}
