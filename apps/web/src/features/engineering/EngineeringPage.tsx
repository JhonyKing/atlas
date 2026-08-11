"use client";

import { useLocale } from "@/i18n";

import { AgentWorkspace } from "../agent/AgentWorkspace";

const REPOSITORY = "https://github.com/JhonyKing/atlas/blob/main";

const capabilities = [
  { id: "rag", evidence: `${REPOSITORY}/docs/architecture/001-cited-answer.md` },
  { id: "agents", evidence: `${REPOSITORY}/docs/architecture/019-agent-tool-orchestration.md` },
  { id: "retrieval", evidence: `${REPOSITORY}/docs/architecture/007-retrieval-quality-multilingual.md` },
  { id: "verification", evidence: `${REPOSITORY}/docs/adr/0001-evidence-first-answer-boundary.md` },
  { id: "citations", evidence: `${REPOSITORY}/specs/001-cited-answer/contracts/answer-events.md` },
  { id: "structured", evidence: `${REPOSITORY}/docs/architecture/003-reports.md` },
  { id: "persistence", evidence: `${REPOSITORY}/docs/verification/021-supabase-migration.md` },
  { id: "evals", evidence: `${REPOSITORY}/docs/architecture/011-evaluation-quality-loop.md` },
  { id: "observability", evidence: `${REPOSITORY}/docs/verification/013-observability-langsmith.md` },
  { id: "architecture", evidence: `${REPOSITORY}/docs/portfolio/architecture-map.md` },
] as const;

export function EngineeringPage() {
  const { messages } = useLocale();
  const copy = messages.engineering;

  return (
    <article className="engineering-experience">
      <header className="engineering-hero">
        <p className="eyebrow">{copy.eyebrow}</p>
        <h1>{copy.title}</h1>
        <p className="lede">{copy.lede}</p>
      </header>

      <section className="engineering-flow" aria-labelledby="engineering-flow-title">
        <div className="section-heading">
          <p className="eyebrow">RAG + agents + verification</p>
          <h2 id="engineering-flow-title">{copy.flowTitle}</h2>
        </div>
        <ol>
          {copy.flow.map((step, index) => (
            <li key={step}>
              <span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>
              <strong>{step}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="engineering-capabilities" aria-labelledby="engineering-capabilities-title">
        <div className="section-heading">
          <h2 id="engineering-capabilities-title">{copy.capabilitiesTitle}</h2>
          <p>{copy.capabilitiesLede}</p>
        </div>
        <div className="engineering-capability-grid">
          {capabilities.map((capability) => {
            const content = copy.capabilityCopy[capability.id];
            return (
              <article key={capability.id} data-engineering-capability>
                <h3>{content.title}</h3>
                <p>{content.summary}</p>
                <a href={capability.evidence} target="_blank" rel="noreferrer">
                  {copy.evidence}<span aria-hidden="true"> ↗</span>
                </a>
              </article>
            );
          })}
        </div>
      </section>

      <details className="engineering-agent-details">
        <summary>{copy.advancedTitle}</summary>
        <p>{copy.advancedLede}</p>
        <AgentWorkspace />
      </details>
    </article>
  );
}
