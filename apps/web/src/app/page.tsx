import { CitedAnswerForm } from "@/features/cited-answer/CitedAnswerForm";
import { CorpusStatus } from "@/features/corpus/CorpusStatus";

export function HomePage() {
  return <main><CorpusStatus /><CitedAnswerForm /></main>;
}

export default HomePage;
