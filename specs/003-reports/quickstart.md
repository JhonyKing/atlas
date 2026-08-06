# Reports Quickstart

## Prerequisites

- PostgreSQL is running and the existing comparison service is available.
- Backend and web dependencies are installed.
- A completed comparison run exists for the current anonymous visitor.

## Validate the contract and schema

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/contract/reports -q
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/unit/reports -q
```

## Generate a report

1. Start the API and web app using the local-development runbook.
2. Complete a comparison in the UI.
3. Submit a report request with the completed comparison run ID, locale, audience, scope, required
   sections, and `docx` format.
4. Read the SSE stream until `report.completed` or `report.failed`.
5. Download the DOCX and PDF variants.

## Validate artifact integrity

```powershell
apps\backend\.venv\Scripts\python.exe -m pytest apps/backend/tests/integration/reports -q
```

The integration suite must verify non-empty DOCX/PDF files, parseability, citation URLs, content
hashes, expiry/delete behavior, and the English/Spanish citation manifest parity. Render each DOCX
and PDF to page images and inspect every page before marking the report job completed.

## Expected result

- The report status reaches `completed` only after all validation gates pass.
- The downloaded artifact contains a title, executive summary, comparison analysis, limitations,
  and references.
- A Spanish report localizes headings and narrative while preserving original evidence excerpts and
  citation IDs.
