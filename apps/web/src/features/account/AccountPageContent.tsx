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
        <p className="eyebrow">{locale === "es-MX" ? "Investigación privada opcional" : "Optional private research"}</p>
        <h1>{locale === "es-MX" ? "Tu espacio privado de investigación" : "Your private research space"}</h1>
        <p className="lede">
          {locale === "es-MX"
            ? "Iniciar sesión es opcional. Hazlo cuando quieras conservar materiales privados y mantenerlos separados de la investigación pública."
            : "Signing in is optional. Use it when you want to keep private materials separate from public research."}
        </p>
        <p className="account-anonymous-note">{locale === "es-MX" ? "La investigación anónima sigue disponible desde Preguntar, Comparar y Noticias." : "Anonymous research remains available through Ask, Compare, and News."}</p>
      </div>
      <div className="account-grid">
        <SessionPanel locale={locale} />
        <PrivateResourcesPanel locale={locale} />
        <PrivateUploadPanel locale={locale} />
      </div>
    </main>
  );
}
