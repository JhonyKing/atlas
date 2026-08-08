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
});
