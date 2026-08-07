# Quickstart

```powershell
pnpm test:model-router
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/models -q
```

The local deterministic adapter does not require provider keys. Production provider calls require
server-side secrets and are never enabled from browser input.
