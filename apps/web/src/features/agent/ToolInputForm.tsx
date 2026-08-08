"use client";

import { useState } from "react";

import type { AgentTool } from "./types";
import { agentInputLabel } from "./i18n";
import { useLocale } from "@/i18n";

type Props = { tool: AgentTool; onSubmit: (input: Record<string, unknown>) => void; disabled?: boolean };

export function ToolInputForm({ tool, onSubmit, disabled = false }: Props) {
  const { locale } = useLocale();
  const properties = (tool.input_schema.properties ?? {}) as Record<string, { type?: string }>;
  const required = new Set((tool.input_schema.required ?? []) as string[]);
  const [values, setValues] = useState<Record<string, string>>({});
  const entries = Object.entries(properties);
  if (entries.length === 0) {
    return <button type="button" onClick={() => onSubmit({})} disabled={disabled}>Continue</button>;
  }
  return (
    <form className="agent-tool-form" onSubmit={(event) => { event.preventDefault(); onSubmit(values); }}>
      {entries.map(([name, definition]) => (
        <label className="account-field" key={name}>
          <span>{agentInputLabel(locale, name)}{required.has(name) ? " *" : ""}</span>
          {definition.type === "array" ? (
            <input value={values[name] ?? ""} onChange={(event) => setValues({ ...values, [name]: event.target.value })} placeholder="value1, value2" />
          ) : name === "question" || name === "scope" ? (
            <textarea value={values[name] ?? ""} onChange={(event) => setValues({ ...values, [name]: event.target.value })} />
          ) : (
            <input value={values[name] ?? ""} onChange={(event) => setValues({ ...values, [name]: event.target.value })} />
          )}
        </label>
      ))}
      <button type="submit" disabled={disabled}>{tool.approval === "none" ? "Create plan" : "Review approval"}</button>
    </form>
  );
}
