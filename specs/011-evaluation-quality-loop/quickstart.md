# Quickstart

```powershell
pnpm test:evals
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/evaluation -q
```

The deterministic suite runs without provider keys. Live judge traces are opt-in and must use the
existing redaction boundary.
