import { expect, test } from "@playwright/test";

test("Spanish report journey keeps original-evidence wording", async ({ page }) => {
  await page.route("**/v1/reports", async (route) => {
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ report_id: "report-es" }) });
  });
  await page.route("**/v1/reports/report-es", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ report_id: "report-es", status: "completed" }) });
  });
  await page.goto("/es");
  await page.getByLabel("ID de comparación completada").fill("comparison-es");
  await page.getByRole("button", { name: "Generar informe" }).click();
  await expect(page.getByText("Informe listo.", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Descargar PDF" })).toBeVisible();
});
