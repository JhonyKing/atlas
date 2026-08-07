import { notFound } from "next/navigation";

import { SessionPanel } from "@/features/auth/SessionPanel";
import { PrivateResourcesPanel } from "@/features/private-data/PrivateResourcesPanel";
import { PrivateUploadPanel } from "@/features/private-data/PrivateUploadPanel";

export default async function LocalizedAccountPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (locale !== "en" && locale !== "es") notFound();
  return <main><SessionPanel /><PrivateResourcesPanel /><PrivateUploadPanel /></main>;
}
