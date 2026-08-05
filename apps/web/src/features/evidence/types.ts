import type { CitedClaim, CitedEvidence } from "@/features/cited-answer/types";

export type FeedbackLabel = "useful" | "not_useful";
export type FeedbackCategory =
  | "incorrect_citation"
  | "incorrect_answer"
  | "outdated"
  | "incomplete"
  | "other";

export type FeedbackInput = {
  label: FeedbackLabel;
  category: FeedbackCategory | null;
  comment?: string | null;
};

export type EvidencePanelProps = {
  claims: CitedClaim[];
  citations: CitedEvidence[];
  limitations?: string[];
  answerStatus?: "complete" | "partial";
  onFeedback: (feedback: FeedbackInput) => void | Promise<void>;
};
