import { expect, test } from "@playwright/test";

test("supported question reveals verified claims only in the terminal event", async ({ page }) => {
  await page.route("**/v1/answers", async (route) => {
    await route.fulfill({
      status: 200,
      headers: { "Content-Type": "text/event-stream", "X-Atlas-Run-ID": "e2e-run-1" },
      body:
        'id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n' +
        'id: 2\nevent: answer.completed\ndata: {"answer_status":"complete","claims":[{"id":"c1","ordinal":0,"text":"Verified claim","type":"factual","citation_ids":["e1"]}],"citations":[{"id":"e1","evidence_id":"e1","source_title":"Official docs","publisher":"Publisher","canonical_url":"https://docs.example.test","excerpt":"Evidence","captured_at":"2026-08-04T00:00:00Z","source_type":"documentation"}],"limitations":[]}\n\n',
    });
  });
  await page.goto("/");
  await page.getByLabel("Technical question").fill("How does LangGraph work?");
  await page.getByRole("button", { name: "Ask ATLAS" }).click();

  await expect(page.getByText("Verified claim")).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Official docs" })).toBeVisible();
});

test("invalid question keeps entered text and offers a correction", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Technical question").fill("???");
  await page.getByRole("button", { name: "Ask ATLAS" }).click();

  await expect(page.getByLabel("Technical question")).toHaveValue("???");
  await expect(page.getByRole("alert")).toContainText("technical question");
});

test("explicit cancellation calls the repeat-safe DELETE endpoint", async ({ page }) => {
  await page.addInitScript(() => {
    const originalFetch = window.fetch.bind(window);
    window.fetch = async (input, init) => {
      if (typeof input === "string" && input.endsWith("/v1/answers") && init?.method === "POST") {
        const encoder = new TextEncoder();
        const body = new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(encoder.encode('id: 1\nevent: run.accepted\ndata: {"stage":"accepted"}\n\n'));
          },
        });
        return new Response(body, {
          status: 200,
          headers: { "Content-Type": "text/event-stream", "X-Atlas-Run-ID": "cancel-run" },
        });
      }
      if (typeof input === "string" && input.endsWith("/v1/answers/cancel-run")) {
        return new Response(null, { status: 202 });
      }
      return originalFetch(input, init);
    };
  });
  await page.goto("/");
  await page.getByLabel("Technical question").fill("Can I cancel this?");
  await page.getByRole("button", { name: "Ask ATLAS" }).click();
  await page.getByRole("button", { name: "Cancel request" }).click();

  await expect(page.getByRole("status")).toContainText("Cancellation requested");
});
