import type { Metadata } from "next";

import { EngineeringPage } from "@/features/engineering/EngineeringPage";

export const metadata: Metadata = {
  title: "Engineering case study",
  description: "Explore the RAG, agent, retrieval, verification, persistence, evaluation, and observability architecture behind ATLAS AI.",
  alternates: { canonical: "/engineering" },
  openGraph: {
    type: "website",
    url: "/engineering",
    title: "ATLAS AI Engineering Case Study",
    description: "Inspect the architecture and evidence behind ATLAS AI's verifiable research workflow.",
  },
};

export default function EngineeringRoute() {
  return <main className="engineering-page"><EngineeringPage /></main>;
}
