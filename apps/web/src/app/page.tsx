import { CitedAnswerForm } from "@/features/cited-answer/CitedAnswerForm";
import { CorpusStatus } from "@/features/corpus/CorpusStatus";
import { DailyNews } from "@/features/news/DailyNews";

export function HomePage() {
  return <main><CorpusStatus /><DailyNews /><CitedAnswerForm /></main>;
}

export default HomePage;
