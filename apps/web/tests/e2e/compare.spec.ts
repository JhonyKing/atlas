import { expect, test } from "@playwright/test";

test("Compare exposes typed technology and criterion controls", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/compare", { waitUntil: "networkidle", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: "Compare technologies without invented data." })).toBeVisible();
  await expect(page.getByRole("group", { name: "Technologies (2 to 4)" })).toBeVisible();
  await expect(page.getByRole("group", { name: "Criteria" })).toBeVisible();
  await expect(page.getByRole("checkbox", { name: "LangGraph" })).toBeChecked();
  await expect(page.getByRole("checkbox", { name: "OpenAI" })).toBeChecked();
  await page.getByRole("checkbox", { name: "LangChain" }).check();
  await expect(page.getByText(/3 technologies/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Compare" })).toBeVisible();
  const dimensions = await page.evaluate(() => ({ width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width);
  await page.screenshot({ path: "test-results/020-compare-desktop.png", fullPage: true });
});

test("Compare keeps its control surface usable on a narrow viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/es/compare", { waitUntil: "networkidle", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: "Compara tecnologías sin inventar datos." })).toBeVisible();
  await expect(page.getByRole("button", { name: "Comparar" })).toBeVisible();
  const dimensions = await page.evaluate(() => ({ width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: "test-results/020-compare-mobile.png", fullPage: true });
});

test("Compare renders inspectable evidence states without changing the SSE contract", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.route("**/*", async (route) => {
    if (new URL(route.request().url()).pathname !== "/v1/comparisons") {
      await route.continue();
      return;
    }
    const matrix = {
      technology_ids: ["langgraph", "openai"],
      criterion_ids: ["capability", "context"],
      cells: [
        { technology_id: "langgraph", criterion_id: "capability", state: "supported", value: "Documented", evidence_ids: ["ev-supported"] },
        { technology_id: "langgraph", criterion_id: "context", state: "partial", value: null, explanation: "Sources cover different context paths.", evidence_ids: ["ev-partial"] },
        { technology_id: "openai", criterion_id: "capability", state: "unsupported", value: null, evidence_ids: [] },
        { technology_id: "openai", criterion_id: "context", state: "contradictory", value: null, explanation: "The bounded sources disagree.", evidence_ids: ["ev-a", "ev-b"] },
      ],
      summary: "Fixture matrix for visual and accessibility QA.",
    };
    const body = [
      "event: comparison.accepted\ndata: {\"status\":\"accepted\"}\n",
      `event: comparison.completed\ndata: ${JSON.stringify({ status: "completed", matrix })}\n`,
    ].join("\n");
    await route.fulfill({ status: 200, headers: { "content-type": "text/event-stream", "access-control-allow-origin": "*", "access-control-expose-headers": "X-Atlas-Run-ID", "X-Atlas-Run-ID": "run-visual-qa" }, body });
  });
  await page.goto("/compare", { waitUntil: "networkidle", timeout: 120_000 });
  await page.getByRole("button", { name: "Compare" }).click();
  await expect(page.getByRole("heading", { name: "Comparison matrix" })).toBeVisible();
  await expect(page.locator('[data-state="supported"]')).toHaveCount(2);
  await expect(page.locator('[data-state="partial"]')).toHaveCount(2);
  await expect(page.locator('[data-state="unsupported"]')).toHaveCount(2);
  await expect(page.locator('[data-state="contradictory"]')).toHaveCount(2);
  await page.locator(".comparison-evidence-details").first().locator("summary").click();
  await expect(page.getByText("ev-supported")).toBeVisible();
  await expect(page.locator(".comparison-table-wrap")).toBeVisible();
  await page.screenshot({ path: "test-results/020-compare-matrix-desktop.png", fullPage: true });
});
