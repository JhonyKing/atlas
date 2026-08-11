import { expect, test } from "@playwright/test";

const publicPaths = ["", "compare", "reports", "news", "sources", "account", "engineering"] as const;

test("all public routes resolve anonymously in English and Spanish", async ({ page }) => {
  test.setTimeout(180_000);
  for (const prefix of ["", "/en", "/es"] as const) {
    for (const path of publicPaths) {
      const route = path ? `${prefix}/${path}` : prefix || "/";
      const response = await page.request.get(route);
      expect(response.status(), route).toBe(200);
      const body = await response.text();
      expect(body, route).not.toMatch(/Vercel Authentication|Log in to Vercel|Sign in to Vercel/i);
    }
  }
});

test("engineering pages preserve locale and expose evidence-linked capabilities", async ({ page }) => {
  test.setTimeout(180_000);
  for (const route of ["/en/engineering", "/es/engineering"] as const) {
    await page.goto(route, { waitUntil: "domcontentloaded", timeout: 120_000 });
    await expect(page.locator("[data-engineering-capability]")).toHaveCount(10);
    await expect(page.locator("[data-engineering-capability] a")).toHaveCount(10);
    await expect(page.getByText("NEXT_PUBLIC_API_ORIGIN")).toHaveCount(0);
  }
});
