$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $projectRoot "frontend"

function Resolve-NodeCommand {
  $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
  if ($nodeCommand) {
    return $nodeCommand.Source
  }

  $wingetNode = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter node.exe -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1

  if ($wingetNode) {
    return $wingetNode.FullName
  }

  return $null
}

$nodeExe = Resolve-NodeCommand

if (-not $nodeExe) {
  throw "Node.js is not installed or not on PATH. Install Node.js LTS first, then rerun this script."
}

$nodeDir = Split-Path -Parent $nodeExe
$npmCmd = Join-Path $nodeDir "npm.cmd"

if (-not (Test-Path $npmCmd)) {
  throw "npm.cmd was not found next to node.exe. Reinstall Node.js LTS and try again."
}

$env:PATH = "$nodeDir;$env:PATH"

Set-Location $frontendRoot

if (-not (Test-Path (Join-Path $frontendRoot "node_modules"))) {
  Write-Host "Installing frontend dependencies..."
  & $npmCmd install
}

Write-Host "Starting frontend at http://localhost:5173"
& $npmCmd run dev
