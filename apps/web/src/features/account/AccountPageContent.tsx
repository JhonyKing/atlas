"use client";

import { useLocale } from "@/i18n";

import { SessionPanel } from "@/features/auth/SessionPanel";
import { PrivateResourcesPanel } from "@/features/private-data/PrivateResourcesPanel";
import { PrivateUploadPanel } from "@/features/private-data/PrivateUploadPanel";

export function AccountPageContent() {
  const { locale } = useLocale();
  return (
    <main className="account-page">
      <div className="account-page-intro">
        <p className="eyebrow">{locale === "es-MX" ? "Espacio privado" : "Private workspace"}</p>
        <h1>{locale === "es-MX" ? "Tu espacio ATLAS" : "Your ATLAS workspace"}</h1>
        <p className="lede">
          {locale === "es-MX"
            ? "Administra tu sesión y conserva tus materiales privados bajo tu control."
            : "Manage your session and keep private materials under your control."}
        </p>
      </div>
      <div className="account-grid">
        <SessionPanel locale={locale} />
        <PrivateResourcesPanel locale={locale} />
        <PrivateUploadPanel locale={locale} />
      </div>
    </main>
  );
}
