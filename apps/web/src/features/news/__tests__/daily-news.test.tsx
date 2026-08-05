import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LocaleProvider } from "@/i18n";

import { DailyNews } from "../DailyNews";

const readyPayload = {
  status: "ready",
  day: "2026-08-04",
  timezone: "UTC",
  candidate: {
    title: "Internet signal",
    summary: "Bounded summary",
    publisher: "Example News",
    canonical_url: "https://news.example/story",
    published_at: "2026-08-04T12:00:00Z",
    captured_at: "2026-08-05T01:00:00Z",
    authority_score: 0.9,
    topic_score: 0.9,
    corroboration_count: 2,
    content_sha256: "a".repeat(64),
  },
  candidate_count: 1,
  score: 0.9,
  reason_code: "none",
};

describe("DailyNews", () => {
  it("preserves original attribution and canonical link", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(readyPayload), { status: 200 })));

    render(<LocaleProvider><DailyNews /></LocaleProvider>);

    await waitFor(() => expect(screen.getByRole("heading", { level: 3, name: "Internet signal" })).toBeVisible());
    expect(screen.getByText(/Example News/)).toBeVisible();
    expect(screen.getByRole("link", { name: /open source/i })).toHaveAttribute(
      "href",
      "https://news.example/story",
    );
    expect(screen.getByText(/UTC/)).toBeVisible();
  });

  it("renders the explicit unavailable state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      status: "unavailable",
      day: "2026-08-04",
      timezone: "UTC",
      candidate: null,
      candidate_count: 0,
      score: null,
      reason_code: "no_evidence",
    }), { status: 200 })));

    render(<LocaleProvider><DailyNews /></LocaleProvider>);

    await waitFor(() => expect(screen.getByText(/No verified headline/i)).toBeVisible());
  });
});
