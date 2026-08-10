import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import { LocaleProvider } from "@/i18n";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "ATLAS AI",
  description: "Evidence-first technical research with verifiable citations.",
  icons: {
    icon: [
      { url: "/brand/favicon.svg", type: "image/svg+xml" },
      { url: "/brand/favicon.png", type: "image/png", sizes: "64x64" },
    ],
    apple: "/brand/apple-touch-icon.png",
  },
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body><LocaleProvider><AppShell>{children}</AppShell></LocaleProvider></body>
    </html>
  );
}
