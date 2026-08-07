export type AgentLocale = "en-US" | "es-MX";

export type AgentTool = {
  tool_id: string;
  version: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  scopes: string[];
  side_effect_level: "read" | "private_read" | "mutate" | "publish" | "delete";
  approval: "none" | "explicit_user" | "human_reviewer";
  timeout_ms: number;
  budget: Record<string, number>;
  availability: "enabled" | "disabled" | "provider_unavailable" | "quota_exhausted";
  name: string;
  description: string;
};

export type AgentToolCatalog = {
  version: string;
  locale: AgentLocale;
  tools: AgentTool[];
};
