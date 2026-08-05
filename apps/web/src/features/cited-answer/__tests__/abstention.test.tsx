import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CitedAnswerForm } from "../CitedAnswerForm";

function sseResponse(body: string): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "Content-Type": "text/event-stream", "X-Atlas-Run-ID": "abstention-run" },
  });
}

function ask(question: string) {
  fireEvent.change(screen.getByLabelText("Technical question"), { target: { value: question } });
  fireEvent.click(screen.getByRole("button", { name: "Ask ATLAS" }));
}

describe("abstention and disagreement states", () => {
  it("explains an abstention and suggests an in-scope question", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        sseResponse(
          'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
            'id: 2\nevent: answer.abstained\ndata: {"answer_status":"abstained","limitations":["No launch-corpus source supports this question."],"scope_suggestion":"Ask how LangGraph persists state."}\n\n',
        ),
      ),
    );
    render(<CitedAnswerForm />);
    ask("What is the weather on Mars?");

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/No launch-corpus source/i));
    expect(screen.getByText("Ask how LangGraph persists state.")).toBeVisible();
    expect(screen.queryByText("Verified answer")).not.toBeInTheDocument();
  });

  it("labels a partial answer and presents dated disagreement limitations", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        sseResponse(
          'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
            'id: 2\nevent: answer.completed\ndata: {"stage":"completed","answer_status":"partial","claims":[{"id":"c1","ordinal":0,"text":"Supported part","type":"factual","citation_ids":["e1"]}],"citations":[{"id":"e1","evidence_id":"e1","source_title":"Official docs","publisher":"Publisher","canonical_url":"https://docs.example.test","excerpt":"Evidence","captured_at":"2026-08-04T00:00:00Z","source_type":"documentation"}],"limitations":["Partial answer: LangGraph and LangChain sources disagree as of 2026-07-20."]}\n\n',
        ),
      ),
    );
    render(<CitedAnswerForm />);
    ask("Compare the two persistence models.");

    await waitFor(() => expect(screen.getByText("Supported part")).toBeVisible());
    expect(screen.getByText("Partial answer")).toBeVisible();
    expect(screen.getByText(/sources disagree as of 2026-07-20/i)).toBeVisible();
  });

  it("explains when a question is outside the published corpus scope", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        sseResponse(
          'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
            'id: 2\nevent: answer.abstained\ndata: {"answer_status":"abstained","limitations":["This question is outside the published ATLAS corpus."],"scope_explanation":"ATLAS covers LangGraph, LangChain, and the OpenAI API."}\n\n',
        ),
      ),
    );
    render(<CitedAnswerForm />);
    ask("Explain a private undocumented system.");

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/outside the published ATLAS corpus/i));
    expect(screen.getByText(/ATLAS covers LangGraph, LangChain, and the OpenAI API/i)).toBeVisible();
  });
});
