import { getPublicEnvironment } from "@/lib/env";
import { atlasVisitorHeaders, rememberAtlasVisitor } from "@/lib/atlas-visitor";

export type ReportStatus = {
  report_id: string;
  status: string;
  document?: { format: "docx" | "pdf"; download_name: string } | null;
  error_code?: string | null;
};

function key(): string {
  return typeof crypto.randomUUID === "function" ? crypto.randomUUID() : `${Date.now()}-atlas-report`;
}

export async function createReport(sourceRunId: string, locale: "en-US" | "es-MX"): Promise<string> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/reports`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Idempotency-Key": key(), ...atlasVisitorHeaders() },
    body: JSON.stringify({
      source_run_id: sourceRunId,
      report_type: "comparison",
      locale,
      audience: "technical researcher",
      scope: "completed technology comparison",
    }),
  });
  rememberAtlasVisitor(response);
  if (!response.ok) throw new Error("ATLAS could not create the report.");
  return ((await response.json()) as { report_id: string }).report_id;
}

export async function getReport(reportId: string): Promise<ReportStatus> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/reports/${reportId}`, { headers: atlasVisitorHeaders() });
  rememberAtlasVisitor(response);
  if (!response.ok) throw new Error("ATLAS could not read the report.");
  return (await response.json()) as ReportStatus;
}

export async function downloadReport(reportId: string, format: "docx" | "pdf"): Promise<void> {
  const response = await fetch(reportDownloadUrl(reportId, format), { headers: atlasVisitorHeaders() });
  rememberAtlasVisitor(response);
  if (!response.ok) throw new Error("ATLAS could not download the report.");
  const blobUrl = URL.createObjectURL(await response.blob());
  const anchor = document.createElement("a");
  anchor.href = blobUrl;
  anchor.download = `atlas-report-${reportId}.${format}`;
  anchor.click();
  URL.revokeObjectURL(blobUrl);
}

export function reportDownloadUrl(reportId: string, format: "docx" | "pdf"): string {
  return `${getPublicEnvironment().apiOrigin}/v1/reports/${reportId}/download?format=${format}`;
}

export async function deleteReport(reportId: string): Promise<void> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/reports/${reportId}`, { method: "DELETE", headers: atlasVisitorHeaders() });
  rememberAtlasVisitor(response);
  if (!response.ok) throw new Error("ATLAS could not delete the report.");
}

