"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Button } from "@/components/forms";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [message, setMessage] = useState("");
  const loadGovernance = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const response = await fetch("/v1/corpus/governance");
      if (!response.ok) throw new Error("unavailable");
      const body = (await response.json()) as { collections: Collection[] };
      setCollections(body.collections);
      setMessage(spanish ? "Estado de fuentes actualizado." : "Source status updated.");
    } catch {
      setCollections([]);
      setError(true);
      setMessage(spanish ? "Gobierno del corpus no disponible." : "Corpus governance unavailable.");
    } finally {
      setLoading(false);
    }
  }, [spanish]);
  useEffect(() => {
    const timer = window.setTimeout(() => { void loadGovernance(); }, 0);
    return () => window.clearTimeout(timer);
  }, [loadGovernance]);
  return (
    <section className="admin-panel governance-panel" aria-labelledby="governance-title">
      <h2 id="governance-title">{spanish ? "Gobierno del corpus" : "Corpus governance"}</h2>
      <div className="admin-panel-toolbar"><p aria-live="polite">{loading ? (spanish ? "Cargando…" : "Loading…") : message}</p><Button type="button" variant="tertiary" loading={loading} onClick={() => void loadGovernance()}>{spanish ? "Actualizar" : "Refresh"}</Button></div>
      {error ? <p className="account-error" role="alert">{spanish ? "No se pudo consultar el estado. Intenta de nuevo." : "The status could not be loaded. Try again."}</p> : null}
      {!loading && !error && collections.length ? <ul className="governance-list">
        {collections.slice(0, 16).map((collection) => (
          <li key={collection.slug} className="governance-card">
            <div className="governance-card-heading"><strong>{collection.display_name}</strong><span className="governance-policy">{collection.policy_state}</span></div>
            <dl className="governance-metrics">
              <div><dt>{spanish ? "Fuentes" : "Sources"}</dt><dd>{collection.source_count}</dd></div>
              <div><dt>{spanish ? "Obsoletas" : "Stale"}</dt><dd>{collection.stale_count}</dd></div>
              <div><dt>{spanish ? "Reintentos" : "Retries"}</dt><dd>{collection.retry_count}</dd></div>
              <div><dt>Dead letter</dt><dd>{collection.dead_letter_count}</dd></div>
            </dl>
          </li>
        ))}
      </ul> : !loading && !error ? <div className="empty-state"><strong>{spanish ? "Sin colecciones para mostrar" : "No collections to show"}</strong><span>{spanish ? "El estado aparecerá cuando el corpus esté disponible." : "Status will appear when the corpus is available."}</span></div> : null}
    </section>
  );
}
