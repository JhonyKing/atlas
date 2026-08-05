export type CorpusCollectionSlug = "langgraph" | "langchain" | "openai";
export type CorpusCollectionState = "ready" | "stale" | "refreshing" | "unavailable";
export type CorpusSourceType = "documentation" | "changelog" | "release_note";

export type CorpusCollectionStatus = {
  slug: CorpusCollectionSlug;
  name: string;
  publisher: string;
  source_types: CorpusSourceType[];
  status: CorpusCollectionState;
  last_success_at?: string | null;
  last_attempt_at?: string | null;
  canonical_root: string;
  source_count?: number;
  page_count?: number;
  chunk_count?: number;
  byte_count?: number;
};

export type CorpusStatusPayload = {
  snapshot_id: string;
  generated_at: string;
  collections: CorpusCollectionStatus[];
};
