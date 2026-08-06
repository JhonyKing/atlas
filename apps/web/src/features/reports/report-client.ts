import { getPublicEnvironment } from "@/lib/env";

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
    headers: { "Content-Type": "application/json", "Idempotency-Key": key() },
    body: JSON.stringify({
      source_run_id: sourceRunId,
      report_type: "comparison",
      locale,
      audience: "technical researcher",
      scope: "completed technology comparison",
    }),
  });
  if (!response.ok) throw new Error("ATLAS could not create the report.");
  return ((await response.json()) as { report_id: string }).report_id;
}

export async function getReport(reportId: string): Promise<ReportStatus> {
  const response = await fetch(`${getPublicEnvironment().apiOrigin}/v1/reports/${reportId}`);
  if (!response.ok) throw new Error("ATLAS could not read the report.");
  return (await response.json()) as ReportStatus;
}

export function reportDownloadUrl(reportId: string, format: "docx" | "pdf"): string {
  return `${getPublicEnvironment().apiOrigin}/v1/reports/${reportId}/download?format=${format}`;
}

export async function deleteReport(reportId: string): Promise<void> {
  await fetch(`${getPublicEnvironment().apiOrigin}/v1/reports/${reportId}`, { method: "DELETE" });
}

