import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LocaleProvider } from "./index";
import { CitedAnswerForm } from "@/features/cited-answer/CitedAnswerForm";

describe("locale parity", () => {
  it("switches the cited-answer journey to Mexican Spanish", async () => {
    window.localStorage.clear();
    render(<LocaleProvider><CitedAnswerForm /></LocaleProvider>);

    fireEvent.change(screen.getByLabelText("Language"), { target: { value: "es-MX" } });

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Respuestas que puedes verificar." })).toBeVisible();
      expect(screen.getByLabelText("Pregunta técnica")).toBeVisible();
    });
  });
});
