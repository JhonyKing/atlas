import { Suspense } from "react";

import { ReportRequest } from "@/features/reports/ReportRequest";

export default function ReportsPage() {
  return <main className="report-page"><Suspense fallback={<p>Loading report options…</p>}><ReportRequest /></Suspense></main>;
}
