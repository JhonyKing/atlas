$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot 'apps/backend/.venv/Scripts/python.exe'
Push-Location $repoRoot
try {
  & $python -m pytest apps/backend/tests/unit/evaluation -q
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $python -m evals.promotion_gate evals/results/016-promotion-metrics.json
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally { Pop-Location }
