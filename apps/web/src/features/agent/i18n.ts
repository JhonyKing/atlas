import type { AgentLocale } from "./types";

const inputLabels: Record<AgentLocale, Record<string, string>> = {
  "en-US": {
    question: "Technical question",
    technologies: "Technologies",
    criteria: "Criteria",
    source_run_id: "Source run ID",
    resource_id: "Resource ID",
  },
  "es-MX": {
    question: "Pregunta técnica",
    technologies: "Tecnologías",
    criteria: "Criterios",
    source_run_id: "ID de ejecución fuente",
    resource_id: "ID del recurso",
  },
};

export function agentInputLabel(locale: AgentLocale, name: string): string {
  return inputLabels[locale][name] ?? name.replaceAll("_", " ");
}
