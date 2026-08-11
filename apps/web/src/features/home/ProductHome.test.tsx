import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LocaleProvider } from "@/i18n";

import { ProductHome } from "./ProductHome";

describe("ProductHome", () => {
  it("explains the product through three plain-language actions", () => {
    render(<LocaleProvider><ProductHome /></LocaleProvider>);

    expect(screen.getByRole("heading", { level: 1, name: "Answers you can verify." })).toBeVisible();
    const actions = screen.getByRole("list", { name: "What would you like to do?" });
    expect(within(actions).getAllByRole("link")).toHaveLength(3);
    expect(within(actions).getByRole("link", { name: /Ask a question/i })).toHaveAttribute("href", "#ask-atlas");
    expect(within(actions).getByRole("link", { name: /Compare AI technologies/i })).toHaveAttribute("href", "/en/compare");
    expect(within(actions).getByRole("link", { name: /Create a report/i })).toHaveAttribute("href", "/en/reports");

    expect(document.body).not.toHaveTextContent(/typed tools|budgets|approval rules|evidence state/i);
  });

  it("keeps manual source selection in closed advanced options", () => {
    render(<LocaleProvider><ProductHome /></LocaleProvider>);

    const advanced = screen.getByText("Advanced options").closest("details");
    expect(advanced).not.toHaveAttribute("open");
    expect(screen.getByLabelText("Source selection")).toHaveValue("");
    expect(screen.queryByText(/Corpus \(optional\)/i)).not.toBeInTheDocument();
  });

  it("exposes truthful portfolio destinations", () => {
    render(<LocaleProvider><ProductHome /></LocaleProvider>);

    expect(screen.getByText("Built by Jhonnatan Vazquez — AI Engineer")).toBeVisible();
    expect(screen.getByRole("link", { name: "GitHub" })).toHaveAttribute("href", "https://github.com/JhonyKing/atlas");
    expect(screen.getByRole("link", { name: "Architecture" })).toHaveAttribute("href", "/en/engineering");
    expect(screen.getByRole("link", { name: "Case study" })).toHaveAttribute("href", "/en/engineering#case-study-title");
  });
});
