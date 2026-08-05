"use client";

import { useState } from "react";

import type { CitedClaim, CitedEvidence } from "@/features/cited-answer/types";

import type {
  EvidencePanelProps,
  FeedbackCategory,
  FeedbackInput,
  FeedbackLabel,
} from "./types";

const categoryOptions: Array<{ value: FeedbackCategory; label: string }> = [
  { value: "incorrect_citation", label: "Incorrect citation" },
  { value: "incorrect_answer", label: "Incorrect answer" },
  { value: "outdated", label: "Outdated" },
  { value: "incomplete", label: "Incomplete" },
  { value: "other", label: "Other" },
];

function formatDate(value: string | null | undefined): string {
  if (!value) return "Not provided";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "long",
    timeZone: "UTC",
  }).format(new Date(value));
}

function sourceTypeLabel(value: CitedEvidence["source_type"]): string {
  return value.replaceAll("_", " ");
}

export function EvidencePanel({ claims, citations, limitations = [], onFeedback }: EvidencePanelProps) {
  const [selectedLabel, setSelectedLabel] = useState<FeedbackLabel | null>(null);
  const [category, setCategory] = useState<FeedbackCategory | null>(null);
  const [comment, setComment] = useState("");

  const submitFeedback = (feedback: FeedbackInput) => {
    setSelectedLabel(feedback.label);
    void onFeedback(feedback);
  };

  const saveDetailedFeedback = () => {
    if (!selectedLabel) return;
    const feedback: FeedbackInput = {
      label: selectedLabel,
      category,
    };
    if (comment.trim()) feedback.comment = comment.trim();
    void onFeedback(feedback);
  };

  return (
    <section className="evidence-panel" aria-labelledby="evidence-title">
      <h2 id="evidence-title">Evidence and feedback</h2>
      <div className="claim-list">
        {claims.map((claim) => (
          <ClaimWithEvidence key={claim.id} claim={claim} citations={citations} />
        ))}
      </div>
      {limitations.length ? <p className="limitations">{limitations.join(" ")}</p> : null}

      <div className="feedback" aria-labelledby="feedback-title">
        <h3 id="feedback-title">Was this answer useful?</h3>
        <div className="feedback-actions">
          <button
            type="button"
            aria-pressed={selectedLabel === "useful"}
            onClick={() => submitFeedback({ label: "useful", category: null })}
          >
            Mark answer useful
          </button>
          <button
            type="button"
            aria-pressed={selectedLabel === "not_useful"}
            onClick={() => setSelectedLabel("not_useful")}
          >
            Mark answer not useful
          </button>
        </div>
        {selectedLabel === "not_useful" ? (
          <div className="feedback-details">
            <label htmlFor="feedback-category">Failure category (optional)</label>
            <select
              id="feedback-category"
              value={category ?? ""}
              onChange={(event) => setCategory((event.target.value || null) as FeedbackCategory | null)}
            >
              <option value="">Choose a category</option>
              {categoryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <label htmlFor="feedback-comment">Comment (optional)</label>
            <textarea
              id="feedback-comment"
              value={comment}
              maxLength={1000}
              onChange={(event) => setComment(event.target.value)}
              rows={3}
            />
            <button type="button" onClick={saveDetailedFeedback}>
              Save feedback
            </button>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function ClaimWithEvidence({
  claim,
  citations,
}: {
  claim: CitedClaim;
  citations: CitedEvidence[];
}) {
  const claimCitations = claim.citation_ids
    .map((citationId) => citations.find((citation) => citation.id === citationId))
    .filter((citation): citation is CitedEvidence => citation !== undefined);
  const claimLabel = claim.type === "inference" ? "Inference" : "Factual claim";

  return (
    <article className="claim-card">
      <p className="claim-kind">{claimLabel}</p>
      <p>{claim.text}</p>
      <ul className="citation-list">
        {claimCitations.map((citation) => (
          <li key={citation.id}>
            <CitationDetails citation={citation} />
          </li>
        ))}
      </ul>
    </article>
  );
}

function CitationDetails({ citation }: { citation: CitedEvidence }) {
  return (
    <article className="citation-card">
      <h3>{citation.source_title}</h3>
      <dl>
        <div><dt>Publisher</dt><dd>{citation.publisher}</dd></div>
        <div><dt>Source type</dt><dd>{sourceTypeLabel(citation.source_type)}</dd></div>
        <div><dt>Captured</dt><dd>{formatDate(citation.captured_at)}</dd></div>
        {citation.published_at ? <div><dt>Published</dt><dd>{formatDate(citation.published_at)}</dd></div> : null}
        {citation.version_label ? <div><dt>Version</dt><dd>{citation.version_label}</dd></div> : null}
      </dl>
      <blockquote>{citation.excerpt}</blockquote>
      <p className="citation-links">
        <a href={citation.canonical_url} target="_blank" rel="noreferrer noopener">
          Open {citation.source_title}
        </a>
        {citation.source_revision_url ? (
          <a href={citation.source_revision_url} target="_blank" rel="noreferrer noopener">
            Open source revision
          </a>
        ) : null}
      </p>
    </article>
  );
}
