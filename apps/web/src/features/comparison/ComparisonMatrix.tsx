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
  const stateLabels = {
    supported: spanish ? "Compatible" : "Supported",
    partial: messages.comparison.partial,
    unsupported: messages.comparison.unsupported,
    not_applicable: spanish ? "No aplica" : "Not applicable",
    contradictory: messages.comparison.contradictory,
  };
  return (
    <section className="comparison-results" aria-labelledby="comparison-results-title">
      <div className="comparison-results-heading">
        <div><p className="eyebrow">{spanish ? "Resultados auditables" : "Auditable results"}</p><h2 id="comparison-results-title">{spanish ? "Matriz de comparación" : "Comparison matrix"}</h2></div>
        {matrix.summary ? <p>{matrix.summary}</p> : null}
      </div>
      <ul className="comparison-state-legend" aria-label={spanish ? "Estados de evidencia" : "Evidence states"}>
        {(Object.keys(stateLabels) as Array<keyof typeof stateLabels>).map((state) => <li key={state}><EvidenceStatus state={state} label={stateLabels[state]} /></li>)}
      </ul>
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
                return <td key={criterion} data-cell-coordinate={`${technology}:${criterion}`}>{cell ? <CellView cell={cell} spanish={spanish} /> : <span className="comparison-empty-cell">—</span>}</td>;
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
    not_applicable: spanish ? "No aplica" : "Not applicable",
    partial: messages.comparison.partial,
    contradictory: messages.comparison.contradictory,
  };
  return (
    <div className="comparison-cell" data-cell-state={cell.state} role="group" aria-label={`${cell.technology_id} · ${cell.criterion_id}`}>
      <EvidenceStatus state={cell.state as EvidenceState} label={stateLabels[cell.state]} />
      {cell.value ? <span className="comparison-cell-value">{`${cell.value}${cell.unit ? ` ${cell.unit}` : ""}`}</span> : <p className="comparison-cell-note">{cell.state === "not_applicable" ? (spanish ? "Este criterio no aplica a este producto." : "This criterion does not apply to this product.") : cell.evidence_ids.length > 0 ? (spanish ? "Hay evidencia, pero los valores no son directamente comparables." : "Evidence exists, but the values are not directly comparable.") : messages.comparison.noEvidence}</p>}
      {cell.explanation ? <p>{cell.explanation}</p> : null}
      {cell.evidence_ids.length > 0 ? (
        <details className="comparison-evidence-details">
          <summary>{spanish ? `${cell.evidence_ids.length} evidencia(s)` : `${cell.evidence_ids.length} evidence item(s)`}</summary>
          <ul>{cell.evidence?.length ? cell.evidence.map((evidence) => <li key={evidence.id} className="comparison-evidence-item"><a href={evidence.canonical_url} target="_blank" rel="noreferrer">{evidence.source_title}</a><span>{evidence.publisher}{evidence.version_label ? ` · ${evidence.version_label}` : ""}</span><q>{evidence.excerpt}</q><small>{new Date(evidence.captured_at).toLocaleDateString(spanish ? "es-MX" : "en-US")}</small></li>) : cell.evidence_ids.map((evidenceId) => <li key={evidenceId}><code>{evidenceId}</code></li>)}</ul>
        </details>
      ) : null}
    </div>
  );
}
