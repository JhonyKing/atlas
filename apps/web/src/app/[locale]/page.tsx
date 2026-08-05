import { notFound } from "next/navigation";

import { HomePage } from "@/app/page";

export default async function LocalizedHomePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <HomePage />;
}
