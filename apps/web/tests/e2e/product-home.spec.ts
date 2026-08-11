import { expect, test } from "@playwright/test";

for (const viewport of [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
] as const) {
  test(`${viewport.name} first viewport communicates the product and primary actions`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/en");

    await expect(page.getByRole("heading", { level: 1, name: "Answers you can verify." })).toBeInViewport();
    await expect(page.getByRole("list", { name: "What would you like to do?" })).toBeInViewport();
    await expect(page.getByRole("link", { name: /Ask a question/i })).toBeInViewport();
    await expect(page.getByLabel("What do you want to research?")).toBeInViewport();
    await expect(page.getByText("Advanced options")).toBeVisible();
    await expect(page.getByText(/typed tools|budgets|approval rules|evidence state/i)).toHaveCount(0);
    await expect(page.getByText("NEXT_PUBLIC_API_ORIGIN")).toHaveCount(0);

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(1);
  });
}

test("Home uses automatic sources and reveals manual selection on demand", async ({ page }) => {
  await page.goto("/en");
  const advanced = page.getByText("Advanced options");
  await expect(advanced).toBeVisible();
  await advanced.click();
  await expect(page.getByLabel("Source selection")).toBeVisible();
  await expect(page.getByLabel("Source selection")).toHaveValue("");
});

test("Home offers portfolio attribution and the engineering route", async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto("/en");
  await expect(page.getByText("Built by Jhonnatan Vazquez — AI Engineer")).toBeVisible();
  const architectureLink = page.getByRole("link", { name: "Architecture" });
  await expect(architectureLink).toHaveAttribute("href", "/en/engineering");
  await Promise.all([
    page.waitForURL(/\/en\/engineering$/, { timeout: 60_000 }),
    architectureLink.click(),
  ]);
  await expect(page.locator("[data-engineering-capability]")).toHaveCount(10);
});
