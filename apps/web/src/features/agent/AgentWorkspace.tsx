"use client";

import { useEffect, useState } from "react";

import { useLocale } from "@/i18n";

import { getAgentToolCatalog } from "./api";
import type { AgentTool, AgentToolCatalog } from "./types";

const labels = {
  "en-US": {
    eyebrow: "Agent workspace",
    title: "Choose what ATLAS should do",
    lede: "Each capability is a typed tool with explicit permissions, budgets, and approval rules.",
    loading: "Loading the tool catalog...",
    unavailable: "The agent tool catalog is unavailable.",
    read: "Read-only",
    private_read: "Private data",
    mutate: "Changes data",
    publish: "Publishes",
    delete: "Deletes data",
    approval: "Approval required",
    noApproval: "No approval required",
    disabled: "Unavailable",
  },
  "es-MX": {
    eyebrow: "Espacio del agente",
    title: "Elige qué debe hacer ATLAS",
    lede: "Cada capacidad es una herramienta tipada con permisos, presupuestos y reglas de aprobación explícitos.",
    loading: "Cargando el catálogo de herramientas...",
    unavailable: "El catálogo de herramientas del agente no está disponible.",
    read: "Solo lectura",
    private_read: "Datos privados",
    mutate: "Cambia datos",
    publish: "Publica",
    delete: "Elimina datos",
    approval: "Requiere aprobación",
    noApproval: "No requiere aprobación",
    disabled: "No disponible",
  },
} as const;

export function AgentWorkspace() {
  const { locale } = useLocale();
  const copy = labels[locale];
  const [catalog, setCatalog] = useState<AgentToolCatalog | null>(null);
  const [unavailable, setUnavailable] = useState(false);
  const [selectedTool, setSelectedTool] = useState<AgentTool | null>(null);

  useEffect(() => {
    let active = true;
    void getAgentToolCatalog(locale)
      .then((next) => {
        if (active) {
          setCatalog(next);
          setUnavailable(false);
        }
      })
      .catch(() => { if (active) setUnavailable(true); });
    return () => { active = false; };
  }, [locale]);

  const catalogIsCurrent = catalog?.locale === locale;

  return (
    <section className="agent-workspace" aria-labelledby="agent-workspace-title">
      <p className="eyebrow">{copy.eyebrow}</p>
      <h2 id="agent-workspace-title">{copy.title}</h2>
      <p className="lede">{copy.lede}</p>
      {(!catalogIsCurrent && !unavailable) && <p aria-live="polite">{copy.loading}</p>}
      {unavailable && catalogIsCurrent !== false && <p className="error" aria-live="polite">{copy.unavailable}</p>}
      {catalog && catalogIsCurrent && (
        <>
          <div className="agent-tool-grid" role="list" aria-label={copy.title}>
            {catalog.tools.map((tool) => (
              <button
                className={`agent-tool-card${selectedTool?.tool_id === tool.tool_id ? " selected" : ""}`}
                key={`${tool.tool_id}-${tool.version}`}
                type="button"
                onClick={() => setSelectedTool(tool)}
                role="listitem"
                disabled={tool.availability !== "enabled"}
              >
                <span className="agent-tool-name">{tool.name}</span>
                <span className="agent-tool-description">{tool.description}</span>
                <span className="agent-tool-meta">
                  {copy[tool.side_effect_level]} · {tool.approval === "none" ? copy.noApproval : copy.approval}
                </span>
                {tool.availability !== "enabled" && <span className="error">{copy.disabled}</span>}
              </button>
            ))}
          </div>
          {selectedTool && (
            <p className="agent-selected" aria-live="polite">
              {selectedTool.name} · {selectedTool.tool_id} v{selectedTool.version}
            </p>
          )}
        </>
      )}
    </section>
  );
}
