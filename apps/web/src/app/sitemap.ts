import type { MetadataRoute } from "next";

const SITE_URL = "https://atlasai-lilac.vercel.app";
const publicPaths = ["", "/compare", "/reports", "/news", "/sources", "/account", "/engineering"] as const;

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date("2026-08-11T00:00:00Z");
  return ["", "/en", "/es"].flatMap((prefix) => publicPaths.map((path) => ({
    url: `${SITE_URL}${prefix}${path || ""}` || SITE_URL,
    lastModified,
    changeFrequency: path === "/news" ? "daily" as const : "weekly" as const,
    priority: path === "" ? 1 : path === "/engineering" ? 0.8 : 0.7,
  })));
}
