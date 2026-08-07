"use client";

import { useState } from "react";

import { useLocale, formatDate } from "@/i18n";
import type { CitedClaim, CitedEvidence } from "@/features/cited-answer/types";
import { CitationCard } from "@/components/evidence/CitationCard";
import { EvidenceStatus } from "@/components/evidence/EvidenceStatus";

import type { EvidencePanelProps, FeedbackCategory, FeedbackInput, FeedbackLabel } from "./types";

const categoryValues: FeedbackCategory[] = ["incorrect_citation", "incorrect_answer", "outdated", "incomplete", "other"];

export function EvidencePanel({ claims, citations, limitations = [], answerStatus = "complete", onFeedback }: EvidencePanelProps) {
  const { messages } = useLocale();
  const [selectedLabel, setSelectedLabel] = useState<FeedbackLabel | null>(null);
  const [category, setCategory] = useState<FeedbackCategory | null>(null);
  const [comment, setComment] = useState("");

  const submitFeedback = (feedback: FeedbackInput) => {
    setSelectedLabel(feedback.label);
    void onFeedback(feedback);
  };

  const saveDetailedFeedback = () => {
    if (!selectedLabel) return;
    const feedback: FeedbackInput = { label: selectedLabel, category };
    if (comment.trim()) feedback.comment = comment.trim();
    void onFeedback(feedback);
  };

  return (
    <section className="evidence-panel" aria-labelledby="evidence-title">
      <h2 id="evidence-title">{messages.evidenceTitle}</h2>
      <EvidenceStatus state={answerStatus === "partial" ? "partial" : "supported"} label={answerStatus === "partial" ? messages.partialAnswer : messages.completeAnswer} />
      <div className="claim-list">
        {claims.map((claim) => <ClaimWithEvidence key={claim.id} claim={claim} citations={citations} />)}
      </div>
      {limitations.length ? <p className="limitations">{limitations.join(" ")}</p> : null}
      <div className="feedback" aria-labelledby="feedback-title">
        <h3 id="feedback-title">{messages.usefulQuestion}</h3>
        <div className="feedback-actions">
          <button type="button" aria-pressed={selectedLabel === "useful"} onClick={() => submitFeedback({ label: "useful", category: null })}>{messages.markUseful}</button>
          <button type="button" aria-pressed={selectedLabel === "not_useful"} onClick={() => setSelectedLabel("not_useful")}>{messages.markNotUseful}</button>
        </div>
        {selectedLabel === "not_useful" ? (
          <div className="feedback-details">
            <label htmlFor="feedback-category">{messages.failureCategory}</label>
            <select id="feedback-category" value={category ?? ""} onChange={(event) => setCategory((event.target.value || null) as FeedbackCategory | null)}>
              <option value="">{messages.chooseCategory}</option>
              {categoryValues.map((value) => <option key={value} value={value}>{messages.categories[value]}</option>)}
            </select>
            <label htmlFor="feedback-comment">{messages.comment}</label>
            <textarea id="feedback-comment" value={comment} maxLength={1000} onChange={(event) => setComment(event.target.value)} rows={3} />
            <button type="button" onClick={saveDetailedFeedback}>{messages.saveFeedback}</button>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function ClaimWithEvidence({ claim, citations }: { claim: CitedClaim; citations: CitedEvidence[] }) {
  const { messages } = useLocale();
  const claimCitations = claim.citation_ids
    .map((citationId) => citations.find((citation) => citation.id === citationId))
    .filter((citation): citation is CitedEvidence => citation !== undefined);
  const claimLabel = claim.type === "inference" ? messages.inference : messages.factualClaim;

  return (
    <article className="claim-card">
      <p className="claim-kind">{claimLabel}</p>
      <p>{claim.text}</p>
      <ul className="citation-list">
        {claimCitations.map((citation) => <li key={citation.id}><CitationDetails citation={citation} /></li>)}
      </ul>
    </article>
  );
}

function CitationDetails({ citation }: { citation: CitedEvidence }) {
  const { locale, messages } = useLocale();
  const sourceType = messages.sourceTypes[citation.source_type] ?? citation.source_type.replaceAll("_", " ");
  const metadata = [
    `${messages.captured}: ${formatDate(citation.captured_at, locale)}`,
    citation.published_at ? `${messages.published}: ${formatDate(citation.published_at, locale)}` : null,
    citation.version_label ? `${messages.version}: ${citation.version_label}` : null,
  ].filter((value): value is string => Boolean(value)).join(" · ");
  return (
    <div className="citation-details">
      <CitationCard
        sourceTitle={citation.source_title}
        publisher={citation.publisher}
        sourceType={sourceType}
        excerpt={citation.excerpt}
        canonicalUrl={citation.canonical_url}
        openLabel={messages.openSource}
        metadata={metadata}
      />
      {citation.version_label ? <p className="citation-version">{citation.version_label}</p> : null}
      {citation.source_revision_url ? <p className="citation-links"><a href={citation.source_revision_url} target="_blank" rel="noreferrer noopener">{messages.openRevision}</a></p> : null}
    </div>
  );
}
