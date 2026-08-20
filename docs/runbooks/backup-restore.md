# Backup and restore runbook

Do not assume backups are enabled in Supabase for every environment. Verify the provider setting
and retention window for the exact target before calling a release ready; current ATLAS evidence
does not claim a production restore rehearsal. Rehearse restore only against a non-production
target. Record provider backup ID, restore timestamp, migration head, row-count and checksum
comparison for representative tables, application smoke results, and cleanup.
`scripts/verify-backup-restore.ps1` intentionally stops short of changing an external project.
