# ADR 0017: Progressive disclosure for product and portfolio audiences

**Status**: Accepted  
**Date**: 2026-08-11

## Context

ATLAS implements agent planning, typed tools, budgets, approvals, governed retrieval, evidence
verification, and observability. Showing those mechanisms before the primary question field makes
the system impressive to an engineer but difficult for an ordinary AI user to understand quickly.
Removing them would weaken the product and its portfolio value.

## Decision

1. Make the default Home outcome-led: “Answers you can verify,” three familiar workflow actions,
   and a question form with automatic source selection.
2. Use progressive disclosure for manual source selection and internal agent controls.
3. Preserve the complete agent workspace on the public `/engineering` case-study route.
4. Require every technical capability shown to recruiters to link to repository evidence.
5. Treat missing hosted API configuration as a typed, localized availability state. Never expose
   a secret name, environment key, or raw configuration exception to a visitor.
6. Keep the canonical production domain indexable; accept Vercel's noindex policy on noncanonical
   team/preview aliases.
7. Apply the same boundary to secondary public workflows: decision presets before raw comparison
   controls, completed-research guidance before report IDs, trust language before ingestion
   metrics, and anonymous-use guidance before private-account controls.

## Alternatives considered

- Keep the agent workspace above the question form: rejected because infrastructure terminology
  dominates the first-use experience.
- Remove advanced controls from the frontend: rejected because it hides implemented capabilities
  and reduces operator/recruiter inspectability.
- Build a separate static portfolio site: rejected because it could drift from the executable
  product and make unsupported architecture claims.

## Consequences

Ordinary users receive a smaller cognitive load, while engineers retain direct access to the real
system depth. Home and Engineering must remain consistent with the same SpecKit artifacts and
tests. The UI can safely explain that the API is unavailable, but full hosted functionality still
depends on Feature 018 provisioning the managed backend.

The public routes keep their complete functional controls, but those controls no longer need to be
understood before a visitor knows what the route is for. Native `details` elements preserve
keyboard access and expose manual report identifiers and source-ingestion metadata on demand.
