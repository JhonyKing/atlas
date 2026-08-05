"use client";

import { useLocale } from "@/i18n";

export function ComparisonPlaceholder() {
  const { locale } = useLocale();
  const isSpanish = locale === "es-MX";
  return (
    <section aria-labelledby="comparison-placeholder-title">
      <p>{isSpanish ? "Comparador de tecnologías" : "Technology comparator"}</p>
      <h1 id="comparison-placeholder-title">
        {isSpanish
          ? "Selecciona de 2 a 4 tecnologías para compararlas con evidencia."
          : "Select 2 to 4 technologies to compare them with evidence."}
      </h1>
      <p>
        {isSpanish
          ? "Esta pantalla es solo la base visual. No muestra resultados sin verificar."
          : "This is only the visual foundation. It does not show unverified results."}
      </p>
    </section>
  );
}
