import { randomUUID } from "node:crypto";

import { expect, test, type Page } from "@playwright/test";

const deploymentUrl = process.env.ATLAS_DEPLOYMENT_WEB_ORIGIN?.replace(/\/$/, "");
const apiOrigin = process.env.ATLAS_DEPLOYMENT_API_ORIGIN?.replace(/\/$/, "");

function observeLocalhostFallbacks(page: Page): string[] {
  const localRequests: string[] = [];
  page.on("request", (request) => {
    const host = new URL(request.url()).hostname;
    if (host === "localhost" || host === "127.0.0.1" || host === "::1") localRequests.push(request.url());
  });
  return localRequests;
}

test.describe("deployed release smoke contract", () => {
  test.skip(!deploymentUrl, "Set ATLAS_DEPLOYMENT_WEB_ORIGIN for an operator-run hosted smoke.");
  test.describe.configure({ timeout: 180_000, mode: "serial" });

  test("loads explicit Spanish and English routes with visible flag controls and no localhost requests", async ({ page }) => {
    const localRequests = observeLocalhostFallbacks(page);

    await page.goto(`${deploymentUrl}/es`, { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: "Respuestas que puedes verificar." })).toBeVisible();
    await expect(page.getByRole("button", { name: "Cambiar a inglés" }).locator("img")).toHaveAttribute("src", /flag-us\.svg/);

    await page.goto(`${deploymentUrl}/en`, { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: "Answers you can verify." })).toBeVisible();
    await expect(page.getByRole("button", { name: "Switch to Spanish" }).locator("img")).toHaveAttribute("src", /flag-mx\.svg/);
    expect(localRequests, "deployed pages must not call a local machine").toEqual([]);
  });

  test("loads every public feature route with the expected localized surface", async ({ page }) => {
    const routes = [
      { path: "/es/compare", heading: "Compara tecnologías sin inventar datos." },
      { path: "/es/reports", heading: "Generar informe DOCX/PDF" },
      { path: "/es/news", heading: "Titular del día anterior" },
      { path: "/es/sources", heading: "Estado del corpus" },
    ];
    const localRequests = observeLocalhostFallbacks(page);

    for (const route of routes) {
      await page.goto(`${deploymentUrl}${route.path}`, { waitUntil: "networkidle" });
      await expect(page.getByRole("heading", { name: route.heading })).toBeVisible();
    }
    expect(localRequests, "feature routes must use the managed API origin").toEqual([]);
  });

  test("reports truthful API health and readiness", async ({ page }) => {
    test.skip(!apiOrigin, "Set ATLAS_DEPLOYMENT_API_ORIGIN for the hosted API smoke.");
    const health = await page.request.get(`${apiOrigin}/healthz`);
    const readiness = await page.request.get(`${apiOrigin}/readyz`);
    expect(health.status()).toBe(200);
    expect(readiness.status()).toBe(200);
    expect((await health.json()).status).toBe("ok");
    expect((await readiness.json()).status).toBe("ready");
  });

  test("returns a cited answer and a truthful abstention through the deployed UI", async ({ page }) => {
    test.skip(!apiOrigin, "A managed API origin is required for the answer smoke.");
    await page.goto(`${deploymentUrl}/en`, { waitUntil: "networkidle" });
    await page.getByLabel("Technical question").fill("How does LangGraph persist state across a workflow?");
    await page.getByRole("button", { name: "Ask ATLAS" }).click();
    await expect(page.locator(".evidence-panel")).toBeVisible({ timeout: 120_000 });
    await expect(page.locator(".evidence-panel a").first()).toHaveAttribute("href", /^https:\/\//);

    await page.getByLabel("Technical question").fill("What is the weather on Mars today?");
    await page.getByRole("button", { name: "Ask ATLAS" }).click();
    await expect(page.getByRole("heading", { name: "ATLAS could not verify this answer" })).toBeVisible({ timeout: 120_000 });
    await expect(page.locator(".evidence-panel")).toHaveCount(0);
  });

  test("completes a deployed comparison and generates its DOCX/PDF report", async ({ page }) => {
    test.skip(!apiOrigin, "A managed API origin is required for comparison and report smoke.");
    const comparisonResponse = await page.request.post(`${apiOrigin}/v1/comparisons`, {
      headers: { Accept: "text/event-stream", "Idempotency-Key": randomUUID() },
      data: { technologies: ["langgraph", "openai"], criteria: ["capability"], language: "en-US" },
      timeout: 120_000,
    });
    expect(comparisonResponse.status()).toBe(200);
    expect(await comparisonResponse.text()).toContain("comparison.completed");
    const runId = comparisonResponse.headers()["x-atlas-run-id"];
    expect(runId).toBeTruthy();

    await page.goto(`${deploymentUrl}/en/compare`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Compare" }).click();
    await expect(page.getByRole("heading", { name: "Comparison matrix" })).toBeVisible({ timeout: 120_000 });

    await page.goto(`${deploymentUrl}/en/reports`, { waitUntil: "networkidle" });
    await page.getByLabel("Completed comparison ID").fill(runId!);
    await page.getByRole("button", { name: "Generate report" }).click();
    await expect(page.getByText("Report ready.", { exact: true })).toBeVisible({ timeout: 120_000 });
    await expect(page.getByRole("link", { name: "Download DOCX" })).toHaveAttribute("href", /\/docx$/);
    await expect(page.getByRole("link", { name: "Download PDF" })).toHaveAttribute("href", /\/pdf$/);
  });

  test("shows a non-empty corpus snapshot and a bounded previous-day news state", async ({ page }) => {
    test.skip(!apiOrigin, "A managed API origin is required for corpus and news smoke.");
    await page.goto(`${deploymentUrl}/en/sources`, { waitUntil: "networkidle" });
    await expect(page.locator(".corpus-card").first()).toBeVisible({ timeout: 60_000 });
    await expect(page.locator(".corpus-card")).not.toHaveCount(0);
    await expect(page.getByText("Corpus status unavailable.")).toHaveCount(0);

    await page.goto(`${deploymentUrl}/en/news`, { waitUntil: "networkidle" });
    const news = page.locator(".daily-news");
    await expect(news).toBeVisible({ timeout: 60_000 });
    await expect(news).toHaveAttribute("data-news-state", /^(ready|unavailable)$/);
    await expect(news).not.toContainText("Failed to fetch");
  });
});
