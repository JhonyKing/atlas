import { notFound } from "next/navigation";

import { ReportRequest } from "@/features/reports/ReportRequest";

export default async function LocalizedReportsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main><ReportRequest /></main>;
}
