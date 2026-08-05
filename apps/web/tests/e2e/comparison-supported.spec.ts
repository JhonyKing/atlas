import { expect, test } from "@playwright/test";

test("comparison form renders a verified matrix only in the terminal event", async ({ page }) => {
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
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
        "Access-Control-Allow-Methods": "POST, GET, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Accept, Idempotency-Key",
        "X-Atlas-Run-ID": "comparison-e2e-run",
      },
      body:
        'id: 1\nevent: comparison.accepted\ndata: {"status":"accepted"}\n\n' +
        'id: 2\nevent: comparison.completed\ndata: {"status":"completed","matrix":{"technology_ids":["langgraph","openai"],"criterion_ids":["capability","price"],"cells":[{"technology_id":"langgraph","criterion_id":"capability","state":"supported","value":"Graph workflow","evidence_ids":["e1"]},{"technology_id":"langgraph","criterion_id":"price","state":"unsupported","explanation":"No price evidence.","evidence_ids":[]},{"technology_id":"openai","criterion_id":"capability","state":"supported","value":"Responses API","evidence_ids":["e2"]},{"technology_id":"openai","criterion_id":"price","state":"unsupported","explanation":"No price evidence.","evidence_ids":[]}]}}\n\n',
    });
  });

  await page.goto("/en/compare");
  await expect(page.getByRole("heading", { name: "Compare technologies without invented data." })).toBeVisible();
  await page.getByRole("button", { name: "Compare" }).click();

  await expect(page.getByRole("status")).toContainText("Comparison verified");
  await expect(page.getByText("Graph workflow")).toBeVisible();
  await expect(page.getByText("Unsupported").first()).toBeVisible();
  await expect(page.getByText("No price evidence.").first()).toBeVisible();
});
