import type { ComparisonCell, ComparisonCriterion, ComparisonMatrix as Matrix } from "./types";
import { useLocale } from "@/i18n";
import { EvidenceStatus, type EvidenceState } from "@/components/evidence/EvidenceStatus";

const criterionLabels: Record<ComparisonCriterion, { en: string; es: string }> = {
  capability: { en: "Capability", es: "Capacidad" },
  tool_calling: { en: "Tool calling", es: "Llamada de herramientas" },
  context: { en: "Context", es: "Contexto" },
  latency: { en: "Latency", es: "Latencia" },
  price: { en: "Price", es: "Precio" },
  license: { en: "License", es: "Licencia" },
  freshness: { en: "Freshness", es: "Actualización" },
  operational_risk: { en: "Operational risk", es: "Riesgo operativo" },
};

export function ComparisonMatrix({ matrix, spanish }: { matrix: Matrix; spanish: boolean }) {
  const { messages } = useLocale();
  const cellByKey = new Map(matrix.cells.map((cell) => [`${cell.technology_id}:${cell.criterion_id}`, cell]));
  return (
    <section className="comparison-results" aria-labelledby="comparison-results-title">
      <div className="comparison-results-heading">
        <div><p className="eyebrow">{spanish ? "Resultados auditables" : "Auditable results"}</p><h2 id="comparison-results-title">{spanish ? "Matriz de comparación" : "Comparison matrix"}</h2></div>
        {matrix.summary ? <p>{matrix.summary}</p> : null}
      </div>
      <div className="comparison-table-wrap" role="region" aria-label={spanish ? "Matriz de comparación" : "Comparison matrix"} tabIndex={0}>
      <table>
        <caption>{spanish ? "Resultados con evidencia" : "Evidence-backed results"}</caption>
        <thead>
          <tr>
            <th scope="col">{spanish ? "Tecnología" : "Technology"}</th>
            {matrix.criterion_ids.map((criterion) => (
              <th scope="col" key={criterion}>
                {messages.comparison.criterionLabels[criterion] ?? criterionLabels[criterion][spanish ? "es" : "en"]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.technology_ids.map((technology) => (
            <tr key={technology}>
              <th scope="row">{technology}</th>
              {matrix.criterion_ids.map((criterion) => {
                const cell = cellByKey.get(`${technology}:${criterion}`);
                return <td key={criterion}>{cell ? <CellView cell={cell} spanish={spanish} /> : <span className="comparison-empty-cell">—</span>}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </section>
  );
}

function CellView({ cell, spanish }: { cell: ComparisonCell; spanish: boolean }) {
  const { messages } = useLocale();
  const stateLabels = {
    supported: spanish ? "Compatible" : "Supported",
    unsupported: messages.comparison.unsupported,
    partial: messages.comparison.partial,
    contradictory: messages.comparison.contradictory,
  };
  return (
    <div className="comparison-cell" data-cell-state={cell.state}>
      <EvidenceStatus state={cell.state as EvidenceState} label={stateLabels[cell.state]} />
      {cell.value ? <span>{` ${cell.value}${cell.unit ? ` ${cell.unit}` : ""}`}</span> : null}
      {cell.explanation ? <p>{cell.explanation}</p> : null}
      {cell.evidence_ids.length > 0 ? (
        <details className="comparison-evidence-details">
          <summary>{spanish ? `${cell.evidence_ids.length} evidencia(s)` : `${cell.evidence_ids.length} evidence item(s)`}</summary>
          <ul>{cell.evidence_ids.map((evidenceId) => <li key={evidenceId}><code>{evidenceId}</code></li>)}</ul>
        </details>
      ) : null}
    </div>
  );
}
