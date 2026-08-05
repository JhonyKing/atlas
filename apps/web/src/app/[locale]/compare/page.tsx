import { notFound } from "next/navigation";

import { ComparisonPage } from "@/features/comparison/ComparisonPage";

export default async function LocalizedComparisonPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <ComparisonPage />;
}
