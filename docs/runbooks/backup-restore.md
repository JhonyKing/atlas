# Backup and restore runbook

Backups are enabled in Supabase for each environment. Rehearse restore only against a
non-production target. Record provider backup ID, restore timestamp, migration head, row-count
and checksum comparison for representative tables, application smoke results, and cleanup.
`scripts/verify-backup-restore.ps1` intentionally stops short of changing an external project.
