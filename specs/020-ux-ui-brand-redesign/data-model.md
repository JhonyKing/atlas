# Data Model: ATLAS UX/UI and Brand Redesign

## DesignToken

Central CSS custom property with a semantic name, value, category, and usage rule. Token values are
defined once and consumed by components; raw brand hex values are not repeated in feature styles.

## BrandAsset

| Field | Rules |
|---|---|
| `id` | `stacked`, `horizontal`, `mark`, `favicon`, or app icon |
| `source_reference` | One of the inspected `imgs/` references |
| `format` | SVG primary; transparent PNG fallback where required |
| `dimensions` | Record source and generated dimensions |
| `transparency` | Must be preserved; no gray/screenshot background |
| `allowed_usage` | Route/components where the asset is valid |
| `minimum_size` | Documented in brand guidelines |

## EvidenceStatePresentation

Represents a user-facing state with more than color:

- `state`: supported/partial/unsupported/contradictory/information/stale/unavailable/loading
- `label`
- `icon_or_shape`
- `description`
- `foreground_token`
- `background_token`
- optional `evidence_count`, `snapshot`, `source_link`

## ResearchSurface

Route-level composition with route, purpose, primary action, loading/empty/error states, locale
behavior, required backend client, and visual-QA coverage.

## VisualQAArtifact

- `route`, `viewport`, `theme`, `source_revision`, `screenshot_path`, `check_result`, `findings`
- stored with the feature's verification evidence and never treated as a substitute for functional tests.
