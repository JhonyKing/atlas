"use client";

import { useEffect, useState } from "react";

import { useLocale } from "@/i18n";

import { approveAgentTool, cancelAgentRun, createAgentPlan, getAgentEvents, getAgentToolCatalog, rejectAgentTool, resumeAgentRun, startAgentRun } from "./api";
import { ApprovalCard } from "./ApprovalCard";
import { RunTimeline } from "./RunTimeline";
import { ToolInputForm } from "./ToolInputForm";
import type { AgentPlan, AgentRunEvent, AgentTool, AgentToolCatalog } from "./types";

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
  const [plan, setPlan] = useState<AgentPlan | null>(null);
  const [events, setEvents] = useState<AgentRunEvent[]>([]);
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [working, setWorking] = useState(false);

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

  async function buildPlan(input: Record<string, unknown>) {
    if (!selectedTool) return;
    setWorking(true);
    setError(null);
    try {
      const request = selectedTool.tool_id === "cited_answer"
        ? String(input.question ?? "")
        : selectedTool.name;
      const next = await createAgentPlan(locale, request, selectedTool.tool_id, input);
      setPlan(next);
      setEvents([]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create a plan");
    } finally {
      setWorking(false);
    }
  }

  async function runPlan() {
    if (!plan) return;
    setWorking(true);
    setError(null);
    try {
      const approvalIds = plan.required_approval_ids ?? [];
      for (const approvalId of approvalIds) {
        const decisionKey = plan.approval_decision_keys?.[approvalId];
        if (!decisionKey) throw new Error("Approval token unavailable");
        await approveAgentTool(approvalId, decisionKey, plan.idempotency_key);
      }
      const result = await startAgentRun(
        plan.plan_hash,
        plan.idempotency_key,
        "anonymous",
        approvalIds,
      );
      setRunId(result.run_id);
      setRunStatus(result.status);
      setEvents(result.events);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to start the run");
    } finally {
      setWorking(false);
    }
  }

  async function rejectPlan() {
    if (!plan) return;
    const approvalId = plan.required_approval_ids?.[0];
    const decisionKey = approvalId ? plan.approval_decision_keys?.[approvalId] : undefined;
    if (!approvalId || !decisionKey) return;
    await rejectAgentTool(approvalId, decisionKey, plan.idempotency_key);
    setError(locale === "es-MX" ? "Plan rechazado." : "Plan rejected.");
  }

  async function cancelRun() {
    if (!runId) return;
    await cancelAgentRun(runId);
    setRunStatus("cancelled");
    setEvents(await getAgentEvents(runId));
  }

  async function resumeRun() {
    if (!runId) return;
    await resumeAgentRun(runId);
    setRunStatus("accepted");
    setEvents(await getAgentEvents(runId));
  }

  return (
    <section className="agent-workspace" aria-labelledby="agent-workspace-title">
      <p className="eyebrow">{copy.eyebrow}</p>
      <h2 id="agent-workspace-title">{copy.title}</h2>
      <p className="lede">{copy.lede}</p>
      {!catalogIsCurrent && !unavailable && <p aria-live="polite">{copy.loading}</p>}
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
            <div className="agent-tool-detail">
              <p className="agent-selected" aria-live="polite">
                {selectedTool.name} · {selectedTool.tool_id} v{selectedTool.version}
              </p>
              <ToolInputForm tool={selectedTool} onSubmit={(input) => void buildPlan(input)} disabled={working} />
            </div>
          )}
          {plan && <section className="agent-plan-preview" aria-label="Plan preview">
            <p><strong>{locale === "es-MX" ? "Plan listo" : "Plan ready"}</strong> · {plan.steps.map((step) => step.tool_id).join(" → ")}</p>
            <ApprovalCard plan={plan} onApprove={() => void runPlan()} onReject={() => void rejectPlan()} />
            {!plan.required_approval_ids?.length && <button type="button" onClick={() => void runPlan()} disabled={working}>Run plan</button>}
          </section>}
          {error && <p className="error" role="alert">{error}</p>}
          <RunTimeline events={events} runStatus={runStatus} onCancel={() => void cancelRun()} onResume={() => void resumeRun()} />
        </>
      )}
    </section>
  );
}
