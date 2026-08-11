# Presentation Data Model: Product Clarity and Engineering Portfolio

This feature adds no persisted database entity. The following view models define the public presentation boundary.

## PrimaryAction

- `id`: `ask | compare | report`
- `label`: localized, user-facing action
- `description`: localized outcome statement
- `href`: locale-preserving public route
- `primary`: exactly one action is primary

Validation:

- Exactly three actions are rendered.
- Labels do not use internal tool identifiers.
- Destinations resolve for unprefixed, English, and Spanish routes.

## ResearchSourcePreference

- `mode`: `automatic | manual`
- `collection`: optional existing collection slug

State transitions:

```text
automatic (default) -> advanced options opened -> manual collection selected
manual -> "Automatic" selected -> automatic
```

Validation:

- Automatic mode omits the collection constraint from the existing answer request.
- Manual mode only accepts existing supported collection values.

## EngineeringCapability

- `id`: stable presentation identifier
- `title`: plain-language technical capability
- `summary`: what the capability does in ATLAS
- `evidenceHref`: public repository link to implementation/architecture/verification evidence
- `status`: `implemented | measured | limitation`

Validation:

- Every claim has an evidence link or is explicitly marked as a limitation.
- No private URLs, credentials, internal IDs, or unsupported metrics are rendered.

## ApiAvailability

- `available`: whether a valid public HTTPS API origin is configured for the current environment
- `reason`: internal typed reason, never shown verbatim
- `publicMessage`: localized availability explanation

Validation:

- Hosted environments never fall back to localhost.
- Environment-variable names are absent from rendered content.

## PublicRouteEvidence

- `route`: tested route
- `viewport`: `1440x900 | 390x844`
- `status`: HTTP status
- `anonymous`: no Vercel authentication surface observed
- `overflow`: horizontal overflow count
- `metadata`: title, description, canonical, OpenGraph, robots result
- `capturedAt`: UTC verification time
