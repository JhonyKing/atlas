import { expect, test } from "@playwright/test";

const cases = [
  { name: "reports empty history", path: "/reports", api: null, marker: "Recent completed comparisons" },
  { name: "news unavailable", path: "/news", api: "/v1/news/daily", marker: "No verified headline" },
  { name: "sources unavailable", path: "/sources", api: "/v1/corpus", marker: "Corpus status unavailable" },
  { name: "account private resources unavailable", path: "/account", api: "/v1/private/resources", marker: "Private resources are unavailable" },
  { name: "admin governance retry", path: "/admin", api: "/v1/corpus/governance", marker: "Corpus governance unavailable" },
] as const;

for (const viewport of [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
]) {
  test.describe(`${viewport.name} route states`, () => {
    test.use({ viewport });

    for (const current of cases) {
      test(current.name, async ({ page }) => {
        if (current.api) {
          await page.route("**/*", async (route) => {
            if (new URL(route.request().url()).pathname === current.api) {
              await route.abort();
              return;
            }
            await route.continue();
          });
        }
        const response = await page.goto(current.path, { waitUntil: "networkidle", timeout: 120_000 });
        expect(response?.status(), current.path).toBe(200);
        await expect(page.getByText(current.marker, { exact: false })).toBeVisible();
        await page.screenshot({ path: `test-results/route-state-${viewport.name}-${current.path.slice(1)}.png`, fullPage: true });
      });
    }
  });
}
