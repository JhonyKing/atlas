# Feature 002 verification record

## Current status

The comparator implementation, pricing source policy, `pricing` source type, `not_applicable`
state, bilingual rendering, deterministic conclusion, and bounded evidence metadata are covered by
local contracts and tests. The official pricing manifest is
`corpus/manifests/expansion-v3-pricing.yaml`.

The live closure evidence is still pending. This document must be updated only after the owner
reviews a real Supabase snapshot and a real comparison run; do not replace the placeholders with
invented IDs.

## Live evidence to record

- Supabase migration head: `pending owner verification`
- Pricing snapshot ID: `pending owner verification`
- Live comparison run ID: `pending owner verification`
- Application commit: `pending owner verification`
- Locales exercised: `pending owner verification`
- Evidence artifact: `evals/results/comparator-pricing-live-<run-id>.json`
- Owner checklist: [pricing owner review](../../specs/002-technology-comparator/checklists/owner-review.md)

## Acceptance boundary

Technical documentation cannot support a price claim. Official pricing evidence is required for a
populated price cell; missing reviewed pricing evidence is `unsupported`; framework-only pricing is
`not_applicable`. The live artifact must preserve previous snapshots and include enough evidence
metadata for a reviewer to inspect every populated cell.
