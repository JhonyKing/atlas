"use client";

import { useEffect, useState } from "react";

export function PrivateResourcesPanel() {
  const [items, setItems] = useState<Array<{ resource_id: string; resource_type: string }>>([]);
  useEffect(() => {
    void fetch("/v1/private/resources", { credentials: "include" })
      .then((response) => (response.ok ? response.json() : { items: [] }))
      .then((body: { items: Array<{ resource_id: string; resource_type: string }> }) => setItems(body.items));
  }, []);
  return <section aria-label="Private resources"><h2>Mis recursos privados</h2><ul>{items.map((item) => <li key={item.resource_id}>{item.resource_type}</li>)}</ul></section>;
}
