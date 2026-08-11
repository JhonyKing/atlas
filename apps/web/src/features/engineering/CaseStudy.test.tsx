import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CaseStudy } from "./CaseStudy";

describe("CaseStudy", () => {
  it("presents measured results with evidence and bounded limitations", () => {
    render(<CaseStudy locale="en-US" />);

    const results = screen.getByRole("list", { name: "Measured project results" });
    expect(within(results).getAllByRole("listitem")).toHaveLength(4);
    expect(within(results).getByText("11/11")).toBeVisible();
    expect(within(results).getByText("18.59 s")).toBeVisible();
    expect(within(results).getByText("60/60")).toBeVisible();
    expect(within(results).getByText("21/21")).toBeVisible();
    expect(within(results).getAllByRole("link", { name: /inspect evidence/i })).toHaveLength(4);

    expect(screen.getByRole("heading", { name: "What these results do not prove" })).toBeVisible();
    expect(screen.getAllByText(/not a platform-wide production SLO/i)).toHaveLength(2);
    expect(document.body).not.toHaveTextContent(/99\.5% production availability/i);
  });

  it("preserves the same evidence boundary in Spanish", () => {
    render(<CaseStudy locale="es-MX" />);

    expect(screen.getByRole("heading", { name: "Resultados medidos, no promesas" })).toBeVisible();
    expect(screen.getByRole("list", { name: "Resultados medidos del proyecto" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Lo que estos resultados no demuestran" })).toBeVisible();
  });
});
