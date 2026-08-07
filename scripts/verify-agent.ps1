[CmdletBinding()]
param([switch]$SkipMigration)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root "apps/backend/.venv/Scripts/python.exe"
Push-Location $root
try {
    & $python -m pytest apps/backend/tests/unit/agent apps/backend/tests/contract/agent apps/backend/tests/integration/agent apps/backend/tests/security/test_agent_orchestration.py -q
    & $python -m ruff check apps/backend/src/atlas/agent apps/backend/src/atlas/api/routes/agent.py
    & $python -m mypy apps/backend/src/atlas/agent apps/backend/src/atlas/api/routes/agent.py
    if (-not $SkipMigration) {
        $line = Get-Content .env | Where-Object { $_ -match '^DATABASE_URL=' } | Select-Object -First 1
        $env:ATLAS_DATABASE_URL = $line.Substring('DATABASE_URL='.Length).Trim()
        & (Join-Path $root "apps/backend/.venv/Scripts/alembic.exe") -c database/alembic.ini upgrade head
        Get-Content database/tests/014_agent_checkpoints_reviews.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
    }
} finally { Pop-Location }
