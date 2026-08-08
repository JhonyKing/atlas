param([string]$Target = "non-production")
$ErrorActionPreference = "Stop"
if ($Target -eq "production") { throw "Backup restore verification must target non-production." }
Write-Output "backup/restore rehearsal is operator-assisted; target=$Target"
Write-Output "Provide provider backup ID, restore timestamp, row-count/checksum comparison, and cleanup evidence."
