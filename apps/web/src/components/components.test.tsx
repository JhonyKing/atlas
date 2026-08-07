import { render, screen } from "@testing-library/react";
import { describe, expect, test } from "vitest";

import { AtlasLogo } from "./brand/AtlasLogo";
import { CitationCard } from "./evidence/CitationCard";
import { EvidenceStatus } from "./evidence/EvidenceStatus";
import { Button, Field, Input } from "./forms";
import { ResearchProgress } from "./research/ResearchProgress";

describe("ATLAS shared UX primitives", () => {
  test("renders the selected brand variant as a web-ready asset", () => {
    render(<AtlasLogo variant="mark" />);
    expect(screen.getByAltText("ATLAS")).toHaveAttribute("src", expect.stringContaining("atlas-mark.svg"));
  });

  test("exposes loading and disabled button state", () => {
    render(<Button loading>Ask ATLAS</Button>);
    expect(screen.getByRole("button", { name: "Ask ATLAS" })).toBeDisabled();
    expect(screen.getByRole("button")).toHaveAttribute("aria-busy", "true");
  });

  test("connects field label, helper and error semantics", () => {
    render(<Field id="question" label="Question" helper="One question at a time" error="Required"><Input id="question" aria-invalid="true" /></Field>);
    expect(screen.getByLabelText("Question")).toHaveAttribute("id", "question");
    expect(screen.getByRole("alert")).toHaveTextContent("Required");
  });

  test("communicates evidence state with text and icon", () => {
    render(<EvidenceStatus state="partial" />);
    expect(screen.getByText("Partial")).toBeVisible();
    expect(screen.getByText("◐")).toBeVisible();
  });

  test("renders citation metadata and a direct source link", () => {
    render(<CitationCard number={3} sourceTitle="Graph API" publisher="LangChain" sourceType="documentation" excerpt="Runtime context" canonicalUrl="https://example.com" />);
    expect(screen.getByRole("heading", { name: "Graph API" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Open source" })).toHaveAttribute("href", "https://example.com");
  });

  test("renders research progress without inventing backend events", () => {
    render(<ResearchProgress steps={[{ id: "query", label: "Query validated", status: "complete" }, { id: "evidence", label: "Evaluating evidence", status: "active" }]} />);
    expect(screen.getByText("Query validated")).toBeVisible();
    expect(screen.getByText("Evaluating evidence")).toBeVisible();
  });
});
