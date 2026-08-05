import { getPublicEnvironment } from "@/lib/env";

import type { FeedbackInput } from "./types";

export async function putAnswerFeedback(
  runId: string,
  feedback: FeedbackInput,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/answers/${runId}/feedback`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(feedback),
    signal,
  });
  if (response.ok) return;

  let detail = "ATLAS could not save this feedback.";
  try {
    const payload = (await response.json()) as { detail?: string };
    detail = payload.detail ?? detail;
  } catch {
    // Keep a controlled fallback when a gateway did not return JSON.
  }
  throw new Error(detail);
}
