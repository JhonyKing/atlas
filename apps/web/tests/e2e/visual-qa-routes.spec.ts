import { expect, test } from "@playwright/test";

const routes = [
  "/",
  "/compare",
  "/reports",
  "/news",
  "/sources",
  "/account",
  "/admin",
  "/admin/sources",
  "/admin/reviews",
  "/admin/governance",
  "/en",
  "/en/compare",
  "/en/reports",
  "/en/news",
  "/en/sources",
  "/en/account",
  "/en/admin",
  "/en/admin/sources",
  "/en/admin/reviews",
  "/en/admin/governance",
  "/es",
  "/es/compare",
  "/es/reports",
  "/es/news",
  "/es/sources",
  "/es/account",
  "/es/admin",
  "/es/admin/sources",
  "/es/admin/reviews",
  "/es/admin/governance",
];

for (const viewport of [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
]) {
  test.describe(`${viewport.name} visual QA`, () => {
    test.use({ viewport });

    for (const route of routes) {
      test(`renders ${route}`, async ({ page }) => {
        await page.emulateMedia({ reducedMotion: "reduce" });
        await page.route("**/*", async (requestRoute) => {
          if (new URL(requestRoute.request().url()).pathname.startsWith("/v1/")) {
            await requestRoute.abort();
            return;
          }
          await requestRoute.continue();
        });
        const response = await page.goto(route, { waitUntil: "domcontentloaded", timeout: 120_000 });
        expect(response?.status(), route).toBe(200);

        await expect(page.locator("body")).toBeVisible();
        await page.screenshot({
          path: `test-results/visual-qa-${viewport.name}-${route.slice(1).replaceAll("/", "-") || "home"}.png`,
          fullPage: true,
        });
      });
    }
  });
}
