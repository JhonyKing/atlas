export type CitationCardProps = {
  number?: number;
  sourceTitle: string;
  publisher: string;
  sourceType: string;
  excerpt: string;
  canonicalUrl: string;
  metadata?: string;
};

export function CitationCard({ number, sourceTitle, publisher, sourceType, excerpt, canonicalUrl, metadata }: CitationCardProps) {
  return (
    <article className="atlas-citation-card">
      <div className="atlas-citation-heading">
        {number ? <span className="atlas-citation-number" aria-label={`Citation ${number}`}>{number}</span> : null}
        <div>
          <h3>{sourceTitle}</h3>
          <p>{publisher} · {sourceType}{metadata ? ` · ${metadata}` : ""}</p>
        </div>
      </div>
      <blockquote>{excerpt}</blockquote>
      <a href={canonicalUrl} target="_blank" rel="noreferrer noopener">Open source</a>
    </article>
  );
}
