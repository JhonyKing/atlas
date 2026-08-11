import { expect, test } from "@playwright/test";

test("reader can inspect citation metadata and replace feedback", async ({ page }) => {
  await page.route("**/v1/answers", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "X-Atlas-Run-ID",
        "Content-Type": "text/event-stream",
        "X-Atlas-Run-ID": "e2e-evidence-run",
      },
      body:
        'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
        'id: 2\nevent: answer.completed\ndata: {"answer_status":"complete","claims":[{"id":"c1","ordinal":0,"text":"A checkpointer persists workflow state.","type":"inference","citation_ids":["e1"]}],"citations":[{"id":"e1","evidence_id":"e1","source_title":"Official LangGraph docs","publisher":"LangChain","canonical_url":"https://docs.example.test/langgraph#persistence","source_revision_url":"https://github.com/example/docs/commit/abc123","anchor":"#persistence","excerpt":"LangGraph persists workflow state through its configured checkpointer.","captured_at":"2026-08-04T00:00:00Z","published_at":"2026-07-20T00:00:00Z","version_label":"v1.0","source_type":"documentation"}],"limitations":[]}\n\n',
    });
  });

  let feedbackPayload: Record<string, unknown> | undefined;
  await page.route("**/v1/answers/e2e-evidence-run/feedback", async (route) => {
    feedbackPayload = JSON.parse(route.request().postData() ?? "{}");
    await route.fulfill({
      status: 204,
      headers: { "Access-Control-Allow-Origin": "*" },
    });
  });

  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await expect(page.locator('[data-hydrated="true"]')).toBeVisible();
  await page.getByLabel("What do you want to research?").fill("How does LangGraph persist state?");
  await page.getByRole("button", { name: "Ask ATLAS" }).click();

  await expect(page.getByText("A checkpointer persists workflow state.")).toBeVisible();
  await expect(page.getByText("Inference")).toBeVisible();
  await expect(page.getByRole("region", { name: "Evidence and feedback" }).getByText("LangChain", { exact: true })).toBeVisible();
  await expect(page.getByText("Captured")).toBeVisible();
  await expect(page.getByText("August 4, 2026")).toBeVisible();
  await expect(page.getByText("v1.0", { exact: true })).toBeVisible();

  const canonical = page.getByRole("link", { name: "Open Official LangGraph docs" });
  const revision = page.getByRole("link", { name: "Open source revision" });
  await expect(canonical).toHaveAttribute("target", "_blank");
  await expect(canonical).toHaveAttribute("rel", /noreferrer/);
  await expect(revision).toHaveAttribute("href", "https://github.com/example/docs/commit/abc123");

  await page.getByRole("button", { name: "Mark answer useful" }).click();
  await expect(page.getByRole("status")).toContainText("Feedback saved");
  expect(feedbackPayload).toEqual({ label: "useful", category: null });
});
