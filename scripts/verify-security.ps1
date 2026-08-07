$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot 'apps/backend/.venv/Scripts/python.exe'
Push-Location $repoRoot
try {
    & $python -m pytest apps/backend/tests/security -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
