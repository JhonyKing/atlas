import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import { LocaleProvider } from "@/i18n";

export const metadata: Metadata = {
  title: "ATLAS AI",
  description: "Evidence-first technical research with verifiable citations.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body><LocaleProvider>{children}</LocaleProvider></body>
    </html>
  );
}
