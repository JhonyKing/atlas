# ATLAS web deployment

The public web is a Next.js application intended for Vercel. Configure separate Preview and
Production environments. The only browser-visible API setting is `NEXT_PUBLIC_API_ORIGIN`; it
must be an absolute HTTPS origin in hosted environments and must never contain a secret.

The repository pins Node 24 and pnpm 11. Vercel should use the checked-in `apps/web/vercel.json`
configuration and deploy from the monorepo root. The API and ingestion worker are separate
managed-container workloads; they are not Vercel functions.
