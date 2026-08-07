# Quickstart

```powershell
pnpm test:security
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/security -q
```

The local suite uses synthetic URLs, users and documents. It never requires production secrets or
external security-review credentials.
