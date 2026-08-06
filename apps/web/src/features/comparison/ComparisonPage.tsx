"use client";

import { FormEvent, useMemo, useRef, useState } from "react";

import { useLocale } from "@/i18n";

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
    <main>
      <section aria-labelledby="comparison-title">
        <p>{messages.comparison.eyebrow}</p>
        <h1 id="comparison-title">{messages.comparison.title}</h1>
        <form onSubmit={submit}>
          <fieldset>
            <legend>{messages.comparison.technologies}</legend>
            {technologies.map((technology) => (
              <label key={technology}>
                <input
                  type="checkbox"
                  checked={selectedTechnologies.includes(technology)}
                  onChange={() => toggleTechnology(technology)}
                />
                {labels[technology][spanish ? "es" : "en"]}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>{messages.comparison.criteria}</legend>
            {criteria.map((criterion) => (
              <label key={criterion}>
                <input
                  type="checkbox"
                  checked={selectedCriteria.includes(criterion)}
                  onChange={() => toggleCriterion(criterion)}
                />
                {labels[criterion][spanish ? "es" : "en"]}
              </label>
            ))}
          </fieldset>
          <button type="submit" disabled={active}>
            {messages.comparison.compare}
          </button>
          {active ? <button type="button" onClick={cancel}>{messages.comparison.cancel}</button> : null}
        </form>
        <p role="status">{status}</p>
        {error ? <p role="alert">{error}</p> : null}
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
