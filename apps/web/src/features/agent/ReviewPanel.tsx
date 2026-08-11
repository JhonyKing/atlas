"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";
import { Button, Field, Input, Textarea } from "@/components/forms";
import { getApiUrl } from "@/lib/env";

export function ReviewPanel() {
  const spanish = usePathname()?.startsWith("/es") ?? true;
  const [reviewer, setReviewer] = useState("operator@example.test");
  const [runId, setRunId] = useState("");
  const [evidenceIds, setEvidenceIds] = useState("");
  const [proposal, setProposal] = useState("");
  const [reviewId, setReviewId] = useState<string | null>(null);
  const [status, setStatus] = useState("not_required");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function createReview() {
    setBusy(true);
    setError("");
    try {
      const response = await fetch(getApiUrl("/v1/agent/reviews"), {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          run_id: runId,
          evidence_ids: evidenceIds.split(",").map((value) => value.trim()).filter(Boolean),
          proposed_text: proposal,
          reviewer_id: reviewer,
        }),
      });
      if (!response.ok) throw new Error("create_failed");
      const body = (await response.json()) as { id: string; status: string };
      setReviewId(body.id);
      setStatus(body.status);
      setMessage(spanish ? "Revisión pendiente." : "Review pending.");
    } catch {
      setError(spanish ? "No se pudo crear la revisión." : "Review could not be created.");
    } finally {
      setBusy(false);
    }
  }

  async function decide(action: "approve" | "edit" | "reject") {
    if (!reviewId) return;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(getApiUrl(`/v1/agent/reviews/${reviewId}/decision`), {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          reviewer_id: reviewer,
          action,
          decision_key: `${reviewId}-${action}`,
          edited_text: action === "edit" ? proposal : undefined,
        }),
      });
      if (!response.ok) throw new Error("decision_failed");
      const body = (await response.json()) as { status: string };
      setStatus(body.status);
      setMessage(
        body.status === "rejected"
          ? spanish ? "La publicación fue rechazada." : "Publication rejected."
          : spanish ? "Decisión registrada; publicación autorizada." : "Decision recorded; publication authorized.",
      );
    } catch {
      setError(spanish ? "Decisión rechazada." : "Decision rejected.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="admin-panel review-panel" aria-labelledby="review-title">
      <h2 id="review-title">{spanish ? "Revisión humana" : "Human review"}</h2>
      <p>{spanish ? "Aprueba, edita o rechaza antes de publicar." : "Approve, edit, or reject before publication."}</p>
      <div className="review-form-grid">
        <Field id="review-run-id" label={spanish ? "ID de ejecución" : "Run ID"} helper={spanish ? "Identifica la ejecución que será revisada." : "Identify the run that will be reviewed."}>
          <Input id="review-run-id" value={runId} onChange={(event) => setRunId(event.target.value)} placeholder="UUID" required />
        </Field>
        <Field id="review-evidence-ids" label={spanish ? "IDs de evidencia" : "Evidence IDs"} helper={spanish ? "Separa varios IDs con comas." : "Separate multiple IDs with commas."}>
          <Input id="review-evidence-ids" value={evidenceIds} onChange={(event) => setEvidenceIds(event.target.value)} placeholder="ev-1, ev-2" required />
        </Field>
        <Field id="reviewer" label={spanish ? "Revisor" : "Reviewer"}>
          <Input id="reviewer" type="email" value={reviewer} onChange={(event) => setReviewer(event.target.value)} required />
        </Field>
        <Field id="review-proposal" label={spanish ? "Propuesta" : "Proposal"}>
          <Textarea id="review-proposal" className="review-proposal" value={proposal} onChange={(event) => setProposal(event.target.value)} required />
        </Field>
      </div>
      <div className="actions">
        <Button type="button" loading={busy} onClick={() => void createReview()} disabled={!proposal.trim() || !runId.trim() || !evidenceIds.trim() || !reviewer.trim()}>
          {spanish ? "Solicitar revisión" : "Request review"}
        </Button>
      </div>
      <p aria-live="polite">{spanish ? "Estado" : "Status"}: {status}</p>
      {error ? <p className="account-error" role="alert">{error}</p> : null}
      {reviewId && (
        <div className="actions review-decision-actions">
          <Button type="button" loading={busy} onClick={() => void decide("approve")}>{spanish ? "Aprobar" : "Approve"}</Button>
          <Button type="button" variant="secondary" loading={busy} onClick={() => void decide("edit")}>{spanish ? "Editar y aprobar" : "Edit and approve"}</Button>
          <Button type="button" variant="danger" loading={busy} onClick={() => void decide("reject")}>{spanish ? "Rechazar" : "Reject"}</Button>
        </div>
      )}
      <p aria-live="polite">{message}</p>
    </section>
  );
}
