import { expect, test } from "@playwright/test";

test("comparison matrix explains unsupported and contradictory evidence states", async ({ page }) => {
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
        "X-Atlas-Run-ID": "comparison-states-run",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
      },
      body:
        'id: 1\nevent: comparison.accepted\ndata: {"status":"accepted"}\n\n' +
        'id: 2\nevent: comparison.completed\ndata: {"status":"completed","matrix":{"technology_ids":["langgraph","openai"],"criterion_ids":["price"],"cells":[{"technology_id":"langgraph","criterion_id":"price","state":"unsupported","explanation":"No comparable price evidence.","evidence_ids":[]},{"technology_id":"openai","criterion_id":"price","state":"contradictory","explanation":"Sources use different units.","evidence_ids":["e1","e2"]}]}}\n\n',
    });
  });

  await page.goto("/en/compare");
  await page.getByRole("button", { name: "Compare" }).click();

  await expect(page.getByRole("list", { name: "Evidence states" }).getByText("Unsupported", { exact: true })).toBeVisible();
  await expect(page.getByText("No comparable price evidence.")).toBeVisible();
  await expect(page.getByRole("list", { name: "Evidence states" }).getByText("Contradictory", { exact: true })).toBeVisible();
  await expect(page.getByText("Sources use different units.")).toBeVisible();
});
