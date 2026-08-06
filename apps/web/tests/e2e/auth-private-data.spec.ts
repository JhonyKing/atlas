import { expect, test } from "@playwright/test";

test("anonymous visitor can optionally sign in and keep private history visible", async ({ page }) => {
  await page.route("**/v1/auth/session", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ session_id: "session-e2e" }) });
      return;
    }
    if (route.request().method() === "DELETE") {
      await route.fulfill({ status: 204, body: "" });
      return;
    }
    await route.fulfill({ status: 401, body: JSON.stringify({ detail: "Authentication required" }) });
  });
  await page.route("**/v1/private/resources", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [{ resource_id: "r1", resource_type: "report" }] }) });
  });

  await page.goto("/en");
  await page.getByLabel("Correo").fill("ana@example.test");
  await page.getByLabel("Contraseña").fill("secret");
  await page.getByRole("button", { name: "Iniciar sesión" }).click();

  await expect(page.getByTestId("auth-status")).toContainText("Sesión iniciada");
  await expect(page.getByText("report", { exact: true })).toBeVisible();
});

test("private upload reports a safety rejection", async ({ page }) => {
  await page.route("**/v1/private/resources", async (route) => {
    await route.fulfill({ status: 401, body: "{}" });
  });
  await page.route("**/v1/private/uploads", async (route) => {
    await route.fulfill({ status: 400, contentType: "application/json", body: JSON.stringify({ detail: "upload failed malware scan", indexable: false }) });
  });
  await page.goto("/en");
  await page.locator('input[type="file"]').setInputFiles({ name: "bad.txt", mimeType: "text/plain", buffer: Buffer.from("EICAR-STANDARD-ANTIVIRUS-TEST-FILE") });
  await expect(page.getByText("Archivo rechazado por seguridad.", { exact: true })).toBeVisible();
});

test("private upload accepts a safe file and another user sees no resources", async ({ page }) => {
  await page.route("**/v1/private/resources", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
  });
  await page.route("**/v1/private/uploads", async (route) => {
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ upload_id: "u1", indexable: true }) });
  });
  await page.goto("/en");
  await page.locator('input[type="file"]').setInputFiles({ name: "notes.txt", mimeType: "text/plain", buffer: Buffer.from("safe notes") });
  await expect(page.getByText("Archivo validado y puesto a disposición privada.", { exact: true })).toBeVisible();
  await expect(page.getByText("Mis recursos privados").locator("..").getByText("report", { exact: true })).toHaveCount(0);
});
