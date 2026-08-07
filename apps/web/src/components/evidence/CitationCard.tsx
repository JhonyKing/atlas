export type CitationCardProps = {
  number?: number;
  sourceTitle: string;
  publisher: string;
  sourceType: string;
  excerpt: string;
  canonicalUrl: string;
  metadata?: string;
  openLabel?: string;
};

export function CitationCard({ number, sourceTitle, publisher, sourceType, excerpt, canonicalUrl, metadata, openLabel = "Open source" }: CitationCardProps) {
  return (
    <article className="atlas-citation-card">
      <div className="atlas-citation-heading">
        {number ? <span className="atlas-citation-number" aria-label={`Citation ${number}`}>{number}</span> : null}
        <div>
          <h3>{sourceTitle}</h3>
          <p><span className="atlas-citation-publisher">{publisher}</span> · <span>{sourceType}</span>{metadata ? ` · ${metadata}` : ""}</p>
        </div>
      </div>
      <blockquote>{excerpt}</blockquote>
      <a href={canonicalUrl} target="_blank" rel="noreferrer noopener">{openLabel} {sourceTitle}</a>
    </article>
  );
}
