$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$paths = @("apps/web/.next", "apps/web/src", "apps/backend/src", "docs", "evals/results")
$patterns = @('sk-[A-Za-z0-9]{20,}', 'OPENAI_API_KEY\s*[:=]\s*(sk-|[A-Za-z0-9]{24,})', 'LANGSMITH_API_KEY\s*[:=]\s*([A-Za-z0-9]{24,})', 'Authorization:\s*Bearer\s+[A-Za-z0-9._-]{24,}')
foreach ($relative in $paths) {
    $target = Join-Path $root $relative
    if (-not (Test-Path $target)) { continue }
    $files = Get-ChildItem $target -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "lock" -and $_.Extension -in @(".js", ".map", ".ts", ".tsx", ".py", ".json", ".md", ".yaml", ".yml", ".ps1", ".log") }
    foreach ($pattern in $patterns) {
        foreach ($file in $files) {
            try { $match = Select-String -LiteralPath $file.FullName -Pattern $pattern -ErrorAction Stop }
            catch { continue }
            if ($match) { throw "Potential secret marker found in $relative" }
        }
    }
}
Write-Output "deployment secret boundary passed"
