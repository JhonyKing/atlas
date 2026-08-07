import { notFound } from "next/navigation";

import { GovernancePanel } from "@/features/corpus/GovernancePanel";

export default async function LocalizedAdminSourcesPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main><GovernancePanel /></main>;
}
