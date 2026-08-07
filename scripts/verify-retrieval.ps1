$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $repoRoot 'apps/backend'
$python = Join-Path $backend '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { throw "Backend virtualenv not found: $python" }
Push-Location $repoRoot
try {
    & $python -m pytest apps/backend/tests/unit/retrieval apps/backend/tests/security/test_retrieval_quality.py -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
