"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { useLocale, type Locale } from "@/i18n";

const navigation = [
  { key: "ask", en: "Ask", es: "Preguntar", path: "" },
  { key: "compare", en: "Compare", es: "Comparar", path: "compare" },
  { key: "reports", en: "Reports", es: "Reportes", path: "reports" },
  { key: "news", en: "News", es: "Noticias", path: "news" },
  { key: "sources", en: "Sources", es: "Fuentes", path: "sources" },
  { key: "account", en: "Account", es: "Cuenta", path: "account" },
] as const;

const shellCopy = {
  "en-US": { nav: "Primary navigation", switchTo: "Español", menu: "Menu", brand: "ATLAS" },
  "es-MX": { nav: "Navegación principal", switchTo: "English", menu: "Menú", brand: "ATLAS" },
} as const;

const localeTargetCopy = {
  "en-US": { flagSrc: "/brand/flag-mx.svg", label: "Español", ariaLabel: "Switch to Spanish" },
  "es-MX": { flagSrc: "/brand/flag-us.svg", label: "English", ariaLabel: "Cambiar a inglés" },
} as const;

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname() ?? "/";
  const router = useRouter();
  const { locale, setLocale } = useLocale();
  const [menuOpen, setMenuOpen] = useState(false);
  const spanish = locale === "es-MX";
  const segment = pathname.startsWith("/es") ? "es" : pathname.startsWith("/en") ? "en" : "";
  const routePath = segment ? pathname.slice(segment.length + 1) : pathname.slice(1);
  const copy = shellCopy[locale];
  const targetCopy = localeTargetCopy[locale];

  function hrefFor(path: string): string {
    const suffix = path ? `/${path}` : "";
    return segment ? `/${segment}${suffix}` : path ? `/${path}` : "/";
  }

  function isActive(path: string): boolean {
    if (!path) return routePath === "";
    return routePath === path || routePath.startsWith(`${path}/`);
  }

  function switchLocale() {
    const next: Locale = spanish ? "en-US" : "es-MX";
    const nextSegment = next === "es-MX" ? "es" : "en";
    const suffix = routePath ? `/${routePath}` : "";
    setLocale(next);
    router.push(`/${nextSegment}${suffix}`);
  }

  return (
    <div className="atlas-shell">
      <a className="atlas-skip-link" href="#main-content">Skip to content</a>
      <header className="atlas-header">
        <Link className="atlas-brand" href={hrefFor("")} aria-label={copy.brand}>
          <Image className="atlas-logo-horizontal" src="/brand/atlas-logo-horizontal.svg" alt="ATLAS" width={148} height={46} priority />
          <Image className="atlas-logo-mark" src="/brand/atlas-mark.svg" alt="ATLAS" width={38} height={38} priority />
        </Link>
        <nav id="atlas-navigation" className={menuOpen ? "atlas-nav open" : "atlas-nav"} aria-label={copy.nav}>
          {navigation.map((item) => (
            <Link className={isActive(item.path) ? "atlas-nav-link active" : "atlas-nav-link"} href={hrefFor(item.path)} key={item.key} aria-current={isActive(item.path) ? "page" : undefined} onClick={() => setMenuOpen(false)}>
              {spanish ? item.es : item.en}
            </Link>
          ))}
        </nav>
        <button className="atlas-locale-switch" type="button" onClick={switchLocale} aria-label={targetCopy.ariaLabel}>
          <Image className="atlas-locale-flag" src={targetCopy.flagSrc} alt="" width={22} height={15} aria-hidden="true" />
          <span>{targetCopy.label}</span>
        </button>
        <button className="atlas-mobile-menu" type="button" aria-expanded={menuOpen} aria-controls="atlas-navigation" onClick={() => setMenuOpen((open) => !open)}>
          {copy.menu}
        </button>
      </header>
      <div className="atlas-content" id="main-content" tabIndex={-1}>{children}</div>
    </div>
  );
}
