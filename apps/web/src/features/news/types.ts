export type NewsCandidate = {
  title: string;
  summary: string;
  publisher: string;
  canonical_url: string;
  published_at: string;
  captured_at: string;
  authority_score: number;
  topic_score: number;
  corroboration_count: number;
  content_sha256: string;
};

export type DailyNewsPayload = {
  status: "ready" | "unavailable";
  day: string;
  timezone: "UTC";
  candidate: NewsCandidate | null;
  candidate_count: number;
  score: number | null;
  reason_code: "none" | "not_configured" | "no_evidence" | "insufficient_signal";
};

