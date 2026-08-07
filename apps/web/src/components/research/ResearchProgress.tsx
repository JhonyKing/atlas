export type ResearchStepStatus = "complete" | "active" | "pending" | "error";

export type ResearchStep = {
  id: string;
  label: string;
  status: ResearchStepStatus;
};

export function ResearchProgress({ steps, label = "Research progress" }: { steps: ResearchStep[]; label?: string }) {
  return (
    <section className="research-progress" aria-label={label}>
      <ol>
        {steps.map((step) => (
          <li className={`research-step research-step-${step.status}`} key={step.id}>
            <span className="research-step-indicator" aria-hidden="true">{step.status === "complete" ? "✓" : step.status === "error" ? "!" : step.status === "active" ? "●" : "○"}</span>
            <span>{step.label}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
