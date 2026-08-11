import { expect, test } from "@playwright/test";

test("locale switch updates the route and persists the Spanish preference", async ({ page }) => {
  await page.goto("/en");
  await page.waitForLoadState("networkidle");
  await expect(page.locator('[data-hydrated="true"]')).toBeVisible();
  await expect(page.getByRole("heading", { name: "Answers you can verify." })).toBeVisible();

  await page.getByRole("button", { name: "Switch to Spanish" }).click();
  await expect(page).toHaveURL(/\/es$/);
  await expect(page.getByRole("heading", { name: "Respuestas que puedes verificar." })).toBeVisible();

  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.getByRole("heading", { name: "Respuestas que puedes verificar." })).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("lang", "es-MX");
});

test("Spanish presentation preserves citation identity and original-language evidence", async ({ page }) => {
  await page.route("**/v1/answers", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
        "Content-Type": "text/event-stream",
        "X-Atlas-Run-ID": "es-parity-run",
      },
      body:
        'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
        'id: 2\nevent: answer.completed\ndata: {"answer_status":"complete","claims":[{"id":"c1","ordinal":0,"text":"La afirmación traducida conserva su evidencia.","type":"factual","citation_ids":["e1"]}],"citations":[{"id":"e1","evidence_id":"e1","source_title":"Official docs","publisher":"Publisher","canonical_url":"https://docs.example.test/original","excerpt":"Evidence remains in the original language.","captured_at":"2026-08-04T00:00:00Z","source_type":"documentation"}],"limitations":[]}\n\n',
    });
  });

  await page.goto("/es");
  await page.waitForLoadState("networkidle");
  await expect(page.locator('[data-hydrated="true"]')).toBeVisible();
  await page.getByLabel("¿Qué quieres investigar?").fill("¿Cómo conserva el estado LangGraph?");
  await page.getByRole("button", { name: "Preguntar a ATLAS" }).click();

  await expect(page.getByText("La afirmación traducida conserva su evidencia.")).toBeVisible();
  await expect(page.getByText("Afirmación factual")).toBeVisible();
  await expect(page.getByText("Publisher", { exact: true })).toBeVisible();
  await expect(page.getByText("Evidence remains in the original language.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Abrir Official docs" })).toHaveAttribute(
    "href",
    "https://docs.example.test/original",
  );
});
