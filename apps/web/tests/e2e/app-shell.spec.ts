import { expect, test } from "@playwright/test";

test("AppShell exposes the public research map and active Ask state", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Skip to content" })).toHaveAttribute("href", "#main-content");
  await expect(page.getByRole("link", { name: "Ask", exact: true })).toHaveAttribute("aria-current", "page");
  await expect(page.getByRole("link", { name: "Compare", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Reports", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "News", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Sources", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Account", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Switch to Spanish" })).toContainText("Español");
  await expect(page.getByRole("button", { name: "Switch to Spanish" })).toContainText("🇲🇽");
  await page.getByRole("button", { name: "Switch to Spanish" }).click();
  await expect(page).toHaveURL(/\/es$/);
  await expect(page.getByRole("button", { name: "Cambiar a inglés" })).toContainText("English");
  await expect(page.getByRole("button", { name: "Cambiar a inglés" })).toContainText("🇺🇸");
});

test("required route surfaces resolve without a server error", async ({ page }) => {
  test.setTimeout(180_000);
  for (const route of [
    "/", "/compare", "/reports", "/news", "/sources", "/account",
    "/admin/sources", "/admin/reviews", "/admin/governance",
    "/es", "/es/compare", "/es/reports", "/es/news", "/es/sources", "/es/account",
    "/es/admin", "/es/admin/sources", "/es/admin/reviews", "/es/admin/governance",
  ]) {
    const response = await page.request.get(route);
    expect(response?.status(), route).toBe(200);
  }
});

test("home owns the Ask journey and keeps operations off the public surface", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#page-title")).toBeVisible();
  await expect(page.locator("#corpus-title")).toHaveCount(0);
  await expect(page.locator("#daily-news-title")).toHaveCount(0);
  await expect(page.locator("#auth-title")).toHaveCount(0);
  await expect(page.locator("#report-title")).toHaveCount(0);
  await expect(page.locator("#governance-title")).toHaveCount(0);
  await expect(page.locator("#review-title")).toHaveCount(0);
});

test("mobile navigation is keyboard/touch discoverable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/es");
  const menu = page.getByRole("button", { name: "Menú" });
  await expect(menu).toHaveAttribute("aria-expanded", "false");
  await menu.click();
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await expect(page.getByRole("link", { name: "Comparar", exact: true })).toBeVisible();
});
