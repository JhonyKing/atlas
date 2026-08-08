import { notFound } from "next/navigation";

import { CorpusStatus } from "@/features/corpus/CorpusStatus";

export default async function LocalizedSourcesPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main className="sources-page"><CorpusStatus /></main>;
}
