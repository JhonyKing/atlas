"use client";

import { useEffect, useState } from "react";

import { getCorpusStatus } from "./api";
import type { CorpusCollectionStatus, CorpusStatusPayload } from "./types";

export function CorpusStatus() {
  const [payload, setPayload] = useState<CorpusStatusPayload | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let active = true;
    void getCorpusStatus()
      .then((next) => {
        if (active) setPayload(next);
      })
      .catch(() => {
        if (active) setUnavailable(true);
      });
    return () => {
      active = false;
    };
  }, []);

  if (unavailable) {
    return <p className="corpus-status-message" aria-live="polite">Corpus status unavailable.</p>;
  }
  if (!payload) {
    return <p className="corpus-status-message" aria-live="polite">Loading corpus status…</p>;
  }

  return (
    <section className="corpus-status" aria-labelledby="corpus-title">
      <div className="corpus-status-heading">
        <div>
          <p className="eyebrow">Verified source collections</p>
          <h2 id="corpus-title">Corpus status</h2>
        </div>
        <p className="corpus-snapshot">Snapshot {payload.snapshot_id.slice(0, 8)} · {formatDate(payload.generated_at)}</p>
      </div>
      <ul className="corpus-list">
        {payload.collections.map((collection) => <CollectionCard key={collection.slug} collection={collection} />)}
      </ul>
    </section>
  );
}

function CollectionCard({ collection }: { collection: CorpusCollectionStatus }) {
  return (
    <li className="corpus-card">
      <div className="corpus-card-title">
        <h3>{collection.name}</h3>
        <span className={`corpus-badge corpus-${collection.status}`}>{capitalize(collection.status)}</span>
      </div>
      <p>{collection.publisher} · {collection.source_types.join(", ")}</p>
      <p className="corpus-date">
        Last verified: {collection.last_success_at ? formatDate(collection.last_success_at) : "Not yet verified"}
      </p>
      <a href={collection.canonical_root} target="_blank" rel="noreferrer noopener">Open canonical root</a>
    </li>
  );
}

function capitalize(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeZone: "UTC" }).format(new Date(value));
}
