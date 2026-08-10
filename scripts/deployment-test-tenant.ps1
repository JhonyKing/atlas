param([string]$Environment = "preview")
$ErrorActionPreference = "Stop"
if ($Environment -notin @("preview", "staging")) { throw "Test tenant setup is limited to preview/staging." }
Write-Output "test tenant lifecycle is operator-assisted for $Environment"
Write-Output "Create an isolated tenant, run ownership/deletion smoke, then remove it and retain redacted evidence."
