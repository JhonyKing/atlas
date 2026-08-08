import { notFound } from "next/navigation";

import { ReviewPanel } from "@/features/agent/ReviewPanel";

export default async function LocalizedAdminReviewsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main className="admin-page"><ReviewPanel /></main>;
}
