import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    // Vercel deploys this app with `apps/web` as the project root. Keeping the
    // workspace root locally while using the deployment root on Vercel avoids
    // output-tracing warnings and preserves monorepo imports during development.
    root: process.env.VERCEL === "1" ? __dirname : path.resolve(__dirname, "../.."),
  },
};

export default nextConfig;
