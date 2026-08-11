import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    // Keep the application root stable in local dev, Playwright, and Vercel.
    // Letting Turbopack infer it from `src/app` breaks hydration in the monorepo.
    root: process.cwd(),
  },
};

export default nextConfig;
