# Feature 003 — Report architecture

The report boundary starts from a completed comparison run. `planner.py` creates one neutral
`ReportRepresentation` containing localized presentation text, sections, and a citation manifest.
The DOCX and PDF renderers consume that same representation so format changes cannot silently
change citation identity. `validation.py` checks citation membership, DOCX XML, PDF parseability,
and required references before the job becomes `completed`.

The first local coordinator is in-process and uses bounded storage. The metadata migration
(`0016_reports` plus `0017_report_metadata`) is the durable seam for a later worker/object-store
implementation; it records owner digest, source run, idempotency key, lifecycle state, expiry,
content hash, size, model, prompt version, and corpus snapshot.

Every report request receives the existing request identifier and is associated with the anonymous
visitor digest. Provider keys and raw visitor identifiers are never copied into artifacts. The
source comparison run remains authoritative: missing or citation-less evidence causes a controlled
failure rather than a fluent report.

```text
completed comparison run
          |
          v
ReportSpec -> planner -> ReportRepresentation -> DOCX/PDF renderers
                              |                         |
                              +--> citation validation-+
                                        |
                                        v
                               bounded artifact storage
```
