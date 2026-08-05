export type CollectionSlug = "langgraph" | "langchain" | "openai";

export type AskQuestionInput = {
  question: string;
  product?: CollectionSlug;
  version?: string;
  date_from?: string;
  date_to?: string;
};

export type CitedClaim = {
  id: string;
  ordinal: number;
  text: string;
  type: "factual" | "inference";
  citation_ids: string[];
};

export type CitedEvidence = {
  id: string;
  evidence_id: string;
  source_title: string;
  publisher: string;
  canonical_url: string;
  source_revision_url?: string | null;
  anchor?: string | null;
  excerpt: string;
  captured_at: string;
  published_at?: string | null;
  version_label?: string | null;
  source_type: "documentation" | "changelog" | "release_note";
};

export type AnswerEvent = {
  event: string;
  data: Record<string, unknown>;
};

export type AnswerEventHandler = (event: AnswerEvent) => void;
