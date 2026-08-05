# Research: Evidence-Backed Technology Comparator

## Decision 1: Reuse the existing corpus and exact hybrid retrieval baseline

**Decision**: Each technology/criterion branch searches the selected verified corpus snapshot using
the existing keyword-plus-vector retrieval contract.

**Rationale**: It preserves immutable evidence IDs, source filters, temporal constraints and the
retrieval baseline already evaluated for cited answers.

**Alternatives considered**: A new comparison-only index would duplicate provenance logic; live web
search would violate the feature boundary and make results non-reproducible.

## Decision 2: Use explicit cell states instead of filling every cell

**Decision**: A cell is `supported`, `unsupported`, `partial`, or `contradictory`.

**Rationale**: The PRD requires honest gaps and disagreements. An empty string or model-generated
placeholder would hide uncertainty.

**Alternatives considered**: Treating every cell as prose was rejected because reviewers could not
distinguish missing evidence from a verified negative claim.

## Decision 3: Normalize values before summary prose

**Decision**: Store value, unit, period, version and date context separately. Only compatible units
and periods may be compared directly.

**Rationale**: Price, context limits and latency are frequently reported with different units or
measurement conditions.

**Alternatives considered**: Letting a model normalize values implicitly was rejected because it is
not reproducible and can erase important qualifiers.

## Decision 4: Separate comparison quota from cited-answer quota

**Decision**: Start with five accepted comparisons per anonymous visitor in a rolling 24-hour
window. A repeated idempotency key does not consume another unit.

**Rationale**: A comparison fans out across multiple technologies and has a higher predictable cost
than a single cited question. Five is conservative for the portfolio MVP and can be adjusted by
configuration after measurement.

**Alternatives considered**: Reusing the ten-question quota would make the product's cost boundary
unclear; unlimited anonymous comparisons would violate the constitution's budget-guard requirement.

## Decision 5: Keep the matrix authoritative and summary optional

**Decision**: The structured matrix and cell evidence are the user-visible source of truth. A prose
summary is optional and cannot add claims that are absent from cells.

**Rationale**: This keeps the comparator visibly different from generic chat and preserves claim-
level citation parity across locales.

**Alternatives considered**: Returning only a generated recommendation was rejected because it would
hide unsupported criteria and make audit difficult.
