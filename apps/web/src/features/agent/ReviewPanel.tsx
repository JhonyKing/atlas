"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";

export function ReviewPanel() {
  const spanish = usePathname()?.startsWith("/es") ?? true;
  const [reviewer, setReviewer] = useState("operator@example.test");
  const [runId, setRunId] = useState("");
  const [evidenceIds, setEvidenceIds] = useState("");
  const [proposal, setProposal] = useState("");
  const [reviewId, setReviewId] = useState<string | null>(null);
  const [status, setStatus] = useState("not_required");
  const [message, setMessage] = useState("");

  async function createReview() {
    const response = await fetch("/v1/agent/reviews", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        run_id: runId,
        evidence_ids: evidenceIds.split(",").map((value) => value.trim()).filter(Boolean),
        proposed_text: proposal,
        reviewer_id: reviewer,
      }),
    });
    if (!response.ok) {
      setMessage(spanish ? "No se pudo crear la revisión." : "Review could not be created.");
      return;
    }
    const body = (await response.json()) as { id: string; status: string };
    setReviewId(body.id);
    setStatus(body.status);
    setMessage(spanish ? "Revisión pendiente." : "Review pending.");
  }

  async function decide(action: "approve" | "edit" | "reject") {
    if (!reviewId) return;
    const response = await fetch(`/v1/agent/reviews/${reviewId}/decision`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        reviewer_id: reviewer,
        action,
        decision_key: `${reviewId}-${action}`,
        edited_text: action === "edit" ? proposal : undefined,
      }),
    });
    if (!response.ok) {
      setMessage(spanish ? "Decisión rechazada." : "Decision rejected.");
      return;
    }
    const body = (await response.json()) as { status: string };
    setStatus(body.status);
    setMessage(
      body.status === "rejected"
        ? spanish ? "La publicación fue rechazada." : "Publication rejected."
        : spanish ? "Decisión registrada; publicación autorizada." : "Decision recorded; publication authorized.",
    );
  }

  return (
    <section className="admin-panel review-panel" aria-labelledby="review-title">
      <h2 id="review-title">{spanish ? "Revisión humana" : "Human review"}</h2>
      <p>{spanish ? "Aprueba, edita o rechaza antes de publicar." : "Approve, edit, or reject before publication."}</p>
      <div className="review-form-grid">
        <label className="account-field">
          {spanish ? "ID de ejecución" : "Run ID"}
          <input value={runId} onChange={(event) => setRunId(event.target.value)} placeholder="UUID" />
        </label>
        <label className="account-field">
          {spanish ? "IDs de evidencia" : "Evidence IDs"}
          <input value={evidenceIds} onChange={(event) => setEvidenceIds(event.target.value)} placeholder="ev-1, ev-2" />
        </label>
        <label className="account-field">
          {spanish ? "Revisor" : "Reviewer"}
          <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} />
        </label>
        <label className="account-field review-proposal">
          {spanish ? "Propuesta" : "Proposal"}
          <textarea value={proposal} onChange={(event) => setProposal(event.target.value)} />
        </label>
      </div>
      <div className="actions">
        <button type="button" onClick={() => void createReview()} disabled={!proposal.trim() || !runId.trim() || !evidenceIds.trim()}>
          {spanish ? "Solicitar revisión" : "Request review"}
        </button>
      </div>
      <p aria-live="polite">{spanish ? "Estado" : "Status"}: {status}</p>
      {reviewId && (
        <div className="actions review-decision-actions">
          <button type="button" onClick={() => void decide("approve")}>{spanish ? "Aprobar" : "Approve"}</button>
          <button type="button" onClick={() => void decide("edit")}>{spanish ? "Editar y aprobar" : "Edit and approve"}</button>
          <button type="button" onClick={() => void decide("reject")}>{spanish ? "Rechazar" : "Reject"}</button>
        </div>
      )}
      <p aria-live="polite">{message}</p>
    </section>
  );
}
