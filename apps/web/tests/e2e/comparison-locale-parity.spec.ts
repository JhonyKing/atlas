import { expect, test } from "@playwright/test";

test("English and Spanish comparison presentation preserve the same matrix values", async ({ page }) => {
  await page.route("**/v1/comparisons**", async (route) => {
    if (route.request().method() === "OPTIONS") {
      await route.fulfill({
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, GET, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Accept, Idempotency-Key",
        },
      });
      return;
    }
    await route.fulfill({
      status: 200,
      headers: {
        "Content-Type": "text/event-stream",
        "X-Atlas-Run-ID": "comparison-locale-run",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
      },
      body:
        'id: 1\nevent: comparison.accepted\ndata: {"status":"accepted"}\n\n' +
        'id: 2\nevent: comparison.completed\ndata: {"status":"completed","matrix":{"technology_ids":["langgraph","openai"],"criterion_ids":["capability"],"cells":[{"technology_id":"langgraph","criterion_id":"capability","state":"supported","value":"Graph workflow","evidence_ids":["e1"]},{"technology_id":"openai","criterion_id":"capability","state":"supported","value":"Responses API","evidence_ids":["e2"]}]}}\n\n',
    });
  });

  await page.goto("/en/compare");
  await page.getByRole("button", { name: "Compare" }).click();
  await expect(page.getByText("Graph workflow")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Compare technologies without invented data." })).toBeVisible();

  await page.goto("/es/compare");
  await page.getByRole("button", { name: "Comparar" }).click();
  await expect(page.getByText("Graph workflow")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Compara tecnologías sin inventar datos." })).toBeVisible();
});
