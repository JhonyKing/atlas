import { notFound } from "next/navigation";

import { ComparisonPlaceholder } from "@/features/comparison/ComparisonPlaceholder";

export default async function ComparisonPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main><ComparisonPlaceholder /></main>;
}
