# ATLAS web deployment

The public web is a Next.js application intended for Vercel. Configure separate Preview and
Production environments. The only browser-visible API setting is `NEXT_PUBLIC_API_ORIGIN`; it
must be an absolute HTTPS origin in hosted environments and must never contain a secret.

The repository pins Node 24 and pnpm 11. The Vercel project should use **Root Directory**
`apps/web`, so the app-level `vercel.json` and Next.js defaults are applied. A repository-root
`vercel.json` is also checked in as a safe fallback for projects that still deploy from the
monorepo root; it points the build output at `apps/web/.next`. The workspace lockfile remains at
the repository root and pnpm resolves it through the workspace. The API and ingestion worker are
separate managed-container workloads; they are not Vercel functions.
