import { expect, test } from "@playwright/test";

test("researcher can generate a completed cited report", async ({ page }) => {
  await page.route("**/v1/reports", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ report_id: "report-e2e" }) });
    }
  });
  await page.route("**/v1/reports/report-e2e", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ report_id: "report-e2e", status: "completed" }) });
  });
  await page.goto("/en/reports");
  await page.getByLabel("Completed comparison ID").fill("comparison-e2e");
  await page.getByRole("button", { name: "Generate report" }).click();
  await expect(page.getByText("Report ready.", { exact: true })).toBeVisible();
});
