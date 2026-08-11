import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LocaleProvider } from "./index";
import { ProductHome } from "@/features/home/ProductHome";

describe("locale parity", () => {
  it("uses Mexican Spanish for the explicit /es product journey", async () => {
    window.localStorage.clear();
    window.history.replaceState({}, "", "/es");
    render(<LocaleProvider><ProductHome /></LocaleProvider>);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Respuestas que puedes verificar." })).toBeVisible();
      expect(screen.getByLabelText("¿Qué quieres investigar?")).toBeVisible();
      expect(screen.getByText("Opciones avanzadas")).toBeVisible();
    });
    window.history.replaceState({}, "", "/");
  });
});
