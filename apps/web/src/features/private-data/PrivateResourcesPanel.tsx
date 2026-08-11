"use client";

import { useEffect, useState } from "react";

import { getApiUrl } from "@/lib/env";

export function PrivateResourcesPanel({ locale = "es-MX" }: { locale?: "en-US" | "es-MX" }) {
  const [items, setItems] = useState<Array<{ resource_id: string; resource_type: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [unavailable, setUnavailable] = useState(false);
  useEffect(() => {
    let active = true;
    void Promise.resolve()
      .then(() => fetch(getApiUrl("/v1/private/resources"), { credentials: "include" }))
      .then(async (response) => {
        if (response.status === 401 || response.status === 403) return { items: [] };
        if (!response.ok) throw new Error("private_resources_unavailable");
        return response.json();
      })
      .then((body: { items: Array<{ resource_id: string; resource_type: string }> }) => {
        if (!active) return;
        setItems(body.items);
        setUnavailable(false);
      })
      .catch(() => { if (active) setUnavailable(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const spanish = locale === "es-MX";
  return (
    <section className="account-panel" aria-label={spanish ? "Recursos privados" : "Private resources"}>
      <h2>{spanish ? "Mis recursos privados" : "My private resources"}</h2>
      {loading ? <p className="account-status" role="status">{spanish ? "Cargando recursos…" : "Loading resources…"}</p> : null}
      {!loading && unavailable ? <p className="account-error" role="alert">{spanish ? "Los recursos privados no están disponibles ahora." : "Private resources are unavailable right now."}</p> : null}
      {!loading && !unavailable && items.length ? (
        <ul className="account-resource-list">{items.map((item) => <li key={item.resource_id}>{item.resource_type}</li>)}</ul>
      ) : !loading && !unavailable ? (
        <p className="empty-state">{spanish ? "Todavía no tienes recursos privados." : "You do not have private resources yet."}</p>
      ) : null}
    </section>
  );
}
