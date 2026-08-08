"use client";

import type { AgentRunEvent } from "./types";

type Props = {
  events: AgentRunEvent[];
  runStatus?: string | null;
  onCancel?: () => void;
  onResume?: () => void;
};

export function RunTimeline({ events, runStatus, onCancel, onResume }: Props) {
  if (!events.length) return <p className="empty-state">No run events yet.</p>;
  const canCancel = onCancel && ["accepted", "planned", "running", "awaiting_approval"].includes(runStatus ?? "");
  const canResume = onResume && ["cancelled", "awaiting_approval"].includes(runStatus ?? "");
  return (
    <>
      <ol className="agent-run-timeline" aria-label="Agent run timeline">
        {events.map((event) => (
          <li key={`${event.run_id}-${event.sequence}`}>
            <span className="agent-event-sequence">{event.sequence}</span>
            <span>
              <strong>{event.event_type}</strong>
              <small>{event.status}{event.tool_id ? ` · ${event.tool_id}` : ""}</small>
              {!!(event.evidence_ids.length || event.artifact_ids.length) && (
                <small>Evidence: {event.evidence_ids.length} · Artifacts: {event.artifact_ids.length}</small>
              )}
            </span>
          </li>
        ))}
      </ol>
      {(canCancel || canResume) && (
        <div className="actions agent-run-actions">
          {canCancel && <button type="button" className="secondary" onClick={onCancel}>Cancel run</button>}
          {canResume && <button type="button" onClick={onResume}>Resume run</button>}
        </div>
      )}
    </>
  );
}
