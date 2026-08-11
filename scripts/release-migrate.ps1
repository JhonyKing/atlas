param(
    [string]$DatabaseUrl = $env:ATLAS_DATABASE_URL,
    [switch]$DryRun,
    [string]$ExpectedHead = "foreign_key_indexes"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root "apps/backend/.venv/Scripts/python.exe"
if (-not (Test-Path $python)) { throw "Backend virtual environment not found." }
if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) { throw "ATLAS_DATABASE_URL is required." }

$env:ATLAS_DATABASE_URL = $DatabaseUrl
$manifest = & $python (Join-Path $root "scripts/supabase/verify_repository_migrations.py")
if ($LASTEXITCODE -ne 0) { throw "Repository migration manifest is invalid." }
if ($manifest -notmatch [regex]::Escape($ExpectedHead)) { throw "Expected migration head $ExpectedHead was not found." }
if ($DryRun) { Write-Output "migration preflight passed (dry-run); no database was changed"; exit 0 }

Push-Location $root
try {
    & $python -m alembic -c database/alembic.ini upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Alembic migration failed." }
} finally { Pop-Location }
Write-Output "migration applied through $ExpectedHead"
