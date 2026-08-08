"use client";

import type { AgentPlan } from "./types";

type Props = {
  plan: AgentPlan;
  onApprove: () => void;
  onReject: () => void;
};

export function ApprovalCard({ plan, onApprove, onReject }: Props) {
  if (!plan.required_approval_ids?.length) return null;
  return (
    <aside className="agent-approval-card" aria-label="Approval required">
      <strong>Approval required</strong>
      <p>Review the exact tool, version, target, arguments, expiry, and risk before continuing.</p>
      {plan.steps.map((step) => (
        <details key={`${step.tool_id}-${step.tool_version}`} open>
          <summary>{step.tool_id} v{step.tool_version}</summary>
          <pre>{JSON.stringify(step.arguments, null, 2)}</pre>
        </details>
      ))}
      <small>Expires: {new Date(plan.expires_at).toLocaleString()}</small>
      {plan.risk_summary.length > 0 && <small>Risk: {plan.risk_summary.join(", ")}</small>}
      <div className="actions">
        <button type="button" onClick={onApprove}>Approve and run</button>
        <button type="button" className="secondary" onClick={onReject}>Reject</button>
      </div>
    </aside>
  );
}
