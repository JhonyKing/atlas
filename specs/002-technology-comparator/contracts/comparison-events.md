# Comparison Event Contract

The `POST /v1/comparisons` response uses `text/event-stream`. Each event includes a monotonically
increasing `id` and JSON `data` with the public `run_id`.

Allowed stages are:

1. `comparison.accepted`
2. `comparison.retrieval.started`
3. `comparison.retrieval.completed`
4. `comparison.normalization.completed`
5. `comparison.verification.completed`
6. `comparison.completed`
7. `comparison.abstained`
8. `comparison.cancelled`
9. `comparison.failed`

The terminal `completed` event contains the verified matrix. It MUST NOT contain a cell marked
`supported` without at least one evidence ID. `unsupported` cells may have no evidence IDs but MUST
include an explanation. No claim text is emitted before the terminal verification event.
