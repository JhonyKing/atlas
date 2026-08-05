"use client";

import { useState } from "react";

import { useLocale, formatDate } from "@/i18n";
import type { CitedClaim, CitedEvidence } from "@/features/cited-answer/types";

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
      <p className="answer-state">{answerStatus === "partial" ? messages.partialAnswer : messages.completeAnswer}</p>
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
  return (
    <article className="citation-card">
      <h3>{citation.source_title}</h3>
      <dl>
        <div><dt>{messages.publisher}</dt><dd>{citation.publisher}</dd></div>
        <div><dt>{messages.sourceType}</dt><dd>{sourceType}</dd></div>
        <div><dt>{messages.captured}</dt><dd>{formatDate(citation.captured_at, locale)}</dd></div>
        {citation.published_at ? <div><dt>{messages.published}</dt><dd>{formatDate(citation.published_at, locale)}</dd></div> : null}
        {citation.version_label ? <div><dt>{messages.version}</dt><dd>{citation.version_label}</dd></div> : null}
      </dl>
      <p className="excerpt-label">{messages.originalSource}</p>
      <blockquote>{citation.excerpt}</blockquote>
      <p className="citation-links">
        <a href={citation.canonical_url} target="_blank" rel="noreferrer noopener">{messages.openSource} {citation.source_title}</a>
        {citation.source_revision_url ? <a href={citation.source_revision_url} target="_blank" rel="noreferrer noopener">{messages.openRevision}</a> : null}
      </p>
    </article>
  );
}
