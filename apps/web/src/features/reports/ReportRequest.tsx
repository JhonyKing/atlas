"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { useLocale } from "@/i18n";
import { Button, Field, Input } from "@/components/forms";

import { createReport, deleteReport, downloadReport, getReport, reportDownloadUrl, type ReportStatus } from "./report-client";

export function ReportRequest() {
  const { locale } = useLocale();
  const searchParams = useSearchParams();
  const spanish = locale === "es-MX";
  const prefix = spanish ? "/es" : "/en";
  const [sourceRunId, setSourceRunId] = useState(() => searchParams.get("comparison_id") ?? "");
  const [report, setReport] = useState<ReportStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [downloading, setDownloading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!sourceRunId.trim()) {
      setError(spanish ? "Escribe el ID de una comparación completada." : "Enter the ID of a completed comparison.");
      return;
    }
    setSubmitting(true);
    try {
      const id = await createReport(sourceRunId.trim(), locale);
      setReport({ report_id: id, status: "queued" });
      for (let attempt = 0; attempt < 100; attempt += 1) {
        const next = await getReport(id);
        setReport(next);
        if (["completed", "failed", "expired", "deleted"].includes(next.status)) return;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } catch (cause) {
      const reason = cause instanceof Error ? cause.message : "";
      const known: Record<string, [string, string]> = {
        source_run_not_found: ["No encontramos esa comparación para esta sesión del navegador.", "That comparison is not available to this browser session."],
        source_run_not_completed: ["La comparación todavía no está terminada.", "The comparison has not completed yet."],
        source_run_has_no_evidence: ["La comparación no tiene evidencias para respaldar un reporte.", "The comparison has no evidence to support a report."],
        report_type_not_implemented: ["Este tipo de reporte aún no está disponible.", "This report type is not available yet."],
        quota_exceeded: ["Alcanzaste el límite temporal de reportes. Inténtalo más tarde.", "You reached the temporary report limit. Try again later."],
        idempotency_conflict: ["La solicitud del reporte entró en conflicto. Vuelve a intentarlo.", "The report request conflicted. Please try again."],
      };
      const message = known[reason];
      setError(message ? message[spanish ? 0 : 1] : reason && reason !== "ATLAS could not create the report."
        ? `${spanish ? "No se pudo crear el reporte" : "Report creation failed"}: ${reason}`
        : spanish ? "No pudimos crear el reporte. Inténtalo de nuevo más tarde." : "We couldn't create the report. Try again later.");
    } finally {
      setSubmitting(false);
    }
  }

  async function removeReport() {
    if (!report) return;
    setDeleting(true);
    try {
      await deleteReport(report.report_id);
      setReport(null);
    } catch {
      setError(spanish ? "No se pudo eliminar el informe." : "The report could not be deleted.");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <section className="report-request-panel" aria-labelledby="report-title">
      <p className="report-kicker">{spanish ? "Reportes con evidencia" : "Evidence-backed reports"}</p>
      <h2 id="report-title">{spanish ? "Crea un reporte a partir de investigación verificada" : "Create a report from verified research"}</h2>
      <p className="report-intro">{spanish ? "Convierte una comparación terminada en DOCX y PDF conservando sus fuentes, citas y limitaciones." : "Turn a completed comparison into DOCX and PDF while preserving its sources, citations, and limitations."}</p>
      <section className="report-primary-path" aria-labelledby="report-start-title">
        <div>
          <h3 id="report-start-title">{spanish ? "Primero termina una comparación" : "Start with a completed comparison"}</h3>
          <p>{spanish ? "ATLAS necesita resultados verificados antes de crear un documento." : "ATLAS needs verified results before it can create a document."}</p>
        </div>
        <Link className="report-primary-link" href={`${prefix}/compare`}>{spanish ? "Comparar tecnologías primero" : "Compare technologies first"}</Link>
      </section>
      <details className="report-advanced" open={Boolean(sourceRunId)}>
        <summary>{spanish ? "Opciones avanzadas: ingresar un ID de comparación" : "Advanced options: enter a comparison ID"}</summary>
        <form onSubmit={submit}>
          <Field id="source-run-id" label={spanish ? "ID de comparación completada" : "Completed comparison ID"} helper={spanish ? "Pega el ID que aparece en los resultados o ábrelo desde la comparación." : "Paste the ID shown on the results screen, or open this page from the comparison."} error={error ?? undefined}>
            <Input id="source-run-id" value={sourceRunId} onChange={(event) => setSourceRunId(event.target.value)} placeholder="e.g. 7d3e…" autoComplete="off" required />
          </Field>
          <Button type="submit" loading={submitting}>{spanish ? "Generar informe" : "Generate report"}</Button>
        </form>
      </details>
      {report ? <ReportArtifacts report={report} spanish={spanish} deleting={deleting} downloading={downloading} onDownload={async (format) => { setError(null); setDownloading(true); try { await downloadReport(report.report_id, format); } catch { setError(spanish ? "No se pudo descargar el informe." : "The report could not be downloaded."); } finally { setDownloading(false); } }} onDelete={() => void removeReport()} /> : <section className="report-recent-card" aria-labelledby="report-recent-title"><h3 id="report-recent-title">{spanish ? "Aún no hay comparaciones terminadas" : "No completed comparisons yet"}</h3><p>{spanish ? "Cuando termines una comparación, aparecerá aquí para convertirla en reporte. Si ya tienes un ID, usa Opciones avanzadas." : "When you finish a comparison, it will appear here for report creation. If you already have an ID, use Advanced options."}</p></section>}
    </section>
  );
}

function ReportArtifacts({ report, spanish, deleting, downloading, onDownload, onDelete }: { report: ReportStatus; spanish: boolean; deleting: boolean; downloading: boolean; onDownload: (format: "docx" | "pdf") => void; onDelete: () => void }) {
  if (report.status !== "completed") return <div className="report-artifact-status" data-report-state={report.status}><p role={report.status === "failed" ? "alert" : "status"}>{report.status === "failed" ? (spanish ? `No se pudo generar el reporte: ${report.error_code ?? "error desconocido"}` : `The report could not be generated: ${report.error_code ?? "unknown error"}`) : (spanish ? `Estado: ${report.status}` : `Status: ${report.status}`)}</p>{["accepted", "planning", "rendering"].includes(report.status) ? <span className="report-progress-bar" aria-hidden="true" /> : null}</div>;
  return (
    <div className="report-artifacts" data-report-state="completed">
      <p role="status">{spanish ? "Informe listo." : "Report ready."}</p>
      <div className="report-downloads"><a className="report-download-link" href={reportDownloadUrl(report.report_id, "docx")} aria-disabled={downloading} onClick={(event) => { event.preventDefault(); if (!downloading) onDownload("docx"); }}>{spanish ? "Descargar DOCX" : "Download DOCX"}</a><a className="report-download-link" href={reportDownloadUrl(report.report_id, "pdf")} aria-disabled={downloading} onClick={(event) => { event.preventDefault(); if (!downloading) onDownload("pdf"); }}>{spanish ? "Descargar PDF" : "Download PDF"}</a></div>
      <Button type="button" variant="tertiary" loading={deleting} onClick={onDelete}>{spanish ? "Eliminar artefactos" : "Delete artifacts"}</Button>
    </div>
  );
}
