import { notFound } from "next/navigation";

import { GovernancePanel } from "@/features/corpus/GovernancePanel";
import { ReviewPanel } from "@/features/agent/ReviewPanel";

export default async function LocalizedAdminPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main className="admin-page"><GovernancePanel /><ReviewPanel /></main>;
}
