import { expect, test } from "@playwright/test";

const tool = {
  tool_id: "cited_answer",
  version: "1.0.0",
  input_schema: {
    type: "object",
    additionalProperties: false,
    required: ["question"],
    properties: { question: { type: "string", minLength: 3 } },
  },
  output_schema: { type: "object" },
  scopes: [],
  side_effect_level: "read",
  approval: "none",
  timeout_ms: 15000,
  budget: { max_calls: 1, max_evidence: 16 },
  availability: "enabled",
  name: "Cited answer",
  description: "Ask one technical question and receive evidence-checked claims.",
};

test("agent workspace selects a typed tool and shows its run timeline", async ({ page }) => {
  await page.route("**/v1/agent/tools*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ version: "1.0.0", locale: "en-US", tools: [tool] }),
    });
  });
  await page.route("**/v1/agent/plans", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        run_id: "00000000-0000-0000-0000-000000000001",
        request: "How does LangGraph persist state?",
        locale: "en-US",
        steps: [{ tool_id: "cited_answer", tool_version: "1.0.0", arguments: { question: "How does LangGraph persist state?" }, dependencies: [], expected_output: "tool_result" }],
        risk_summary: [],
        budget: { max_calls: 1, max_evidence: 16 },
        expires_at: "2099-01-01T00:00:00Z",
        plan_hash: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        required_approval_ids: [],
      }),
    });
  });
  await page.route("**/v1/agent/runs", async (route) => {
    await route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({
        run_id: "00000000-0000-0000-0000-000000000001",
        status: "completed",
        events: [
          { run_id: "00000000-0000-0000-0000-000000000001", sequence: 1, event_type: "run.accepted", occurred_at: "2099-01-01T00:00:00Z", status: "accepted", evidence_ids: [], artifact_ids: [] },
          { run_id: "00000000-0000-0000-0000-000000000001", sequence: 2, event_type: "run.completed", occurred_at: "2099-01-01T00:00:01Z", status: "completed", evidence_ids: [], artifact_ids: [] },
        ],
      }),
    });
  });

  await page.goto("/engineering");
  await page.getByText("Advanced agent controls").click();
  await expect(page.getByRole("heading", { name: "Choose what ATLAS should do" })).toBeVisible();
  await page.getByRole("button", { name: /Cited answer/ }).click();
  await page.locator(".agent-tool-form").getByRole("textbox").fill("How does LangGraph persist state?");
  await page.getByRole("button", { name: "Create plan" }).click();
  await expect(page.getByText("Plan ready")).toBeVisible();
  await page.getByRole("button", { name: "Run plan" }).click();
  await expect(page.getByText("run.completed")).toBeVisible();
});
