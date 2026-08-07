"use client";

import { FormEvent, useMemo, useRef, useState } from "react";

import { useLocale } from "@/i18n";

import { Button, Checkbox } from "@/components/forms";

import { ComparisonMatrix } from "./ComparisonMatrix";
import { streamComparison } from "./api";
import type {
  ComparisonCriterion,
  ComparisonEvent,
  ComparisonMatrix as Matrix,
  ComparisonRequest,
  ComparisonTechnology,
} from "./types";

const technologies: ComparisonTechnology[] = [
  "langgraph",
  "langchain",
  "openai",
  "anthropic",
  "gemini",
];
const criteria: ComparisonCriterion[] = [
  "capability",
  "tool_calling",
  "context",
  "latency",
  "price",
  "license",
  "freshness",
  "operational_risk",
];

const labels: Record<ComparisonTechnology | ComparisonCriterion, { en: string; es: string }> = {
  langgraph: { en: "LangGraph", es: "LangGraph" },
  langchain: { en: "LangChain", es: "LangChain" },
  openai: { en: "OpenAI", es: "OpenAI" },
  anthropic: { en: "Anthropic Claude", es: "Anthropic Claude" },
  gemini: { en: "Google Gemini", es: "Google Gemini" },
  capability: { en: "Capability", es: "Capacidad" },
  tool_calling: { en: "Tool calling", es: "Llamada de herramientas" },
  context: { en: "Context", es: "Contexto" },
  latency: { en: "Latency", es: "Latencia" },
  price: { en: "Price", es: "Precio" },
  license: { en: "License", es: "Licencia" },
  freshness: { en: "Freshness", es: "Actualización" },
  operational_risk: { en: "Operational risk", es: "Riesgo operativo" },
};

export function ComparisonPage() {
  const { locale, messages } = useLocale();
  const spanish = locale === "es-MX";
  const [selectedTechnologies, setSelectedTechnologies] = useState<ComparisonTechnology[]>([
    "langgraph",
    "openai",
  ]);
  const [selectedCriteria, setSelectedCriteria] = useState<ComparisonCriterion[]>(["capability", "price"]);
  const [status, setStatus] = useState(messages.comparison.ready);
  const [error, setError] = useState<string | null>(null);
  const [matrix, setMatrix] = useState<Matrix | null>(null);
  const [active, setActive] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const language = useMemo(() => (spanish ? "es-MX" : "en-US"), [spanish]);

  function toggleTechnology(technology: ComparisonTechnology) {
    setSelectedTechnologies((current) =>
      current.includes(technology)
        ? current.filter((item) => item !== technology)
        : [...current, technology],
    );
  }

  function toggleCriterion(criterion: ComparisonCriterion) {
    setSelectedCriteria((current) =>
      current.includes(criterion) ? current.filter((item) => item !== criterion) : [...current, criterion],
    );
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedTechnologies.length < 2 || selectedTechnologies.length > 4) {
      setError(spanish ? "Selecciona entre 2 y 4 tecnologías." : "Select between 2 and 4 technologies.");
      return;
    }
    if (selectedCriteria.length < 1) {
      setError(spanish ? "Selecciona al menos un criterio." : "Select at least one criterion.");
      return;
    }
    setError(null);
    setMatrix(null);
    setActive(true);
    setStatus(messages.comparison.accepted);
    const nextController = new AbortController();
    controller.current = nextController;
    const input: ComparisonRequest = {
      technologies: selectedTechnologies,
      criteria: selectedCriteria,
      language,
    };
    try {
      await streamComparison(input, handleEvent, nextController.signal);
    } catch (cause) {
      if (nextController.signal.aborted) return;
      setError(cause instanceof Error ? cause.message : spanish ? "No se pudo comparar." : "Comparison failed.");
      setStatus(spanish ? "La comparación terminó sin resultado verificado." : "Comparison ended without a verified result.");
    } finally {
      setActive(false);
      controller.current = null;
    }
  }

  function handleEvent(event: ComparisonEvent) {
    if (event.event === "comparison.completed" && isMatrix(event.data.matrix)) {
      setMatrix(event.data.matrix);
      setStatus(messages.comparison.verified);
    } else if (event.event.endsWith("failed")) {
      setStatus(spanish ? "La comparación falló." : "Comparison failed.");
    } else if (event.event.endsWith("cancelled")) {
      setStatus(spanish ? "Comparación cancelada." : "Comparison cancelled.");
    }
  }

  function cancel() {
    controller.current?.abort();
    setActive(false);
    setStatus(spanish ? "Comparación cancelada." : "Comparison cancelled.");
  }

  return (
    <main className="comparison-page">
      <section className="comparison-experience" aria-labelledby="comparison-title">
        <p className="eyebrow">{messages.comparison.eyebrow}</p>
        <h1 id="comparison-title">{messages.comparison.title}</h1>
        <p className="lede">{spanish ? "Selecciona un conjunto acotado de tecnologías y criterios; ATLAS conserva los estados sin evidencia." : "Select a bounded set of technologies and criteria; ATLAS preserves unsupported states."}</p>
        <form onSubmit={submit}>
          <div className="comparison-control-grid">
          <fieldset className="comparison-control-group">
            <legend>{messages.comparison.technologies}</legend>
            <div className="comparison-chip-list">
              {technologies.map((technology) => <Checkbox key={technology} checked={selectedTechnologies.includes(technology)} onChange={() => toggleTechnology(technology)} label={labels[technology][spanish ? "es" : "en"]} />)}
            </div>
          </fieldset>
          <fieldset className="comparison-control-group">
            <legend>{messages.comparison.criteria}</legend>
            <div className="comparison-chip-list">
              {criteria.map((criterion) => <Checkbox key={criterion} checked={selectedCriteria.includes(criterion)} onChange={() => toggleCriterion(criterion)} label={labels[criterion][spanish ? "es" : "en"]} />)}
            </div>
          </fieldset>
          </div>
          <div className="comparison-selection" aria-live="polite">
            <span>{selectedTechnologies.length} {spanish ? "tecnologías" : "technologies"} · {selectedCriteria.length} {spanish ? "criterios" : "criteria"}</span>
          </div>
          <div className="actions">
            <Button type="submit" disabled={active} loading={active}>{messages.comparison.compare}</Button>
            {active ? <Button type="button" variant="secondary" onClick={cancel}>{messages.comparison.cancel}</Button> : null}
          </div>
        </form>
        <p className="progress" role="status" aria-live="polite">{status}</p>
        {error ? <p className="error" role="alert">{error}</p> : null}
      </section>
      {matrix ? <ComparisonMatrix matrix={matrix} spanish={spanish} /> : null}
    </main>
  );
}

function isMatrix(value: unknown): value is Matrix {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Partial<Matrix>;
  return Array.isArray(candidate.technology_ids) && Array.isArray(candidate.criterion_ids) && Array.isArray(candidate.cells);
}
