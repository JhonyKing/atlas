import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { LocaleProvider } from "@/i18n";

import { ComparisonPage } from "../ComparisonPage";

afterEach(() => {
  cleanup();
  window.history.replaceState({}, "", "/");
});

describe("comparison locale parity", () => {
  it("changes presentation language without changing the comparison route contract", () => {
    window.history.replaceState({}, "", "/en/compare");
    const english = render(<LocaleProvider><ComparisonPage /></LocaleProvider>);
    expect(screen.getByRole("heading", { name: "Compare AI technologies for a real decision" })).toBeVisible();
    english.unmount();

    window.history.replaceState({}, "", "/es/compare");
    render(<LocaleProvider><ComparisonPage /></LocaleProvider>);
    expect(screen.getByRole("heading", { name: "Compara tecnologías de IA para una decisión real" })).toBeVisible();
  });
});
