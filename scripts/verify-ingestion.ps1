[CmdletBinding()]
param(
    [switch]$SkipMigration,
    [switch]$SkipBrowser
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root "apps/backend/.venv/Scripts/python.exe"

Push-Location $root
try {
    & $python -m pytest apps/backend/tests/unit/ingestion apps/backend/tests/contract/ingestion `
        apps/backend/tests/integration/ingestion apps/backend/tests/security/test_ingestion_governance.py -q
    if (-not $SkipMigration) {
        $databaseLine = Get-Content .env | Where-Object { $_ -match '^DATABASE_URL=' } | Select-Object -First 1
        if ($databaseLine) {
            $env:ATLAS_DATABASE_URL = $databaseLine.Substring('DATABASE_URL='.Length).Trim()
            & (Join-Path $root "apps/backend/.venv/Scripts/alembic.exe") -c database/alembic.ini upgrade head
            Get-Content database/tests/013_ingestion_governance.sql | docker exec -i atlas-ai-postgres-1 psql -U atlas -d atlas -v ON_ERROR_STOP=1
        } else {
            Write-Warning "DATABASE_URL no está configurada; se omite el contrato SQL."
        }
    }
    if (-not $SkipBrowser) {
        pnpm --filter @atlas/web test:e2e -- --project=chromium
    }
} finally {
    Pop-Location
}
