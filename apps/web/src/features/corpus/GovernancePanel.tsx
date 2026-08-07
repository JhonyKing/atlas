"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

type Collection = {
  slug: string;
  display_name: string;
  kind: string;
  policy_state: string;
  enabled: boolean;
  source_count: number;
  stale_count: number;
  disabled_count: number;
  retry_count: number;
  dead_letter_count: number;
};

export function GovernancePanel() {
  const pathname = usePathname();
  const spanish = pathname?.startsWith("/es") ?? true;
  const [collections, setCollections] = useState<Collection[]>([]);
  const [message, setMessage] = useState(
    spanish ? "Cargando gobierno del corpus…" : "Loading corpus governance…",
  );
  useEffect(() => {
    void fetch("/v1/corpus/governance")
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error("unavailable"))))
      .then((body: { collections: Collection[] }) => {
        setCollections(body.collections);
        setMessage(spanish ? "Estado de fuentes actualizado." : "Source status updated.");
      })
      .catch(() =>
        setMessage(
          spanish ? "Gobierno del corpus no disponible." : "Corpus governance unavailable.",
        ),
      );
  }, [spanish]);
  return (
    <section aria-labelledby="governance-title">
      <h2 id="governance-title">{spanish ? "Gobierno del corpus" : "Corpus governance"}</h2>
      <p aria-live="polite">{message}</p>
      <ul>
        {collections.slice(0, 16).map((collection) => (
          <li key={collection.slug}>
            <strong>{collection.display_name}</strong>: {collection.policy_state}; {collection.source_count}{" "}
            {spanish ? "fuentes" : "sources"}; {collection.stale_count}{" "}
            {spanish ? "obsoletas" : "stale"}; {collection.dead_letter_count} dead letter.
          </li>
        ))}
      </ul>
    </section>
  );
}
