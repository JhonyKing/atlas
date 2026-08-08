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

export type AgentPlanStep = {
  tool_id: string;
  tool_version: string;
  arguments: Record<string, unknown>;
  dependencies: string[];
  expected_output: string;
};

export type AgentPlan = {
  run_id: string;
  request: string;
  locale: AgentLocale;
  steps: AgentPlanStep[];
  risk_summary: string[];
  budget: Record<string, number>;
  expires_at: string;
  plan_hash: string;
  required_approval_ids?: string[];
  approval_decision_keys?: Record<string, string>;
};

export type AgentRunEvent = {
  run_id: string;
  sequence: number;
  event_type: string;
  occurred_at: string;
  status: string;
  tool_id?: string | null;
  call_id?: string | null;
  evidence_ids: string[];
  artifact_ids: string[];
  error_category?: string | null;
};
