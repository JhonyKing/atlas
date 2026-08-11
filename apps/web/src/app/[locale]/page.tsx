import type { Metadata } from "next";
import { notFound } from "next/navigation";

import HomePage from "@/app/page";

type LocalizedHomeProps = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: LocalizedHomeProps): Promise<Metadata> {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") return {};
  const spanish = locale === "es";
  const canonical = `/${locale}`;
  const title = spanish ? "Respuestas que puedes verificar" : "Answers you can verify";
  const description = spanish
    ? "Investiga tecnologías y decisiones de IA con respuestas respaldadas por fuentes y citas inspeccionables."
    : "Research AI technologies and decisions with answers backed by inspectable sources and citations.";
  return {
    title,
    description,
    alternates: { canonical, languages: { "en-US": "/en", "es-MX": "/es" } },
    openGraph: { type: "website", url: canonical, title: `ATLAS AI — ${title}`, description },
  };
}

export default async function LocalizedHomePage({ params }: LocalizedHomeProps) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <HomePage />;
}
