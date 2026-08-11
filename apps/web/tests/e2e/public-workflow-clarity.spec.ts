import { expect, test } from "@playwright/test";

test("Compare frames evidence around a real AI decision", async ({ page }) => {
  await page.goto("/en/compare");

  await expect(page.getByRole("heading", { level: 1, name: "Compare AI technologies for a real decision" })).toBeVisible();
  await expect(page.getByText(/shows what the sources support/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: "Start with a common decision" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Choose an agent framework" })).toBeVisible();
  await expect(page.getByText(/bounded|unsupported states/i)).toHaveCount(0);
});

test("Reports starts with a completed-research path and hides manual IDs", async ({ page }) => {
  await page.goto("/en/reports");

  await expect(page.getByRole("heading", { name: "Create a report from verified research" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Compare technologies first" })).toHaveAttribute("href", "/en/compare");
  const advanced = page.locator(".report-advanced");
  await expect(advanced).not.toHaveAttribute("open", "");
  await expect(page.getByLabel("Completed comparison ID")).not.toBeVisible();
});

test("News explains the user benefit before its unavailable state", async ({ page }) => {
  await page.route("**/v1/news/daily", async (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ status: "unavailable", day: "2026-08-10", timezone: "UTC", candidate: null, candidate_count: 0, score: null, reason_code: "insufficient_signal" }),
  }));
  await page.goto("/en/news");

  await expect(page.getByRole("heading", { name: "Yesterday's most important verified AI story" })).toBeVisible();
  await expect(page.getByText(/one useful AI development from the previous day/i)).toBeVisible();
  await expect(page.getByText(/No story met the evidence threshold/i)).toBeVisible();
});

test("Sources presents trust first and keeps ingestion metrics advanced", async ({ page }) => {
  await page.route("**/v1/corpus", async (route) => route.abort());
  await page.goto("/en/sources");

  await expect(page.getByRole("heading", { name: "Sources ATLAS can verify" })).toBeVisible();
  await expect(page.getByText(/These are the approved sources ATLAS can use/i)).toBeVisible();
  await expect(page.getByText("Corpus status", { exact: true })).toHaveCount(0);
  await expect(page.getByText(/couldn't load the source catalog/i)).toBeVisible();
});

test("Account explains optional sign-in and private-data benefit", async ({ page }) => {
  await page.goto("/en/account");

  await expect(page.getByRole("heading", { level: 1, name: "Your private research space" })).toBeVisible();
  await expect(page.getByText(/Signing in is optional/i)).toBeVisible();
  await expect(page.getByText(/Anonymous research remains available/i)).toBeVisible();
});

for (const viewport of [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
] as const) {
  test(`${viewport.name} P1 public workflows have clear first sections and no overflow`, async ({ page }) => {
    test.setTimeout(60_000);
    await page.setViewportSize(viewport);
    await page.route("**/v1/**", async (route) => route.abort());
    for (const route of ["/en/compare", "/en/reports", "/en/news", "/en/sources", "/en/account"] as const) {
      await page.goto(route);
      await expect(page.locator("h1, h2").first()).toBeVisible();
      if (route.endsWith("/news")) await expect(page.getByText(/No story met the evidence threshold/i)).toBeVisible();
      if (route.endsWith("/sources")) await expect(page.getByText(/couldn't load the source catalog/i)).toBeVisible();
      if (route.endsWith("/account")) await expect(page.getByText(/Private resources are unavailable/i)).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow, route).toBeLessThanOrEqual(1);
      await page.evaluate(() => new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
      await page.screenshot({
        path: `test-results/022-p1-${viewport.name}-${route.slice(4)}.png`,
        fullPage: true,
        caret: "initial",
      });
    }
  });
}
