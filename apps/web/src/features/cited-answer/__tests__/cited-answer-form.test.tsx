import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CitedAnswerForm } from "../CitedAnswerForm";

function sseResponse(frames: string[]): Response {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const frame of frames) controller.enqueue(encoder.encode(frame));
      controller.close();
    },
  });
  return new Response(body, {
    status: 200,
    headers: { "Content-Type": "text/event-stream", "X-Atlas-Run-ID": "run-123" },
  });
}

describe("CitedAnswerForm", () => {
  it("preserves invalid entered text and explains the correction", () => {
    render(<CitedAnswerForm />);
    const input = screen.getByLabelText("Technical question");
    fireEvent.change(input, { target: { value: "???" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask ATLAS" }));

    expect(input).toHaveValue("???");
    expect(screen.getByRole("alert")).toHaveTextContent(/question/i);
  });

  it("shows live progress, exposes cancellation, and renders claims only after completion", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      sseResponse([
        'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n',
        'id: 2\nevent: retrieval.completed\ndata: {"stage":"retrieving","candidate_count":2}\n\n',
        'id: 3\nevent: answer.completed\ndata: {"answer_status":"complete","claims":[{"id":"claim-1","ordinal":0,"text":"Verified claim","type":"factual","citation_ids":["citation-1"]}],"citations":[{"id":"citation-1","evidence_id":"evidence-1","source_title":"Official docs","publisher":"Publisher","canonical_url":"https://docs.example.test","excerpt":"Evidence","captured_at":"2026-08-04T00:00:00Z","source_type":"documentation"}],"limitations":[]}\n\n',
      ]),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<CitedAnswerForm />);
    fireEvent.change(screen.getByLabelText("Technical question"), {
      target: { value: "How does LangGraph work?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask ATLAS" }));

    expect(screen.getByRole("button", { name: "Cancel request" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent(/retrieving|accepted/i);
    expect(screen.queryByText("Verified claim")).not.toBeInTheDocument();

    await waitFor(() => expect(screen.getByText("Verified claim")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: "Open Official docs" })).toHaveAttribute(
      "href",
      "https://docs.example.test/",
    );
    expect(screen.queryByRole("button", { name: "Cancel request" })).not.toBeInTheDocument();
  });

  it("sends explicit cancellation for an active run", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      sseResponse(['id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n']),
    );
    vi.stubGlobal("fetch", fetchMock);
    render(<CitedAnswerForm />);
    fireEvent.change(screen.getByLabelText("Technical question"), {
      target: { value: "Can I cancel this?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask ATLAS" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel request" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(fetchMock.mock.calls[1]?.[0]).toContain("/v1/answers/run-123");
    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({ method: "DELETE" });
  });
});
