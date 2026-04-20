$checks = @(
  @{ Name = "Python"; Command = "python --version" },
  @{ Name = "SBCL"; Command = "sbcl --version" },
  @{ Name = "SWI-Prolog"; Command = "swipl --version" },
  @{ Name = "Node.js"; Command = "node --version" },
  @{ Name = "npm"; Command = "npm --version" }
)

foreach ($check in $checks) {
  Write-Host "Checking $($check.Name)..."

  try {
    Invoke-Expression $check.Command
  } catch {
    Write-Host "Unavailable: $($check.Name)" -ForegroundColor Yellow
  }

  Write-Host ""
}

