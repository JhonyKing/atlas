"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";

const RUN_ID = "00000000-0000-0000-0000-000000000006";

export function ReviewPanel() {
  const spanish = usePathname()?.startsWith("/es") ?? true;
  const [reviewer, setReviewer] = useState("operator@example.test");
  const [proposal, setProposal] = useState("");
  const [reviewId, setReviewId] = useState<string | null>(null);
  const [status, setStatus] = useState("not_required");
  const [message, setMessage] = useState("");

  async function createReview() {
    const response = await fetch("/v1/agent/reviews", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        run_id: RUN_ID,
        evidence_ids: ["fixture-evidence-1"],
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
        ? spanish
          ? "La publicación fue rechazada."
          : "Publication rejected."
        : spanish
          ? "Decisión registrada; publicación autorizada."
          : "Decision recorded; publication authorized.",
    );
  }

  return (
    <section aria-labelledby="review-title">
      <h2 id="review-title">{spanish ? "Revisión humana" : "Human review"}</h2>
      <p>{spanish ? "Aprueba, edita o rechaza antes de publicar." : "Approve, edit, or reject before publication."}</p>
      <label>
        {spanish ? "Revisor" : "Reviewer"}
        <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} />
      </label>
      <label>
        {spanish ? "Propuesta" : "Proposal"}
        <textarea value={proposal} onChange={(event) => setProposal(event.target.value)} />
      </label>
      <button type="button" onClick={createReview} disabled={!proposal.trim()}>
        {spanish ? "Solicitar revisión" : "Request review"}
      </button>
      <p aria-live="polite">{spanish ? "Estado" : "Status"}: {status}</p>
      {reviewId && (
        <div>
          <button type="button" onClick={() => void decide("approve")}>{spanish ? "Aprobar" : "Approve"}</button>
          <button type="button" onClick={() => void decide("edit")}>{spanish ? "Editar y aprobar" : "Edit and approve"}</button>
          <button type="button" onClick={() => void decide("reject")}>{spanish ? "Rechazar" : "Reject"}</button>
        </div>
      )}
      <p aria-live="polite">{message}</p>
    </section>
  );
}
