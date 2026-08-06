import { CitedAnswerForm } from "@/features/cited-answer/CitedAnswerForm";
import { CorpusStatus } from "@/features/corpus/CorpusStatus";
import { DailyNews } from "@/features/news/DailyNews";
import { ReportRequest } from "@/features/reports/ReportRequest";
import { SessionPanel } from "@/features/auth/SessionPanel";
import { PrivateResourcesPanel } from "@/features/private-data/PrivateResourcesPanel";
import { PrivateUploadPanel } from "@/features/private-data/PrivateUploadPanel";

export function HomePage() {
  return <main><CorpusStatus /><DailyNews /><SessionPanel /><PrivateResourcesPanel /><PrivateUploadPanel /><CitedAnswerForm /><ReportRequest /></main>;
}

export default HomePage;
