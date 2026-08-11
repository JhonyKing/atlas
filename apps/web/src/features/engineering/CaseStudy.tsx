import evidenceLedger from "../../../../../docs/portfolio/evidence-ledger.json";
import kpis from "../../../../../docs/portfolio/kpis.json";

import type { Locale } from "@/i18n";

const REPOSITORY_BLOB = "https://github.com/JhonyKing/atlas/blob/main";

type MeasurementId =
  | "comparator-citation-precision-t043"
  | "comparator-terminal-latency-t042"
  | "cited-answer-offline-60"
  | "canonical-public-routes-21";

type Measurement = {
  result_id: string;
  kpi: string;
  value: number;
  display: string;
  scope: string;
  captured_at: string;
  artifact: string;
  limitation: string;
  status: string;
};

type DisplayMeasurement = Measurement & { result_id: MeasurementId };

const resultCopy: Record<MeasurementId, { en: string; es: string }> = {
  "comparator-citation-precision-t043": {
    en: "Owner-reviewed citation precision",
    es: "Precisión de citas revisada por el owner",
  },
  "comparator-terminal-latency-t042": {
    en: "Comparator terminal latency",
    es: "Latencia terminal del comparador",
  },
  "cited-answer-offline-60": {
    en: "Deterministic cited-answer cases",
    es: "Casos deterministas de respuestas citadas",
  },
  "canonical-public-routes-21": {
    en: "Anonymous canonical routes",
    es: "Rutas canónicas anónimas",
  },
};

const copy = {
  "en-US": {
    eyebrow: "Evidence-backed case study",
    title: "Measured results, not promises",
    lede: "These numbers come from retained evaluation or deployment artifacts. Each result states exactly what was measured and what remains outside its scope.",
    resultsLabel: "Measured project results",
    scope: "Measured scope",
    limitation: "Limit",
    evidence: "Inspect evidence",
    problemTitle: "The engineering problem",
    problem: "LLM answers can sound certain even when retrieval is weak, citations are mismatched, or a provider is unavailable.",
    approachTitle: "The ATLAS response",
    approach: "Separate retrieval, structured claims, citation verification, agent tools, persistence, evaluations, and observability into reviewable boundaries.",
    outcomeTitle: "The product outcome",
    outcome: "People receive inspectable evidence or an explicit limitation instead of an unsupported answer.",
    limitsTitle: "What these results do not prove",
    limits: [
      "They are not a platform-wide production SLO or continuous availability record.",
      "Deterministic fixture results do not replace live-provider quality and cost evaluation.",
      "The external five-second comprehension review and seven-day refresh window are still pending.",
    ],
  },
  "es-MX": {
    eyebrow: "Caso de estudio respaldado por evidencia",
    title: "Resultados medidos, no promesas",
    lede: "Estas cifras provienen de artefactos conservados de evaluación o despliegue. Cada resultado explica exactamente qué se midió y qué queda fuera de su alcance.",
    resultsLabel: "Resultados medidos del proyecto",
    scope: "Alcance medido",
    limitation: "Límite",
    evidence: "Inspeccionar evidencia",
    problemTitle: "El problema de ingeniería",
    problem: "Las respuestas de un LLM pueden sonar seguras aunque la recuperación sea débil, las citas no coincidan o un proveedor no esté disponible.",
    approachTitle: "La respuesta de ATLAS",
    approach: "Separar recuperación, afirmaciones estructuradas, verificación de citas, herramientas del agente, persistencia, evaluaciones y observabilidad en límites revisables.",
    outcomeTitle: "El resultado para el usuario",
    outcome: "Las personas reciben evidencia inspeccionable o una limitación explícita, en lugar de una respuesta sin respaldo.",
    limitsTitle: "Lo que estos resultados no demuestran",
    limits: [
      "No son un SLO general de producción ni un registro continuo de disponibilidad.",
      "Los resultados de fixtures deterministas no sustituyen evaluaciones en vivo de calidad y costo.",
      "La revisión externa de comprensión en cinco segundos y la ventana de actualización de siete días siguen pendientes.",
    ],
  },
} as const;

function isMeasurementId(value: string): value is MeasurementId {
  return value in resultCopy;
}

function measuredResults(): DisplayMeasurement[] {
  return kpis.measurements.filter(
    (measurement): measurement is DisplayMeasurement =>
      isMeasurementId(measurement.result_id) &&
      measurement.status === "measured" &&
      evidenceLedger.entries.some(
        (entry) => entry.artifact === measurement.artifact && entry.status !== "pending",
      ),
  );
}

const MEASURED_RESULTS = measuredResults();

export function CaseStudy({ locale }: { locale: Locale }) {
  const content = copy[locale];
  const spanish = locale === "es-MX";

  return (
    <section className="engineering-case-study" aria-labelledby="case-study-title">
      <div className="section-heading">
        <p className="eyebrow">{content.eyebrow}</p>
        <h2 id="case-study-title">{content.title}</h2>
        <p>{content.lede}</p>
      </div>

      <dl className="case-study-narrative">
        <div>
          <dt>{content.problemTitle}</dt>
          <dd>{content.problem}</dd>
        </div>
        <div>
          <dt>{content.approachTitle}</dt>
          <dd>{content.approach}</dd>
        </div>
        <div>
          <dt>{content.outcomeTitle}</dt>
          <dd>{content.outcome}</dd>
        </div>
      </dl>

      <ul className="case-study-results" aria-label={content.resultsLabel}>
        {MEASURED_RESULTS.map((result) => (
          <li key={result.result_id} data-case-study-metric>
            <p className="case-study-value">{result.display}</p>
            <h3>{resultCopy[result.result_id][spanish ? "es" : "en"]}</h3>
            <p><strong>{content.scope}:</strong> {result.scope}</p>
            <p className="case-study-limit"><strong>{content.limitation}:</strong> {result.limitation}</p>
            <a href={`${REPOSITORY_BLOB}/${result.artifact}`} target="_blank" rel="noreferrer">
              {content.evidence}<span aria-hidden="true"> ↗</span>
            </a>
          </li>
        ))}
      </ul>

      <aside className="case-study-limitations" aria-labelledby="case-study-limitations-title">
        <h3 id="case-study-limitations-title">{content.limitsTitle}</h3>
        <ul>
          {content.limits.map((limitation) => <li key={limitation}>{limitation}</li>)}
        </ul>
      </aside>
    </section>
  );
}
