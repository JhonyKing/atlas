import { expect, test } from "@playwright/test";

test("Compare exposes typed technology and criterion controls", async ({ page }) => {
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
  await page.screenshot({ path: "test-results/020-compare-mobile.png", fullPage: true });
});
