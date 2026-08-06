"use client";

import { FormEvent, useState } from "react";

import { useLocale } from "@/i18n";

import { createReport, deleteReport, getReport, reportDownloadUrl, type ReportStatus } from "./report-client";

export function ReportRequest() {
  const { locale } = useLocale();
  const spanish = locale === "es-MX";
  const [sourceRunId, setSourceRunId] = useState("");
  const [report, setReport] = useState<ReportStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const id = await createReport(sourceRunId.trim(), locale);
      for (let attempt = 0; attempt < 100; attempt += 1) {
        const next = await getReport(id);
        setReport(next);
        if (["completed", "failed", "expired", "deleted"].includes(next.status)) return;
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Report failed.");
    }
  }

  return (
    <section aria-labelledby="report-title">
      <p>{spanish ? "Artefactos auditables" : "Auditable artifacts"}</p>
      <h2 id="report-title">{spanish ? "Generar informe DOCX/PDF" : "Generate DOCX/PDF report"}</h2>
      <form onSubmit={submit}>
        <label htmlFor="source-run-id">{spanish ? "ID de comparación completada" : "Completed comparison ID"}</label>
        <input id="source-run-id" value={sourceRunId} onChange={(event) => setSourceRunId(event.target.value)} required />
        <button type="submit">{spanish ? "Generar informe" : "Generate report"}</button>
      </form>
      {report ? <ReportArtifacts report={report} spanish={spanish} onDelete={() => void deleteReport(report.report_id)} /> : null}
      {error ? <p role="alert">{error}</p> : null}
    </section>
  );
}

function ReportArtifacts({ report, spanish, onDelete }: { report: ReportStatus; spanish: boolean; onDelete: () => void }) {
  if (report.status !== "completed") return <p role="status">{spanish ? `Estado: ${report.status}` : `Status: ${report.status}`}</p>;
  return (
    <div>
      <p role="status">{spanish ? "Informe listo." : "Report ready."}</p>
      <a href={reportDownloadUrl(report.report_id, "docx")}>{spanish ? "Descargar DOCX" : "Download DOCX"}</a>{" "}
      <a href={reportDownloadUrl(report.report_id, "pdf")}>{spanish ? "Descargar PDF" : "Download PDF"}</a>{" "}
      <button type="button" onClick={onDelete}>{spanish ? "Eliminar" : "Delete"}</button>
    </div>
  );
}

