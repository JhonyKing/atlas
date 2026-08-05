"use client";

import { useEffect, useState } from "react";

import { formatDate, useLocale } from "@/i18n";
import { getCorpusStatus } from "./api";
import type { CorpusCollectionStatus, CorpusStatusPayload } from "./types";

export function CorpusStatus() {
  const { locale, messages } = useLocale();
  const [payload, setPayload] = useState<CorpusStatusPayload | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let active = true;
    void getCorpusStatus()
      .then((next) => { if (active) setPayload(next); })
      .catch(() => { if (active) setUnavailable(true); });
    return () => { active = false; };
  }, []);

  if (unavailable) return <p className="corpus-status-message" aria-live="polite">{messages.unavailableCorpus}</p>;
  if (!payload) return <p className="corpus-status-message" aria-live="polite">{messages.loadingCorpus}</p>;

  return (
    <section className="corpus-status" aria-labelledby="corpus-title">
      <div className="corpus-status-heading">
        <div><p className="eyebrow">{messages.corpusEyebrow}</p><h2 id="corpus-title">{messages.corpusTitle}</h2></div>
        <p className="corpus-snapshot">{messages.snapshot} {payload.snapshot_id.slice(0, 8)} · {formatDate(payload.generated_at, locale, "medium")}</p>
      </div>
      <ul className="corpus-list">{payload.collections.map((collection) => <CollectionCard key={collection.slug} collection={collection} />)}</ul>
    </section>
  );
}

function CollectionCard({ collection }: { collection: CorpusCollectionStatus }) {
  const { locale, messages } = useLocale();
  const stateLabel = messages.states[collection.status] ?? collection.status;
  const sourceTypes = collection.source_types.map((type) => messages.sourceTypes[type] ?? type).join(", ");
  return (
    <li className="corpus-card">
      <div className="corpus-card-title"><h3>{collection.name}</h3><span className={`corpus-badge corpus-${collection.status}`}>{stateLabel}</span></div>
      <p>{collection.publisher} · {sourceTypes}</p>
      <p className="corpus-counts">
        {messages.sourceCount}: {collection.source_count ?? 0} · {messages.pageCount}: {collection.page_count ?? 0} · {messages.chunkCount}: {collection.chunk_count ?? 0}
      </p>
      <p className="corpus-date">{messages.lastVerified}: {collection.last_success_at ? formatDate(collection.last_success_at, locale, "medium") : messages.notVerified}</p>
      <a href={collection.canonical_root} target="_blank" rel="noreferrer noopener">{messages.openCanonical}</a>
    </li>
  );
}
