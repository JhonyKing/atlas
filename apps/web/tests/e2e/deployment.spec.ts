import { expect, test } from "@playwright/test";

const deploymentUrl = process.env.ATLAS_DEPLOYMENT_WEB_ORIGIN;

test.describe("deployed release smoke contract", () => {
  test.skip(!deploymentUrl, "Set ATLAS_DEPLOYMENT_WEB_ORIGIN for an operator-run hosted smoke.");

  test("loads the deployed Spanish entry point without localhost fallback", async ({ page }) => {
    await page.goto(`${deploymentUrl}/es`, { waitUntil: "domcontentloaded" });
    await expect(page).toHaveURL(/\/es/);
    await expect(page.locator("body")).not.toContainText("localhost");
  });

  test("keeps the English locale reachable", async ({ page }) => {
    await page.goto(`${deploymentUrl}/en`, { waitUntil: "domcontentloaded" });
    await expect(page).toHaveURL(/\/en/);
    await expect(page.locator("body")).not.toContainText("Failed to fetch");
  });

  test("loads the deployed feature routes without a local-origin fallback", async ({ page }) => {
    for (const route of ["/es/compare", "/es/reports", "/es/news", "/es/sources"]) {
      await page.goto(`${deploymentUrl}${route}`, { waitUntil: "domcontentloaded" });
      await expect(page).toHaveURL(new RegExp(`${route.replace("/", "\\/")}$`));
      await expect(page.locator("body")).not.toContainText("localhost");
    }
  });

  test("reports API health and readiness from the deployed origin", async ({ page }) => {
    const apiOrigin = process.env.ATLAS_DEPLOYMENT_API_ORIGIN;
    test.skip(!apiOrigin, "Set ATLAS_DEPLOYMENT_API_ORIGIN for the hosted API smoke.");
    const health = await page.request.get(`${apiOrigin}/healthz`);
    const readiness = await page.request.get(`${apiOrigin}/readyz`);
    expect(health.status()).toBe(200);
    expect(readiness.status()).toBe(200);
    expect((await health.json()).status).toBe("ok");
    expect((await readiness.json()).status).toBe("ready");
  });
});
