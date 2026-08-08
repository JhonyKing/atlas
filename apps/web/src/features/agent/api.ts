import { getPublicEnvironment } from "@/lib/env";

import type { AgentLocale, AgentPlan, AgentRunEvent, AgentToolCatalog } from "./types";

export async function getAgentToolCatalog(locale: AgentLocale): Promise<AgentToolCatalog> {
  const response = await fetch(
    `${getPublicEnvironment().apiOrigin}/v1/agent/tools?locale=${encodeURIComponent(locale)}`,
    { headers: { Accept: "application/json" }, cache: "no-store" },
  );
  if (!response.ok) throw new Error("Agent tool catalog unavailable");
  return (await response.json()) as AgentToolCatalog;
}

export async function createAgentPlan(
  locale: AgentLocale,
  request: string,
  selectedTool: string | null,
  input: Record<string, unknown>,
): Promise<AgentPlan> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/plans`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ request, locale, selected_tool: selectedTool, input }),
  });
  if (!response.ok) throw new Error((await response.text()) || "Agent plan unavailable");
  return (await response.json()) as AgentPlan;
}

export async function approveAgentTool(
  approvalId: string,
  decisionKey: string,
  actorId = "anonymous",
): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/approvals/${approvalId}/decision`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ actor_id: actorId, decision: "approved", decision_key: decisionKey }),
  });
  if (!response.ok) throw new Error((await response.text()) || "Agent approval unavailable");
}

export async function rejectAgentTool(
  approvalId: string,
  decisionKey: string,
  actorId = "anonymous",
): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/approvals/${approvalId}/decision`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ actor_id: actorId, decision: "rejected", decision_key: decisionKey }),
  });
  if (!response.ok) throw new Error((await response.text()) || "Agent rejection unavailable");
}

export async function startAgentRun(
  planHash: string,
  actorId = "anonymous",
  approvalIds: string[] = [],
): Promise<{ run_id: string; status: string; events: AgentRunEvent[] }> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/runs`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ plan_hash: planHash, actor_id: actorId, approval_ids: approvalIds }),
  });
  if (!response.ok) throw new Error((await response.text()) || "Agent run unavailable");
  return (await response.json()) as { run_id: string; status: string; events: AgentRunEvent[] };
}

export async function getAgentEvents(runId: string, afterSequence = 0): Promise<AgentRunEvent[]> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/runs/${runId}/events?after_sequence=${afterSequence}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Agent events unavailable");
  const body = (await response.json()) as { events: AgentRunEvent[] };
  return body.events;
}

export async function cancelAgentRun(runId: string): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/runs/${runId}/cancel`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error((await response.text()) || "Agent cancellation unavailable");
}

export async function resumeAgentRun(runId: string): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/agent/runs/${runId}/resume`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error((await response.text()) || "Agent resume unavailable");
}
