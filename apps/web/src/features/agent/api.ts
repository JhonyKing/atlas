import { getPublicEnvironment } from "@/lib/env";

import type { AgentLocale, AgentToolCatalog } from "./types";

export async function getAgentToolCatalog(locale: AgentLocale): Promise<AgentToolCatalog> {
  const response = await fetch(
    `${getPublicEnvironment().apiOrigin}/v1/agent/tools?locale=${encodeURIComponent(locale)}`,
    { headers: { Accept: "application/json" }, cache: "no-store" },
  );
  if (!response.ok) throw new Error("Agent tool catalog unavailable");
  return (await response.json()) as AgentToolCatalog;
}
