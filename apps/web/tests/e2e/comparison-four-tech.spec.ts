import { expect, test } from "@playwright/test";

test("four-technology comparison preserves all selected rows and supports keyboard selection", async ({ page }) => {
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
        "X-Atlas-Run-ID": "comparison-four-tech-run",
      },
      body:
        'id: 1\nevent: comparison.accepted\ndata: {"status":"accepted"}\n\n' +
        'id: 2\nevent: comparison.completed\ndata: {"status":"completed","matrix":{"technology_ids":["langgraph","langchain","openai","anthropic"],"criterion_ids":["capability"],"cells":[' +
        '{"technology_id":"langgraph","criterion_id":"capability","state":"supported","value":"Graph","evidence_ids":["e1"]},' +
        '{"technology_id":"langchain","criterion_id":"capability","state":"supported","value":"Chains","evidence_ids":["e2"]},' +
        '{"technology_id":"openai","criterion_id":"capability","state":"supported","value":"Responses","evidence_ids":["e3"]},' +
        '{"technology_id":"anthropic","criterion_id":"capability","state":"supported","value":"Claude","evidence_ids":["e4"]}]}}\n\n',
    });
  });

  await page.goto("/en/compare");
  await page.getByLabel("LangChain").check();
  await page.getByLabel("Anthropic Claude").check();
  await page.getByLabel("LangGraph").focus();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("LangChain")).toBeFocused();
  await page.getByRole("button", { name: "Compare" }).click();

  await expect(page.getByRole("status")).toContainText("Comparison verified");
  await expect(page.getByText("Graph", { exact: true })).toBeVisible();
  await expect(page.getByText("Chains", { exact: true })).toBeVisible();
  await expect(page.getByText("Responses", { exact: true })).toBeVisible();
  await expect(page.getByText("Claude", { exact: true })).toBeVisible();

  await page.goto("/es/compare");
  await page.getByLabel("LangChain").check();
  await page.getByLabel("Anthropic Claude").check();
  await page.getByRole("button", { name: "Comparar" }).click();
  await expect(page.getByRole("status")).toContainText("Comparación verificada.");
  await expect(page.getByText("Claude", { exact: true })).toBeVisible();
});
