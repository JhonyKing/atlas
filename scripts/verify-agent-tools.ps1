[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root "apps/backend/.venv/Scripts/python.exe"
$dataset = Join-Path $root "evals/datasets/agent_tool_orchestration.jsonl"
Push-Location $root
try {
    & $python -m pytest apps/backend/tests/agent apps/backend/tests/contract/agent/test_tool_orchestration.py apps/backend/tests/security/test_agent_tool_boundaries.py -q
    & $python -m ruff check apps/backend/src/atlas/agent apps/backend/src/atlas/api/routes/agent.py apps/backend/src/atlas/observability/agent_trace.py
    & $python -m mypy apps/backend/src/atlas/agent apps/backend/src/atlas/api/routes/agent.py apps/backend/src/atlas/observability/agent_trace.py

    $cases = @(Get-Content -LiteralPath $dataset | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
    if ($cases.Count -ne 5) { throw "Expected 5 agent-tool evaluation cases, found $($cases.Count)" }
    $ids = @($cases | ForEach-Object { $_.case_id })
    if (($ids | Sort-Object -Unique).Count -ne $cases.Count) { throw "Evaluation case IDs must be unique" }
    if (-not ($cases | Where-Object { $_.case_id -eq "agent-prompt-injection-denied" -and $_.expected.unknown_tool -eq $true })) {
        throw "Prompt-injection denial case is missing"
    }
    [pscustomobject]@{ status = "passed"; cases = $cases.Count; dataset = $dataset }
} finally { Pop-Location }
