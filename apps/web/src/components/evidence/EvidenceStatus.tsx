export type EvidenceState = "supported" | "partial" | "unsupported" | "contradictory";

const stateCopy: Record<EvidenceState, { icon: string; label: string }> = {
  supported: { icon: "✓", label: "Supported" },
  partial: { icon: "◐", label: "Partial" },
  unsupported: { icon: "—", label: "Unsupported" },
  contradictory: { icon: "!", label: "Contradictory" },
};

export function EvidenceStatus({ state, label }: { state: EvidenceState; label?: string }) {
  const copy = stateCopy[state];
  return (
    <span className={`evidence-status evidence-status-${state}`} data-state={state} title={copy.label}>
      <span aria-hidden="true">{copy.icon}</span>
      <span>{label ?? copy.label}</span>
    </span>
  );
}
