import { expect, test } from "@playwright/test";

const routes = ["/", "/compare", "/reports", "/news", "/sources", "/account", "/engineering", "/admin"] as const;
const viewports = [
  { name: "375", width: 375, height: 844 },
  { name: "390", width: 390, height: 844 },
  { name: "768", width: 768, height: 900 },
  { name: "1024", width: 1024, height: 900 },
  { name: "1280", width: 1280, height: 900 },
  { name: "1440", width: 1440, height: 900 },
  { name: "1920", width: 1920, height: 1080 },
] as const;

function parseRgb(value: string): [number, number, number] | null {
  const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  return match ? [Number(match[1]), Number(match[2]), Number(match[3])] : null;
}

function contrastRatio(foreground: [number, number, number], background: [number, number, number]): number {
  const weights = [0.2126, 0.7152, 0.0722] as const;
  const luminance = (rgb: [number, number, number]) => rgb.map((channel) => {
    const normalized = channel / 255;
    return normalized <= 0.03928 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
  }).reduce((sum, value, index) => sum + value * (weights[index] ?? 0), 0);
  const light = luminance(foreground);
  const dark = luminance(background);
  return (Math.max(light, dark) + 0.05) / (Math.min(light, dark) + 0.05);
}

for (const viewport of viewports) {
  test.describe(`${viewport.name}px visual matrix`, () => {
    for (const route of routes) {
      test(`${route} has no overflow, reachable focus, assets, and touch-safe controls`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
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

        const dimensions = await page.evaluate(() => {
          const width = window.innerWidth;
          const offenders = [...document.querySelectorAll<HTMLElement>("*")]
            .map((element) => ({ element, rect: element.getBoundingClientRect() }))
            .filter(({ rect }) => rect.right > width + 1 || rect.left < -1)
            .slice(0, 8)
            .map(({ element, rect }) => ({ tag: element.tagName, className: element.className, text: element.textContent?.trim().slice(0, 60), left: rect.left, right: rect.right, width: rect.width }));
          return { width, scrollWidth: document.documentElement.scrollWidth, offenders };
        });
        expect(dimensions.scrollWidth, JSON.stringify(dimensions)).toBeLessThanOrEqual(dimensions.width + 1);

        await page.keyboard.press("Tab");
        await expect(page.locator(".atlas-skip-link")).toBeFocused();
        const assetResponse = await page.request.get("/brand/favicon.svg");
        expect(assetResponse.status()).toBe(200);
        await expect(page.locator('img[src*=".svg"]').first()).toHaveJSProperty("complete", true);

        const controls = await page.locator("button:visible, a.atlas-nav-link:visible, .atlas-locale-switch:visible").evaluateAll((elements) => elements.map((element) => {
          const rect = element.getBoundingClientRect();
          return { tag: element.tagName, className: element.className, text: element.textContent?.trim().slice(0, 80), height: rect.height, width: rect.width };
        }));
        expect(controls.every((control) => control.height >= 40 && control.width >= 40), JSON.stringify(controls)).toBe(true);

        const semanticFields = await page.locator("input:visible, textarea:visible, select:visible").evaluateAll((elements) => elements.every((element) => Boolean((element as HTMLInputElement).labels?.length || element.getAttribute("aria-label"))));
        expect(semanticFields).toBe(true);

        const reducedMotion = await page.locator("*").evaluateAll((elements) => elements.filter((element) => {
          const style = getComputedStyle(element);
          return style.animationDuration !== "0s" && parseFloat(style.animationDuration) > 0.05;
        }).length);
        expect(reducedMotion).toBe(0);

        const contrastValues = await page.locator("main").evaluate((element) => {
          const style = getComputedStyle(element);
          const bodyBackground = getComputedStyle(document.body).backgroundColor;
          const background = style.backgroundColor === "rgba(0, 0, 0, 0)" || style.backgroundColor === "transparent"
            ? bodyBackground
            : style.backgroundColor;
          return { foreground: style.color, background };
        });
        const foreground = parseRgb(contrastValues.foreground);
        const background = parseRgb(contrastValues.background);
        const contrast = foreground && background ? contrastRatio(foreground, background) : 7;
        expect(contrast, JSON.stringify({ ...contrastValues, contrast })).toBeGreaterThanOrEqual(4.5);
        await page.screenshot({ path: `test-results/visual-matrix-${viewport.name}-${route.slice(1).replaceAll("/", "-") || "home"}.png`, fullPage: true });
      });
    }
  });
}
