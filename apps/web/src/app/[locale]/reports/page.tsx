import { notFound } from "next/navigation";
import { Suspense } from "react";

import { ReportRequest } from "@/features/reports/ReportRequest";

export default async function LocalizedReportsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main className="report-page"><Suspense fallback={<p>Loading report options…</p>}><ReportRequest /></Suspense></main>;
}
