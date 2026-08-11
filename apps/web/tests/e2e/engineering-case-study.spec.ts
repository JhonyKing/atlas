import { expect, test } from "@playwright/test";

for (const route of ["/en/engineering", "/es/engineering"] as const) {
  for (const viewport of [
    { name: "desktop", width: 1440, height: 900 },
    { name: "mobile", width: 390, height: 844 },
  ] as const) {
    test(`${route} exposes measured proof and semantic architecture on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto(route, { waitUntil: "domcontentloaded", timeout: 120_000 });

      await expect(page.locator("[data-case-study-metric]")).toHaveCount(4);
      await expect(page.locator("[data-case-study-metric] a")).toHaveCount(4);
      await expect(page.getByRole("figure", { name: /architecture boundaries|límites de arquitectura/i })).toBeVisible();
      await expect(page.locator("[data-architecture-layer]")).toHaveCount(5);
      await expect(page.getByText("NEXT_PUBLIC_API_ORIGIN")).toHaveCount(0);

      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow).toBeLessThanOrEqual(1);

      const locale = route.startsWith("/es") ? "es" : "en";
      await page.screenshot({
        path: `../../docs/verification/artifacts/022/p2/engineering-${locale}-${viewport.name}.png`,
        fullPage: true,
      });
    });
  }
}
