"use client";

import { useEffect, useState } from "react";

export function PrivateResourcesPanel({ locale = "es-MX" }: { locale?: "en-US" | "es-MX" }) {
  const [items, setItems] = useState<Array<{ resource_id: string; resource_type: string }>>([]);
  useEffect(() => {
    void fetch("/v1/private/resources", { credentials: "include" })
      .then((response) => (response.ok ? response.json() : { items: [] }))
      .then((body: { items: Array<{ resource_id: string; resource_type: string }> }) => setItems(body.items));
  }, []);
  const spanish = locale === "es-MX";
  return (
    <section className="account-panel" aria-label={spanish ? "Recursos privados" : "Private resources"}>
      <h2>{spanish ? "Mis recursos privados" : "My private resources"}</h2>
      {items.length ? (
        <ul className="account-resource-list">{items.map((item) => <li key={item.resource_id}>{item.resource_type}</li>)}</ul>
      ) : (
        <p className="empty-state">{spanish ? "Todavía no tienes recursos privados." : "You do not have private resources yet."}</p>
      )}
    </section>
  );
}
