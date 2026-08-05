import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EvidencePanel } from "../EvidencePanel";

const citation = {
  id: "citation-1",
  evidence_id: "evidence-1",
  source_title: "Official LangGraph docs",
  publisher: "LangChain",
  canonical_url: "https://docs.example.test/langgraph#persistence",
  source_revision_url: "https://github.com/example/docs/commit/abc123",
  anchor: "#persistence",
  excerpt: "LangGraph persists workflow state through its configured checkpointer.",
  captured_at: "2026-08-04T00:00:00Z",
  published_at: "2026-07-20T00:00:00Z",
  version_label: "v1.0",
  source_type: "documentation" as const,
};

const claim = {
  id: "claim-1",
  ordinal: 0,
  text: "A checkpointer persists workflow state.",
  type: "inference" as const,
  citation_ids: [citation.id],
};

describe("EvidencePanel", () => {
  it("exposes source metadata and a textual inference label", () => {
    render(<EvidencePanel claims={[claim]} citations={[citation]} onFeedback={vi.fn()} />);

    expect(screen.getByText("Official LangGraph docs")).toBeVisible();
    expect(screen.getByText("LangChain")).toBeVisible();
    expect(screen.getByText(/captured/i)).toHaveTextContent(/2026/);
    expect(screen.getByText(/published/i)).toHaveTextContent(/2026/);
    expect(screen.getByText("v1.0")).toBeVisible();
    expect(screen.getByText(/inference/i)).toBeVisible();
  });

  it("opens canonical and revision links in a new browser context", () => {
    render(<EvidencePanel claims={[claim]} citations={[citation]} onFeedback={vi.fn()} />);

    const canonical = screen.getByRole("link", { name: /open official langgraph docs/i });
    const revision = screen.getByRole("link", { name: /open source revision/i });
    expect(canonical).toHaveAttribute("href", citation.canonical_url);
    expect(canonical).toHaveAttribute("target", "_blank");
    expect(canonical).toHaveAttribute("rel", expect.stringContaining("noreferrer"));
    expect(revision).toHaveAttribute("href", citation.source_revision_url);
    expect(revision).toHaveAttribute("target", "_blank");
  });

  it("keeps citation navigation and feedback controls keyboard reachable", () => {
    const onFeedback = vi.fn();
    render(<EvidencePanel claims={[claim]} citations={[citation]} onFeedback={onFeedback} />);

    const canonical = screen.getByRole("link", { name: /open official langgraph docs/i });
    canonical.focus();
    expect(document.activeElement).toBe(canonical);

    const useful = screen.getByRole("button", { name: /mark answer useful/i });
    useful.focus();
    expect(document.activeElement).toBe(useful);
    fireEvent.click(useful);
    expect(onFeedback).toHaveBeenCalledWith({ label: "useful", category: null });
  });

  it("does not communicate inference or source identity by color alone", () => {
    render(<EvidencePanel claims={[claim]} citations={[citation]} onFeedback={vi.fn()} />);

    const inference = screen.getByText(/inference/i);
    expect(inference).toHaveTextContent(/inference/i);
    expect(screen.getByRole("link", { name: /open official langgraph docs/i })).toHaveTextContent(
      /official langgraph docs/i,
    );
  });
});
