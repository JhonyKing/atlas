import { CitedAnswerForm } from "@/features/cited-answer/CitedAnswerForm";
import { AgentWorkspace } from "@/features/agent/AgentWorkspace";

export function HomePage() {
  return <main className="ask-page"><AgentWorkspace /><CitedAnswerForm /></main>;
}

export default HomePage;
