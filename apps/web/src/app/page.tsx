import type { Metadata } from "next";

import { ProductHome } from "@/features/home/ProductHome";

export const metadata: Metadata = {
  title: "Answers you can verify",
  description: "Research AI technologies and decisions with answers backed by inspectable sources and citations.",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url: "/",
    title: "ATLAS AI — Answers you can verify",
    description: "Research AI technologies and decisions with answers backed by inspectable sources and citations.",
  },
};

function HomePage() {
  return <main className="ask-page"><ProductHome /></main>;
}

export default HomePage;
