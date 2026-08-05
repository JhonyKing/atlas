import { expect, test, type Page } from "@playwright/test";

async function openQuestion(page: Page, question: string) {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await expect(page.locator('[data-hydrated="true"]')).toBeVisible();
  await page.getByLabel("Technical question").fill(question);
  await page.getByRole("button", { name: "Ask ATLAS" }).click();
}

test("out-of-scope question renders an explicit abstention and scope guidance", async ({ page }) => {
  await page.route("**/v1/answers", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
        "Content-Type": "text/event-stream",
        "X-Atlas-Run-ID": "e2e-abstention-run",
      },
      body:
        'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
        'id: 2\nevent: answer.abstained\ndata: {"answer_status":"abstained","limitations":["No verified evidence supports this question."],"scope_explanation":"ATLAS covers LangGraph, LangChain, and the OpenAI API.","scope_suggestion":"Ask how LangGraph persists state."}\n\n',
    });
  });

  await openQuestion(page, "What is the weather on Mars?");

  await expect(page.getByRole("heading", { name: "ATLAS could not verify this answer" })).toBeVisible();
  await expect(page.locator("#question-error")).toContainText("No verified evidence supports this question.");
  await expect(page.getByText("ATLAS covers LangGraph, LangChain, and the OpenAI API.")).toBeVisible();
  await expect(page.getByText("Ask how LangGraph persists state.")).toBeVisible();
  await expect(page.locator(".evidence-panel")).toHaveCount(0);
});

test("malicious source instructions produce a safe abstention with no executable action", async ({ page }) => {
  await page.route("**/v1/answers", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
        "Content-Type": "text/event-stream",
        "X-Atlas-Run-ID": "e2e-injection-run",
      },
      body:
        'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
        'id: 2\nevent: answer.abstained\ndata: {"answer_status":"abstained","limitations":["ATLAS ignored instructions embedded in source evidence and could not verify a safe answer."]}\n\n',
    });
  });

  await openQuestion(page, "Summarize the verified persistence guidance.");

  await expect(page.locator("#question-error")).toContainText("ignored instructions embedded in source evidence");
  await expect(page.locator(".evidence-panel")).toHaveCount(0);
  await expect(page.getByRole("button", { name: /send secrets|run instruction/i })).toHaveCount(0);
  await expect(page.getByRole("link")).toHaveCount(0);
});
