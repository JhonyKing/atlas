import { expect, test } from "@playwright/test";

test("operator can inspect governed collection coverage", async ({ page }) => {
  await page.route("**/v1/corpus/governance", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        collections: [
          { slug: "framework-langgraph", display_name: "LangGraph", kind: "framework", policy_state: "approved", enabled: true, source_count: 2, stale_count: 0, disabled_count: 0, retry_count: 0, dead_letter_count: 0 },
          { slug: "provider-openai", display_name: "OpenAI", kind: "model_provider", policy_state: "approved", enabled: true, source_count: 3, stale_count: 1, disabled_count: 0, retry_count: 0, dead_letter_count: 0 },
        ],
        coverage: { collection_count: 16, dead_letter_count: 0 },
      }),
    });
  });
  await page.goto("/es");
  await expect(page.getByRole("heading", { name: "Gobierno del corpus" })).toBeVisible();
  await expect(page.locator("li").filter({ hasText: "LangGraph" })).toBeVisible();
  await expect(page.getByText("Estado de fuentes actualizado.")).toBeVisible();
});
