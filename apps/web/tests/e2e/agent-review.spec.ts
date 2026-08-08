import { expect, test } from "@playwright/test";

test("reviewer can approve a proposal before publication", async ({ page }) => {
  await page.route("**/v1/agent/reviews", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "review-1", status: "pending" }) });
  });
  await page.route("**/v1/agent/reviews/review-1/decision", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: "review-1", status: "approved" }) });
  });
  await page.goto("/es/admin/reviews");
  await page.getByLabel("ID de ejecución").fill("00000000-0000-0000-0000-000000000006");
  await page.getByLabel("IDs de evidencia").fill("fixture-evidence-1");
  await expect(page.getByRole("heading", { name: "Revisión humana" })).toBeVisible();
  await page.getByLabel("Propuesta").fill("Propuesta con evidencia verificada");
  await page.getByRole("button", { name: "Solicitar revisión" }).click();
  await expect(page.getByText("Revisión pendiente", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Aprobar", exact: true }).click();
  await expect(page.getByText("publicación autorizada", { exact: false })).toBeVisible();
});
