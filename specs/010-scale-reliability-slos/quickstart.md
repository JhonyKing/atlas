# Quickstart

```powershell
pnpm test:slo
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/slo -q
```

Local deterministic measurements are not production load certification; live load scenarios must
record their environment and remain explicit operational evidence.
