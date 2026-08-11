"use client";

import { FormEvent, useMemo, useRef, useState } from "react";

import { useLocale } from "@/i18n";

import { Button } from "@/components/forms";

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
    } catch {
      if (nextController.signal.aborted) return;
      setError(spanish ? "No pudimos completar la comparación. Inténtalo de nuevo más tarde." : "We couldn't complete the comparison. Try again later.");
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

  function applyDecisionPreset(preset: "framework" | "provider" | "production") {
    if (preset === "framework") {
      setSelectedTechnologies(["langgraph", "langchain"]);
      setSelectedCriteria(["capability", "tool_calling", "operational_risk"]);
    } else if (preset === "provider") {
      setSelectedTechnologies(["openai", "anthropic"]);
      setSelectedCriteria(["tool_calling", "context", "price"]);
    } else {
      setSelectedTechnologies(["openai", "anthropic", "gemini"]);
      setSelectedCriteria(["latency", "price", "freshness", "operational_risk"]);
    }
    setError(null);
    setMatrix(null);
    setStatus(messages.comparison.ready);
  }

  const copy = spanish
    ? {
        selected: "Seleccionada",
        available: "Disponible",
        technologyHelp: "Elige entre 2 y 4 tecnologías.",
        criteriaHelp: "Elige al menos un criterio para comparar.",
        selectedSummary: `${selectedTechnologies.length} tecnologías · ${selectedCriteria.length} criterios`,
        lede: "Compara opciones para una decisión de IA. ATLAS muestra qué respaldan las fuentes y dónde todavía falta evidencia.",
        commonTitle: "Empieza con una decisión común",
        presets: [
          { id: "framework" as const, title: "Elegir un framework de agentes", description: "LangGraph vs. LangChain para flujos con herramientas y revisión humana." },
          { id: "provider" as const, title: "Elegir un proveedor de modelos", description: "OpenAI vs. Anthropic en herramientas, contexto y precio." },
          { id: "production" as const, title: "Planear para producción", description: "Compara latencia, precio, actualización y riesgo operativo." },
        ],
      }
    : {
        selected: "Selected",
        available: "Available",
        technologyHelp: "Choose between 2 and 4 technologies.",
        criteriaHelp: "Choose at least one criterion to compare.",
        selectedSummary: `${selectedTechnologies.length} technologies · ${selectedCriteria.length} criteria`,
        lede: "Compare options for a real AI decision. ATLAS shows what the sources support—and where evidence is still missing.",
        commonTitle: "Start with a common decision",
        presets: [
          { id: "framework" as const, title: "Choose an agent framework", description: "LangGraph vs. LangChain for tools and human review." },
          { id: "provider" as const, title: "Choose a model provider", description: "OpenAI vs. Anthropic for tools, context, and price." },
          { id: "production" as const, title: "Plan for production", description: "Compare latency, price, freshness, and operational risk." },
        ],
      };

  return (
    <main className="comparison-page">
      <section className="comparison-experience" aria-labelledby="comparison-title">
        <p className="eyebrow">{messages.comparison.eyebrow}</p>
        <h1 id="comparison-title">{messages.comparison.title}</h1>
        <p className="lede">{copy.lede}</p>
        <section className="comparison-decision-presets" aria-labelledby="comparison-decisions-title">
          <h2 id="comparison-decisions-title">{copy.commonTitle}</h2>
          <div className="comparison-preset-list">
            {copy.presets.map((preset) => (
              <button key={preset.id} type="button" onClick={() => applyDecisionPreset(preset.id)}>
                <strong>{preset.title}</strong>
                <span>{preset.description}</span>
              </button>
            ))}
          </div>
        </section>
        <form onSubmit={submit}>
          <div className="comparison-control-grid">
          <fieldset className="comparison-control-group" aria-describedby="comparison-technologies-help" aria-invalid={selectedTechnologies.length < 2 || selectedTechnologies.length > 4}>
            <legend>{messages.comparison.technologies}</legend>
            <p id="comparison-technologies-help" className="comparison-control-help">{copy.technologyHelp}</p>
            <div className="comparison-chip-list">
              {technologies.map((technology) => {
                const selected = selectedTechnologies.includes(technology);
                const limitReached = !selected && selectedTechnologies.length >= 4;
                return <label className={`comparison-chip${selected ? " is-selected" : ""}${limitReached ? " is-disabled" : ""}`} key={technology}>
                  <input type="checkbox" checked={selected} disabled={limitReached} onChange={() => toggleTechnology(technology)} />
                  <span className="comparison-chip-label">{labels[technology][spanish ? "es" : "en"]}</span>
                  <span className="comparison-chip-state">{selected ? copy.selected : copy.available}</span>
                </label>;
              })}
            </div>
          </fieldset>
          <fieldset className="comparison-control-group" aria-describedby="comparison-criteria-help" aria-invalid={selectedCriteria.length < 1}>
            <legend>{messages.comparison.criteria}</legend>
            <p id="comparison-criteria-help" className="comparison-control-help">{copy.criteriaHelp}</p>
            <div className="comparison-chip-list">
              {criteria.map((criterion) => {
                const selected = selectedCriteria.includes(criterion);
                return <label className={`comparison-chip${selected ? " is-selected" : ""}`} key={criterion}>
                  <input type="checkbox" checked={selected} onChange={() => toggleCriterion(criterion)} />
                  <span className="comparison-chip-label">{labels[criterion][spanish ? "es" : "en"]}</span>
                  <span className="comparison-chip-state">{selected ? copy.selected : copy.available}</span>
                </label>;
              })}
            </div>
          </fieldset>
          </div>
          <div className="comparison-selection" aria-live="polite">
            <strong>{copy.selectedSummary}</strong>
            <span>{spanish ? "Puedes cambiar la selección antes de iniciar." : "You can change the selection before starting."}</span>
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
