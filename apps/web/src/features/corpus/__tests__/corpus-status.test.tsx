import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CorpusStatus } from "../CorpusStatus";
import { LocaleProvider } from "@/i18n";

const payload = {
  snapshot_id: "00000000-0000-0000-0000-000000000701",
  generated_at: "2026-08-04T12:00:00Z",
  collections: [
    {
      slug: "langgraph",
      name: "LangGraph",
      publisher: "LangChain",
      source_types: ["documentation", "release_note"],
      status: "ready",
      last_success_at: "2026-08-04T10:00:00Z",
      last_attempt_at: "2026-08-04T10:00:00Z",
      canonical_root: "https://langchain-ai.github.io/langgraph/",
    },
    {
      slug: "langchain",
      name: "LangChain",
      publisher: "LangChain",
      source_types: ["documentation", "changelog"],
      status: "stale",
      last_success_at: "2026-08-01T10:00:00Z",
      last_attempt_at: "2026-08-04T10:00:00Z",
      canonical_root: "https://python.langchain.com/",
    },
    {
      slug: "openai",
      name: "OpenAI API",
      publisher: "OpenAI",
      source_types: ["documentation"],
      status: "unavailable",
      last_success_at: null,
      last_attempt_at: null,
      canonical_root: "https://platform.openai.com/docs/",
    },
  ],
};

describe("CorpusStatus", () => {
  it("shows freshness and availability for every supported collection", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(payload), { status: 200 })));

    render(<LocaleProvider><CorpusStatus /></LocaleProvider>);

    await waitFor(() => expect(screen.getByText("LangGraph")).toBeVisible());
    expect(screen.getByText("Ready")).toBeVisible();
    expect(screen.getByText("Stale")).toBeVisible();
    expect(screen.getByText("Unavailable")).toBeVisible();
    expect(screen.getByText("OpenAI API")).toBeVisible();
    expect(screen.getByText(/Snapshot/)).toBeVisible();
  });

  it("fails closed without exposing transport details", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("database password")));

    render(<LocaleProvider><CorpusStatus /></LocaleProvider>);

    await waitFor(() => expect(screen.getByText("Corpus status unavailable.")).toBeVisible());
    expect(screen.getByRole("heading", { name: "Corpus status" })).toBeVisible();
    expect(screen.queryByText(/database password/i)).not.toBeInTheDocument();
  });
});
