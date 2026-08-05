import { getPublicEnvironment } from "@/lib/env";

import type {
  ComparisonEvent,
  ComparisonEventHandler,
  ComparisonRequest,
  ComparisonRun,
} from "./types";

export class ComparisonApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ComparisonApiError";
    this.status = status;
  }
}

function idempotencyKey(): string {
  return typeof crypto.randomUUID === "function"
    ? crypto.randomUUID()
    : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export async function streamComparison(
  input: ComparisonRequest,
  onEvent: ComparisonEventHandler,
  signal?: AbortSignal,
  onRunId?: (runId: string) => void,
): Promise<string> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/comparisons`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "Idempotency-Key": idempotencyKey(),
    },
    body: JSON.stringify(input),
    signal,
  });
  if (!response.ok) throw await parseError(response, "ATLAS could not start the comparison.");
  const runId = response.headers.get("X-Atlas-Run-ID");
  if (!runId) throw new ComparisonApiError(502, "ATLAS returned no comparison run identifier.");
  onRunId?.(runId);
  if (!response.body) throw new ComparisonApiError(502, "ATLAS returned no event stream.");
  await consumeEvents(response.body, onEvent);
  return runId;
}

export async function getComparison(runId: string, signal?: AbortSignal): Promise<ComparisonRun> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/comparisons/${runId}`, {
    signal,
  });
  if (!response.ok) throw await parseError(response, "ATLAS could not read the comparison.");
  return (await response.json()) as ComparisonRun;
}

export async function cancelComparison(runId: string, signal?: AbortSignal): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/comparisons/${runId}`, {
    method: "DELETE",
    signal,
  });
  if (!response.ok && response.status !== 404) {
    throw await parseError(response, "ATLAS could not cancel the comparison.");
  }
}

async function parseError(response: Response, fallback: string): Promise<ComparisonApiError> {
  let detail = fallback;
  try {
    const payload = (await response.json()) as { detail?: string };
    detail = payload.detail ?? fallback;
  } catch {
    // Keep the controlled fallback when the gateway did not return JSON.
  }
  return new ComparisonApiError(response.status, detail);
}

async function consumeEvents(
  stream: ReadableStream<Uint8Array>,
  onEvent: ComparisonEventHandler,
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

function parseFrame(frame: string): ComparisonEvent | null {
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
