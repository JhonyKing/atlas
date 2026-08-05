# ATLAS LangSmith dashboard definitions

These definitions are a reproducible query contract, not a claim that a hosted
dashboard is already provisioned. Create the charts in the configured LangSmith
workspace using the field names below; keep query exports under version control
when the workspace supports them.

## Required dimensions

Every chart should allow filtering by `locale`, `collection`, `answer_status`,
`application_version`, `prompt_version`, `retrieval_version`,
`embedding_profile` and `corpus_snapshot`. These are safe metadata fields; raw
questions, answers and excerpts are intentionally not dimensions.

## Query catalog

| ID | Question answered | Filter/group fields | Measures |
|---|---|---|---|
| OBS-Q001 | Are requests available and terminating? | environment, answer_status | request count, failed count, abstained count, error rate |
| OBS-Q002 | Is answer latency stable? | locale, collection, corpus_snapshot | p50/p95 duration, max duration |
| OBS-Q003 | Is first-token latency stable? | model, locale, application_version | p50/p95 TTFT when recorded, missing-TTFT count |
| OBS-Q004 | Are citations and abstentions safe? | answer_status, retrieval_version | citation coverage, abstention rate, verification failures |
| OBS-Q005 | What does the model cost? | model, embedding_profile, prompt_version | input/output/reasoning tokens, estimated cost class |
| OBS-Q006 | Which versions regress? | prompt_version, retrieval_version, corpus_snapshot | error rate, citation failures, latency p95 |
| OBS-Q007 | What needs human review? | feedback_category, locale, corpus_snapshot | incorrect-citation count, not-useful rate, review backlog |

## Evidence and retention

Export aggregate values with the dataset version, application commit and corpus
snapshot. Do not export trace inputs or outputs. Retention/deletion operations
must follow `langsmith-runbook.md` and be recorded as an operator action without
copying credentials into the repository.
