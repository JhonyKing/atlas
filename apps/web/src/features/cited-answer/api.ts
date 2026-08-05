import { getPublicEnvironment } from "@/lib/env";

import type { AnswerEvent, AnswerEventHandler, AskQuestionInput } from "./types";

export class AtlasApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "AtlasApiError";
    this.status = status;
    this.detail = detail;
  }
}

function idempotencyKey(): string {
  return typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export async function streamCitedAnswer(
  input: AskQuestionInput,
  onEvent: AnswerEventHandler,
  signal?: AbortSignal,
  onRunId?: (runId: string) => void,
): Promise<string> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/answers`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "Idempotency-Key": idempotencyKey(),
    },
    body: JSON.stringify(input),
    signal,
  });
  if (!response.ok) {
    let detail = "ATLAS could not process the question.";
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // Keep the controlled fallback detail when a gateway did not return JSON.
    }
    throw new AtlasApiError(response.status, detail);
  }
  if (!response.body) throw new AtlasApiError(502, "ATLAS returned no event stream.");

  const runId = response.headers.get("X-Atlas-Run-ID");
  if (!runId) throw new AtlasApiError(502, "ATLAS returned no run identifier.");
  onRunId?.(runId);
  await consumeEvents(response.body, onEvent);
  return runId;
}

export async function cancelAnswer(runId: string, signal?: AbortSignal): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/answers/${runId}`, {
    method: "DELETE",
    signal,
  });
  if (!response.ok && response.status !== 404) {
    throw new AtlasApiError(response.status, "ATLAS could not cancel this request.");
  }
}

async function consumeEvents(
  stream: ReadableStream<Uint8Array>,
  onEvent: AnswerEventHandler,
): Promise<void> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value, { stream: !done });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      const parsed = parseFrame(frame);
      if (parsed) onEvent(parsed);
    }
    if (done) break;
  }
  const finalFrame = parseFrame(buffer);
  if (finalFrame) onEvent(finalFrame);
}

function parseFrame(frame: string): AnswerEvent | null {
  let event = "message";
  let data = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice("event:".length).trim();
    if (line.startsWith("data:")) data += line.slice("data:".length).trim();
  }
  if (!data) return null;
  try {
    const parsed: unknown = JSON.parse(data);
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) return null;
    return { event, data: parsed as Record<string, unknown> };
  } catch {
    return null;
  }
}
