"use client";

import { useLocale } from "@/i18n";

import { AgentWorkspace } from "../agent/AgentWorkspace";
import { CaseStudy } from "./CaseStudy";

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

const architectureCopy = {
  "en-US": {
    eyebrow: "System boundaries",
    title: "Architecture boundaries",
    lede: "The public interface stays simple while each technical responsibility remains explicit, testable, and replaceable.",
    caption: "Five reviewable layers connect a user request to evidence, durable state, and quality controls.",
    layers: [
      { title: "Product experience", detail: "Ask, Compare, Reports, News, and Sources provide one bilingual public entry point." },
      { title: "Agent orchestration", detail: "A typed tool registry, bounded plans, approvals, cancellation, and replay coordinate work." },
      { title: "Evidence pipeline", detail: "Hybrid retrieval, structured claims, and citation verification decide what ATLAS may support." },
      { title: "Durable state", detail: "Supabase Postgres, migrations, ownership, row-level security, and artifacts preserve governed state." },
      { title: "Quality and operations", detail: "Deterministic and live evals, LangSmith traces, CI gates, and safe telemetry expose regressions." },
    ],
  },
  "es-MX": {
    eyebrow: "Límites del sistema",
    title: "Límites de arquitectura",
    lede: "La interfaz pública permanece simple mientras cada responsabilidad técnica sigue explícita, comprobable y reemplazable.",
    caption: "Cinco capas revisables conectan una solicitud con evidencia, estado duradero y controles de calidad.",
    layers: [
      { title: "Experiencia de producto", detail: "Preguntas, comparaciones, reportes, noticias y fuentes ofrecen una entrada pública bilingüe." },
      { title: "Orquestación del agente", detail: "Un registro tipado de herramientas, planes acotados, aprobaciones, cancelación y replay coordinan el trabajo." },
      { title: "Pipeline de evidencia", detail: "Recuperación híbrida, afirmaciones estructuradas y verificación de citas deciden qué puede respaldar ATLAS." },
      { title: "Estado duradero", detail: "Supabase Postgres, migraciones, propiedad, seguridad por fila y artefactos conservan estado gobernado." },
      { title: "Calidad y operaciones", detail: "Evals deterministas y en vivo, trazas de LangSmith, CI y telemetría segura exponen regresiones." },
    ],
  },
} as const;

export function EngineeringPage() {
  const { locale, messages } = useLocale();
  const copy = messages.engineering;
  const architecture = architectureCopy[locale];

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

      <figure className="engineering-architecture" aria-labelledby="engineering-architecture-title">
        <div className="section-heading">
          <p className="eyebrow">{architecture.eyebrow}</p>
          <h2 id="engineering-architecture-title">{architecture.title}</h2>
          <p>{architecture.lede}</p>
        </div>
        <ol>
          {architecture.layers.map((layer, index) => (
            <li key={layer.title} data-architecture-layer>
              <span aria-hidden="true">{String(index + 1).padStart(2, "0")}</span>
              <div>
                <h3>{layer.title}</h3>
                <p>{layer.detail}</p>
              </div>
            </li>
          ))}
        </ol>
        <figcaption>{architecture.caption}</figcaption>
      </figure>

      <CaseStudy locale={locale} />

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
