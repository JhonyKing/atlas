import { CitedAnswerForm } from "@/features/cited-answer/CitedAnswerForm";
import { CorpusStatus } from "@/features/corpus/CorpusStatus";
import { DailyNews } from "@/features/news/DailyNews";
import { ReportRequest } from "@/features/reports/ReportRequest";

export function HomePage() {
  return <main><CorpusStatus /><DailyNews /><CitedAnswerForm /><ReportRequest /></main>;
}

export default HomePage;
