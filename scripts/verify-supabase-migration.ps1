param(
    [string]$SnapshotPath,
    [switch]$RequireRemoteSnapshot
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$windowsPython = Join-Path $root "apps/backend/.venv/Scripts/python.exe"
$unixPython = Join-Path $root "apps/backend/.venv/bin/python"
$python = if (Test-Path $windowsPython) { $windowsPython } else { $unixPython }
if (-not (Test-Path $python)) {
    throw "Backend virtual environment not found. Run uv sync --project apps/backend first."
}

Write-Output "[supabase] verifying repository migration manifest"
& $python (Join-Path $root "scripts/supabase/verify_repository_migrations.py") | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Repository migration verification failed." }

Write-Output "[supabase] validating committed evidence artifacts"
$artifacts = Get-ChildItem (Join-Path $root "evals/results") -Filter "supabase-migration-*.json" -File
if ($artifacts.Count -eq 0) { throw "No Supabase migration evidence artifacts were found." }
$artifactPaths = @($artifacts | ForEach-Object { $_.FullName })
& $python -c "import sys; from atlas.database.migration_evidence import MigrationEvidence; [MigrationEvidence.model_validate_json(open(path, encoding='utf-8').read()) for path in sys.argv[1:]]" @artifactPaths
if ($LASTEXITCODE -ne 0) { throw "Evidence artifact validation failed." }

if ([string]::IsNullOrWhiteSpace($SnapshotPath)) {
    if ($RequireRemoteSnapshot) {
        throw "A remote MCP snapshot is required but -SnapshotPath was not provided."
    }
    Write-Output "[supabase] remote snapshot not supplied; no live read was attempted"
    exit 0
}

if (-not (Test-Path $SnapshotPath)) { throw "Snapshot file not found: $SnapshotPath" }
Write-Output "[supabase] performing read-only repository-to-remote comparison"
& $python (Join-Path $root "scripts/supabase/compare_state.py") --snapshot $SnapshotPath
if ($LASTEXITCODE -ne 0) { throw "Remote snapshot comparison found drift." }
Write-Output "[supabase] verification passed"
