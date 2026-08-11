import { expect, test } from "@playwright/test";

test("completed report exposes DOCX, PDF, and delete controls", async ({ page }) => {
  await page.route("**/v1/reports", async (route) => {
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ report_id: "report-artifacts" }) });
  });
  await page.route("**/v1/reports/report-artifacts", async (route) => {
    if (route.request().method() === "DELETE") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "deleted" }) });
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ report_id: "report-artifacts", status: "completed" }) });
  });
  await page.goto("/en/reports");
  await page.getByText("Advanced options: enter a comparison ID").click();
  await page.getByLabel("Completed comparison ID").fill("comparison-artifacts");
  await page.getByRole("button", { name: "Generate report" }).click();
  await expect(page.getByRole("link", { name: "Download DOCX" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Download PDF" })).toBeVisible();
  await page.getByRole("button", { name: "Delete" }).click();
});
