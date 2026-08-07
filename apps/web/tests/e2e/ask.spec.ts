import { expect, test } from "@playwright/test";

test("Ask ATLAS has a focused research entry point and example questions", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: "Answers you can verify." })).toBeVisible();
  await expect(page.getByText(/Verified sources:/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Try a focused question" })).toBeVisible();
  const question = page.getByLabel("Technical question");
  await page.getByRole("button", { name: "How does LangGraph persist state?" }).click();
  await expect(question).toHaveValue("How does LangGraph persist state?");
  await expect(page.getByRole("button", { name: "Ask ATLAS" })).toBeVisible();
  await expect(page.locator("#question")).toHaveAttribute("aria-invalid", "false");
  const dimensions = await page.evaluate(() => ({ width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width);
  await page.screenshot({ path: "test-results/020-ask-desktop.png", fullPage: true });
});

test("Ask ATLAS remains usable at 390px without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/es", { waitUntil: "networkidle", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: "Respuestas que puedes verificar." })).toBeVisible();
  await expect(page.getByLabel("Pregunta técnica")).toBeVisible();
  await expect(page.getByRole("button", { name: "Preguntar a ATLAS" })).toBeVisible();
  const dimensions = await page.evaluate(() => ({ width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.width);
  await page.screenshot({ path: "test-results/020-ask-mobile.png", fullPage: true });
});
