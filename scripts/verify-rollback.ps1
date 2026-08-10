param([switch]$AllowExternalExecution)
$ErrorActionPreference = "Stop"
if (-not $AllowExternalExecution) {
    Write-Output "rollback rehearsal is operator-assisted; no external deployment was changed"
    exit 0
}
throw "External rollback execution requires an approved provider-specific adapter."
