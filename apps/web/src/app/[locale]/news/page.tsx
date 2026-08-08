import { notFound } from "next/navigation";

import { DailyNews } from "@/features/news/DailyNews";

export default async function LocalizedNewsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main className="news-page"><DailyNews /></main>;
}
