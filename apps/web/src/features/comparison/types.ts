export type ComparisonTechnology = "langgraph" | "langchain" | "openai";
export type ComparisonCriterion =
  | "capability"
  | "tool_calling"
  | "context"
  | "latency"
  | "price"
  | "license"
  | "freshness"
  | "operational_risk";
export type ComparisonCellState = "supported" | "unsupported" | "partial" | "contradictory";
export type ComparisonStatus =
  | "accepted"
  | "retrieving"
  | "normalizing"
  | "verifying"
  | "completed"
  | "abstained"
  | "cancelled"
  | "failed";

export type ComparisonRequest = {
  technologies: ComparisonTechnology[];
  criteria: ComparisonCriterion[];
  product?: ComparisonTechnology;
  version?: string;
  date_from?: string;
  date_to?: string;
  source_type?: "documentation" | "changelog" | "release_note";
  language?: "en-US" | "es-MX";
};

export type ComparisonCell = {
  technology_id: ComparisonTechnology;
  criterion_id: ComparisonCriterion;
  state: ComparisonCellState;
  value?: string | null;
  unit?: string | null;
  period?: string | null;
  version?: string | null;
  explanation?: string | null;
  evidence_ids: string[];
};

export type ComparisonMatrix = {
  technology_ids: ComparisonTechnology[];
  criterion_ids: ComparisonCriterion[];
  cells: ComparisonCell[];
  summary?: string | null;
};

export type ComparisonRun = {
  run_id: string;
  status: ComparisonStatus;
  created_at: string;
  completed_at?: string | null;
  matrix?: ComparisonMatrix | null;
};

export type ComparisonEvent = {
  event: string;
  data: Record<string, unknown>;
};

export type ComparisonEventHandler = (event: ComparisonEvent) => void;
