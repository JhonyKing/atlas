import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { EngineeringPage } from "@/features/engineering/EngineeringPage";

type LocalizedEngineeringProps = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: LocalizedEngineeringProps): Promise<Metadata> {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") return {};
  const spanish = locale === "es";
  const canonical = `/${locale}/engineering`;
  const title = spanish ? "Caso de ingeniería" : "Engineering case study";
  const description = spanish
    ? "Explora la arquitectura RAG, agentes, recuperación, verificación, persistencia, evaluación y observabilidad de ATLAS AI."
    : "Explore the RAG, agent, retrieval, verification, persistence, evaluation, and observability architecture behind ATLAS AI.";
  return {
    title,
    description,
    alternates: { canonical, languages: { "en-US": "/en/engineering", "es-MX": "/es/engineering" } },
    openGraph: { type: "website", url: canonical, title: `ATLAS AI — ${title}`, description },
  };
}

export default async function LocalizedEngineeringRoute({ params }: LocalizedEngineeringProps) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main className="engineering-page"><EngineeringPage /></main>;
}
