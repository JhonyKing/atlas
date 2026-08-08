import { notFound } from "next/navigation";

import { AccountPageContent } from "@/features/account/AccountPageContent";

export default async function LocalizedAccountPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <AccountPageContent />;
}
