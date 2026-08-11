"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

import { useLocale } from "@/i18n";
import { Button, Field, Input } from "@/components/forms";

import { createReport, deleteReport, getReport, reportDownloadUrl, type ReportStatus } from "./report-client";

export function ReportRequest() {
  const { locale } = useLocale();
  const spanish = locale === "es-MX";
  const prefix = spanish ? "/es" : "/en";
  const [sourceRunId, setSourceRunId] = useState("");
  const [report, setReport] = useState<ReportStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);

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
    } catch {
      setError(spanish ? "No pudimos crear el reporte. Inténtalo de nuevo más tarde." : "We couldn't create the report. Try again later.");
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
      <details className="report-advanced">
        <summary>{spanish ? "Opciones avanzadas: ingresar un ID de comparación" : "Advanced options: enter a comparison ID"}</summary>
        <form onSubmit={submit}>
          <Field id="source-run-id" label={spanish ? "ID de comparación completada" : "Completed comparison ID"} helper={spanish ? "Pega el ID que aparece en la pantalla de resultados." : "Paste the ID shown on the completed results screen."} error={error ?? undefined}>
            <Input id="source-run-id" value={sourceRunId} onChange={(event) => setSourceRunId(event.target.value)} placeholder="e.g. 7d3e…" autoComplete="off" required />
          </Field>
          <Button type="submit" loading={submitting}>{spanish ? "Generar informe" : "Generate report"}</Button>
        </form>
      </details>
      {report ? <ReportArtifacts report={report} spanish={spanish} deleting={deleting} onDelete={() => void removeReport()} /> : <section className="report-recent-card" aria-labelledby="report-recent-title"><h3 id="report-recent-title">{spanish ? "Aún no hay comparaciones terminadas" : "No completed comparisons yet"}</h3><p>{spanish ? "Cuando termines una comparación, aparecerá aquí para convertirla en reporte. Si ya tienes un ID, usa Opciones avanzadas." : "When you finish a comparison, it will appear here for report creation. If you already have an ID, use Advanced options."}</p></section>}
    </section>
  );
}

function ReportArtifacts({ report, spanish, deleting, onDelete }: { report: ReportStatus; spanish: boolean; deleting: boolean; onDelete: () => void }) {
  if (report.status !== "completed") return <div className="report-artifact-status" data-report-state={report.status}><p role="status">{spanish ? `Estado: ${report.status}` : `Status: ${report.status}`}</p><span className="report-progress-bar" aria-hidden="true" /></div>;
  return (
    <div className="report-artifacts" data-report-state="completed">
      <p role="status">{spanish ? "Informe listo." : "Report ready."}</p>
      <div className="report-downloads"><a className="report-download-link" href={reportDownloadUrl(report.report_id, "docx")}>{spanish ? "Descargar DOCX" : "Download DOCX"}</a><a className="report-download-link" href={reportDownloadUrl(report.report_id, "pdf")}>{spanish ? "Descargar PDF" : "Download PDF"}</a></div>
      <Button type="button" variant="tertiary" loading={deleting} onClick={onDelete}>{spanish ? "Eliminar artefactos" : "Delete artifacts"}</Button>
    </div>
  );
}
