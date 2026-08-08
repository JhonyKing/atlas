# Rollback runbook

Rollback deploys the previous immutable web build and API image digest. Database migrations are
forward-only: first verify the previous application is compatible with the current schema; if it
is not, use a reviewed expand/contract migration rather than destructive downgrade. Rehearse in
preview and retain the evidence bundle. No production rollback is claimed from local Docker.
