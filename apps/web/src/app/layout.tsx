import type { Metadata } from "next";
import { headers } from "next/headers";
import type { ReactNode } from "react";

import "./globals.css";
import { LocaleProvider, type Locale } from "@/i18n";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  metadataBase: new URL("https://atlasai-lilac.vercel.app"),
  title: {
    default: "ATLAS AI — Answers you can verify",
    template: "%s | ATLAS AI",
  },
  description: "Research AI technologies and decisions with answers backed by inspectable sources, dates, and citations.",
  applicationName: "ATLAS AI",
  authors: [{ name: "Jhonnatan Vazquez", url: "https://github.com/JhonyKing" }],
  creator: "Jhonnatan Vazquez",
  keywords: ["AI research", "RAG", "AI agents", "citation verification", "LLM evaluation"],
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    siteName: "ATLAS AI",
    title: "ATLAS AI — Answers you can verify",
    description: "Research AI technologies and decisions with answers backed by inspectable sources and citations.",
    images: [{ url: "/brand/atlas-logo-horizontal.png", alt: "ATLAS AI" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ATLAS AI — Answers you can verify",
    description: "Evidence-backed research for AI technologies and decisions.",
    images: ["/brand/atlas-logo-horizontal.png"],
  },
  icons: {
    icon: [
      { url: "/brand/favicon.svg", type: "image/svg+xml" },
      { url: "/brand/favicon.png", type: "image/png", sizes: "64x64" },
    ],
    apple: "/brand/apple-touch-icon.png",
  },
};

export default async function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  const requestHeaders = await headers();
  const localeHeader = requestHeaders.get("x-atlas-locale");
  const initialLocale: Locale | undefined = localeHeader === "es-MX" || localeHeader === "en-US"
    ? localeHeader
    : undefined;

  return (
    <html lang={initialLocale ?? "en-US"}>
      <body><LocaleProvider initialLocale={initialLocale}><AppShell>{children}</AppShell></LocaleProvider></body>
    </html>
  );
}
