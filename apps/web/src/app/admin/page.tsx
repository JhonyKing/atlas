import { GovernancePanel } from "@/features/corpus/GovernancePanel";
import { ReviewPanel } from "@/features/agent/ReviewPanel";

export default function AdminPage() {
  return <main className="admin-page"><GovernancePanel /><ReviewPanel /></main>;
}
